import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import src.adapters.repositories.models as models
from src.infra.database import Base, get_db
from src.main import app

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=test_engine)

def test_api_endpoints_flow(client):
    r_user = client.post("/api/users", json={"nome": "Prof. Carlos", "email": "carlos@cefet.br", "tipo": "professor"})
    assert r_user.status_code == 200, r_user.text
    user_id = r_user.json()["id"]

    r_field = client.post("/api/admin/fields", json={"nome": "conteudo_programatico", "tipo": "textarea", "obrigatorio": True, "ordem": 1})
    assert r_field.status_code == 200, r_field.text

    r_per = client.post("/api/coordinator/periodo", json={
        "ano": 2026, "semestre": 1,
        "data_inicio": "2026-02-01", "data_fim": "2026-07-01",
        "data_limite_entrega_plano": "2026-03-01", "minutos_por_dia_letivo": 100, "ativo": True
    })
    assert r_per.status_code == 200, r_per.text
    periodo_id = r_per.json()["id"]

    r_disc = client.post("/api/coordinator/disciplinas", json={"codigo": "DECOM10", "nome": "Engenharia de Software", "carga_horaria": 60})
    assert r_disc.status_code == 200, r_disc.text
    disc_id = r_disc.json()["id"]

    r_at = client.post("/api/coordinator/atribuicao", json={"professor_id": user_id, "disciplina_id": disc_id, "periodo_letivo_id": periodo_id, "horario": "2T12"})
    assert r_at.status_code == 200, r_at.text
    atribuicao_id = r_at.json()["id"]

    dias = [{"data": f"2026-02-{(i%28)+1:02d}", "turno": "matutino"} for i in range(36)]
    r_dias = client.post("/api/coordinator/dias-letivos", json={"atribuicao_id": atribuicao_id, "dias": dias})
    assert r_dias.status_code == 200, r_dias.text

    r_plan = client.post("/api/plans/submit", json={
        "professor_id": user_id,
        "disciplina_id": disc_id,
        "periodo_letivo_id": periodo_id,
        "campos": {"conteudo_programatico": "Modulo 1: Requisitos, Modulo 2: DDD"}
    })
    assert r_plan.status_code == 200, r_plan.text
    plan_id = r_plan.json()["id"]

    r_pdf = client.get(f"/api/plans/{plan_id}/pdf")
    assert r_pdf.status_code == 200, r_pdf.text
    assert r_pdf.headers["content-type"] == "application/pdf"
    assert len(r_pdf.content) > 500

    r_delay = client.post("/api/notifications/check-delays")
    assert r_delay.status_code == 200, r_delay.text
