def organize_rules(rules):
    """
    组织规则条目，按层级结构添加子项，并收集 url_paths。
    :param rules: 规则对象列表
    :return: 顶层规则条目列表
    """
    # 创建一个字典来存储条目，键为规则的 ID
    rules_dict = {rule.id: rule for rule in rules}

    # 初始化每个条目的 child 和 url_paths 字段
    for rule in rules:
        rule.child = []
        rule.url_paths = ""

    # 遍历所有条目，将子项添加到父项的 child 字段中
    for rule in rules:
        if rule.pid in rules_dict:  # 如果父 ID 存在于字典中
            rules_dict[rule.pid].child.append(rule)

    # 获取顶层条目（没有父 ID 的条目）
    top_level_rules = [rule for rule in rules if rule.pid not in rules_dict]

    # 定义一个递归函数以收集 url_paths
    def collect_url_paths(rule):
        paths = []
        for child in rule.child:
            paths.append(child.url_path)
            paths.extend(collect_url_paths(child))  # 递归收集子项的 url_path
        return paths

    # 为顶层条目设置 url_paths 属性
    for rule in top_level_rules:
        all_paths = collect_url_paths(rule)
        rule.url_paths = ','.join(all_paths)
    
    return top_level_rules

def organize_admin_rules(admin_rules):
    """
    组织管理员规则。
    :param admin_rules: 管理员规则对象列表
    :return: 顶层管理员规则条目列表
    """
    return organize_rules(admin_rules)

def organize_user_rules(user_rules):
    """
    组织用户规则。
    :param user_rules: 用户规则对象列表
    :return: 顶层用户规则条目列表
    """
    return organize_rules(user_rules)
