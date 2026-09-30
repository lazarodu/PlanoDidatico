from typing import List, Dict, Any, Optional
from datetime import date, datetime, time
from src.domain.entities.notification import NotificationPreference, NotificationLog
from src.domain.repositories.interfaces import (
    INotificationRepository,
    IAtribuicaoRepository,
    IPeriodoLetivoRepository,
    IDidacticPlanRepository,
    IUsuarioRepository,
    INotifier
)


class ConfigurarCanaisUseCase:
    """UC16: Configure notification preferences per user / global"""
    def __init__(self, notification_repo: INotificationRepository):
        self.notification_repo = notification_repo

    def execute(
        self,
        usuario_id: int,
        canal_email: bool = True,
        canal_telegram: bool = False,
        chat_id_telegram: Optional[str] = None,
        horario_preferido: Optional[time] = None
    ) -> NotificationPreference:
        existing = self.notification_repo.find_preference_by_usuario_id(usuario_id)
        if existing:
            pref = existing
            pref.canal_email = canal_email
            pref.canal_telegram = canal_telegram
            pref.chat_id_telegram = chat_id_telegram
            pref.horario_preferido = horario_preferido
        else:
            pref = NotificationPreference(
                id=None,
                usuario_id=usuario_id,
                canal_email=canal_email,
                canal_telegram=canal_telegram,
                chat_id_telegram=chat_id_telegram,
                horario_preferido=horario_preferido
            )
        return self.notification_repo.save_preference(pref)


class DetectarNotificarAtrasosUseCase:
    """UC15 / RF06 / RF12: Detect delayed plan deliveries and dispatch notifications"""
    def __init__(
        self,
        periodo_repo: IPeriodoLetivoRepository,
        atribuicao_repo: IAtribuicaoRepository,
        plan_repo: IDidacticPlanRepository,
        user_repo: IUsuarioRepository,
        notification_repo: INotificationRepository,
        email_notifier: Optional[INotifier] = None,
        telegram_notifier: Optional[INotifier] = None
    ):
        self.periodo_repo = periodo_repo
        self.atribuicao_repo = atribuicao_repo
        self.plan_repo = plan_repo
        self.user_repo = user_repo
        self.notification_repo = notification_repo
        self.email_notifier = email_notifier
        self.telegram_notifier = telegram_notifier

    async def execute(self, hoje: Optional[date] = None) -> List[NotificationLog]:
        hoje_ref = hoje or date.today()
        periodo_ativo = self.periodo_repo.get_ativo()
        if not periodo_ativo:
            return []

        if hoje_ref <= periodo_ativo.data_limite_entrega_plano:
            return []

        atribuicoes = self.atribuicao_repo.list_atribuicoes_by_periodo(periodo_ativo.id)
        logs_gerados = []

        for at in atribuicoes:
            plan = self.plan_repo.find_by_professor_disciplina_periodo(at.professor_id, at.disciplina_id, periodo_ativo.id)
            if plan and not plan.esta_pendente():
                continue

            usuario = self.user_repo.find_by_id(at.professor_id)
            if not usuario:
                continue

            pref = self.notification_repo.find_preference_by_usuario_id(usuario.id)
            disciplina = self.atribuicao_repo.find_disciplina_by_id(at.disciplina_id)
            nome_disc = disciplina.nome if disciplina else "Disciplina"

            msg = (
                f"Atenção Professor(a) {usuario.nome}! O plano didático da disciplina "
                f"'{nome_disc}' ({periodo_ativo.ano}/{periodo_ativo.semestre}) está em atraso. "
                f"A data limite foi {periodo_ativo.data_limite_entrega_plano.strftime('%d/%m/%Y')}."
            )
            titulo = "Lembrete: Plano Didático em Atraso"

            if not pref or (not pref.canal_email and not pref.canal_telegram):
                log = NotificationLog(
                    id=None,
                    usuario_id=usuario.id,
                    atribuicao_id=at.id,
                    canal="NONE",
                    status="FAIL_NO_CHANNEL",
                    mensagem_erro="Nenhum canal ativo configurado",
                    criado_em=datetime.now()
                )
                logs_gerados.append(self.notification_repo.save_log(log))
                continue

            if pref.canal_email and self.email_notifier:
                try:
                    success = await self.email_notifier.enviar(usuario.email, msg, titulo)
                    st = "SUCCESS" if success else "FAIL_RETRY"
                    err = None if success else "Falha ao enviar e-mail"
                except Exception as e:
                    st = "FAIL_RETRY"
                    err = str(e)

                log = NotificationLog(
                    id=None,
                    usuario_id=usuario.id,
                    atribuicao_id=at.id,
                    canal="email",
                    status=st,
                    mensagem_erro=err,
                    criado_em=datetime.now()
                )
                logs_gerados.append(self.notification_repo.save_log(log))

            if pref.canal_telegram and pref.chat_id_telegram and self.telegram_notifier:
                try:
                    success = await self.telegram_notifier.enviar(pref.chat_id_telegram, msg, titulo)
                    st = "SUCCESS" if success else "FAIL_RETRY"
                    err = None if success else "Falha ao enviar Telegram"
                except Exception as e:
                    st = "FAIL_RETRY"
                    err = str(e)

                log = NotificationLog(
                    id=None,
                    usuario_id=usuario.id,
                    atribuicao_id=at.id,
                    canal="telegram",
                    status=st,
                    mensagem_erro=err,
                    criado_em=datetime.now()
                )
                logs_gerados.append(self.notification_repo.save_log(log))

        return logs_gerados
