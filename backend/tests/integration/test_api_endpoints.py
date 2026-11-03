import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.infra.database import Base, get_db
from src.main import app


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_api_endpoints_flow(client):
    r_user = await client.post("/api/users", json={"nome": "Prof. Carlos", "email": "carlos@cefet.br", "tipo": "professor"})
    assert r_user.status_code == 200, r_user.text
    user_id = r_user.json()["id"]

    r_field = await client.post("/api/admin/fields", json={"nome": "conteudo_programatico", "tipo": "textarea", "obrigatorio": True, "ordem": 1})
    assert r_field.status_code == 200, r_field.text

    r_per = await client.post("/api/coordinator/periodo", json={
        "ano": 2026, "semestre": 1,
        "data_inicio": "2026-02-01", "data_fim": "2026-07-01",
        "data_limite_entrega_plano": "2026-03-01", "minutos_por_dia_letivo": 100, "ativo": True
    })
    assert r_per.status_code == 200, r_per.text
    periodo_id = r_per.json()["id"]

    r_disc = await client.post("/api/coordinator/disciplinas", json={"codigo": "DECOM10", "nome": "Engenharia de Software", "carga_horaria": 60})
    assert r_disc.status_code == 200, r_disc.text
    disc_id = r_disc.json()["id"]

    r_at = await client.post("/api/coordinator/atribuicao", json={"professor_id": user_id, "disciplina_id": disc_id, "periodo_letivo_id": periodo_id, "horario": "2T12"})
    assert r_at.status_code == 200, r_at.text
    atribuicao_id = r_at.json()["id"]

    dias = [{"data": f"2026-02-{(i%28)+1:02d}", "turno": "matutino"} for i in range(36)]
    r_dias = await client.post("/api/coordinator/dias-letivos", json={"atribuicao_id": atribuicao_id, "dias": dias})
    assert r_dias.status_code == 200, r_dias.text

    r_plan = await client.post("/api/plans/submit", json={
        "professor_id": user_id,
        "disciplina_id": disc_id,
        "periodo_letivo_id": periodo_id,
        "campos": {"conteudo_programatico": "Modulo 1: Requisitos, Modulo 2: DDD"}
    })
    assert r_plan.status_code == 200, r_plan.text
    plan_id = r_plan.json()["id"]

    r_pdf = await client.get(f"/api/plans/{plan_id}/pdf")
    assert r_pdf.status_code == 200, r_pdf.text
    assert r_pdf.headers["content-type"] == "application/pdf"
    assert len(r_pdf.content) > 500

    r_delay = await client.post("/api/notifications/check-delays")
    assert r_delay.status_code == 200, r_delay.text
