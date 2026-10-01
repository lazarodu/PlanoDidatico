from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class DiaLetivo:
    data: date
    turno: str  # matutino, vespertino, noturno
