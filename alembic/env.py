"""
Alembic environment configuration

This file configures Alembic for database migrations.
Uses synchronous connection for migrations (more reliable).
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import all models to ensure they are registered
from leedhunter.infrastructure.database.base import Base
from leedhunter.infrastructure.database.models import (
    EntityModel,
    EntityIdentityModel,
    EvidenceModel,
    SignalModel,
    OpportunityModel,
    LeadModel,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url() -> str:
    """Get database URL from environment or config"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Try to get from environment
    db_host = os.getenv("LEEDHUNTER_DB_HOST", "localhost")
    db_port = os.getenv("LEEDHUNTER_DB_PORT", "5432")
    db_user = os.getenv("LEEDHUNTER_DB_USER", "leedhunter")
    db_password = os.getenv("LEEDHUNTER_DB_PASSWORD", "leedhunter")
    db_name = os.getenv("LEEDHUNTER_DB_NAME", "leedhunter")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
