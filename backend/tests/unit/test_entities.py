import pytest
from datetime import date
from src.domain.entities.user import Usuario, Professor
from src.domain.entities.atribuicao import Disciplina, PeriodoLetivo, AtribuicaoProfessorDisciplina, DiaLetivoDisciplina
from src.domain.entities.didactic_plan import DidacticPlan
from src.domain.entities.notification import NotificationPreference, NotificationLog
from src.domain.value_objects.field_config import CampoFormulario
from src.domain.value_objects.dia_letivo import DiaLetivo

def test_usuario_permissions():
    admin = Usuario(id=1, nome="Admin", email="admin@cefet.br", tipo="admin")
    coord = Usuario(id=2, nome="Coord", email="coord@cefet.br", tipo="coordenador")
    prof = Usuario(id=3, nome="Prof", email="prof@cefet.br", tipo="professor")

    assert admin.eh_admin() is True
    assert admin.pode_gerenciar_campos_formulario() is True

    assert coord.eh_coordenador() is True
    assert coord.pode_importar_campos_fixos() is True
    assert coord.eh_admin() is False

    assert prof.eh_professor() is True
    assert prof.pode_preencher_campos_variaveis() is True
    assert prof.eh_coordenador() is False

def test_didactic_plan_status():
    plan = DidacticPlan(id=1, professor_id=3, disciplina_id=10, periodo_letivo_id=1)
    assert plan.esta_pendente() is True

    plan.marcar_como_entregue(data=date(2026, 3, 10))
    assert plan.esta_pendente() is False
    assert plan.get_status() == "ENTREGUE"

    data_limite = date(2026, 3, 1)
    assert plan.verificar_atraso(data_limite=data_limite) is True

def test_periodo_letivo_and_atribuicao():
    periodo = PeriodoLetivo(
        id=1, ano=2026, semestre=1, ativo=True,
        data_inicio=date(2026, 2, 1), data_fim=date(2026, 7, 1),
        data_limite_entrega_plano=date(2026, 3, 1), minutos_por_dia_letivo=100
    )
    atribuicao = AtribuicaoProfessorDisciplina(id=1, professor_id=3, disciplina_id=10, periodo_letivo_id=1)

    for i in range(36):
        atribuicao.adicionar_dia_letivo(DiaLetivoDisciplina(id=i, atribuicao_id=1, data=date(2026, 2, 2)))

    assert atribuicao.calcular_total_minutos(periodo.minutos_por_dia_letivo) == 3600
    assert atribuicao.validar_carga_horaria_suficiente(carga_horaria_disciplina=60, minutos_por_dia=100) is True

def test_notification_preference():
    pref = NotificationPreference(id=1, usuario_id=3)
    assert pref.pode_receber_via_email() is True
    assert pref.pode_receber_via_telegram() is False

    pref.ativar_canal_telegram("123456789")
    assert pref.pode_receber_via_telegram() is True
    assert pref.get_chat_id_telegram() == "123456789"
