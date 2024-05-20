"""Alembic environment configuration."""

from logging.config import fileConfig
from os import getenv as os_getenv

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from alembic import context
from dds_glossary.model import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config  # pylint: disable=no-member

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata
database_url = os_getenv(
    "DATABASE_URL",
    config.get_main_option(
        "sqlalchemy.url",
        "postgresql+psycopg://user:pass@localhost:5432/dbname",
    ),
)


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(  # pylint: disable=no-member
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():  # pylint: disable=no-member
        context.run_migrations()  # pylint: disable=no-member


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(database_url, poolclass=NullPool)

    with connectable.connect() as connection:
        context.configure(  # pylint: disable=no-member
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():  # pylint: disable=no-member
            context.run_migrations()  # pylint: disable=no-member


if context.is_offline_mode():  # pylint: disable=no-member
    run_migrations_offline()
else:
    run_migrations_online()
