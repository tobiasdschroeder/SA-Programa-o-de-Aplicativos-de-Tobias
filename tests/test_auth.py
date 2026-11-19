"""Testes da autenticação Flask.

Valida redirecionamentos, sessão, login, logout, CSRF e primeiro cadastro.
"""

import unittest
from app import create_app


# Repositório falso usado pelos testes para não depender de dados reais.
class RepositorioUsuarioTeste:
    def verificar_senha(self, usuario, senha):
        if usuario == "teste" and senha == "senha-correta":
            return {"id": 1, "nome": "Usuário Teste", "usuario": "teste"}
        return None

    def contar_usuarios(self):
        return 1


class RepositorioSemUsuariosTeste:
    def contar_usuarios(self):
        return 0


class WebAuthTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "USUARIO_REPOSITORY": RepositorioUsuarioTeste(),
        })
        self.client = self.app.test_client()

    def obter_token(self):
        with self.client.session_transaction() as sessao:
            return sessao.get("csrf_token")

    def test_sem_login_redireciona_para_login(self):
        resposta = self.client.get("/dashboard")
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login", resposta.headers["Location"])

    def test_login_valido_abre_dashboard(self):
        self.client.get("/login")
        resposta = self.client.post("/login", data={
            "usuario": "teste",
            "senha": "senha-correta",
            "csrf_token": self.obter_token(),
        })
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/dashboard", resposta.headers["Location"])

    def test_senha_incorreta_rejeita_acesso(self):
        self.client.get("/login")
        resposta = self.client.post("/login", data={
            "usuario": "teste",
            "senha": "incorreta",
            "csrf_token": self.obter_token(),
        })
        self.assertEqual(resposta.status_code, 401)

    def test_usuario_inexistente_rejeita_acesso(self):
        self.client.get("/login")
        resposta = self.client.post("/login", data={
            "usuario": "inexistente",
            "senha": "qualquer",
            "csrf_token": self.obter_token(),
        })
        self.assertEqual(resposta.status_code, 401)

    def test_campos_vazios_rejeitados(self):
        self.client.get("/login")
        resposta = self.client.post("/login", data={
            "usuario": "",
            "senha": "",
            "csrf_token": self.obter_token(),
        })
        self.assertEqual(resposta.status_code, 400)

    def test_logout_encerra_sessao(self):
        self.client.get("/login")
        self.client.post("/login", data={
            "usuario": "teste",
            "senha": "senha-correta",
            "csrf_token": self.obter_token(),
        })
        token = self.obter_token()
        resposta = self.client.post("/logout", data={"csrf_token": token})
        self.assertEqual(resposta.status_code, 302)
        resposta = self.client.get("/dashboard")
        self.assertIn("/login", resposta.headers["Location"])

    def test_pacientes_exigem_login_e_acceptam_sessao_valida(self):
        resposta = self.client.get("/pacientes/cadastrar")
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login", resposta.headers["Location"])

        self.client.get("/login")
        token = self.obter_token()
        self.client.post("/login", data={
            "usuario": "teste",
            "senha": "senha-correta",
            "csrf_token": token,
        })
        resposta = self.client.get("/pacientes/cadastrar")
        self.assertEqual(resposta.status_code, 200)

    def test_csrf_invalido(self):
        resposta = self.client.post("/login", data={
            "usuario": "teste",
            "senha": "senha-correta",
            "csrf_token": "token-invalido",
        })
        self.assertEqual(resposta.status_code, 400)

    def test_primeiro_acesso_redireciona_para_cadastro(self):
        app = create_app({
            "TESTING": True,
            "USUARIO_REPOSITORY": RepositorioSemUsuariosTeste(),
        })
        client = app.test_client()
        resposta_raiz = client.get("/")
        resposta_login = client.get("/login")
        self.assertIn("/usuarios/cadastrar", resposta_raiz.headers["Location"])
        self.assertIn("/usuarios/cadastrar", resposta_login.headers["Location"])


if __name__ == "__main__":
    unittest.main()
