import json
from app.models.admin_rule import AdminRule
from app.models.user_rule import UserRule
from collections import defaultdict

def process_admin_rules(database_rules):
    admin_rules_dicts = []
    json_data = ""

    for admin_rule in database_rules:
        admin_rule_dict = AdminRule.to_dict(admin_rule)
        children_query = (
            AdminRule.query
            .filter(AdminRule.pid == admin_rule.id, AdminRule.type == "menu")
            .order_by(AdminRule.id.asc())
        )
        admin_rule_dict["child"] = [
            AdminRule.to_dict(child) for child in children_query.all()
        ]
        url_paths = [child["url_path"] for child in admin_rule_dict["child"]]
        admin_rule_dict["url_paths"] = url_paths
        admin_rules_dicts.append(admin_rule_dict)

    json_data = json.dumps(admin_rules_dicts, default=str)
    # cache.set("admin_rules", json_data, expire=3600 * 24 * 7)
    return admin_rules_dicts


def process_user_rules(database_rules):
    user_rules_dicts = []
    json_data = ""

    for user_rule in database_rules:
        user_rule_dict = UserRule.to_dict(user_rule)
        children_query = (
            UserRule.query
            .filter(UserRule.pid == user_rule.id, UserRule.type == "menu")
            .order_by(UserRule.id.asc())
        )
        user_rule_dict["child"] = [
            UserRule.to_dict(child) for child in children_query.all()
        ]
        url_paths = [child["url_path"] for child in user_rule_dict["child"]]
        user_rule_dict["url_paths"] = url_paths
        user_rules_dicts.append(user_rule_dict)

    json_data = json.dumps(user_rules_dicts, default=str)
    # cache.set("user_rules", json_data, expire=3600 * 24 * 7)
    return user_rules_dicts

def organize_admin_rules(admin_rules):
    # 创建一个字典来存储条目
    rules_dict = {rule.id: rule for rule in admin_rules}

    # 初始化每个条目的 child 字段
    for rule in admin_rules:
        rule.child = []

    # 遍历所有条目，将子项添加到父项的 child 字段中
    for rule in admin_rules:
        if rule.pid in rules_dict:  # 如果父 ID 存在于字典中
            rules_dict[rule.pid].child.append(rule)

    # 获取顶层条目（没有父 ID 的条目）
    top_level_rules = [rule for rule in admin_rules if rule.pid not in rules_dict]

    return top_level_rules

def organize_user_rules(user_rules):
    # 创建一个字典来存储条目
    rules_dict = {rule.id: rule for rule in user_rules}

    # 初始化每个条目的 child 字段
    for rule in user_rules:
        rule.child = []

    # 遍历所有条目，将子项添加到父项的 child 字段中
    for rule in user_rules:
        if rule.pid in rules_dict:  # 如果父 ID 存在于字典中
            rules_dict[rule.pid].child.append(rule)

    # 获取顶层条目（没有父 ID 的条目）
    top_level_rules = [rule for rule in user_rules if rule.pid not in rules_dict]

    return top_level_rules