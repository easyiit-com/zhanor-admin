import json
from app.models.admin_rule import AdminRule
from app.models.user_rule import UserRule
from collections import defaultdict

def organize_admin_rules(admin_rules):
    # 创建一个字典来存储条目
    rules_dict = {rule.id: rule for rule in admin_rules}

    # 初始化每个条目的 child 和 url_paths 字段
    for rule in admin_rules:
        rule.child = []
        rule.url_paths = ""

    # 遍历所有条目，将子项添加到父项的 child 字段中
    for rule in admin_rules:
        if rule.pid in rules_dict:  # 如果父 ID 存在于字典中
            rules_dict[rule.pid].child.append(rule)

    # 获取顶层条目（没有父 ID 的条目）
    top_level_rules = [rule for rule in admin_rules if rule.pid not in rules_dict]

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
     # cache.set("admin_rules", json_data, expire=3600 * 24 * 7)
    return top_level_rules

def organize_user_rules(admin_rules):
    # 创建一个字典来存储条目
    rules_dict = {rule.id: rule for rule in admin_rules}

    # 初始化每个条目的 child 和 url_paths 字段
    for rule in admin_rules:
        rule.child = []
        rule.url_paths = ""

    # 遍历所有条目，将子项添加到父项的 child 字段中
    for rule in admin_rules:
        if rule.pid in rules_dict:  # 如果父 ID 存在于字典中
            rules_dict[rule.pid].child.append(rule)

    # 获取顶层条目（没有父 ID 的条目）
    top_level_rules = [rule for rule in admin_rules if rule.pid not in rules_dict]

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
     # cache.set("admin_rules", json_data, expire=3600 * 24 * 7)
    return top_level_rules