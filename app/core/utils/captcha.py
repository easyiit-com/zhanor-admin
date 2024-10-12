from captcha.image import ImageCaptcha  # 验证码图像生成器
import random  # 随机模块

class CaptchaManager:
    """
    验证码管理类，生成验证码文本并根据文本生成相应的验证码图像。
    支持字母和数字组合的验证码。
    """

    @staticmethod
    def generate_captcha_text(length=6):
        """
        生成随机验证码文本，默认长度为6位字符，包含字母和数字。
        
        :param length: 验证码字符长度，默认6位
        :return: 随机生成的验证码文本
        """
        characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'  # 字母和数字字符集
        return ''.join(random.choice(characters) for _ in range(length))  # 随机选择字符生成验证码

    @staticmethod
    def generate_captcha_image(text):
        """
        根据传入的验证码文本生成验证码图像。
        
        :param text: 验证码文本
        :return: 生成的验证码图像数据和对应的验证码文本
        """
        image = ImageCaptcha()  # 创建验证码图像生成器实例
        data = image.generate(text)  # 根据文本生成图像数据
        return data, text  # 返回图像数据和验证码文本
