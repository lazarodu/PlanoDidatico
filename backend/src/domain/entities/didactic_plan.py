from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import date

@dataclass
class DidacticPlan:
    id: Optional[int]
    professor_id: int
    disciplina_id: int
    periodo_letivo_id: int
    campos: Dict[str, Any] = field(default_factory=dict)
    status: str = "PENDENTE"  # PENDENTE, ENTREGUE, VALIDADO, REPROVADO
    data_entrega: Optional[date] = None

    def esta_pendente(self) -> bool:
        return self.status == "PENDENTE"

    def marcar_como_entregue(self, data: Optional[date] = None) -> None:
        self.status = "ENTREGUE"
        self.data_entrega = data or date.today()

    def verificar_atraso(self, data_limite: date, hoje: Optional[date] = None) -> bool:
        hoje_ref = hoje or date.today()
        if self.status != "ENTREGUE":
            return hoje_ref > data_limite
        elif self.data_entrega:
            return self.data_entrega > data_limite
        return False

    def get_status(self) -> str:
        return self.status
