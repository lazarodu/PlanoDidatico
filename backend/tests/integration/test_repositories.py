import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.infra.database import Base
from src.adapters.repositories.sqlalchemy_repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyDidacticPlanRepository,
)
from src.domain.entities.user import Usuario, Professor
from src.domain.entities.didactic_plan import DidacticPlan
from src.domain.value_objects.field_config import CampoFormulario


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_sqlalchemy_user_repo(db_session):
    repo = SQLAlchemyUserRepository(db_session)
    u = Usuario(id=None, nome="Carlos", email="carlos@cefet.br", tipo="professor")
    saved = await repo.save(u)
    assert saved.id is not None

    found = await repo.find_by_email("carlos@cefet.br")
    assert found is not None
    assert found.nome == "Carlos"

    prof = Professor(usuario_id=saved.id, matricula="20261001", departamento="DECOM")
    await repo.save_professor(prof)
    found_prof = await repo.find_professor_by_id(saved.id)
    assert found_prof is not None
    assert found_prof.matricula == "20261001"


@pytest.mark.asyncio
async def test_sqlalchemy_plan_repo(db_session):
    repo = SQLAlchemyDidacticPlanRepository(db_session)
    campo = CampoFormulario(id=None, nome="metodologia", tipo="textarea", obrigatorio=True, ordem=1)
    saved_campo = await repo.save_campo_formulario(campo)
    assert saved_campo.id is not None

    campos_list = await repo.list_campos_formulario()
    assert len(campos_list) == 1

    plan = DidacticPlan(id=None, professor_id=1, disciplina_id=1, periodo_letivo_id=1, campos={"metodologia": "Ativa"})
    saved_plan = await repo.save(plan)
    assert saved_plan.id is not None

    found_plan = await repo.find_by_id(saved_plan.id)
    assert found_plan.campos == {"metodologia": "Ativa"}
