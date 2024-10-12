from sqlalchemy.types import TypeDecorator, VARCHAR
import json

class JSONEncodedDict(TypeDecorator):
    """
    将不可变的字典结构以 JSON 编码字符串的形式表示。

    此类用于在 SQLAlchemy 中将 Python 字典类型的数据存储为 VARCHAR 类型的字段。
    """

    impl = VARCHAR  # 定义使用的基础数据库类型为 VARCHAR

    def process_bind_param(self, value, dialect):
        """
        在将 Python 对象绑定到 SQL 语句的参数之前，将其转换为 JSON 编码字符串。
        
        :param value: 需要存储的字典对象
        :param dialect: 数据库方言，用于适配不同数据库（此处未使用）
        :return: JSON 编码的字符串，如果 value 为 None，返回 None
        """
        if value is not None:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        """
        在从数据库中检索数据时，将 JSON 编码字符串转换回 Python 对象。

        :param value: 数据库中存储的 JSON 字符串
        :param dialect: 数据库方言，用于适配不同数据库（此处未使用）
        :return: 转换后的字典对象，如果 value 为 None，返回 None
        """
        if value is not None:
            return json.loads(value)
