from src.domain.entities.atribuicao import AtribuicaoProfessorDisciplina, Disciplina, PeriodoLetivo

class ValidadorCargaHoraria:
    """
    Domain Service implementing Rule RF11:
    Validates that total minutes (dias_letivos * minutos_por_dia_letivo) >= carga_horaria of the disciplina.
    """
    @staticmethod
    def validar(atribuicao: AtribuicaoProfessorDisciplina, disciplina: Disciplina, periodo: PeriodoLetivo) -> bool:
        total_dias = len(atribuicao.dias_letivos)
        minutos_por_dia = periodo.minutos_por_dia_letivo
        total_minutos = total_dias * minutos_por_dia

        carga_horaria_minutos = disciplina.carga_horaria * 60 if disciplina.carga_horaria < 200 else disciplina.carga_horaria

        return total_minutos >= carga_horaria_minutos

    @staticmethod
    def calcular_minutos_faltantes(atribuicao: AtribuicaoProfessorDisciplina, disciplina: Disciplina, periodo: PeriodoLetivo) -> int:
        total_dias = len(atribuicao.dias_letivos)
        total_minutos = total_dias * periodo.minutos_por_dia_letivo
        carga_minutos = disciplina.carga_horaria * 60 if disciplina.carga_horaria < 200 else disciplina.carga_horaria
        faltante = carga_minutos - total_minutos
        return max(0, faltante)
