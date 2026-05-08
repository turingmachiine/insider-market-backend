import importlib
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.backend.admin_service.infrastructure.db.metadata import mapper_registry

importlib.import_module("src.backend.admin_service.infrastructure.db.tables")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = mapper_registry.metadata


def get_url() -> str:
    import os
    from urllib.parse import quote_plus

    database_url = os.getenv("DATABASE_URL_ADMIN")
    if database_url:
        return database_url

    user = os.getenv("POSTGRES_USER_ADMIN", "postgres")
    password = os.getenv("POSTGRES_PASSWORD_ADMIN", "postgres")  # NOSONAR(S2068)
    host = os.getenv("POSTGRES_HOST_ADMIN", "localhost")
    port = os.getenv("POSTGRES_PORT_ADMIN", "5439")
    db = os.getenv("POSTGRES_DB_ADMIN", "admin_db")
    return f"postgresql+asyncpg://{user}:{quote_plus(password)}@{host}:{port}/{db}"


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def run_async_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    def do_run_migrations(connection: Connection) -> None:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    import asyncio

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
