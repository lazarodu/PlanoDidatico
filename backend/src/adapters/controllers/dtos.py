from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, time

class UserCreateDTO(BaseModel):
    nome: str
    email: str
    tipo: str  # admin, coordenador, professor

class UserResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    tipo: str

class CampoFormularioDTO(BaseModel):
    id: Optional[int] = None
    nome: str
    tipo: str  # text, select, textarea, date
    obrigatorio: bool = False
    ordem: int = 0
    opcoes: Optional[List[str]] = None

class PeriodoLetivoDTO(BaseModel):
    id: Optional[int] = None
    ano: int
    semestre: int
    data_inicio: date
    data_fim: date
    data_limite_entrega_plano: date
    minutos_por_dia_letivo: int = 100
    ativo: bool = True

class DisciplinaDTO(BaseModel):
    id: Optional[int] = None
    codigo: str
    nome: str
    carga_horaria: int
    natureza: str = "Obrigatória"
    area_formacao: str = "Específica"
    departamento: str = "DECOM"

class AtribuicaoDTO(BaseModel):
    id: Optional[int] = None
    professor_id: int
    disciplina_id: int
    periodo_letivo_id: int
    horario: str = ""

class DiaLetivoDTO(BaseModel):
    data: date
    turno: str = "matutino"

class CadastrarDiasLetivosDTO(BaseModel):
    atribuicao_id: int
    dias: List[DiaLetivoDTO]

class SubmitPlanDTO(BaseModel):
    professor_id: int
    disciplina_id: int
    periodo_letivo_id: int
    campos: Dict[str, Any]

class PlanResponseDTO(BaseModel):
    id: int
    professor_id: int
    disciplina_id: int
    periodo_letivo_id: int
    status: str
    data_entrega: Optional[date] = None
    campos: Dict[str, Any]

class NotificationConfigDTO(BaseModel):
    usuario_id: int
    canal_email: bool = True
    canal_telegram: bool = False
    chat_id_telegram: Optional[str] = None
    horario_preferido: Optional[time] = None
