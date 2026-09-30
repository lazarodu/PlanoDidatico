from dataclasses import dataclass
from typing import Optional, List
from datetime import time, datetime

@dataclass
class NotificationPreference:
    id: Optional[int]
    usuario_id: int
    canal_email: bool = True
    canal_telegram: bool = False
    chat_id_telegram: Optional[str] = None
    horario_preferido: Optional[time] = None

    def ativar_canal_email(self) -> None:
        self.canal_email = True

    def desativar_canal_email(self) -> None:
        self.canal_email = False

    def ativar_canal_telegram(self, chat_id: str) -> None:
        self.canal_telegram = True
        self.chat_id_telegram = chat_id

    def desativar_canal_telegram(self) -> None:
        self.canal_telegram = False
        self.chat_id_telegram = None

    def pode_receber_via_email(self) -> bool:
        return self.canal_email

    def pode_receber_via_telegram(self) -> bool:
        return self.canal_telegram and bool(self.chat_id_telegram)

    def get_chat_id_telegram(self) -> Optional[str]:
        return self.chat_id_telegram


@dataclass
class NotificationLog:
    id: Optional[int]
    usuario_id: int
    atribuicao_id: Optional[int]
    canal: str  # email, telegram
    status: str  # SENT, FAIL_NO_CHANNEL, FAIL_RETRY, SUCCESS
    mensagem_erro: Optional[str] = None
    criado_em: Optional[datetime] = None
