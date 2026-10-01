from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from sqlalchemy.orm import Session
import csv
import io

from src.infra.database import get_db
from src.adapters.repositories.sqlalchemy_repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyDidacticPlanRepository,
    SQLAlchemyAtribuicaoRepository,
    SQLAlchemyPeriodoLetivoRepository,
    SQLAlchemyNotificationRepository
)
from src.adapters.notifiers.strategy_notifiers import EmailSmtpNotifier, TelegramNotifier
from src.adapters.pdf_generator import PDFGeneratorAdapter
from src.adapters.controllers.dtos import (
    UserCreateDTO, UserResponseDTO,
    CampoFormularioDTO,
    PeriodoLetivoDTO,
    DisciplinaDTO, AtribuicaoDTO, CadastrarDiasLetivosDTO,
    SubmitPlanDTO, PlanResponseDTO,
    NotificationConfigDTO
)
from src.application.use_cases.submit_didactic_plan import SubmitDidacticPlanUseCase, ManageFieldsUseCase
from src.application.use_cases.atribuicao_use_cases import (
    DefinirPeriodoLetivoUseCase,
    ImportarGerenciarProfessoresUseCase,
    AtribuirProfessorDisciplinaUseCase,
    CadastrarDiasLetivosUseCase
)
from src.application.use_cases.notification_use_cases import ConfigurarCanaisUseCase, DetectarNotificarAtrasosUseCase
from src.domain.entities.user import Usuario
from src.domain.entities.atribuicao import Disciplina

router = APIRouter()

@router.post("/users", response_model=UserResponseDTO)
def create_user(dto: UserCreateDTO, db: Session = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    u = Usuario(id=None, nome=dto.nome, email=dto.email, tipo=dto.tipo)
    saved = repo.save(u)
    return UserResponseDTO(id=saved.id, nome=saved.nome, email=saved.email, tipo=saved.tipo)

@router.get("/users", response_model=List[UserResponseDTO])
def list_users(db: Session = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    users = repo.list_all()
    return [UserResponseDTO(id=u.id, nome=u.nome, email=u.email, tipo=u.tipo) for u in users]

@router.post("/admin/fields", response_model=CampoFormularioDTO)
def create_field(dto: CampoFormularioDTO, db: Session = Depends(get_db)):
    repo = SQLAlchemyDidacticPlanRepository(db)
    uc = ManageFieldsUseCase(repo)
    campo = uc.add_campo(nome=dto.nome, tipo=dto.tipo, obrigatorio=dto.obrigatorio, ordem=dto.ordem, opcoes=dto.opcoes)
    return CampoFormularioDTO(id=campo.id, nome=campo.nome, tipo=campo.tipo, obrigatorio=campo.obrigatorio, ordem=campo.ordem, opcoes=campo.opcoes)

@router.get("/admin/fields", response_model=List[CampoFormularioDTO])
def list_fields(db: Session = Depends(get_db)):
    repo = SQLAlchemyDidacticPlanRepository(db)
    uc = ManageFieldsUseCase(repo)
    campos = uc.list_campos()
    return [CampoFormularioDTO(id=c.id, nome=c.nome, tipo=c.tipo, obrigatorio=c.obrigatorio, ordem=c.ordem, opcoes=c.opcoes) for c in campos]

@router.delete("/admin/fields/{campo_id}")
def delete_field(campo_id: int, db: Session = Depends(get_db)):
    repo = SQLAlchemyDidacticPlanRepository(db)
    uc = ManageFieldsUseCase(repo)
    success = uc.delete_campo(campo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Campo não encontrado")
    return {"status": "deleted"}

@router.post("/coordinator/periodo", response_model=PeriodoLetivoDTO)
def create_periodo(dto: PeriodoLetivoDTO, db: Session = Depends(get_db)):
    repo = SQLAlchemyPeriodoLetivoRepository(db)
    uc = DefinirPeriodoLetivoUseCase(repo)
    p = uc.execute(
        ano=dto.ano, semestre=dto.semestre,
        data_inicio=dto.data_inicio, data_fim=dto.data_fim,
        data_limite_entrega_plano=dto.data_limite_entrega_plano,
        minutos_por_dia_letivo=dto.minutos_por_dia_letivo,
        ativo=dto.ativo
    )
    return PeriodoLetivoDTO(
        id=p.id, ano=p.ano, semestre=p.semestre,
        data_inicio=p.data_inicio, data_fim=p.data_fim,
        data_limite_entrega_plano=p.data_limite_entrega_plano,
        minutos_por_dia_letivo=p.minutos_por_dia_letivo,
        ativo=p.ativo
    )

@router.get("/coordinator/periodo/ativo", response_model=Optional[PeriodoLetivoDTO])
def get_periodo_ativo(db: Session = Depends(get_db)):
    repo = SQLAlchemyPeriodoLetivoRepository(db)
    p = repo.get_ativo()
    if not p:
        return None
    return PeriodoLetivoDTO(
        id=p.id, ano=p.ano, semestre=p.semestre,
        data_inicio=p.data_inicio, data_fim=p.data_fim,
        data_limite_entrega_plano=p.data_limite_entrega_plano,
        minutos_por_dia_letivo=p.minutos_por_dia_letivo,
        ativo=p.ativo
    )

@router.post("/coordinator/professors/import")
async def import_professors_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    user_repo = SQLAlchemyUserRepository(db)
    uc = ImportarGerenciarProfessoresUseCase(user_repo)
    content = await file.read()
    text = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(text))
    linhas = [row for row in csv_reader]
    criados = uc.importar_csv_professores(linhas)
    return {"status": "success", "imported_count": len(criados)}

@router.post("/coordinator/disciplinas", response_model=DisciplinaDTO)
def create_disciplina(dto: DisciplinaDTO, db: Session = Depends(get_db)):
    repo = SQLAlchemyAtribuicaoRepository(db)
    d = Disciplina(id=None, codigo=dto.codigo, nome=dto.nome, carga_horaria=dto.carga_horaria, natureza=dto.natureza, area_formacao=dto.area_formacao, departamento=dto.departamento)
    saved = repo.save_disciplina(d)
    return DisciplinaDTO(id=saved.id, codigo=saved.codigo, nome=saved.nome, carga_horaria=saved.carga_horaria, natureza=saved.natureza, area_formacao=saved.area_formacao, departamento=saved.departamento)

@router.get("/coordinator/disciplinas", response_model=List[DisciplinaDTO])
def list_disciplinas(db: Session = Depends(get_db)):
    repo = SQLAlchemyAtribuicaoRepository(db)
    discs = repo.list_disciplinas()
    return [DisciplinaDTO(id=d.id, codigo=d.codigo, nome=d.nome, carga_horaria=d.carga_horaria, natureza=d.natureza, area_formacao=d.area_formacao, departamento=d.departamento) for d in discs]

@router.post("/coordinator/atribuicao", response_model=AtribuicaoDTO)
def atribuir_professor(dto: AtribuicaoDTO, db: Session = Depends(get_db)):
    at_repo = SQLAlchemyAtribuicaoRepository(db)
    per_repo = SQLAlchemyPeriodoLetivoRepository(db)
    uc = AtribuirProfessorDisciplinaUseCase(at_repo, per_repo)
    at = uc.execute(professor_id=dto.professor_id, disciplina_id=dto.disciplina_id, periodo_letivo_id=dto.periodo_letivo_id, horario=dto.horario)
    return AtribuicaoDTO(id=at.id, professor_id=at.professor_id, disciplina_id=at.disciplina_id, periodo_letivo_id=at.periodo_letivo_id, horario=at.horario)

@router.post("/coordinator/dias-letivos")
def cadastrar_dias_letivos(dto: CadastrarDiasLetivosDTO, db: Session = Depends(get_db)):
    at_repo = SQLAlchemyAtribuicaoRepository(db)
    per_repo = SQLAlchemyPeriodoLetivoRepository(db)
    uc = CadastrarDiasLetivosUseCase(at_repo, per_repo)
    try:
        dias_dict = [{"data": d.data, "turno": d.turno} for d in dto.dias]
        at = uc.execute(atribuicao_id=dto.atribuicao_id, dias=dias_dict)
        return {"status": "success", "atribuicao_id": at.id, "total_dias": len(at.dias_letivos)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/plans/submit", response_model=PlanResponseDTO)
def submit_plan(dto: SubmitPlanDTO, db: Session = Depends(get_db)):
    plan_repo = SQLAlchemyDidacticPlanRepository(db)
    per_repo = SQLAlchemyPeriodoLetivoRepository(db)
    uc = SubmitDidacticPlanUseCase(plan_repo, per_repo)
    try:
        plan = uc.execute(
            professor_id=dto.professor_id,
            disciplina_id=dto.disciplina_id,
            periodo_letivo_id=dto.periodo_letivo_id,
            campos=dto.campos
        )
        return PlanResponseDTO(
            id=plan.id, professor_id=plan.professor_id,
            disciplina_id=plan.disciplina_id, periodo_letivo_id=plan.periodo_letivo_id,
            status=plan.status, data_entrega=plan.data_entrega, campos=plan.campos
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/plans", response_model=List[PlanResponseDTO])
def list_plans(db: Session = Depends(get_db)):
    plan_repo = SQLAlchemyDidacticPlanRepository(db)
    plans = plan_repo.list_all()
    return [
        PlanResponseDTO(
            id=p.id, professor_id=p.professor_id,
            disciplina_id=p.disciplina_id, periodo_letivo_id=p.periodo_letivo_id,
            status=p.status, data_entrega=p.data_entrega, campos=p.campos
        ) for p in plans
    ]

@router.get("/plans/{plan_id}/pdf")
def get_plan_pdf(plan_id: int, db: Session = Depends(get_db)):
    plan_repo = SQLAlchemyDidacticPlanRepository(db)
    user_repo = SQLAlchemyUserRepository(db)
    at_repo = SQLAlchemyAtribuicaoRepository(db)
    per_repo = SQLAlchemyPeriodoLetivoRepository(db)

    plan = plan_repo.find_by_id(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

    prof = user_repo.find_by_id(plan.professor_id)
    disc = at_repo.find_disciplina_by_id(plan.disciplina_id)
    per = per_repo.find_by_id(plan.periodo_letivo_id)

    prof_nome = prof.nome if prof else "Professor"
    disc_cod = disc.codigo if disc else "DISC"
    disc_nome = disc.nome if disc else "Disciplina"
    per_str = f"{per.ano}/{per.semestre}" if per else "2026/1"

    pdf_bytes = PDFGeneratorAdapter.generate_plan_pdf(
        prof_nome=prof_nome,
        disciplina_codigo=disc_cod,
        disciplina_nome=disc_nome,
        periodo_str=per_str,
        campos=plan.campos
    )
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=plano_didatico_{plan_id}.pdf"})

@router.post("/notifications/config")
def config_notifications(dto: NotificationConfigDTO, db: Session = Depends(get_db)):
    repo = SQLAlchemyNotificationRepository(db)
    uc = ConfigurarCanaisUseCase(repo)
    pref = uc.execute(
        usuario_id=dto.usuario_id,
        canal_email=dto.canal_email,
        canal_telegram=dto.canal_telegram,
        chat_id_telegram=dto.chat_id_telegram,
        horario_preferido=dto.horario_preferido
    )
    return {"status": "success", "usuario_id": pref.usuario_id}

@router.post("/notifications/check-delays")
async def trigger_check_delays(db: Session = Depends(get_db)):
    per_repo = SQLAlchemyPeriodoLetivoRepository(db)
    at_repo = SQLAlchemyAtribuicaoRepository(db)
    plan_repo = SQLAlchemyDidacticPlanRepository(db)
    user_repo = SQLAlchemyUserRepository(db)
    notif_repo = SQLAlchemyNotificationRepository(db)

    email_notifier = EmailSmtpNotifier()
    telegram_notifier = TelegramNotifier()

    uc = DetectarNotificarAtrasosUseCase(
        per_repo, at_repo, plan_repo, user_repo, notif_repo, email_notifier, telegram_notifier
    )
    logs = await uc.execute()
    return {"status": "executed", "notifications_sent": len(logs)}
