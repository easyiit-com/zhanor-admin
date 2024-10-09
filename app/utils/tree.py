import copy
class Tree:
    def __init__(self, options=None):
        self.instance = None
        self.config = {}
        self.options = {}
        self.arr = []
        self.icon = ['&nbsp&nbsp&nbsp&nbsp', '├', '└']
        self.nbsp = "&nbsp;"
        self.pidname = 'pid'
        if options:
            self.options = dict(copy.deepcopy(self.config), **options)
        else:
            self.options = self.config
    
    @staticmethod
    def instance(options=None):
        if not Tree.instance:
            Tree.instance = Tree(options)
        return Tree.instance
    
    def init(self, arr=None, pidname=None, nbsp=None):
        if arr:
            self.arr = arr
        if pidname:
            self.pidname = pidname
        if nbsp:
            self.nbsp = nbsp
        return self
    
    def getChild(self, myid):
        newarr = {}
        for value in self.arr:
            if 'id' not in value:
                continue
            if value[self.pidname] == myid:
                newarr[value['id']] = value
        return newarr
    
    def getChildren(self, myid, withself=False):
        newarr = []
        for value in self.arr:
            if 'id' not in value:
                continue
            if str(value[self.pidname]) == str(myid):
                newarr.append(value)
                newarr.extend(self.getChildren(value['id']))
            elif withself and str(value['id']) == str(myid):
                newarr.append(value)
        return newarr
    
    def getChildrenIds(self, myid, withself=False):
        childrenlist = self.getChildren(myid, withself)
        childrenids = []
        for value in childrenlist:
            childrenids.append(value['id'])
        return childrenids
    
    def getParent(self, myid):
        pid = 0
        newarr = []
        for value in self.arr:
            if 'id' not in value:
                continue
            if value['id'] == myid:
                pid = value[self.pidname]
                break
        if pid:
            for value in self.arr:
                if value['id'] == pid:
                    newarr.append(value)
                    break
        return newarr
    
    def getParents(self, myid, withself=False):
        pid = 0
        newarr = []
        for value in self.arr:
            if 'id' not in value:
                continue
            if value['id'] == myid:
                if withself:
                    newarr.append(value)
                pid = value[self.pidname]
                break
        if pid:
            arr = self.getParents(pid, True)
            newarr.extend(arr)
        return newarr
    
    def getParentsIds(self, myid, withself=False):
        parentlist = self.getParents(myid, withself)
        parentsids = []
        for value in parentlist:
            parentsids.append(value['id'])
        return parentsids
    
    def getTree(self, myid, itemtpl="<option value=@id @selected @disabled>@spacer@name</option>", selectedids='', disabledids='', itemprefix='', toptpl=''):
        ret = ''
        number = 1
        childs = self.getChild(myid)
        if childs:
            total = len(childs)
            for value in childs.values():
                id = value['id']
                j = k = ''
                if number == total:
                    j += self.icon[2]
                    k = self.nbsp if itemprefix else ''
                else:
                    j += self.icon[1]
                    k = self.icon[0] if itemprefix else ''
                spacer = itemprefix + j if itemprefix else ''
                selected = 'selected' if selectedids and str(id) in (selectedids if isinstance(selectedids, list) else selectedids.split(',')) else ''
                disabled = 'disabled' if disabledids and str(id) in (disabledids if isinstance(disabledids, list) else disabledids.split(',')) else ''
                value = dict(value, selected=selected, disabled=disabled, spacer=spacer)
                value = {f"@{key}": value[key] for key in value}
                nstr = (toptpl if (str(value[f"@{self.pidname}"]) == "0" or self.getChild(id)) and toptpl else itemtpl).replace("@{", "{").format(**value)
                ret += nstr
                ret += self.getTree(id, itemtpl, selectedids, disabledids, itemprefix + k + self.nbsp, toptpl)
                number += 1
        return ret
    
    def getTreeUl(self, myid, itemtpl, selectedids='', disabledids='', wraptag='ul', wrapattr=''):
        str = ''
        childs = self.getChild(myid)
        if childs:
            for value in childs.values():
                id = value['id']
                del value['child']
                selected = 'selected' if selectedids and str(id) in (selectedids if isinstance(selectedids, list) else selectedids.split(',')) else ''
                disabled = 'disabled' if disabledids and str(id) in (disabledids if isinstance(disabledids, list) else disabledids.split(',')) else ''
                value = dict(value, selected=selected, disabled=disabled)
                value = {f"@{key}": value[key] for key in value}
                nstr = itemtpl.format(**value)
                childdata = self.getTreeUl(id, itemtpl, selectedids, disabledids, wraptag, wrapattr)
                childlist = f"<{wraptag} {wrapattr}>{childdata}</{wraptag}>" if childdata else ""
                str += nstr.replace("@{childlist}", childlist)
        return str
    
    def getTreeMenu(self, myid, itemtpl, selectedids='', disabledids='', wraptag='ul', wrapattr='', deeplevel=0):
        str = ''
        childs = self.getChild(myid)
        if childs:
            for value in childs.values():
                id = value['id']
                del value['child']
                selected = 'selected' if str(id) in (selectedids if isinstance(selectedids, list) else selectedids.split(',')) else ''
                disabled = 'disabled' if str(id) in (disabledids if isinstance(disabledids, list) else disabledids.split(',')) else ''
                value = dict(value, selected=selected, disabled=disabled)
                value = {f"@{key}": value[key] for key in value}
                bakvalue = {k: value[k] for k in value.keys() if k in ['@url', '@caret', '@class']}
                value = {k: value[k] for k in value.keys() if k not in bakvalue}
                nstr = itemtpl.format(**value)
                value.update(bakvalue)
                childdata = self.getTreeMenu(id, itemtpl, selectedids, disabledids, wraptag, wrapattr, deeplevel + 1)
                childlist = f"<{wraptag} {wrapattr}>{childdata}</{wraptag}>" if childdata else ""
                childlist = childlist.replace("@class", 'last' if childlist else '')
                value.update({
                    "@childlist": childlist,
                    "@url": "javascript:;" if childdata or value.get('@url') is None else value['@url'],
                    "@addtabs": ("" if childdata or value.get('@url') is None else (('&' if '?' in value['@url'] else '?') + "ref=addtabs")),
                    "@caret": "<i class=\"fa fa-angle-left\"></i>" if childdata and (not value.get('@badge') or not value['@badge']) else '',
                    "@badge": value['@badge'] if '@badge' in value else '',
                    "@class": (f" active" if value['selected'] else '') + (f" disabled" if value['disabled'] else '') + (f" treeview{' treeview-open' if True else ''}" if childdata else '')
                })
                str += nstr.format(**value)
        return str
    
    def getTreeSpecial(self, myid, itemtpl1, itemtpl2, selectedids=0, disabledids=0, itemprefix=''):
        ret = ''
        number = 1
        childs = self.getChild(myid)
        if childs:
            total = len(childs)
            for id,value in childs.items():
                j = k = ''
                if number == total:
                    j += self.icon[2]
                    k = self.nbsp if itemprefix else ''
                else:
                    j += self.icon[1]
                    k = self.icon[0] if itemprefix else ''
                spacer = itemprefix + j if itemprefix else ''
                selected = 'selected' if selectedids and str(id) in (selectedids if isinstance(selectedids, list) else selectedids.split(',')) else ''
                disabled = 'disabled' if disabledids and str(id) in (disabledids if isinstance(disabledids, list) else disabledids.split(',')) else ''
                value = dict(value, selected=selected, disabled=disabled, spacer=spacer)
                value = {f"@{key}": value[key] for key in value}
                nstr = (itemtpl1 if "@disabled" not in value or not value[f"@disabled"] else itemtpl2).format(**value)
                ret += nstr
                ret += self.getTreeSpecial(id, itemtpl1, itemtpl2, selectedids, disabledids, itemprefix + k + self.nbsp)
                number += 1
        return ret
    
    def getTreeArray(self, myid, itemprefix=''):
        childs = self.getChild(myid)
        n = 0
        data = []
        number = 1
        if childs:
            total = len(childs)
            for _, value in childs.items():
                j = k = ''
                if number == total:
                    j += self.icon[2]
                    k = self.nbsp if itemprefix else ''
                else:
                    j += self.icon[1]
                    k = self.icon[0] if itemprefix else ''
                spacer = itemprefix + j if itemprefix else ''
                value['spacer'] = spacer
                data.append(value)
                data[n]['childlist'] = self.getTreeArray(value['id'], itemprefix + k + self.nbsp)
                n += 1
                number += 1
        return data
    
    def getTreeList(self, data=None, field='name'):
        arr = []
        for value in data:
            childlist = value['childlist']
            del value['childlist']
            value[field] = value['spacer'] + ' ' + value[field]
            value['haschild'] = 1 if childlist else 0
            if value['id']:
                arr.append(value)
            if childlist:
                arr.extend(self.getTreeList(childlist, field))
        return arr
    
    
    
    
    
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