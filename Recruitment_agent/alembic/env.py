from logging.config import fileConfig

import os
import sys

from dotenv import load_dotenv
from sqlalchemy import pool, create_engine

from alembic import context


# Load .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Add app/ to Python path
sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "app")
)

# Import SQLAlchemy Base and models
from database import Base
from models import Job


# Alembic Config object
config = context.config


# Configure Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:

    url = DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:

    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()