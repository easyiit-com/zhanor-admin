
from flask import Blueprint, Response, session
from app.utils.captcha import generate_captcha_image, generate_captcha_text

bp = Blueprint("captcha", __name__)
@bp.route('/captcha.png')
def captcha():
    captcha_text = generate_captcha_text()
    session['captcha'] = captcha_text
    captcha_image, _ = generate_captcha_image(captcha_text)
    return Response(captcha_image, mimetype='image/png')