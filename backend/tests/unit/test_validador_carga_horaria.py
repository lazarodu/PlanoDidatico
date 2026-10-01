import pytest
from datetime import date
from src.domain.entities.atribuicao import AtribuicaoProfessorDisciplina, Disciplina, PeriodoLetivo, DiaLetivoDisciplina
from src.domain.services.validador_carga_horaria import ValidadorCargaHoraria

def test_validador_carga_horaria_exato_e_insuficiente():
    disciplina = Disciplina(id=1, codigo="DECOM01", nome="Laboratório de Programação Web", carga_horaria=60)
    periodo = PeriodoLetivo(
        id=1, ano=2026, semestre=1, ativo=True,
        data_inicio=date(2026,2,1), data_fim=date(2026,7,1),
        data_limite_entrega_plano=date(2026,3,1), minutos_por_dia_letivo=100
    )
    atribuicao = AtribuicaoProfessorDisciplina(id=1, professor_id=1, disciplina_id=1, periodo_letivo_id=1)

    for i in range(35):
        atribuicao.adicionar_dia_letivo(DiaLetivoDisciplina(id=i, atribuicao_id=1, data=date(2026,2,1)))

    assert ValidadorCargaHoraria.validar(atribuicao, disciplina, periodo) is False
    assert ValidadorCargaHoraria.calcular_minutos_faltantes(atribuicao, disciplina, periodo) == 100

    atribuicao.adicionar_dia_letivo(DiaLetivoDisciplina(id=35, atribuicao_id=1, data=date(2026,2,2)))
    assert ValidadorCargaHoraria.validar(atribuicao, disciplina, periodo) is True
    assert ValidadorCargaHoraria.calcular_minutos_faltantes(atribuicao, disciplina, periodo) == 0

    atribuicao.adicionar_dia_letivo(DiaLetivoDisciplina(id=36, atribuicao_id=1, data=date(2026,2,3)))
    assert ValidadorCargaHoraria.validar(atribuicao, disciplina, periodo) is True
