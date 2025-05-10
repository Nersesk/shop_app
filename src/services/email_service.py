import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ..configs import settings

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.mail_from = settings.MAIL_FROM

    @property
    def email_client(self) -> smtplib.SMTP:
        client = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
        client.ehlo()
        client.login(self.smtp_username, self.smtp_password)
        return client

    def _construct_mail_body(self, plain_body) -> str:
        return f"""<html><body>
        <div><p> {plain_body}</p></div>
        <br>
        <br>
        <div><p><strong>With regards shop administration!</p></div>
        </body></html>"""

    def send_email(self, to_email: str, subject: str, email_body: str) -> bool:
        client = self.email_client
        body = self._construct_mail_body(email_body)

        msg = MIMEMultipart()
        msg['From'] = self.mail_from
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            client.sendmail(self.mail_from, to_email, msg.as_bytes())
        except Exception as e:
            print(f"Email send failed: {e}")
            return False
        else:
            return True

    async def send_email_async(self, to_email: str, subject: str, email_body: str) -> bool:
        return await asyncio.to_thread(self.send_email,
                                       to_email,
                                       subject,
                                       email_body)


email_service = EmailService()