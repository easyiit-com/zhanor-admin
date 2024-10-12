import copy

class Tree:
    def __init__(self, options=None):
        """
        初始化 Tree 类的实例，设置默认配置，并合并传入的配置选项。

        :param options: 可选的配置字典
        """
        self.instance = None  # 单例模式下的 Tree 实例
        self.config = {}  # 默认配置
        self.options = {}  # 最终配置
        self.arr = []  # 存储树结构数据的数组
        self.icon = ['&nbsp&nbsp&nbsp&nbsp', '├', '└']  # 树形结构的符号
        self.nbsp = "&nbsp;"  # HTML 空格符
        self.pidname = 'pid'  # 父节点的字段名称
        self.options = dict(copy.deepcopy(self.config), **options) if options else self.config  # 深拷贝配置
    
    @staticmethod
    def instance(options=None):
        """
        获取 Tree 类的单例实例。如果实例尚未创建，则创建实例。

        :param options: 可选的配置字典
        :return: Tree 类的单例实例
        """
        if not Tree.instance:
            Tree.instance = Tree(options)
        return Tree.instance
    
    def init(self, arr=None, pidname=None, nbsp=None):
        """
        初始化树结构数据以及相关设置。

        :param arr: 树结构数据数组
        :param pidname: 父节点字段名称
        :param nbsp: HTML 空格符
        :return: Tree 实例本身
        """
        if arr:
            self.arr = arr
        if pidname:
            self.pidname = pidname
        if nbsp:
            self.nbsp = nbsp
        return self
    
    def getChild(self, myid):
        """
        获取指定 ID 的所有直接子节点。

        :param myid: 需要查找的节点 ID
        :return: 一个包含所有直接子节点的字典，以节点 ID 为键，节点内容为值
        """
        newarr = {}  # 存储找到的子节点
        for value in self.arr:
            if 'id' not in value:  # 跳过没有 ID 的节点
                continue
            if value[self.pidname] == myid:  # 如果节点的父 ID 等于传入的 ID
                newarr[value['id']] = value  # 将此节点添加到结果字典中
        return newarr  # 返回找到的子节点
    
    def getChildren(self, myid, withself=False):
        """
        获取指定 ID 的所有子节点，支持递归获取，并可选择包含自身节点。

        :param myid: 需要查找的节点 ID
        :param withself: 是否包含自身节点，默认为 False
        :return: 包含所有子节点的列表
        """
        newarr = []  # 存储子节点的列表
        for value in self.arr:
            if 'id' not in value:  # 跳过没有 ID 的节点
                continue
            if str(value[self.pidname]) == str(myid):  # 匹配父节点 ID
                newarr.append(value)  # 添加子节点
                newarr.extend(self.getChildren(value['id']))  # 递归添加子节点
            elif withself and str(value['id']) == str(myid):  # 如果包含自身，则添加
                newarr.append(value)
        return newarr  # 返回子节点列表
    
    def getChildrenIds(self, myid, withself=False):
        """
        获取指定 ID 的所有子节点的 ID。

        :param myid: 需要查找的节点 ID
        :param withself: 是否包含自身节点，默认为 False
        :return: 包含所有子节点 ID 的列表
        """
        childrenlist = self.getChildren(myid, withself)  # 获取所有子节点
        return [value['id'] for value in childrenlist]  # 返回子节点 ID 列表
    
    def getParent(self, myid):
        """
        获取指定 ID 的直接父节点。

        :param myid: 需要查找的节点 ID
        :return: 父节点的列表（最多包含一个父节点）
        """
        pid = 0  # 初始化父 ID
        newarr = []  # 存储父节点的列表
        for value in self.arr:
            if 'id' not in value:  # 跳过没有 ID 的节点
                continue
            if value['id'] == myid:  # 匹配当前节点 ID
                pid = value[self.pidname]  # 获取父 ID
                break
        if pid:  # 如果找到父节点 ID
            for value in self.arr:
                if value['id'] == pid:  # 匹配父节点 ID
                    newarr.append(value)  # 添加父节点到列表
                    break
        return newarr  # 返回父节点
    
    def getParents(self, myid, withself=False):
        """
        获取指定 ID 的所有父节点，支持递归获取，并可选择包含自身节点。

        :param myid: 需要查找的节点 ID
        :param withself: 是否包含自身节点，默认为 False
        :return: 包含所有父节点的列表
        """
        pid = 0  # 初始化父 ID
        newarr = []  # 存储父节点的列表
        for value in self.arr:
            if 'id' not in value:  # 跳过没有 ID 的节点
                continue
            if value['id'] == myid:  # 匹配当前节点 ID
                if withself:
                    newarr.append(value)  # 如果包含自身，则添加自身节点
                pid = value[self.pidname]  # 获取父节点 ID
                break
        if pid:  # 如果找到父节点 ID
            arr = self.getParents(pid, True)  # 递归获取所有父节点
            newarr.extend(arr)  # 合并父节点列表
        return newarr  # 返回父节点列表
    
    def getParentsIds(self, myid, withself=False):
        """
        获取指定 ID 的所有父节点的 ID。

        :param myid: 需要查找的节点 ID
        :param withself: 是否包含自身节点，默认为 False
        :return: 包含所有父节点 ID 的列表
        """
        parentlist = self.getParents(myid, withself)  # 获取所有父节点
        return [value['id'] for value in parentlist]  # 返回父节点 ID 列表
    
    def getTree(self, myid, itemtpl="<option value=@id @selected @disabled>@spacer@name</option>", selectedids='', disabledids='', itemprefix='', toptpl=''):
        """
        根据指定 ID 生成树形结构的 HTML 字符串。

        :param myid: 需要生成树形结构的起始节点 ID
        :param itemtpl: HTML 模板字符串
        :param selectedids: 选中的节点 ID 列表
        :param disabledids: 禁用的节点 ID 列表
        :param itemprefix: 树形结构的前缀符号
        :param toptpl: 顶层节点的特殊模板
        :return: 树形结构的 HTML 字符串
        """
        ret = ''  # 初始化返回字符串
        number = 1  # 当前处理的节点序号
        childs = self.getChild(myid)  # 获取子节点
        if childs:
            total = len(childs)  # 子节点总数
            for value in childs.values():
                id = value['id']
                j = k = ''  # 初始化符号变量
                if number == total:  # 如果是最后一个子节点
                    j += self.icon[2]  # 使用特殊符号
                    k = self.nbsp if itemprefix else ''
                else:
                    j += self.icon[1]
                    k = self.icon[0] if itemprefix else ''
                spacer = itemprefix + j if itemprefix else ''  # 生成前缀符号
                selected = 'selected' if str(id) in (selectedids if isinstance(selectedids, list) else selectedids.split(',')) else ''  # 判断是否选中
                disabled = 'disabled' if str(id) in (disabledids if isinstance(disabledids, list) else disabledids.split(',')) else ''  # 判断是否禁用
                value.update({'selected': selected, 'disabled': disabled, 'spacer': spacer})  # 更新节点信息
                value = {f"@{key}": value[key] for key in value}  # 格式化模板占位符
                nstr = (toptpl if (str(value[f"@{self.pidname}"]) == "0" or self.getChild(id)) and toptpl else itemtpl).replace("@{", "{").format(**value)  # 根据条件选择模板
                ret += nstr  # 拼接字符串
                ret += self.getTree(id, itemtpl, selectedids, disabledids, itemprefix + k + self.nbsp, toptpl)  # 递归生成子树
                number += 1
        return ret  # 返回树形结构字符串
    
    def getTreeUl(self, myid, itemtpl, selectedids='', disabledids='', wraptag='ul', wrapattr=''):
        """
        根据指定 ID 生成树形结构的 HTML 列表（使用 ul 标签）。

        :param myid: 需要生成树形结构的起始节点 ID
        :param itemtpl: HTML 模板字符串
        :param selectedids: 选中的节点 ID 列表
        :param disabledids: 禁用的节点 ID 列表
        :param wraptag: 包裹子节点的标签，默认为 ul
        :param wrapattr: 包裹标签的 HTML 属性
        :return: 树形结构的 HTML 列表
        """
        str = ''  # 初始化返回字符串
        childs = self.getChild(myid)  # 获取子节点
        if childs:
            for value in childs.values():
                id = value['id']
                del value['child']  # 删除 child 字段
                selected = 'selected' if str(id) in (selectedids if isinstance(selectedids, list) else selectedids.split(',')) else ''  # 判断是否选中
                disabled = 'disabled' if str(id) in (disabledids if isinstance(disabledids, list) else disabledids.split(',')) else ''  # 判断是否禁用
                value.update({'selected': selected, 'disabled': disabled})  # 更新节点信息
                value = {f"@{key}": value[key] for key in value}  # 格式化模板占位符
                nstr = itemtpl.format(**value)  # 格式化生成节点
                childdata = self.getTreeUl(id, itemtpl, selectedids, disabledids, wraptag, wrapattr)  # 递归获取子节点
                childlist = f"<{wraptag} {wrapattr}>{childdata}</{wraptag}>" if childdata else ""  # 包裹子节点
                str += nstr.replace("@{childlist}", childlist)  # 拼接子节点
        return str  # 返回树形结构
    
    def getTreeMenu(self, myid, itemtpl, selectedids='', disabledids='', wraptag='ul', wrapattr='', deeplevel=0):
        """
        根据指定 ID 生成树形结构的菜单 HTML。

        :param myid: 需要生成树形结构的起始节点 ID
        :param itemtpl: HTML 模板字符串
        :param selectedids: 选中的节点 ID 列表
        :param disabledids: 禁用的节点 ID 列表
        :param wraptag: 包裹子节点的标签，默认为 ul
        :param wrapattr: 包裹标签的 HTML 属性
        :param deeplevel: 当前节点的层级深度
        :return: 树形结构的菜单 HTML 字符串
        """
        str = ''  # 初始化返回字符串
        childs = self.getChild(myid)  # 获取子节点
        if childs:
            for value in childs.values():
                id = value['id']
                del value['child']  # 删除 child 字段
                selected = 'selected' if str(id) in (selectedids if isinstance(selectedids, list) else selectedids.split(',')) else ''  # 判断是否选中
                disabled = 'disabled' if str(id) in (disabledids if isinstance(disabledids, list) else disabledids.split(',')) else ''  # 判断是否禁用
                value.update({'selected': selected, 'disabled': disabled})  # 更新节点信息
                value = {f"@{key}": value[key] for key in value}  # 格式化模板占位符
                bakvalue = {k: value[k] for k in value.keys() if k in ['@url', '@caret', '@class']}  # 备份部分键值对
                value = {k: value[k] for k in value.keys() if k not in bakvalue}  # 更新剩余键值对
                nstr = itemtpl.format(**value)  # 格式化生成节点
                value.update(bakvalue)  # 恢复备份的键值对
                childdata = self.getTreeMenu(id, itemtpl, selectedids, disabledids, wraptag, wrapattr, deeplevel + 1)  # 递归获取子节点
                childlist = f"<{wraptag} {wrapattr}>{childdata}</{wraptag}>" if childdata else ""  # 包裹子节点
                childlist = childlist.replace("@class", 'last' if childlist else '')  # 替换 class 属性
                value.update({
                    "@childlist": childlist,
                    "@url": "javascript:;" if childdata or value.get('@url') is None else value['@url'],  # 判断是否有子节点
                    "@addtabs": ("" if childdata or value.get('@url') is None else (('&' if '?' in value['@url'] else '?') + "ref=addtabs")),  # 添加额外参数
                    "@caret": "<i class=\"fa fa-angle-left\"></i>" if childdata and (not value.get('@badge') or not value['@badge']) else '',  # 处理 caret 图标
                    "@badge": value['@badge'] if '@badge' in value else '',  # 处理 badge
                    "@class": (f" active" if value['selected'] else '') + (f" disabled" if value['disabled'] else '') + (f" treeview{' treeview-open' if True else ''}" if childdata else '')  # 处理 class 属性
                })
                str += nstr.format(**value)  # 拼接字符串
        return str  # 返回树形菜单 HTML
    
    def getTreeSpecial(self, myid, itemtpl1, itemtpl2, selectedids=0, disabledids=0, itemprefix=''):
        """
        根据指定 ID 生成特殊格式的树形结构 HTML。

        :param myid: 需要生成树形结构的起始节点 ID
        :param itemtpl1: 正常节点的 HTML 模板
        :param itemtpl2: 禁用节点的 HTML 模板
        :param selectedids: 选中的节点 ID 列表
        :param disabledids: 禁用的节点 ID 列表
        :param itemprefix: 树形结构的前缀符号
        :return: 树形结构的 HTML 字符串
        """
        ret = ''  # 初始化返回字符串
        number = 1  # 当前处理的节点序号
        childs = self.getChild(myid)  # 获取子节点
        if childs:
            total = len(childs)  # 子节点总数
            for id, value in childs.items():
                j = k = ''  # 初始化符号变量
                if number == total:  # 如果是最后一个子节点
                    j += self.icon[2]  # 使用特殊符号
                    k = self.nbsp if itemprefix else ''
                else:
                    j += self.icon[1]
                    k = self.icon[0] if itemprefix else ''
                spacer = itemprefix + j if itemprefix else ''  # 生成前缀符号
                selected = 'selected' if str(id) in (selectedids if isinstance(selectedids, list) else selectedids.split(',')) else ''  # 判断是否选中
                disabled = 'disabled' if str(id) in (disabledids if isinstance(disabledids, list) else disabledids.split(',')) else ''  # 判断是否禁用
                value.update({'selected': selected, 'disabled': disabled, 'spacer': spacer})  # 更新节点信息
                value = {f"@{key}": value[key] for key in value}  # 格式化模板占位符
                nstr = (itemtpl1 if "@disabled" not in value or not value[f"@disabled"] else itemtpl2).format(**value)  # 根据条件选择模板
                ret += nstr  # 拼接字符串
                ret += self.getTreeSpecial(id, itemtpl1, itemtpl2, selectedids, disabledids, itemprefix + k + self.nbsp)  # 递归生成子树
                number += 1
        return ret  # 返回树形结构 HTML
    
    def getTreeArray(self, myid, itemprefix=''):
        """
        生成树形结构的数组表示形式。

        :param myid: 需要生成树形结构的起始节点 ID
        :param itemprefix: 树形结构的前缀符号
        :return: 树形结构的数组
        """
        childs = self.getChild(myid)  # 获取子节点
        n = 0  # 初始化计数器
        data = []  # 存储树形结构的数组
        number = 1  # 当前处理的节点序号
        if childs:
            total = len(childs)  # 子节点总数
            for _, value in childs.items():
                j = k = ''  # 初始化符号变量
                if number == total:  # 如果是最后一个子节点
                    j += self.icon[2]  # 使用特殊符号
                    k = self.nbsp if itemprefix else ''
                else:
                    j += self.icon[1]
                    k = self.icon[0] if itemprefix else ''
                spacer = itemprefix + j if itemprefix else ''  # 生成前缀符号
                value['spacer'] = spacer  # 更新节点信息
                data.append(value)  # 添加节点到数组
                data[n]['childlist'] = self.getTreeArray(value['id'], itemprefix + k + self.nbsp)  # 递归生成子节点
                n += 1
                number += 1
        return data  # 返回树形结构的数组
    
    def getTreeList(self, data=None, field='name'):
        """
        将树形结构数据转换为列表形式，并按指定字段格式化。

        :param data: 树形结构数据数组
        :param field: 要格式化的字段名，默认为 'name'
        :return: 格式化后的树形结构列表
        """
        arr = []  # 初始化返回数组
        for value in data:
            childlist = value['childlist']  # 获取子节点列表
            del value['childlist']  # 删除子节点列表字段
            value[field] = value['spacer'] + ' ' + value[field]  # 格式化节点名称
            value['haschild'] = 1 if childlist else 0  # 判断是否有子节点
            if value['id']:
                arr.append(value)  # 添加节点到返回数组
            if childlist:
                arr.extend(self.getTreeList(childlist, field))  # 递归处理子节点
        return arr  # 返回格式化后的树形结构列表

    
    
    
    # options = {
    #     'pidname': 'pid',
    #     'nbsp': '&nbsp;&nbsp;&nbsp;&nbsp;',
    # }
    # data = [{
    #             'id': rule.id,
    #             'type': rule.type,
    #             'pid': rule.pid,
    #             'name': rule.name,
    #             'title': rule.title,
    #             'icon': rule.icon,
    #             'ismenu': rule.ismenu,
    #             'weigh': rule.weigh,
    #             'created_at': rule.created_at,
    #             'updated_at': rule.updated_at,
    #             'status': rule.status
    #         } for rule in admin_rule_list]
    # tree = Tree(options)
    # tree.init(data)
    # admin_rule_tree_list = tree.getTreeList(tree.getTreeArray(0),field='title')