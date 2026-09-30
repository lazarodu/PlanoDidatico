from typing import Optional, List, Dict, Any
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
    INotificationRepository,
    INotifier
)

class InMemoryUsuarioRepository(IUsuarioRepository):
    def __init__(self):
        self.users: Dict[int, Usuario] = {}
        self.profs: Dict[int, Professor] = {}
        self.counter = 1

    def save(self, usuario: Usuario) -> Usuario:
        if usuario.id is None:
            usuario.id = self.counter
            self.counter += 1
        self.users[usuario.id] = usuario
        return usuario

    def find_by_id(self, usuario_id: int) -> Optional[Usuario]:
        return self.users.get(usuario_id)

    def find_by_email(self, email: str) -> Optional[Usuario]:
        for u in self.users.values():
            if u.email == email:
                return u
        return None

    def list_all(self) -> List[Usuario]:
        return list(self.users.values())

    def save_professor(self, professor: Professor) -> Professor:
        self.profs[professor.usuario_id] = professor
        return professor

    def find_professor_by_id(self, usuario_id: int) -> Optional[Professor]:
        return self.profs.get(usuario_id)


class InMemoryDidacticPlanRepository(IDidacticPlanRepository):
    def __init__(self):
        self.plans: Dict[int, DidacticPlan] = {}
        self.campos: Dict[int, CampoFormulario] = {}
        self.plan_counter = 1
        self.campo_counter = 1

    def save(self, plan: DidacticPlan) -> DidacticPlan:
        if plan.id is None:
            plan.id = self.plan_counter
            self.plan_counter += 1
        self.plans[plan.id] = plan
        return plan

    def find_by_id(self, plan_id: int) -> Optional[DidacticPlan]:
        return self.plans.get(plan_id)

    def find_by_professor_disciplina_periodo(self, professor_id: int, disciplina_id: int, periodo_letivo_id: int) -> Optional[DidacticPlan]:
        for p in self.plans.values():
            if p.professor_id == professor_id and p.disciplina_id == disciplina_id and p.periodo_letivo_id == periodo_letivo_id:
                return p
        return None

    def list_by_professor(self, professor_id: int) -> List[DidacticPlan]:
        return [p for p in self.plans.values() if p.professor_id == professor_id]

    def list_by_periodo(self, periodo_letivo_id: int) -> List[DidacticPlan]:
        return [p for p in self.plans.values() if p.periodo_letivo_id == periodo_letivo_id]

    def list_all(self) -> List[DidacticPlan]:
        return list(self.plans.values())

    def save_campo_formulario(self, campo: CampoFormulario) -> CampoFormulario:
        if campo.id is None:
            campo = CampoFormulario(id=self.campo_counter, nome=campo.nome, tipo=campo.tipo, obrigatorio=campo.obrigatorio, ordem=campo.ordem, opcoes=campo.opcoes)
            self.campo_counter += 1
        self.campos[campo.id] = campo
        return campo

    def list_campos_formulario(self) -> List[CampoFormulario]:
        return sorted(self.campos.values(), key=lambda c: c.ordem)

    def delete_campo_formulario(self, campo_id: int) -> bool:
        if campo_id in self.campos:
            del self.campos[campo_id]
            return True
        return False


class InMemoryAtribuicaoRepository(IAtribuicaoRepository):
    def __init__(self):
        self.disciplinas: Dict[int, Disciplina] = {}
        self.atribuicoes: Dict[int, AtribuicaoProfessorDisciplina] = {}
        self.disc_counter = 1
        self.at_counter = 1
        self.dia_counter = 1

    def save_disciplina(self, disciplina: Disciplina) -> Disciplina:
        if disciplina.id is None:
            disciplina.id = self.disc_counter
            self.disc_counter += 1
        self.disciplinas[disciplina.id] = disciplina
        return disciplina

    def find_disciplina_by_id(self, disciplina_id: int) -> Optional[Disciplina]:
        return self.disciplinas.get(disciplina_id)

    def list_disciplinas(self) -> List[Disciplina]:
        return list(self.disciplinas.values())

    def save_atribuicao(self, atribuicao: AtribuicaoProfessorDisciplina) -> AtribuicaoProfessorDisciplina:
        if atribuicao.id is None:
            atribuicao.id = self.at_counter
            self.at_counter += 1
        self.atribuicoes[atribuicao.id] = atribuicao
        return atribuicao

    def find_atribuicao_by_id(self, atribuicao_id: int) -> Optional[AtribuicaoProfessorDisciplina]:
        return self.atribuicoes.get(atribuicao_id)

    def list_atribuicoes_by_periodo(self, periodo_letivo_id: int) -> List[AtribuicaoProfessorDisciplina]:
        return [a for a in self.atribuicoes.values() if a.periodo_letivo_id == periodo_letivo_id]

    def list_atribuicoes_by_professor(self, professor_id: int) -> List[AtribuicaoProfessorDisciplina]:
        return [a for a in self.atribuicoes.values() if a.professor_id == professor_id]

    def save_dia_letivo(self, dia: DiaLetivoDisciplina) -> DiaLetivoDisciplina:
        if dia.id is None:
            dia.id = self.dia_counter
            self.dia_counter += 1
        return dia

    def delete_dia_letivo(self, dia_id: int) -> bool:
        return True


class InMemoryPeriodoLetivoRepository(IPeriodoLetivoRepository):
    def __init__(self):
        self.periodos: Dict[int, PeriodoLetivo] = {}
        self.counter = 1

    def save(self, periodo: PeriodoLetivo) -> PeriodoLetivo:
        if periodo.id is None:
            periodo.id = self.counter
            self.counter += 1
        self.periodos[periodo.id] = periodo
        return periodo

    def find_by_id(self, periodo_id: int) -> Optional[PeriodoLetivo]:
        return self.periodos.get(periodo_id)

    def get_ativo(self) -> Optional[PeriodoLetivo]:
        for p in self.periodos.values():
            if p.ativo:
                return p
        return None

    def set_ativo(self, periodo_id: int) -> None:
        for p in self.periodos.values():
            p.ativo = (p.id == periodo_id)

    def list_all(self) -> List[PeriodoLetivo]:
        return list(self.periodos.values())


class InMemoryNotificationRepository(INotificationRepository):
    def __init__(self):
        self.prefs: Dict[int, NotificationPreference] = {}
        self.logs: List[NotificationLog] = []
        self.pref_counter = 1
        self.log_counter = 1

    def save_preference(self, pref: NotificationPreference) -> NotificationPreference:
        if pref.id is None:
            pref.id = self.pref_counter
            self.pref_counter += 1
        self.prefs[pref.usuario_id] = pref
        return pref

    def find_preference_by_usuario_id(self, usuario_id: int) -> Optional[NotificationPreference]:
        return self.prefs.get(usuario_id)

    def save_log(self, log: NotificationLog) -> NotificationLog:
        if log.id is None:
            log.id = self.log_counter
            self.log_counter += 1
        self.logs.append(log)
        return log

    def list_logs_by_usuario(self, usuario_id: int) -> List[NotificationLog]:
        return [l for l in self.logs if l.usuario_id == usuario_id]


class FakeNotifier(INotifier):
    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        self.sent_messages = []

    async def enviar(self, destinatario: str, mensagem: str, titulo: Optional[str] = None) -> bool:
        if self.should_succeed:
            self.sent_messages.append((destinatario, mensagem, titulo))
            return True
        return False
