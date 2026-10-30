from typing import Dict, Any, List, Optional
from datetime import date
from src.domain.entities.didactic_plan import DidacticPlan
from src.domain.value_objects.field_config import CampoFormulario
from src.domain.repositories.interfaces import IDidacticPlanRepository, IPeriodoLetivoRepository


class SubmitDidacticPlanUseCase:
    """UC1, UC2, UC3: Submit Didactic Plan"""
    def __init__(self, plan_repo: IDidacticPlanRepository, periodo_repo: IPeriodoLetivoRepository):
        self.plan_repo = plan_repo
        self.periodo_repo = periodo_repo

    async def execute(self, professor_id: int, disciplina_id: int, periodo_letivo_id: int, campos: Dict[str, Any]) -> DidacticPlan:
        campos_config = await self.plan_repo.list_campos_formulario()
        for c in campos_config:
            if c.obrigatorio and (c.nome not in campos or campos[c.nome] is None or campos[c.nome] == ""):
                raise ValueError(f"Campo obrigatório não preenchido: {c.nome}")

        existing = await self.plan_repo.find_by_professor_disciplina_periodo(professor_id, disciplina_id, periodo_letivo_id)
        if existing:
            existing.campos = campos
            existing.marcar_como_entregue(date.today())
            return await self.plan_repo.save(existing)

        new_plan = DidacticPlan(
            id=None,
            professor_id=professor_id,
            disciplina_id=disciplina_id,
            periodo_letivo_id=periodo_letivo_id,
            campos=campos,
            status="ENTREGUE",
            data_entrega=date.today()
        )
        return await self.plan_repo.save(new_plan)


class ManageFieldsUseCase:
    """UC8: Manage form fields (Admin)"""
    def __init__(self, plan_repo: IDidacticPlanRepository):
        self.plan_repo = plan_repo

    async def add_campo(self, nome: str, tipo: str, obrigatorio: bool, ordem: int = 0, opcoes: Optional[List[str]] = None) -> CampoFormulario:
        campo = CampoFormulario(id=None, nome=nome, tipo=tipo, obrigatorio=obrigatorio, ordem=ordem, opcoes=opcoes)
        return await self.plan_repo.save_campo_formulario(campo)

    async def list_campos(self) -> List[CampoFormulario]:
        return await self.plan_repo.list_campos_formulario()

    async def delete_campo(self, campo_id: int) -> bool:
        return await self.plan_repo.delete_campo_formulario(campo_id)