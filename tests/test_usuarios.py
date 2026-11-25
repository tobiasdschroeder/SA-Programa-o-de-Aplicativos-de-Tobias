# Testes isolados do repositório de usuários usando SQLite temporário.

import tempfile
import unittest
from pathlib import Path

from models.usuario import UsuarioRepository


class UsuarioRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.diretorio = tempfile.TemporaryDirectory()
        self.banco = Path(self.diretorio.name) / "usuarios.sqlite3"
        self.repositorio = UsuarioRepository(self.banco)

    def tearDown(self):
        self.diretorio.cleanup()

    def test_cria_e_autentica_usuario(self):
        self.repositorio.criar_usuario("Usuário Teste", "teste", "senha-correta")
        autenticado = self.repositorio.verificar_senha("teste", "senha-correta")
        self.assertEqual(autenticado["usuario"], "teste")

    def test_senha_incorreta_rejeitada(self):
        self.repositorio.criar_usuario("Usuário Teste", "teste", "senha-correta")
        self.assertIsNone(self.repositorio.verificar_senha("teste", "senha-incorreta"))

    def test_atualiza_perfil_e_senha(self):
        usuario_id = self.repositorio.criar_usuario("Usuário Teste", "teste", "senha-correta")
        self.repositorio.atualizar_usuario(usuario_id, "Nome Atualizado", "novo-teste", "nova-senha")
        perfil = self.repositorio.buscar_por_id(usuario_id)
        self.assertEqual(perfil["nome"], "Nome Atualizado")
        self.assertEqual(perfil["usuario"], "novo-teste")
        self.assertIsNotNone(self.repositorio.verificar_senha("novo-teste", "nova-senha"))

    def test_exclui_usuario(self):
        usuario_id = self.repositorio.criar_usuario("Usuário Teste", "teste", "senha-correta")
        self.repositorio.excluir_usuario(usuario_id)
        self.assertIsNone(self.repositorio.buscar_por_id(usuario_id))


if __name__ == "__main__":
    unittest.main()
