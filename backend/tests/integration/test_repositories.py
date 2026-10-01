import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infra.database import Base
from src.adapters.repositories.sqlalchemy_repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyDidacticPlanRepository,
    SQLAlchemyAtribuicaoRepository,
    SQLAlchemyPeriodoLetivoRepository,
    SQLAlchemyNotificationRepository
)
from src.domain.entities.user import Usuario, Professor
from src.domain.entities.atribuicao import Disciplina, PeriodoLetivo, AtribuicaoProfessorDisciplina
from src.domain.entities.didactic_plan import DidacticPlan
from src.domain.value_objects.field_config import CampoFormulario

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_sqlalchemy_user_repo(db_session):
    repo = SQLAlchemyUserRepository(db_session)
    u = Usuario(id=None, nome="Carlos", email="carlos@cefet.br", tipo="professor")
    saved = repo.save(u)
    assert saved.id is not None

    found = repo.find_by_email("carlos@cefet.br")
    assert found is not None
    assert found.nome == "Carlos"

    prof = Professor(usuario_id=saved.id, matricula="20261001", departamento="DECOM")
    repo.save_professor(prof)
    found_prof = repo.find_professor_by_id(saved.id)
    assert found_prof is not None
    assert found_prof.matricula == "20261001"

def test_sqlalchemy_plan_repo(db_session):
    repo = SQLAlchemyDidacticPlanRepository(db_session)
    campo = CampoFormulario(id=None, nome="metodologia", tipo="textarea", obrigatorio=True, ordem=1)
    saved_campo = repo.save_campo_formulario(campo)
    assert saved_campo.id is not None

    campos_list = repo.list_campos_formulario()
    assert len(campos_list) == 1

    plan = DidacticPlan(id=None, professor_id=1, disciplina_id=1, periodo_letivo_id=1, campos={"metodologia": "Ativa"})
    saved_plan = repo.save(plan)
    assert saved_plan.id is not None

    found_plan = repo.find_by_id(saved_plan.id)
    assert found_plan.campos == {"metodologia": "Ativa"}
