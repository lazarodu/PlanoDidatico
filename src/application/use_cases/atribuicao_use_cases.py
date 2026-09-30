from typing import List, Optional, Dict, Any
from datetime import date
from src.domain.entities.atribuicao import PeriodoLetivo, Disciplina, AtribuicaoProfessorDisciplina, DiaLetivoDisciplina
from src.domain.entities.user import Usuario, Professor
from src.domain.repositories.interfaces import IPeriodoLetivoRepository, IAtribuicaoRepository, IUsuarioRepository
from src.domain.services.validador_carga_horaria import ValidadorCargaHoraria


class DefinirPeriodoLetivoUseCase:
    """UC13: Define Periodo Letivo"""
    def __init__(self, periodo_repo: IPeriodoLetivoRepository):
        self.periodo_repo = periodo_repo

    def execute(self, ano: int, semestre: int, data_inicio: date, data_fim: date, data_limite_entrega_plano: date, minutos_por_dia_letivo: int = 100, ativo: bool = True) -> PeriodoLetivo:
        periodo = PeriodoLetivo(
            id=None,
            ano=ano,
            semestre=semestre,
            ativo=ativo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            data_limite_entrega_plano=data_limite_entrega_plano,
            minutos_por_dia_letivo=minutos_por_dia_letivo
        )
        saved = self.periodo_repo.save(periodo)
        if ativo and saved.id:
            self.periodo_repo.set_ativo(saved.id)
        return saved


class ImportarGerenciarProfessoresUseCase:
    """UC11 & RF07/RF08: Import and manage professors"""
    def __init__(self, user_repo: IUsuarioRepository):
        self.user_repo = user_repo

    def importar_csv_professores(self, linhas_csv: List[Dict[str, str]]) -> List[Usuario]:
        professores_criados = []
        for row in linhas_csv:
            email = row.get("email", "").strip()
            nome = row.get("nome", "").strip()
            matricula = row.get("matricula", "").strip()
            departamento = row.get("departamento", "DECOM").strip()

            if not email or not nome:
                continue

            existing = self.user_repo.find_by_email(email)
            if not existing:
                usuario = Usuario(id=None, nome=nome, email=email, tipo="professor")
                usuario = self.user_repo.save(usuario)
            else:
                usuario = existing

            if usuario.id:
                prof = Professor(usuario_id=usuario.id, matricula=matricula, departamento=departamento)
                self.user_repo.save_professor(prof)
                professores_criados.append(usuario)

        return professores_criados


class AtribuirProfessorDisciplinaUseCase:
    """UC12: Assign teacher to discipline in a period"""
    def __init__(self, atribuicao_repo: IAtribuicaoRepository, periodo_repo: IPeriodoLetivoRepository):
        self.atribuicao_repo = atribuicao_repo
        self.periodo_repo = periodo_repo

    def execute(self, professor_id: int, disciplina_id: int, periodo_letivo_id: int, horario: str = "") -> AtribuicaoProfessorDisciplina:
        atribuicao = AtribuicaoProfessorDisciplina(
            id=None,
            professor_id=professor_id,
            disciplina_id=disciplina_id,
            periodo_letivo_id=periodo_letivo_id,
            horario=horario
        )
        return self.atribuicao_repo.save_atribuicao(atribuicao)


class CadastrarDiasLetivosUseCase:
    """UC14: Register class days and validate RF11"""
    def __init__(self, atribuicao_repo: IAtribuicaoRepository, periodo_repo: IPeriodoLetivoRepository):
        self.atribuicao_repo = atribuicao_repo
        self.periodo_repo = periodo_repo

    def execute(self, atribuicao_id: int, dias: List[Dict[str, Any]]) -> AtribuicaoProfessorDisciplina:
        atribuicao = self.atribuicao_repo.find_atribuicao_by_id(atribuicao_id)
        if not atribuicao:
            raise ValueError(f"Atribuição {atribuicao_id} não encontrada.")

        disciplina = self.atribuicao_repo.find_disciplina_by_id(atribuicao.disciplina_id)
        if not disciplina:
            raise ValueError(f"Disciplina {atribuicao.disciplina_id} não encontrada.")

        periodo = self.periodo_repo.find_by_id(atribuicao.periodo_letivo_id)
        if not periodo:
            raise ValueError(f"Período letivo {atribuicao.periodo_letivo_id} não encontrado.")

        atribuicao.dias_letivos = []
        for d in dias:
            data_val = d["data"] if isinstance(d["data"], date) else date.fromisoformat(str(d["data"]))
            turno = d.get("turno", "matutino")
            dia_entity = DiaLetivoDisciplina(id=None, atribuicao_id=atribuicao_id, data=data_val, turno=turno)
            atribuicao.adicionar_dia_letivo(dia_entity)

        valido = ValidadorCargaHoraria.validar(atribuicao, disciplina, periodo)
        if not valido:
            faltantes = ValidadorCargaHoraria.calcular_minutos_faltantes(atribuicao, disciplina, periodo)
            raise ValueError(f"RF11 Violição: Carga horária insuficiente! Faltam {faltantes} minutos para atingir a carga de {disciplina.carga_horaria}h.")

        return self.atribuicao_repo.save_atribuicao(atribuicao)
