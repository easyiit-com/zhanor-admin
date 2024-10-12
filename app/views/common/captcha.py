
from flask import Blueprint, Response, session
from app.core.utils.captcha import CaptchaManager

bp = Blueprint("captcha", __name__)
@bp.route('/captcha.png')
def captcha():
    captcha_text = CaptchaManager.generate_captcha_text()
    session['captcha'] = captcha_text
    captcha_image, _ = CaptchaManager.generate_captcha_image(captcha_text)
    return Response(captcha_image, mimetype='image/png')