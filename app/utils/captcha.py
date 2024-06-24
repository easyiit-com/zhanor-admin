from captcha.image import ImageCaptcha
import string
import random

def generate_captcha_text():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))  # 生成4位验证码

def generate_captcha_image(text):
    image = ImageCaptcha()
    data = image.generate(text)
    return data, text