"""Testes das operações web de pacientes usando dados totalmente fictícios."""

import tempfile
import unittest
from pathlib import Path

from app import create_app
from models.paciente import PacienteManager, SQLitePacienteRepository


class RepositorioUsuarioTeste:
    """Repositório mínimo que permite autenticar uma conta fictícia nos testes."""

    def contar_usuarios(self):
        return 1

    def verificar_senha(self, usuario, senha):
        if usuario == "ficticio" and senha == "senha-ficticia":
            return {"id": 1, "nome": "Usuário Fictício", "usuario": "ficticio"}
        return None


class OperacoesPacienteWebTests(unittest.TestCase):
    def setUp(self):
        self.diretorio = tempfile.TemporaryDirectory()
        banco = Path(self.diretorio.name) / "pacientes.sqlite3"
        manager = PacienteManager(SQLitePacienteRepository(banco))
        self.app = create_app({
            "TESTING": True,
            "USUARIO_REPOSITORY": RepositorioUsuarioTeste(),
            "PACIENTE_MANAGER": manager,
        })
        self.client = self.app.test_client()

    def tearDown(self):
        self.diretorio.cleanup()

    def autenticar(self):
        self.client.get("/login")
        with self.client.session_transaction() as sessao:
            token = sessao.get("csrf_token")
        return self.client.post("/login", data={
            "usuario": "ficticio",
            "senha": "senha-ficticia",
            "csrf_token": token,
        })

    def token_csrf(self):
        with self.client.session_transaction() as sessao:
            return sessao.get("csrf_token")

    def dados_paciente(self, cpf="11111111111"):
        return {
            "nome": "Paciente Demonstracao",
            "cpf": cpf,
            "data_nascimento": "10/05/1990",
            "telefone": "(11) 91234-5678",
            "endereco": "Rua Fictícia, 100",
            "tipo_sanguineo": "O+",
            "csrf_token": self.token_csrf(),
        }

    def test_login_dados_ficticios_cadastro_duplicado_e_verificacao(self):
        self.assertEqual(self.autenticar().status_code, 302)

        cadastro = self.client.post("/pacientes/cadastrar", data=self.dados_paciente())
        self.assertEqual(cadastro.status_code, 200)

        duplicado = self.client.post("/pacientes/cadastrar", data=self.dados_paciente())
        conteudo = duplicado.get_data(as_text=True)
        self.assertIn("já está cadastrado", conteudo)

        verificacao = self.client.post("/pacientes/verificar", data={
            "cpf": "11111111111",
            "csrf_token": self.token_csrf(),
        })
        self.assertEqual(verificacao.status_code, 200)
        self.assertIn("já cadastrado", verificacao.get_data(as_text=True))

    def test_csrf_invalido_em_operacao_de_paciente(self):
        self.autenticar()
        resposta = self.client.post("/pacientes/cadastrar", data={
            **self.dados_paciente(),
            "csrf_token": "token-invalido",
        })
        self.assertEqual(resposta.status_code, 400)


if __name__ == "__main__":
    unittest.main()
