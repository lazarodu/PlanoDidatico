from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date

@dataclass
class Disciplina:
    id: Optional[int]
    codigo: str
    nome: str
    carga_horaria: int
    natureza: str = "Obrigatória"
    area_formacao: str = "Específica"
    departamento: str = "DECOM"


@dataclass
class PeriodoLetivo:
    id: Optional[int]
    ano: int
    semestre: int
    ativo: bool
    data_inicio: date
    data_fim: date
    data_limite_entrega_plano: date
    minutos_por_dia_letivo: int = 100

    def get_minutos_por_dia_letivo(self) -> int:
        return self.minutos_por_dia_letivo

    def get_data_limite_entrega_plano(self) -> date:
        return self.data_limite_entrega_plano

    def validar_plano_entregue_no_prazo(self, data_entrega: date) -> bool:
        return data_entrega <= self.data_limite_entrega_plano


@dataclass
class DiaLetivoDisciplina:
    id: Optional[int]
    atribuicao_id: Optional[int]
    data: date
    turno: str = "matutino"  # matutino, vespertino, noturno

    def get_minutos_contribuicao(self, periodo_minutos: int) -> int:
        return periodo_minutos


@dataclass
class AtribuicaoProfessorDisciplina:
    id: Optional[int]
    professor_id: int
    disciplina_id: int
    periodo_letivo_id: int
    horario: str = ""
    dias_letivos: List[DiaLetivoDisciplina] = field(default_factory=list)

    def adicionar_dia_letivo(self, dia: DiaLetivoDisciplina) -> None:
        self.dias_letivos.append(dia)

    def remover_dia_letivo(self, dia_id: int) -> None:
        self.dias_letivos = [d for d in self.dias_letivos if d.id != dia_id]

    def calcular_total_minutos(self, minutos_por_dia: int = 100) -> int:
        return len(self.dias_letivos) * minutos_por_dia

    def validar_carga_horaria_suficiente(self, carga_horaria_disciplina: int, minutos_por_dia: int = 100) -> bool:
        carga_minutos = carga_horaria_disciplina * 60 if carga_horaria_disciplina < 200 else carga_horaria_disciplina
        return self.calcular_total_minutos(minutos_por_dia) >= carga_minutos
