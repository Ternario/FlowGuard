from pathlib import Path
from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from alembic.config import Config as AlembicConfig

from config import config

SQLALCHEMY_DATABASE_URI = f'sqlite:///{config.DB_PATH}'

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def run_migrations() -> None:
    alembic_ini_path: Path = Path(__file__).parent.parent.parent / 'alembic.ini'
    alembic_cfg: AlembicConfig = AlembicConfig(str(alembic_ini_path))
    alembic_cfg.set_main_option('sqlalchemy.url', SQLALCHEMY_DATABASE_URI)

    command.upgrade(alembic_cfg, 'head')


def init_db() -> bool:
    is_first_run: bool = config.DB_PATH.exists()

    run_migrations()

    return is_first_run
