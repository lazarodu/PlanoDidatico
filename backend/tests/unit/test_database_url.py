from src.infra.database import normalize_database_url


def test_converts_postgres_scheme_to_asyncpg():
    url = normalize_database_url("postgres://user:pass@db.example.com:5432/planos")
    assert url == "postgresql+asyncpg://user:pass@db.example.com:5432/planos"


def test_converts_postgresql_scheme_to_asyncpg():
    url = normalize_database_url("postgresql://user:pass@db.example.com/planos")
    assert url == "postgresql+asyncpg://user:pass@db.example.com/planos"


def test_keeps_asyncpg_scheme_untouched():
    url = "postgresql+asyncpg://user:pass@db.example.com/planos"
    assert normalize_database_url(url) == url


def test_translates_libpq_ssl_options_to_asyncpg():
    url = normalize_database_url(
        "postgres://user:pass@db.example.com/planos"
        "?sslmode=require&channel_binding=require"
    )
    assert url == "postgresql+asyncpg://user:pass@db.example.com/planos?ssl=require"


def test_preserves_supported_query_parameters():
    url = normalize_database_url(
        "postgresql://user:pass@db.example.com/planos?application_name=api"
    )
    assert url == "postgresql+asyncpg://user:pass@db.example.com/planos?application_name=api"
