class UserMixin:
    """
    提供 Flask-Login 所需的用户对象方法的默认实现。
    """

    # Python 3 中，如果我们重写了 __eq__，__hash__ 会隐式设置为 None
    # 这里将其恢复为默认实现
    __hash__ = object.__hash__

    @property
    def is_active(self):
        """检查用户是否激活。"""
        return True

    @property
    def is_authenticated(self):
        """检查用户是否已认证。"""
        return self.is_active

    @property
    def is_anonymous(self):
        """检查用户是否为匿名用户。"""
        return False

    def get_id(self):
        """返回用户的唯一标识符 ID，如果没有则抛出异常。"""
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError("没有 `id` 属性 - 请重写 `get_id`") from None

    def __eq__(self, other):
        """
        使用 `get_id` 检查两个 `UserMixin` 对象的相等性。
        """
        if isinstance(other, UserMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        使用 `get_id` 检查两个 `UserMixin` 对象的非相等性。
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


class AnonymousUserMixin:
    """
    表示匿名用户的默认对象。
    """

    @property
    def is_authenticated(self):
        """检查匿名用户是否已认证。"""
        return False

    @property
    def is_active(self):
        """检查匿名用户是否激活。"""
        return False

    @property
    def is_anonymous(self):
        """检查是否为匿名用户。"""
        return True

    def get_id(self):
        """返回匿名用户的唯一标识符，通常为 None。"""
        return None
