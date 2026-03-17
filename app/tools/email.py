import asyncio
from typing import Optional
from .base import Tool, ToolType


class EmailTool(Tool):
    """Email sending tool"""

    def __init__(self):
        super().__init__(
            name="emailTool",
            description="一个用于发送邮件的工具，可以通过邮箱发送邮件给指定的收件人。邮件发送采用异步方式，不会阻塞工具调用。",
            tool_type=ToolType.OPTIONAL,
            func=self._send_email
        )

    async def _send_email_async(self, to: str, subject: str, content: str) -> str:
        """Send email asynchronously"""
        try:
            from app.config import settings
            import aiosmtplib
            from email.message import EmailMessage

            # Validate parameters
            if not to or not to.strip():
                return "错误：收件人邮箱地址不能为空"
            if not subject or not subject.strip():
                return "错误：邮件主题不能为空"
            if not content or not content.strip():
                return "错误：邮件内容不能为空"

            if "@" not in to:
                return "错误：收件人邮箱地址格式不正确"

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

            return f"邮件已发送！\n收件人: {to}\n主题: {subject}"
        except Exception as e:
            return f"错误：邮件发送失败 - {str(e)}"

    def _send_email(self, to: str, subject: str, content: str) -> str:
        """Send email (wrapper for async)"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._send_email_async(to, subject, content))
