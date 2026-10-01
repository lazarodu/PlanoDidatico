from dataclasses import dataclass
from typing import Optional

@dataclass
class Usuario:
    id: Optional[int]
    nome: str
    email: str
    tipo: str  # admin, coordenador, professor

    def eh_admin(self) -> bool:
        return self.tipo == "admin"

    def eh_coordenador(self) -> bool:
        return self.tipo in ("admin", "coordenador")

    def eh_professor(self) -> bool:
        return self.tipo in ("admin", "coordenador", "professor")

    def pode_gerenciar_campos_formulario(self) -> bool:
        return self.eh_admin()

    def pode_importar_campos_fixos(self) -> bool:
        return self.eh_coordenador()

    def pode_preencher_campos_variaveis(self) -> bool:
        return self.eh_professor()


@dataclass
class Professor:
    usuario_id: int
    matricula: str
    departamento: str
