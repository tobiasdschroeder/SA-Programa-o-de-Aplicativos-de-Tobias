"""Configurações centralizadas da aplicação Flask."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    PERMANENT_SESSION_LIFETIME = 1800
    DATABASE = os.environ.get("DATABASE_PATH", str(INSTANCE_DIR / "database.db"))


class TestConfig(Config):
    """Configurações separadas por ambiente e por testes automatizados."""
    TESTING = True
    SECRET_KEY = "chave-local-apenas-para-testes"
