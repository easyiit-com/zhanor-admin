"""
This file is based on the original Flask-Login project, copyrighted by Matthew Frazier.
The original project's license is the MIT License, see https://github.com/maxcountryman/flask-login for details.
"""


from flask.testing import FlaskClient


class AdminLoginClient(FlaskClient):
    """
    A Admin test client that knows how to log in admins
    using the Admin-Login extension.
    """

    def __init__(self, *args, **kwargs):
        admin = kwargs.pop("admin", None)
        fresh = kwargs.pop("fresh_login", True)

        super().__init__(*args, **kwargs)

        if admin:
            with self.session_transaction() as sess:
                sess["_admin_id"] = admin.get_id()
                sess["_fresh"] = fresh
