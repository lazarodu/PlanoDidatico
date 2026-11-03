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


class EmailApiNotifier(INotifier):
    """Notificador por API HTTP (Resend/Brevo).

    Usado em ambientes que bloqueiam as portas SMTP, como o plano Free do
    Render. Escolha o provedor com ``EMAIL_PROVIDER`` e informe a chave em
    ``EMAIL_API_KEY``. Sem chave, o envio é simulado (útil no desenvolvimento).
    """

    RESEND_URL = "https://api.resend.com/emails"
    BREVO_URL = "https://api.brevo.com/v3/smtp/email"

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        from_addr: Optional[str] = None,
        from_name: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.provider = (provider or os.getenv("EMAIL_PROVIDER", "resend")).strip().lower()
        self.api_key = api_key if api_key is not None else os.getenv("EMAIL_API_KEY", "")
        self.from_addr = from_addr or os.getenv("EMAIL_FROM", "noreply@cefet.br")
        self.from_name = from_name or os.getenv("EMAIL_FROM_NAME", "Planos Didáticos CEFET-MG")
        self.client = client

    async def enviar(self, destinatario: str, mensagem: str, titulo: Optional[str] = None) -> bool:
        subject = titulo or "Notificação - CEFET-MG"
        if not self.api_key:
            print(f"[EmailApiNotifier SIMULATED] To: {destinatario} | Subject: {subject} | Body: {mensagem}")
            return True

        if self.provider == "resend":
            url = self.RESEND_URL
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "from": f"{self.from_name} <{self.from_addr}>" if self.from_name else self.from_addr,
                "to": [destinatario],
                "subject": subject,
                "text": mensagem,
            }
        elif self.provider == "brevo":
            url = self.BREVO_URL
            headers = {"api-key": self.api_key}
            payload = {
                "sender": {"name": self.from_name, "email": self.from_addr},
                "to": [{"email": destinatario}],
                "subject": subject,
                "textContent": mensagem,
            }
        else:
            print(f"[EmailApiNotifier Error] Provedor desconhecido: {self.provider}")
            return False

        client = self.client or httpx.AsyncClient(timeout=10.0)
        try:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code in (200, 201, 202):
                return True
            print(
                f"[EmailApiNotifier Error] {self.provider} HTTP "
                f"{response.status_code}: {response.text[:500]}"
            )
            return False
        except Exception as e:
            print(f"[EmailApiNotifier Error] {e}")
            return False
        finally:
            if self.client is None:
                await client.aclose()


def build_email_notifier() -> INotifier:
    """Usa a API HTTP quando configurada; caso contrário, mantém o SMTP."""
    if os.getenv("EMAIL_API_KEY", "").strip():
        return EmailApiNotifier()
    return EmailSmtpNotifier()


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
