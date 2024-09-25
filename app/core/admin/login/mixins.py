"""
This file is based on the original Flask-Login project, copyrighted by Matthew Frazier.
The original project's license is the MIT License, see https://github.com/maxcountryman/flask-login for details.
"""


class AdminMixin:
    """
    这个类提供了 Flask-Login 期望管理员对象具有的方法的默认实现。
    """

    # Python 3 如果我们重写 __eq__，会隐式将 __hash__ 设置为 None
    # 我们将其恢复为默认实现
    __hash__ = object.__hash__

    @property
    def is_active(self):
        """
        检查用户是否处于活跃状态。
        通常返回 True，表示用户可以正常使用应用程序。
        """
        return True

    @property
    def is_authenticated(self):
        """
        检查用户是否已通过身份验证。
        这个属性会返回 is_active 的值，因此活跃用户被视为已认证。
        """
        return self.is_active

    @property
    def is_anonymous(self):
        """
        检查用户是否是匿名用户。
        对于此类用户，返回 False，表示他们不是匿名用户。
        """
        return False

    def get_id(self):
        """
        获取用户的唯一标识符。
        如果对象具有 `id` 属性，则返回其字符串形式。
        否则，抛出 NotImplementedError，提示子类重写此方法。
        """
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError("没有 `id` 属性 - 请重写 `get_id`") from None

    def __eq__(self, other):
        """
        使用 `get_id` 方法检查两个 `AdminMixin` 对象的相等性。
        如果传入的对象也是 `AdminMixin` 类型，则比较它们的 ID。
        否则返回 NotImplemented，表示不支持的比较。
        """
        if isinstance(other, AdminMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        使用 `get_id` 方法检查两个 `AdminMixin` 对象的不相等性。
        首先调用 `__eq__` 方法进行比较。
        如果结果是 NotImplemented，返回 NotImplemented。
        否则，返回相等结果的否定值。
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


class AnonymousAdminMixin:
    """
    这是表示匿名管理员的默认对象。
    """

    @property
    def is_authenticated(self):
        """
        检查用户是否已通过身份验证。
        对于匿名用户，这个属性返回 False，表示他们未被认证。
        """
        return False

    @property
    def is_active(self):
        """
        检查用户是否处于活跃状态。
        对于匿名用户，返回 False，表示他们不是活跃用户。
        """
        return False

    @property
    def is_anonymous(self):
        """
        检查用户是否是匿名用户。
        对于此类用户，返回 True，表示他们是匿名用户。
        """
        return True

    def get_id(self):
        """
        获取匿名用户的唯一标识符。
        对于匿名用户，这个方法不返回任何值。
        """
        return
