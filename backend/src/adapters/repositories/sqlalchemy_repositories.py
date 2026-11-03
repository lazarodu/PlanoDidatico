from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
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
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, usuario: Usuario) -> Usuario:
        if usuario.id:
            result = await self.session.execute(
                select(UsuarioModel).filter(UsuarioModel.id == usuario.id)
            )
            model = result.scalar_one_or_none()
            if model:
                model.nome = usuario.nome
                model.email = usuario.email
                model.tipo = usuario.tipo
        else:
            model = UsuarioModel(nome=usuario.nome, email=usuario.email, tipo=usuario.tipo)
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)
        usuario.id = model.id
        return usuario

    async def find_by_id(self, usuario_id: int) -> Optional[Usuario]:
        result = await self.session.execute(
            select(UsuarioModel).filter(UsuarioModel.id == usuario_id)
        )
        m = result.scalar_one_or_none()
        if m:
            return Usuario(id=m.id, nome=m.nome, email=m.email, tipo=m.tipo)
        return None

    async def find_by_email(self, email: str) -> Optional[Usuario]:
        result = await self.session.execute(
            select(UsuarioModel).filter(UsuarioModel.email == email)
        )
        m = result.scalar_one_or_none()
        if m:
            return Usuario(id=m.id, nome=m.nome, email=m.email, tipo=m.tipo)
        return None

    async def list_all(self) -> List[Usuario]:
        result = await self.session.execute(select(UsuarioModel).order_by(UsuarioModel.id))
        models = result.scalars().all()
        return [Usuario(id=m.id, nome=m.nome, email=m.email, tipo=m.tipo) for m in models]

    async def save_professor(self, professor: Professor) -> Professor:
        m = await self.session.execute(
            select(ProfessorModel).filter(ProfessorModel.usuario_id == professor.usuario_id)
        )
        model = m.scalar_one_or_none()
        if model:
            model.matricula = professor.matricula
            model.departamento = professor.departamento
        else:
            model = ProfessorModel(usuario_id=professor.usuario_id, matricula=professor.matricula, departamento=professor.departamento)
            self.session.add(model)

        await self.session.commit()
        return professor

    async def find_professor_by_id(self, usuario_id: int) -> Optional[Professor]:
        result = await self.session.execute(
            select(ProfessorModel).filter(ProfessorModel.usuario_id == usuario_id)
        )
        m = result.scalar_one_or_none()
        if m:
            return Professor(usuario_id=m.usuario_id, matricula=m.matricula, departamento=m.departamento)
        return None


class SQLAlchemyDidacticPlanRepository(IDidacticPlanRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, plan: DidacticPlan) -> DidacticPlan:
        if plan.id:
            result = await self.session.execute(
                select(DidacticPlanModel).filter(DidacticPlanModel.id == plan.id)
            )
            model = result.scalar_one_or_none()
            if model:
                model.professor_id = plan.professor_id
                model.disciplina_id = plan.disciplina_id
                model.periodo_letivo_id = plan.periodo_letivo_id
                model.status = plan.status
                model.data_entrega = plan.data_entrega
                model.campos = plan.campos
        else:
            model = DidacticPlanModel(
                professor_id=plan.professor_id,
                disciplina_id=plan.disciplina_id,
                periodo_letivo_id=plan.periodo_letivo_id,
                status=plan.status,
                data_entrega=plan.data_entrega,
                campos=plan.campos
            )
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)
        plan.id = model.id
        return plan

    async def find_by_id(self, plan_id: int) -> Optional[DidacticPlan]:
        result = await self.session.execute(
            select(DidacticPlanModel).filter(DidacticPlanModel.id == plan_id)
        )
        m = result.scalar_one_or_none()
        if m:
            return DidacticPlan(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, status=m.status,
                data_entrega=m.data_entrega, campos=m.campos or {}
            )
        return None

    async def find_by_professor_disciplina_periodo(self, professor_id: int, disciplina_id: int, periodo_letivo_id: int) -> Optional[DidacticPlan]:
        result = await self.session.execute(
            select(DidacticPlanModel).filter(
                DidacticPlanModel.professor_id == professor_id,
                DidacticPlanModel.disciplina_id == disciplina_id,
                DidacticPlanModel.periodo_letivo_id == periodo_letivo_id
            )
        )
        m = result.scalar_one_or_none()
        if m:
            return DidacticPlan(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, status=m.status,
                data_entrega=m.data_entrega, campos=m.campos or {}
            )
        return None

    async def list_by_professor(self, professor_id: int) -> List[DidacticPlan]:
        result = await self.session.execute(
            select(DidacticPlanModel).filter(DidacticPlanModel.professor_id == professor_id).order_by(DidacticPlanModel.id)
        )
        models = result.scalars().all()
        return [
            DidacticPlan(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, status=m.status,
                data_entrega=m.data_entrega, campos=m.campos or {}
            ) for m in models
        ]

    async def list_by_periodo(self, periodo_letivo_id: int) -> List[DidacticPlan]:
        result = await self.session.execute(
            select(DidacticPlanModel).filter(DidacticPlanModel.periodo_letivo_id == periodo_letivo_id).order_by(DidacticPlanModel.id)
        )
        models = result.scalars().all()
        return [
            DidacticPlan(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, status=m.status,
                data_entrega=m.data_entrega, campos=m.campos or {}
            ) for m in models
        ]

    async def list_all(self) -> List[DidacticPlan]:
        result = await self.session.execute(select(DidacticPlanModel).order_by(DidacticPlanModel.id))
        models = result.scalars().all()
        return [
            DidacticPlan(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, status=m.status,
                data_entrega=m.data_entrega, campos=m.campos or {}
            ) for m in models
        ]

    async def save_campo_formulario(self, campo: CampoFormulario) -> CampoFormulario:
        if campo.id:
            result = await self.session.execute(
                select(CampoFormularioModel).filter(CampoFormularioModel.id == campo.id)
            )
            model = result.scalar_one_or_none()
            if model:
                model.nome = campo.nome
                model.tipo = campo.tipo
                model.obrigatorio = campo.obrigatorio
                model.ordem = campo.ordem
                model.opcoes = campo.opcoes
        else:
            model = CampoFormularioModel(
                nome=campo.nome, tipo=campo.tipo, obrigatorio=campo.obrigatorio,
                ordem=campo.ordem, opcoes=campo.opcoes
            )
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)
        return CampoFormulario(
            id=model.id, nome=model.nome, tipo=model.tipo, obrigatorio=model.obrigatorio,
            ordem=model.ordem, opcoes=model.opcoes
        )

    async def list_campos_formulario(self) -> List[CampoFormulario]:
        result = await self.session.execute(select(CampoFormularioModel).order_by(CampoFormularioModel.ordem))
        models = result.scalars().all()
        return [
            CampoFormulario(
                id=m.id, nome=m.nome, tipo=m.tipo, obrigatorio=m.obrigatorio,
                ordem=m.ordem, opcoes=m.opcoes
            ) for m in models
        ]

    async def delete_campo_formulario(self, campo_id: int) -> bool:
        result = await self.session.execute(
            select(CampoFormularioModel).filter(CampoFormularioModel.id == campo_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False


class SQLAlchemyAtribuicaoRepository(IAtribuicaoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_disciplina(self, disciplina: Disciplina) -> Disciplina:
        result = await self.session.execute(
            select(DisciplinaModel).filter(DisciplinaModel.id == disciplina.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.codigo = disciplina.codigo
            model.nome = disciplina.nome
            model.carga_horaria = disciplina.carga_horaria
            model.natureza = disciplina.natureza
            model.area_formacao = disciplina.area_formacao
            model.departamento = disciplina.departamento
        else:
            model = DisciplinaModel(
                codigo=disciplina.codigo, nome=disciplina.nome, carga_horaria=disciplina.carga_horaria,
                natureza=disciplina.natureza, area_formacao=disciplina.area_formacao, departamento=disciplina.departamento
            )
            self.session.add(model)

        await self.session.commit()
        disciplina.id = model.id
        return disciplina

    async def find_disciplina_by_id(self, disciplina_id: int) -> Optional[Disciplina]:
        result = await self.session.execute(
            select(DisciplinaModel).filter(DisciplinaModel.id == disciplina_id)
        )
        m = result.scalar_one_or_none()
        if m:
            return Disciplina(
                id=m.id, codigo=m.codigo, nome=m.nome, carga_horaria=m.carga_horaria,
                natureza=m.natureza, area_formacao=m.area_formacao, departamento=m.departamento
            )
        return None

    async def list_disciplinas(self) -> List[Disciplina]:
        result = await self.session.execute(select(DisciplinaModel).order_by(DisciplinaModel.id))
        models = result.scalars().all()
        return [
            Disciplina(
                id=m.id, codigo=m.codigo, nome=m.nome, carga_horaria=m.carga_horaria,
                natureza=m.natureza, area_formacao=m.area_formacao, departamento=m.departamento
            ) for m in models
        ]

    async def save_atribuicao(self, atribuicao: AtribuicaoProfessorDisciplina) -> AtribuicaoProfessorDisciplina:
        result = await self.session.execute(
            select(AtribuicaoModel).filter(AtribuicaoModel.id == atribuicao.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.professor_id = atribuicao.professor_id
            model.disciplina_id = atribuicao.disciplina_id
            model.periodo_letivo_id = atribuicao.periodo_letivo_id
            model.horario = atribuicao.horario
        else:
            model = AtribuicaoModel(
                professor_id=atribuicao.professor_id,
                disciplina_id=atribuicao.disciplina_id,
                periodo_letivo_id=atribuicao.periodo_letivo_id,
                horario=atribuicao.horario
            )
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)
        atribuicao.id = model.id

        # Delete existing dias_letivos and create new ones
        result = await self.session.execute(
            select(DiaLetivoModel).filter(DiaLetivoModel.atribuicao_id == atribuicao.id)
        )
        existing = result.scalars().all()
        for d in existing:
            await self.session.delete(d)

        for d in atribuicao.dias_letivos:
            d_model = DiaLetivoModel(atribuicao_id=atribuicao.id, data=d.data, turno=d.turno)
            self.session.add(d_model)

        await self.session.commit()
        return await self.find_atribuicao_by_id(atribuicao.id)

    async def find_atribuicao_by_id(self, atribuicao_id: int) -> Optional[AtribuicaoProfessorDisciplina]:
        result = await self.session.execute(
            select(AtribuicaoModel).filter(AtribuicaoModel.id == atribuicao_id)
        )
        m = result.scalar_one_or_none()
        if m:
            result2 = await self.session.execute(
                select(DiaLetivoModel).filter(DiaLetivoModel.atribuicao_id == atribuicao_id)
            )
            dias_rows = result2.scalars().all()
            dias = [
                DiaLetivoDisciplina(id=d.id, atribuicao_id=d.atribuicao_id, data=d.data, turno=d.turno)
                for d in dias_rows
            ]
            return AtribuicaoProfessorDisciplina(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, horario=m.horario, dias_letivos=dias
            )
        return None

    async def list_atribuicoes_by_periodo(self, periodo_letivo_id: int) -> List[AtribuicaoProfessorDisciplina]:
        result = await self.session.execute(
            select(AtribuicaoModel).filter(AtribuicaoModel.periodo_letivo_id == periodo_letivo_id).order_by(AtribuicaoModel.id)
        )
        models = result.scalars().all()
        res = []
        for m in models:
            result2 = await self.session.execute(
                select(DiaLetivoModel).filter(DiaLetivoModel.atribuicao_id == m.id)
            )
            dias_rows = result2.scalars().all()
            res.append(AtribuicaoProfessorDisciplina(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, horario=m.horario, dias_letivos=[
                    DiaLetivoDisciplina(id=d.id, atribuicao_id=d.atribuicao_id, data=d.data, turno=d.turno)
                    for d in dias_rows
                ]
            ))
        return res

    async def list_atribuicoes_by_professor(self, professor_id: int) -> List[AtribuicaoProfessorDisciplina]:
        result = await self.session.execute(
            select(AtribuicaoModel).filter(AtribuicaoModel.professor_id == professor_id).order_by(AtribuicaoModel.id)
        )
        models = result.scalars().all()
        res = []
        for m in models:
            result2 = await self.session.execute(
                select(DiaLetivoModel).filter(DiaLetivoModel.atribuicao_id == m.id)
            )
            dias_rows = result2.scalars().all()
            res.append(AtribuicaoProfessorDisciplina(
                id=m.id, professor_id=m.professor_id, disciplina_id=m.disciplina_id,
                periodo_letivo_id=m.periodo_letivo_id, horario=m.horario, dias_letivos=[
                    DiaLetivoDisciplina(id=d.id, atribuicao_id=d.atribuicao_id, data=d.data, turno=d.turno)
                    for d in dias_rows
                ]
            ))
        return res

    async def save_dia_letivo(self, dia: DiaLetivoDisciplina) -> DiaLetivoDisciplina:
        m = DiaLetivoModel(atribuicao_id=dia.atribuicao_id, data=dia.data, turno=dia.turno)
        self.session.add(m)
        await self.session.commit()
        await self.session.refresh(m)
        dia.id = m.id
        return dia

    async def delete_dia_letivo(self, dia_id: int) -> bool:
        result = await self.session.execute(
            select(DiaLetivoModel).filter(DiaLetivoModel.id == dia_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False


class SQLAlchemyPeriodoLetivoRepository(IPeriodoLetivoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, periodo: PeriodoLetivo) -> PeriodoLetivo:
        result = await self.session.execute(
            select(PeriodoLetivoModel).filter(PeriodoLetivoModel.id == periodo.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.ano = periodo.ano
            model.semestre = periodo.semestre
            model.ativo = periodo.ativo
            model.data_inicio = periodo.data_inicio
            model.data_fim = periodo.data_fim
            model.data_limite_entrega_plano = periodo.data_limite_entrega_plano
            model.minutos_por_dia_letivo = periodo.minutos_por_dia_letivo
        else:
            model = PeriodoLetivoModel(
                ano=periodo.ano, semestre=periodo.semestre, ativo=periodo.ativo,
                data_inicio=periodo.data_inicio, data_fim=periodo.data_fim,
                data_limite_entrega_plano=periodo.data_limite_entrega_plano,
                minutos_por_dia_letivo=periodo.minutos_por_dia_letivo
            )
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)
        periodo.id = model.id
        return periodo

    async def find_by_id(self, periodo_id: int) -> Optional[PeriodoLetivo]:
        result = await self.session.execute(
            select(PeriodoLetivoModel).filter(PeriodoLetivoModel.id == periodo_id)
        )
        m = result.scalar_one_or_none()
        if m:
            return PeriodoLetivo(
                id=m.id, ano=m.ano, semestre=m.semestre, ativo=m.ativo,
                data_inicio=m.data_inicio, data_fim=m.data_fim,
                data_limite_entrega_plano=m.data_limite_entrega_plano,
                minutos_por_dia_letivo=m.minutos_por_dia_letivo
            )
        return None

    async def get_ativo(self) -> Optional[PeriodoLetivo]:
        result = await self.session.execute(
            select(PeriodoLetivoModel).filter(PeriodoLetivoModel.ativo == True)
        )
        m = result.scalar_one_or_none()
        if m:
            return PeriodoLetivo(
                id=m.id, ano=m.ano, semestre=m.semestre, ativo=m.ativo,
                data_inicio=m.data_inicio, data_fim=m.data_fim,
                data_limite_entrega_plano=m.data_limite_entrega_plano,
                minutos_por_dia_letivo=m.minutos_por_dia_letivo
            )
        return None

    async def set_ativo(self, periodo_id: int) -> None:
        await self.session.execute(
            update(PeriodoLetivoModel).where(PeriodoLetivoModel.id == periodo_id).values(ativo=False)
        )
        await self.session.execute(
            update(PeriodoLetivoModel).where(PeriodoLetivoModel.id == periodo_id).values(ativo=True)
        )
        await self.session.commit()

    async def list_all(self) -> List[PeriodoLetivo]:
        result = await self.session.execute(select(PeriodoLetivoModel).order_by(PeriodoLetivoModel.id))
        models = result.scalars().all()
        return [
            PeriodoLetivo(
                id=m.id, ano=m.ano, semestre=m.semestre, ativo=m.ativo,
                data_inicio=m.data_inicio, data_fim=m.data_fim,
                data_limite_entrega_plano=m.data_limite_entrega_plano,
                minutos_por_dia_letivo=m.minutos_por_dia_letivo
            ) for m in models
        ]


class SQLAlchemyNotificationRepository(INotificationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_preference(self, pref: NotificationPreference) -> NotificationPreference:
        result = await self.session.execute(
            select(NotificationPreferenceModel).filter(NotificationPreferenceModel.usuario_id == pref.usuario_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.canal_email = pref.canal_email
            model.canal_telegram = pref.canal_telegram
            model.chat_id_telegram = pref.chat_id_telegram
            model.horario_preferido = pref.horario_preferido
        else:
            model = NotificationPreferenceModel(
                usuario_id=pref.usuario_id,
                canal_email=pref.canal_email,
                canal_telegram=pref.canal_telegram,
                chat_id_telegram=pref.chat_id_telegram,
                horario_preferido=pref.horario_preferido
            )
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)
        pref.id = model.id
        return pref

    async def find_preference_by_usuario_id(self, usuario_id: int) -> Optional[NotificationPreference]:
        result = await self.session.execute(
            select(NotificationPreferenceModel).filter(NotificationPreferenceModel.usuario_id == usuario_id)
        )
        m = result.scalar_one_or_none()
        if m:
            return NotificationPreference(
                id=m.id, usuario_id=m.usuario_id, canal_email=m.canal_email,
                canal_telegram=m.canal_telegram, chat_id_telegram=m.chat_id_telegram,
                horario_preferido=m.horario_preferido
            )
        return None

    async def save_log(self, log: NotificationLog) -> NotificationLog:
        model = NotificationLogModel(
            usuario_id=log.usuario_id, atribuicao_id=log.atribuicao_id,
            canal=log.canal, status=log.status, mensagem_erro=log.mensagem_erro
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        log.id = model.id
        log.criado_em = m.criado_em
        return log

    async def list_logs_by_usuario(self, usuario_id: int) -> List[NotificationLog]:
        result = await self.session.execute(
            select(NotificationLogModel).filter(NotificationLogModel.usuario_id == usuario_id).order_by(NotificationLogModel.criado_em)
        )
        models = result.scalars().all()
        return [
            NotificationLog(
                id=m.id, usuario_id=m.usuario_id, atribuicao_id=m.atribuicao_id,
                canal=m.canal, status=m.status, mensagem_erro=m.mensagem_erro, criado_em=m.criado_em
            ) for m in models
        ]