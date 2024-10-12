from app.core.utils.logger import logger
import smtplib
from email.mime.text import MIMEText

class MailService:
    """
    邮件服务类，用于通过SMTP服务器发送邮件。
    """

    def __init__(self, smtp_host, smtp_port, smtp_username, smtp_password, use_tls=True):
        """
        初始化邮件服务类。

        :param smtp_host: SMTP服务器主机地址
        :param smtp_port: SMTP服务器端口
        :param smtp_username: SMTP登录用户名
        :param smtp_password: SMTP登录密码
        :param use_tls: 是否使用TLS加密，默认使用
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.use_tls = use_tls

    def send_email(self, subject, body, sender, recipients):
        """
        发送邮件方法。

        :param subject: 邮件主题
        :param body: 邮件正文
        :param sender: 发件人邮箱地址
        :param recipients: 收件人邮箱地址列表
        :return: 发送成功返回True，失败返回False
        """
        # 创建邮件正文
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)  # 收件人列表

        try:
            # 使用SMTP服务器发送邮件
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.ehlo()  # 向服务器标识客户端身份
                    server.starttls()  # 启用TLS加密
                    server.ehlo()  # 再次ehlo以更新服务器状态

                # 登录SMTP服务器
                server.login(self.smtp_username, self.smtp_password)
                
                # 发送邮件
                server.sendmail(sender, recipients, msg.as_string())
            
            logger.info("邮件发送成功")  # 成功日志记录
            return True
        except smtplib.SMTPException as e:
            # 记录错误日志
            logger.error(f"Error: 无法发送邮件 {e}")
            return False
