import os
from typing import Optional
import httpx
from src.domain.repositories.interfaces import INotifier

class EmailSmtpNotifier(INotifier):
    """SMTP Notifier Adapter (aiosmtplib + TLS) for RF12"""
    def __init__(
        self,
        hostname: Optional[str] = None,
        port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_addr: Optional[str] = None
    ):
        self.hostname = hostname or os.getenv("SMTP_HOST", "localhost")
        self.port = int(port or os.getenv("SMTP_PORT", 587))
        self.username = username or os.getenv("SMTP_USER", "")
        self.password = password or os.getenv("SMTP_PASSWORD", "")
        self.from_addr = from_addr or os.getenv("SMTP_FROM", "noreply@cefet.br")

    async def enviar(self, destinatario: str, mensagem: str, titulo: Optional[str] = None) -> bool:
        subject = titulo or "Notificação - CEFET-MG"
        if not self.hostname or self.hostname == "localhost":
            print(f"[EmailSmtpNotifier SIMULATED] To: {destinatario} | Subject: {subject} | Body: {mensagem}")
            return True

        import aiosmtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["From"] = self.from_addr
        msg["To"] = destinatario
        msg["Subject"] = subject
        msg.set_content(mensagem)

        try:
            await aiosmtplib.send(
                msg,
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                start_tls=True
            )
            return True
        except Exception as e:
            print(f"[EmailSmtpNotifier Error] {e}")
            return False


class TelegramNotifier(INotifier):
    """Telegram Notifier Adapter (httpx -> api.telegram.org) for RF12"""
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")

    async def enviar(self, destinatario: str, mensagem: str, titulo: Optional[str] = None) -> bool:
        if not self.bot_token or self.bot_token == "dummy_token":
            print(f"[TelegramNotifier SIMULATED] ChatID: {destinatario} | Text: {mensagem}")
            return True

        text = f"<b>{titulo}</b>\n\n{mensagem}" if titulo else mensagem
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": destinatario,
            "text": text,
            "parse_mode": "HTML"
        }

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, timeout=5.0)
                return resp.status_code == 200
            except Exception as e:
                print(f"[TelegramNotifier Error] {e}")
                return False
