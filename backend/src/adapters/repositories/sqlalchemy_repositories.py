from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.entities.user import Usuario, Professor
from src.domain.entities.didactic_plan import DidacticPlan
from src.domain.entities.atribuicao import Disciplina, PeriodoLetivo, AtribuicaoProfessorDisciplina, DiaLetivoDisciplina
from src.domain.entities.notification import NotificationPreference, NotificationLog
from src.domain.value_objects.field_config import CampoFormulario
from src.domain.repositories.interfaces import (
    IUsuarioRepository,
    IDidacticPlanRepository,
    IAtribuicaoRepository,
    IPeriodoLetivoRepository,
    INotificationRepository
)
from src.adapters.repositories.models import (
    UsuarioModel,
    ProfessorModel,
    DisciplinaModel,
    PeriodoLetivoModel,
    AtribuicaoModel,
    DiaLetivoModel,
    DidacticPlanModel,
    CampoFormularioModel,
    NotificationPreferenceModel,
    NotificationLogModel
)


class SQLAlchemyUserRepository(IUsuarioRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, usuario: Usuario) -> Usuario:
        if usuario.id:
            model = self.session.query(UsuarioModel).filter(UsuarioModel.id == usuario.id).first()
            if model:
                model.nome = usuario.nome
                model.email = usuario.email
                model.tipo = usuario.tipo
        else:
            model = UsuarioModel(nome=usuario.nome, email=usuario.email, tipo=usuario.tipo)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        usuario.id = model.id
        return usuario

    def find_by_id(self, usuario_id: int) -> Optional[Usuario]:
        m = self.session.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        if m:
            return Usuario(id=m.id, nome=m.nome, email=m.email, tipo=m.tipo)
        return None

    def find_by_email(self, email: str) -> Optional[Usuario]:
        m = self.session.query(UsuarioModel).filter(UsuarioModel.email == email).first()
        if m:
            return Usuario(id=m.id, nome=m.nome, email=m.email, tipo=m.tipo)
        return None

    def list_all(self) -> List[Usuario]:
        models = self.session.query(UsuarioModel).all()
        return [Usuario(id=m.id, nome=m.nome, email=m.email, tipo=m.tipo) for m in models]

    def save_professor(self, professor: Professor) -> Professor:
        m = self.session.query(ProfessorModel).filter(ProfessorModel.usuario_id == professor.usuario_id).first()
        if m:
            m.matricula = professor.matricula
            m.departamento = professor.departamento
        else:
            m = ProfessorModel(usuario_id=professor.usuario_id, matricula=professor.matricula, departamento=professor.departamento)
            self.session.add(m)
        self.session.commit()
        return professor

    def find_professor_by_id(self, usuario_id: int) -> Optional[Professor]:
        m = self.session.query(ProfessorModel).filter(ProfessorModel.usuario_id == usuario_id).first()
        if m:
            return Professor(usuario_id=m.usuario_id, matricula=m.matricula, departamento=m.departamento)
        return None


class SQLAlchemyDidacticPlanRepository(IDidacticPlanRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, plan: DidacticPlan) -> DidacticPlan:
        if plan.id:
            m = self.session.query(DidacticPlanModel).filter(DidacticPlanModel.id == plan.id).first()
            if m:
                m.professor_id = plan.professor_id
                m.disciplina_id = plan.disciplina_id
                m.periodo_letivo_id = plan.periodo_letivo_id
                m.status = plan.status
                m.data_entrega = plan.data_entrega
                m.campos = plan.campos
        else:
            m = DidacticPlanModel(
                professor_id=plan.professor_id,
                disciplina_id=plan.disciplina_id,
                periodo_letivo_id=plan.periodo_letivo_id,
                status=plan.status,
                data_entrega=plan.data_entrega,
                campos=plan.campos
            )
            self.session.add(m)
        self.session.commit()
        self.session.refresh(m)
        plan.id = m.id
        return plan

    def find_by_id(self, plan_id: int) -> Optional[DidacticPlan]:
        m = self.session.query(DidacticPlanModel).filter(DidacticPlanModel.id == plan_id).first()
        if m:
            return DidacticPlan(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, status=m.status,
                data_entrega=m.data_entrega, campos=m.campos or {}
            )
        return None

    def find_by_professor_disciplina_periodo(self, professor_id: int, disciplina_id: int, periodo_letivo_id: int) -> Optional[DidacticPlan]:
        m = self.session.query(DidacticPlanModel).filter(
            DidacticPlanModel.professor_id == professor_id,
            DidacticPlanModel.disciplina_id == disciplina_id,
            DidacticPlanModel.periodo_letivo_id == periodo_letivo_id
        ).first()
        if m:
            return DidacticPlan(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, status=m.status,
                data_entrega=m.data_entrega, campos=m.campos or {}
            )
        return None

    def list_by_professor(self, professor_id: int) -> List[DidacticPlan]:
        models = self.session.query(DidacticPlanModel).filter(DidacticPlanModel.professor_id == professor_id).all()
        return [
            DidacticPlan(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, status=m.status,
                data_entrega=m.data_entrega, campos=m.campos or {}
            ) for m in models
        ]

    def list_by_periodo(self, periodo_letivo_id: int) -> List[DidacticPlan]:
        models = self.session.query(DidacticPlanModel).filter(DidacticPlanModel.periodo_letivo_id == periodo_letivo_id).all()
        return [
            DidacticPlan(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, status=m.status,
                data_entrega=m.data_entrega, campos=m.campos or {}
            ) for m in models
        ]

    def list_all(self) -> List[DidacticPlan]:
        models = self.session.query(DidacticPlanModel).all()
        return [
            DidacticPlan(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, status=m.status,
                data_entrega=m.data_entrega, campos=m.campos or {}
            ) for m in models
        ]

    def save_campo_formulario(self, campo: CampoFormulario) -> CampoFormulario:
        if campo.id:
            m = self.session.query(CampoFormularioModel).filter(CampoFormularioModel.id == campo.id).first()
            if m:
                m.nome = campo.nome
                m.tipo = campo.tipo
                m.obrigatorio = campo.obrigatorio
                m.ordem = campo.ordem
                m.opcoes = campo.opcoes
        else:
            m = CampoFormularioModel(
                nome=campo.nome, tipo=campo.tipo, obrigatorio=campo.obrigatorio,
                ordem=campo.ordem, opcoes=campo.opcoes
            )
            self.session.add(m)
        self.session.commit()
        self.session.refresh(m)
        return CampoFormulario(
            id=m.id, nome=m.nome, tipo=m.tipo, obrigatorio=m.obrigatorio,
            ordem=m.ordem, opcoes=m.opcoes
        )

    def list_campos_formulario(self) -> List[CampoFormulario]:
        models = self.session.query(CampoFormularioModel).order_by(CampoFormularioModel.ordem).all()
        return [
            CampoFormulario(
                id=m.id, nome=m.nome, tipo=m.tipo, obrigatorio=m.obrigatorio,
                ordem=m.ordem, opcoes=m.opcoes
            ) for m in models
        ]

    def delete_campo_formulario(self, campo_id: int) -> bool:
        m = self.session.query(CampoFormularioModel).filter(CampoFormularioModel.id == campo_id).first()
        if m:
            self.session.delete(m)
            self.session.commit()
            return True
        return False


class SQLAlchemyAtribuicaoRepository(IAtribuicaoRepository):
    def __init__(self, session: Session):
        self.session = session

    def save_disciplina(self, disciplina: Disciplina) -> Disciplina:
        if disciplina.id:
            m = self.session.query(DisciplinaModel).filter(DisciplinaModel.id == disciplina.id).first()
            if m:
                m.codigo = disciplina.codigo
                m.nome = disciplina.nome
                m.carga_horaria = disciplina.carga_horaria
                m.natureza = disciplina.natureza
                m.area_formacao = disciplina.area_formacao
                m.departamento = disciplina.departamento
        else:
            m = DisciplinaModel(
                codigo=disciplina.codigo, nome=disciplina.nome, carga_horaria=disciplina.carga_horaria,
                natureza=disciplina.natureza, area_formacao=disciplina.area_formacao, departamento=disciplina.departamento
            )
            self.session.add(m)
        self.session.commit()
        self.session.refresh(m)
        disciplina.id = m.id
        return disciplina

    def find_disciplina_by_id(self, disciplina_id: int) -> Optional[Disciplina]:
        m = self.session.query(DisciplinaModel).filter(DisciplinaModel.id == disciplina_id).first()
        if m:
            return Disciplina(
                id=m.id, codigo=m.codigo, nome=m.nome, carga_horaria=m.carga_horaria,
                natureza=m.natureza, area_formacao=m.area_formacao, departamento=m.departamento
            )
        return None

    def list_disciplinas(self) -> List[Disciplina]:
        models = self.session.query(DisciplinaModel).all()
        return [
            Disciplina(
                id=m.id, codigo=m.codigo, nome=m.nome, carga_horaria=m.carga_horaria,
                natureza=m.natureza, area_formacao=m.area_formacao, departamento=m.departamento
            ) for m in models
        ]

    def save_atribuicao(self, atribuicao: AtribuicaoProfessorDisciplina) -> AtribuicaoProfessorDisciplina:
        if atribuicao.id:
            m = self.session.query(AtribuicaoModel).filter(AtribuicaoModel.id == atribuicao.id).first()
            if m:
                m.professor_id = atribuicao.professor_id
                m.disciplina_id = atribuicao.disciplina_id
                m.periodo_letivo_id = atribuicao.periodo_letivo_id
                m.horario = atribuicao.horario
        else:
            m = AtribuicaoModel(
                professor_id=atribuicao.professor_id,
                disciplina_id=atribuicao.disciplina_id,
                periodo_letivo_id=atribuicao.periodo_letivo_id,
                horario=atribuicao.horario
            )
            self.session.add(m)
            self.session.commit()
            self.session.refresh(m)
            atribuicao.id = m.id

        self.session.query(DiaLetivoModel).filter(DiaLetivoModel.atribuicao_id == atribuicao.id).delete()
        for d in atribuicao.dias_letivos:
            d_model = DiaLetivoModel(atribuicao_id=atribuicao.id, data=d.data, turno=d.turno)
            self.session.add(d_model)

        self.session.commit()
        return self.find_atribuicao_by_id(atribuicao.id)  # type: ignore

    def find_atribuicao_by_id(self, atribuicao_id: int) -> Optional[AtribuicaoProfessorDisciplina]:
        m = self.session.query(AtribuicaoModel).filter(AtribuicaoModel.id == atribuicao_id).first()
        if m:
            dias = [
                DiaLetivoDisciplina(id=d.id, atribuicao_id=d.atribuicao_id, data=d.data, turno=d.turno)
                for d in m.dias_letivos
            ]
            return AtribuicaoProfessorDisciplina(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, horario=m.horario, dias_letivos=dias
            )
        return None

    def list_atribuicoes_by_periodo(self, periodo_letivo_id: int) -> List[AtribuicaoProfessorDisciplina]:
        models = self.session.query(AtribuicaoModel).filter(AtribuicaoModel.periodo_letivo_id == periodo_letivo_id).all()
        res = []
        for m in models:
            dias = [DiaLetivoDisciplina(id=d.id, atribuicao_id=d.atribuicao_id, data=d.data, turno=d.turno) for d in m.dias_letivos]
            res.append(AtribuicaoProfessorDisciplina(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, horario=m.horario, dias_letivos=dias
            ))
        return res

    def list_atribuicoes_by_professor(self, professor_id: int) -> List[AtribuicaoProfessorDisciplina]:
        models = self.session.query(AtribuicaoModel).filter(AtribuicaoModel.professor_id == professor_id).all()
        res = []
        for m in models:
            dias = [DiaLetivoDisciplina(id=d.id, atribuicao_id=d.atribuicao_id, data=d.data, turno=d.turno) for d in m.dias_letivos]
            res.append(AtribuicaoProfessorDisciplina(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, horario=m.horario, dias_letivos=dias
            ))
        return res

    def save_dia_letivo(self, dia: DiaLetivoDisciplina) -> DiaLetivoDisciplina:
        m = DiaLetivoModel(atribuicao_id=dia.atribuicao_id, data=dia.data, turno=dia.turno)
        self.session.add(m)
        self.session.commit()
        self.session.refresh(m)
        dia.id = m.id
        return dia

    def delete_dia_letivo(self, dia_id: int) -> bool:
        m = self.session.query(DiaLetivoModel).filter(DiaLetivoModel.id == dia_id).first()
        if m:
            self.session.delete(m)
            self.session.commit()
            return True
        return False


class SQLAlchemyPeriodoLetivoRepository(IPeriodoLetivoRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, periodo: PeriodoLetivo) -> PeriodoLetivo:
        if periodo.id:
            m = self.session.query(PeriodoLetivoModel).filter(PeriodoLetivoModel.id == periodo.id).first()
            if m:
                m.ano = periodo.ano
                m.semestre = periodo.semestre
                m.ativo = periodo.ativo
                m.data_inicio = periodo.data_inicio
                m.data_fim = periodo.data_fim
                m.data_limite_entrega_plano = periodo.data_limite_entrega_plano
                m.minutos_por_dia_letivo = periodo.minutos_por_dia_letivo
        else:
            m = PeriodoLetivoModel(
                ano=periodo.ano, semestre=periodo.semestre, ativo=periodo.ativo,
                data_inicio=periodo.data_inicio, data_fim=periodo.data_fim,
                data_limite_entrega_plano=periodo.data_limite_entrega_plano,
                minutos_por_dia_letivo=periodo.minutos_por_dia_letivo
            )
            self.session.add(m)
        self.session.commit()
        self.session.refresh(m)
        periodo.id = m.id
        return periodo

    def find_by_id(self, periodo_id: int) -> Optional[PeriodoLetivo]:
        m = self.session.query(PeriodoLetivoModel).filter(PeriodoLetivoModel.id == periodo_id).first()
        if m:
            return PeriodoLetivo(
                id=m.id, ano=m.ano, semestre=m.semestre, ativo=m.ativo,
                data_inicio=m.data_inicio, data_fim=m.data_fim,
                data_limite_entrega_plano=m.data_limite_entrega_plano,
                minutos_por_dia_letivo=m.minutos_por_dia_letivo
            )
        return None

    def get_ativo(self) -> Optional[PeriodoLetivo]:
        m = self.session.query(PeriodoLetivoModel).filter(PeriodoLetivoModel.ativo == True).first()
        if m:
            return PeriodoLetivo(
                id=m.id, ano=m.ano, semestre=m.semestre, ativo=m.ativo,
                data_inicio=m.data_inicio, data_fim=m.data_fim,
                data_limite_entrega_plano=m.data_limite_entrega_plano,
                minutos_por_dia_letivo=m.minutos_por_dia_letivo
            )
        return None

    def set_ativo(self, periodo_id: int) -> None:
        self.session.query(PeriodoLetivoModel).update({PeriodoLetivoModel.ativo: False})
        self.session.query(PeriodoLetivoModel).filter(PeriodoLetivoModel.id == periodo_id).update({PeriodoLetivoModel.ativo: True})
        self.session.commit()

    def list_all(self) -> List[PeriodoLetivo]:
        models = self.session.query(PeriodoLetivoModel).all()
        return [
            PeriodoLetivo(
                id=m.id, ano=m.ano, semestre=m.semestre, ativo=m.ativo,
                data_inicio=m.data_inicio, data_fim=m.data_fim,
                data_limite_entrega_plano=m.data_limite_entrega_plano,
                minutos_por_dia_letivo=m.minutos_por_dia_letivo
            ) for m in models
        ]


class SQLAlchemyNotificationRepository(INotificationRepository):
    def __init__(self, session: Session):
        self.session = session

    def save_preference(self, pref: NotificationPreference) -> NotificationPreference:
        m = self.session.query(NotificationPreferenceModel).filter(NotificationPreferenceModel.usuario_id == pref.usuario_id).first()
        if m:
            m.canal_email = pref.canal_email
            m.canal_telegram = pref.canal_telegram
            m.chat_id_telegram = pref.chat_id_telegram
            m.horario_preferido = pref.horario_preferido
        else:
            m = NotificationPreferenceModel(
                usuario_id=pref.usuario_id,
                canal_email=pref.canal_email,
                canal_telegram=pref.canal_telegram,
                chat_id_telegram=pref.chat_id_telegram,
                horario_preferido=pref.horario_preferido
            )
            self.session.add(m)
        self.session.commit()
        self.session.refresh(m)
        pref.id = m.id
        return pref

    def find_preference_by_usuario_id(self, usuario_id: int) -> Optional[NotificationPreference]:
        m = self.session.query(NotificationPreferenceModel).filter(NotificationPreferenceModel.usuario_id == usuario_id).first()
        if m:
            return NotificationPreference(
                id=m.id, usuario_id=m.usuario_id, canal_email=m.canal_email,
                canal_telegram=m.canal_telegram, chat_id_telegram=m.chat_id_telegram,
                horario_preferido=m.horario_preferido
            )
        return None

    def save_log(self, log: NotificationLog) -> NotificationLog:
        m = NotificationLogModel(
            usuario_id=log.usuario_id, atribuicao_id=log.atribuicao_id,
            canal=log.canal, status=log.status, mensagem_erro=log.mensagem_erro
        )
        self.session.add(m)
        self.session.commit()
        self.session.refresh(m)
        log.id = m.id
        log.criado_em = m.criado_em
        return log

    def list_logs_by_usuario(self, usuario_id: int) -> List[NotificationLog]:
        models = self.session.query(NotificationLogModel).filter(NotificationLogModel.usuario_id == usuario_id).all()
        return [
            NotificationLog(
                id=m.id, usuario_id=m.usuario_id, atribuicao_id=m.atribuicao_id,
                canal=m.canal, status=m.status, mensagem_erro=m.mensagem_erro, criado_em=m.criado_em
            ) for m in models
        ]
