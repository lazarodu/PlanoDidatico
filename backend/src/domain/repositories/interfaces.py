from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from src.domain.entities.user import Usuario, Professor
from src.domain.entities.didactic_plan import DidacticPlan
from src.domain.entities.atribuicao import Disciplina, PeriodoLetivo, AtribuicaoProfessorDisciplina, DiaLetivoDisciplina
from src.domain.entities.notification import NotificationPreference, NotificationLog
from src.domain.value_objects.field_config import CampoFormulario


class IUsuarioRepository(ABC):
    @abstractmethod
    async def save(self, usuario: Usuario) -> Usuario: pass

    @abstractmethod
    async def find_by_id(self, usuario_id: int) -> Optional[Usuario]: pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Usuario]: pass

    @abstractmethod
    async def list_all(self) -> List[Usuario]: pass

    @abstractmethod
    async def save_professor(self, professor: Professor) -> Professor: pass

    @abstractmethod
    async def find_professor_by_id(self, usuario_id: int) -> Optional[Professor]: pass


class IDidacticPlanRepository(ABC):
    @abstractmethod
    async def save(self, plan: DidacticPlan) -> DidacticPlan: pass

    @abstractmethod
    async def find_by_id(self, plan_id: int) -> Optional[DidacticPlan]: pass

    @abstractmethod
    async def find_by_professor_disciplina_periodo(self, professor_id: int, disciplina_id: int, periodo_letivo_id: int) -> Optional[DidacticPlan]: pass

    @abstractmethod
    async def list_by_professor(self, professor_id: int) -> List[DidacticPlan]: pass

    @abstractmethod
    async def list_by_periodo(self, periodo_letivo_id: int) -> List[DidacticPlan]: pass

    @abstractmethod
    async def list_all(self) -> List[DidacticPlan]: pass

    @abstractmethod
    async def save_campo_formulario(self, campo: CampoFormulario) -> CampoFormulario: pass

    @abstractmethod
    async def list_campos_formulario(self) -> List[CampoFormulario]: pass

    @abstractmethod
    async def delete_campo_formulario(self, campo_id: int) -> bool: pass


class IAtribuicaoRepository(ABC):
    @abstractmethod
    async def save_disciplina(self, disciplina: Disciplina) -> Disciplina: pass

    @abstractmethod
    async def find_disciplina_by_id(self, disciplina_id: int) -> Optional[Disciplina]: pass

    @abstractmethod
    async def list_disciplinas(self) -> List[Disciplina]: pass

    @abstractmethod
    async def save_atribuicao(self, atribuicao: AtribuicaoProfessorDisciplina) -> AtribuicaoProfessorDisciplina: pass

    @abstractmethod
    async def find_atribuicao_by_id(self, atribuicao_id: int) -> Optional[AtribuicaoProfessorDisciplina]: pass

    @abstractmethod
    async def list_atribuicoes_by_periodo(self, periodo_letivo_id: int) -> List[AtribuicaoProfessorDisciplina]: pass

    @abstractmethod
    async def list_atribuicoes_by_professor(self, professor_id: int) -> List[AtribuicaoProfessorDisciplina]: pass

    @abstractmethod
    async def save_dia_letivo(self, dia: DiaLetivoDisciplina) -> DiaLetivoDisciplina: pass

    @abstractmethod
    async def delete_dia_letivo(self, dia_id: int) -> bool: pass


class IPeriodoLetivoRepository(ABC):
    @abstractmethod
    async def save(self, periodo: PeriodoLetivo) -> PeriodoLetivo: pass

    @abstractmethod
    async def find_by_id(self, periodo_id: int) -> Optional[PeriodoLetivo]: pass

    @abstractmethod
    async def get_ativo(self) -> Optional[PeriodoLetivo]: pass

    @abstractmethod
    async def set_ativo(self, periodo_id: int) -> None: pass

    @abstractmethod
    async def list_all(self) -> List[PeriodoLetivo]: pass


class INotificationRepository(ABC):
    @abstractmethod
    async def save_preference(self, pref: NotificationPreference) -> NotificationPreference: pass

    @abstractmethod
    async def find_preference_by_usuario_id(self, usuario_id: int) -> Optional[NotificationPreference]: pass

    @abstractmethod
    async def save_log(self, log: NotificationLog) -> NotificationLog: pass

    @abstractmethod
    async def list_logs_by_usuario(self, usuario_id: int) -> List[NotificationLog]: pass


class INotifier(ABC):
    @abstractmethod
    async def enviar(self, destinatario: str, mensagem: str, titulo: Optional[str] = None) -> bool: pass
