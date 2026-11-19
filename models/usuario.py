"""Modelo e persistência dos usuários do sistema.

Classe e repositório responsáveis pelo cadastro, hash e autenticação de usuários.
"""

import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from database import database_connection


class UsuarioRepository:
    # Persiste contas e verifica credenciais por meio de hashes seguros.

    def __init__(self, caminho=None):
        self.caminho = caminho
        self._inicializar()

    def _inicializar(self):
        with database_connection(caminho=self.caminho) as conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    usuario TEXT NOT NULL UNIQUE,
                    senha_hash TEXT NOT NULL,
                    ativo INTEGER NOT NULL DEFAULT 1
                        CHECK (ativo IN (0, 1))
                )
            """)

    def criar_usuario(self, nome, usuario, senha, ativo=1):
        nome = str(nome).strip()
        usuario = str(usuario).strip()
        senha = str(senha)
        if not nome or not usuario or not senha:
            raise ValueError("Nome, usuário e senha são obrigatórios.")
        if len(usuario) < 3:
            raise ValueError("O nome de usuário deve ter pelo menos 3 caracteres.")
        if len(senha) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        with database_connection(caminho=self.caminho) as conexao:
            try:
                cursor = conexao.execute("""
                    INSERT INTO usuarios (nome, usuario, senha_hash, ativo)
                    VALUES (?, ?, ?, ?)
                """, (nome, usuario, generate_password_hash(senha), int(bool(ativo))))
                return cursor.lastrowid
            except sqlite3.IntegrityError as erro:
                raise ValueError("O usuário já está cadastrado.") from erro

    def buscar_por_usuario(self, usuario):
        with database_connection(caminho=self.caminho) as conexao:
            registro = conexao.execute("""
                SELECT id, nome, usuario, senha_hash, ativo
                FROM usuarios WHERE usuario = ?
            """, (str(usuario).strip(),)).fetchone()
            return dict(registro) if registro else None

    def verificar_senha(self, usuario, senha):
        registro = self.buscar_por_usuario(usuario)
        if not registro or not registro["ativo"]:
            return None
        if not check_password_hash(registro["senha_hash"], str(senha)):
            return None
        return {"id": registro["id"], "nome": registro["nome"], "usuario": registro["usuario"]}

    def contar_usuarios(self):
        with database_connection(caminho=self.caminho) as conexao:
            registro = conexao.execute("SELECT COUNT(*) AS total FROM usuarios").fetchone()
            return int(registro["total"])
