import logging
import smtplib
from email.mime.text import MIMEText

class MailService:
    def __init__(self, smtp_host, smtp_port, smtp_username, smtp_password, use_tls=True):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.use_tls = use_tls

    def send_email(self, subject, body, sender, recipients):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.ehlo()  # 先执行ehlo命令
                    server.starttls()  # 启用TLS加密
                    server.ehlo()  # 再次ehlo以更新服务器状态
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(sender, recipients, msg.as_string())
            return True
        except smtplib.SMTPException as e:
            logging.error(f"Error: 无法发送邮件{e}")
        return False

       