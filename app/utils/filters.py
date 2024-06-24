def get_type(value):
    lenth = len(value)
    t =  type(value).__name__
    return f'{t}({lenth})'