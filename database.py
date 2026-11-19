"""Criação e acesso ao banco SQLite compartilhado."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path


def get_database_path(app=None):
    if app is not None:
        return app.config["DATABASE"]
    return str(Path(__file__).resolve().parent / "instance" / "database.db")


# Context manager responsável por abrir e fechar conexões SQLite com segurança.
@contextmanager
def database_connection(app=None, caminho=None):
    destino = Path(caminho or get_database_path(app))
    destino.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(destino)
    conexao.row_factory = sqlite3.Row
    try:
        with conexao:
            yield conexao
    finally:
        conexao.close()
