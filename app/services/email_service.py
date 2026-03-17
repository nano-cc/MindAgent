import asyncio
from app.config import settings
import aiosmtplib
from email.message import EmailMessage


class EmailService:
    """Email service for sending emails"""

    @staticmethod
    async def send_email_async(to: str, subject: str, content: str) -> bool:
        """Send email asynchronously"""
        try:
            # Validate parameters
            if not to or not to.strip():
                raise ValueError("收件人邮箱地址不能为空")
            if not subject or not subject.strip():
                raise ValueError("邮件主题不能为空")
            if not content or not content.strip():
                raise ValueError("邮件内容不能为空")

            if "@" not in to:
                raise ValueError("收件人邮箱地址格式不正确")

            # Create message
            msg = EmailMessage()
            msg["From"] = settings.EMAIL_FROM
            msg["To"] = to
            msg["Subject"] = subject
            msg.set_content(content, charset="utf-8")

            # Send email
            smtp = aiosmtplib.SMTP(
                hostname=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                use_tls=True
            )
            await smtp.connect()
            await smtp.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            await smtp.send_message(msg)
            await smtp.quit()

            return True
        except Exception as e:
            print(f"Email send error: {e}")
            return False

    @staticmethod
    def send_email(to: str, subject: str, content: str) -> bool:
        """Send email (synchronous wrapper)"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            EmailService.send_email_async(to, subject, content)
        )
