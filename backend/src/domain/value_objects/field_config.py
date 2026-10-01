from dataclasses import dataclass
from typing import Optional, List

@dataclass(frozen=True)
class CampoFormulario:
    id: Optional[int]
    nome: str
    tipo: str  # text, select, textarea, date
    obrigatorio: bool
    ordem: int = 0
    opcoes: Optional[List[str]] = None
