import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base


def normalize_database_url(url: str) -> str:
    """Adapta a URL do banco para o driver assíncrono usado pela aplicação.

    Provedores de banco (Render, Heroku, Neon etc.) costumam entregar a URL
    com o esquema ``postgres://`` ou ``postgresql://``. O SQLAlchemy precisa
    do driver explícito ``postgresql+asyncpg://``. Também traduzimos opções
    aceitas apenas pelo libpq (``sslmode``) para o parâmetro equivalente do
    asyncpg (``ssl``).
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    parts = urlsplit(url)
    scheme = "postgresql+asyncpg" if parts.scheme == "postgresql" else parts.scheme

    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    sslmode = query.pop("sslmode", None)
    query.pop("channel_binding", None)  # opção exclusiva do libpq

    if sslmode and "ssl" not in query:
        query["ssl"] = sslmode

    return urlunsplit((scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


DATABASE_URL = normalize_database_url(
    os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgrespassword@db:5432/planos_didaticos",
    )
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
