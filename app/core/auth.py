from flask import request
from flask_login import LoginManager, current_user
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

from urllib.parse import urlparse, urljoin

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

login_manager = LoginManager()
jwt = JWTManager()
