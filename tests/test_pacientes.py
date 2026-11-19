"""Testes de regras de negócio e persistência usando somente dados fictícios.

Cada teste usa um banco temporário para não alterar dados reais.
"""

import tempfile
import unittest
from pathlib import Path

from models.paciente import PacienteManager, SQLitePacienteRepository


class PacienteManagerTests(unittest.TestCase):
    def setUp(self):
        self.diretorio = tempfile.TemporaryDirectory()
        caminho_banco = Path(self.diretorio.name) / "teste.sqlite3"
        self.repositorio = SQLitePacienteRepository(caminho_banco)
        self.manager = PacienteManager(self.repositorio)
        self.dados = {
            "nome": "Pessoa Fictícia",
            "cpf": "529.982.247-25",
            "data_nascimento": "10/05/1990",
            "telefone": "(11) 91234-5678",
            "endereco": "Rua de Teste, 10",
            "tipo_sanguineo": "O+",
        }

    def tearDown(self):
        self.diretorio.cleanup()

    def cadastrar(self):
        return self.manager.cadastrar_paciente(self.dados)

    def test_cadastro_valido_e_cpf_repetido(self):
        self.assertTrue(self.cadastrar()["sucesso"])
        repetido = self.manager.cadastrar_paciente(self.dados)
        self.assertFalse(repetido["sucesso"])
        self.assertIn("já está cadastrado", repetido["mensagem"])

    def test_rejeita_cpf_invalido_e_data_futura(self):
        cpf_invalido = dict(self.dados, cpf="11111111111")
        data_futura = dict(self.dados, cpf="11144477735", data_nascimento="31/12/2999")
        self.assertFalse(self.manager.cadastrar_paciente(cpf_invalido)["sucesso"])
        resultado_futuro = self.manager.cadastrar_paciente(data_futura)
        self.assertFalse(resultado_futuro["sucesso"])
        self.assertIn("não pode ser futura", resultado_futuro["mensagem"])

    def test_telefone_valido_e_invalido(self):
        self.assertTrue(self.cadastrar()["sucesso"])
        telefone_invalido = dict(self.dados, cpf="11144477735", telefone="123")
        self.assertFalse(self.manager.cadastrar_paciente(telefone_invalido)["sucesso"])

    def test_consulta_por_id_e_cpf(self):
        paciente = self.cadastrar()["paciente"]
        cpf_normalizado = self.dados["cpf"].replace(".", "").replace("-", "")
        self.assertEqual(
            self.manager.consultar_paciente(paciente["id"])["cpf"],
            cpf_normalizado,
        )
        paciente_por_cpf = self.manager.consultar_paciente(self.dados["cpf"])
        self.assertEqual(paciente_por_cpf["id"], paciente["id"])

    def test_atualizacao_invalida_nao_altera_registro(self):
        paciente = self.cadastrar()["paciente"]
        atualizacao = self.manager.atualizar_paciente(
            paciente["id"],
            {"nome": "Novo nome", "telefone": "ruim"},
        )
        self.assertFalse(atualizacao["sucesso"])
        paciente_atual = self.manager.consultar_paciente(paciente["id"])
        self.assertEqual(paciente_atual["nome"], self.dados["nome"])

    def test_atualizacao_valida_e_inativacao_sao_persistidas(self):
        paciente = self.cadastrar()["paciente"]
        atualizacao = self.manager.atualizar_paciente(
            paciente["id"], {"nome": "Nome Atualizado"}
        )
        self.assertTrue(atualizacao["sucesso"])
        manager_reiniciado = PacienteManager(self.repositorio)
        nome_persistido = manager_reiniciado.consultar_paciente(paciente["id"])["nome"]
        self.assertEqual(nome_persistido, "Nome Atualizado")
        inativacao = self.manager.atualizar_paciente(
            paciente["id"], {"status": "inativo"}
        )
        self.assertTrue(inativacao["sucesso"])
        operacoes = [item["operacao"] for item in self.repositorio.listar_transacoes()]
        self.assertEqual(operacoes, ["CADASTRO", "ATUALIZACAO", "INATIVACAO"])

    def test_persistencia_ciclo_de_vida_e_trilha(self):
        paciente = self.cadastrar()["paciente"]
        manager_reiniciado = PacienteManager(self.repositorio)
        self.assertIsNotNone(manager_reiniciado.consultar_paciente(paciente["id"]))
        exclusao_ativa = manager_reiniciado.excluir_paciente_inativo(paciente["id"])
        self.assertFalse(exclusao_ativa["sucesso"])
        desativacao = manager_reiniciado.desativar_paciente(paciente["id"])
        self.assertTrue(desativacao["sucesso"])
        self.assertEqual(manager_reiniciado.listar_pacientes(), [])
        self.assertEqual(len(manager_reiniciado.listar_pacientes_inativos()), 1)
        exclusao_inativa = manager_reiniciado.excluir_paciente_inativo(paciente["id"])
        self.assertTrue(exclusao_inativa["sucesso"])
        manager_final = PacienteManager(self.repositorio)
        self.assertIsNone(manager_final.consultar_paciente(paciente["id"]))
        operacoes = [item["operacao"] for item in self.repositorio.listar_transacoes()]
        self.assertEqual(operacoes, ["CADASTRO", "INATIVACAO", "EXCLUSAO"])

    def test_reutiliza_ids_excluidos_em_ordem_apos_reinicio(self):
        primeiro = self.cadastrar()["paciente"]
        segundo = self.manager.cadastrar_paciente(
            dict(self.dados, cpf="11144477735")
        )["paciente"]
        terceiro = self.manager.cadastrar_paciente(
            dict(self.dados, cpf="12345678909")
        )["paciente"]
        self.assertEqual(
            [primeiro["id"], segundo["id"], terceiro["id"]],
            [1, 2, 3],
        )

        self.manager.desativar_paciente(segundo["id"])
        self.manager.excluir_paciente_inativo(segundo["id"])
        manager_reiniciado = PacienteManager(self.repositorio)
        resultado_id_dois = manager_reiniciado.cadastrar_paciente(
            dict(self.dados, cpf="11144477735")
        )

        self.assertTrue(resultado_id_dois["sucesso"])
        self.assertEqual(resultado_id_dois["paciente"]["id"], segundo["id"])

        manager_reiniciado.desativar_paciente(terceiro["id"])
        manager_reiniciado.excluir_paciente_inativo(terceiro["id"])
        resultado_id_tres = manager_reiniciado.cadastrar_paciente(
            dict(self.dados, cpf="12345678909")
        )

        self.assertTrue(resultado_id_tres["sucesso"])
        self.assertEqual(resultado_id_tres["paciente"]["id"], terceiro["id"])


if __name__ == "__main__":
    unittest.main()