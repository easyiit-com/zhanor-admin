def get_type(value):
    """
    获取输入值的类型名称以及长度信息（适用于有长度属性的对象）。
    
    :param value: 需要获取类型和长度的对象
    :return: 返回包含类型名称和长度的字符串，如 "str(5)"
    """
    length = len(value)  # 获取对象的长度
    value_type = type(value).__name__  # 获取对象的类型名称
    return f'{value_type}({length})'  # 返回类型名称和长度
