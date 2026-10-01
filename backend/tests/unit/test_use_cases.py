import pytest
from datetime import date
from tests.fakes import (
    InMemoryUsuarioRepository,
    InMemoryDidacticPlanRepository,
    InMemoryAtribuicaoRepository,
    InMemoryPeriodoLetivoRepository,
    InMemoryNotificationRepository,
    FakeNotifier
)
from src.application.use_cases.submit_didactic_plan import SubmitDidacticPlanUseCase, ManageFieldsUseCase
from src.application.use_cases.atribuicao_use_cases import (
    DefinirPeriodoLetivoUseCase,
    ImportarGerenciarProfessoresUseCase,
    AtribuirProfessorDisciplinaUseCase,
    CadastrarDiasLetivosUseCase
)
from src.application.use_cases.notification_use_cases import ConfigurarCanaisUseCase, DetectarNotificarAtrasosUseCase
from src.domain.entities.atribuicao import Disciplina, PeriodoLetivo

@pytest.mark.asyncio
async def test_use_cases_flow():
    user_repo = InMemoryUsuarioRepository()
    plan_repo = InMemoryDidacticPlanRepository()
    atribuicao_repo = InMemoryAtribuicaoRepository()
    periodo_repo = InMemoryPeriodoLetivoRepository()
    notif_repo = InMemoryNotificationRepository()

    manage_fields_uc = ManageFieldsUseCase(plan_repo)
    manage_fields_uc.add_campo(nome="atividades_avaliativas", tipo="textarea", obrigatorio=True, ordem=1)
    manage_fields_uc.add_campo(nome="observacoes", tipo="textarea", obrigatorio=False, ordem=2)

    assert len(plan_repo.list_campos_formulario()) == 2

    periodo_uc = DefinirPeriodoLetivoUseCase(periodo_repo)
    periodo = periodo_uc.execute(
        ano=2026, semestre=1,
        data_inicio=date(2026, 2, 1), data_fim=date(2026, 7, 1),
        data_limite_entrega_plano=date(2026, 3, 1), minutos_por_dia_letivo=100
    )
    assert periodo.id == 1
    assert periodo_repo.get_ativo().id == 1

    import_uc = ImportarGerenciarProfessoresUseCase(user_repo)
    csv_data = [
        {"nome": "Prof. Ana", "email": "ana@cefet.br", "matricula": "123", "departamento": "DECOM"}
    ]
    profs = import_uc.importar_csv_professores(csv_data)
    assert len(profs) == 1
    prof_id = profs[0].id

    disciplina = atribuicao_repo.save_disciplina(
        Disciplina(id=None, codigo="DECOM01", nome="Laboratório de Web", carga_horaria=60)
    )
    atribuir_uc = AtribuirProfessorDisciplinaUseCase(atribuicao_repo, periodo_repo)
    atribuicao = atribuir_uc.execute(professor_id=prof_id, disciplina_id=disciplina.id, periodo_letivo_id=periodo.id)

    dias_uc = CadastrarDiasLetivosUseCase(atribuicao_repo, periodo_repo)
    dias = [{"data": date(2026, 2, i % 28 + 1), "turno": "matutino"} for i in range(36)]

    atribuicao_atualizada = dias_uc.execute(atribuicao.id, dias)
    assert len(atribuicao_atualizada.dias_letivos) == 36

    with pytest.raises(ValueError) as exc:
        dias_uc.execute(atribuicao.id, dias[:30])
    assert "RF11 Violição" in str(exc.value)

    submit_uc = SubmitDidacticPlanUseCase(plan_repo, periodo_repo)
    plan = submit_uc.execute(
        professor_id=prof_id,
        disciplina_id=disciplina.id,
        periodo_letivo_id=periodo.id,
        campos={"atividades_avaliativas": "Provas e trabalhos", "observacoes": "Nenhuma"}
    )
    assert plan.status == "ENTREGUE"

    with pytest.raises(ValueError):
        submit_uc.execute(
            professor_id=prof_id,
            disciplina_id=disciplina.id,
            periodo_letivo_id=periodo.id,
            campos={"observacoes": "Nenhuma"}
        )

    config_canal_uc = ConfigurarCanaisUseCase(notif_repo)
    config_canal_uc.execute(usuario_id=prof_id, canal_email=True, canal_telegram=True, chat_id_telegram="987654")

    email_notifier = FakeNotifier(should_succeed=True)
    telegram_notifier = FakeNotifier(should_succeed=True)

    detect_uc = DetectarNotificarAtrasosUseCase(
        periodo_repo, atribuicao_repo, plan_repo, user_repo, notif_repo, email_notifier, telegram_notifier
    )

    logs = await detect_uc.execute(hoje=date(2026, 2, 15))
    assert len(logs) == 0

    logs = await detect_uc.execute(hoje=date(2026, 3, 5))
    assert len(logs) == 0
