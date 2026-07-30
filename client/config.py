import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(dotenv_path=BASE_DIR / '.env')


class Config:
    GRPC_HOST: str = os.getenv('GRPC_HOST', 'localhost')
    GRPC_PORT: int = int(os.getenv('GRPC_PORT', '50051'))

    @property
    def GRPC_URL(self) -> str:
        return f'{self.GRPC_HOST}:{self.GRPC_PORT}'

    DB_NAME: str = os.getenv('DB_NAME', 'local.db')
    DB_PATH: Path = BASE_DIR / DB_NAME

    APP_TITLE: str = os.getenv('APP_TITLE', 'gRPC Client')


config = Config()
