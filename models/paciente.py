"""Validações, entidade, persistência e casos de uso do módulo de pacientes."""

import re
import sqlite3
from datetime import date, datetime

from database import database_connection


STATUS_ATIVO = "ativo"
STATUS_INATIVO = "inativo"
TIPOS_SANGUINEOS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
CAMPOS_CADASTRO = {"nome", "cpf", "data_nascimento", "telefone", "endereco", "tipo_sanguineo"}
CAMPOS_ATUALIZACAO = CAMPOS_CADASTRO | {"status"}


def validar_texto(valor, campo):
    texto = str(valor).strip() if valor is not None else ""
    if not texto:
        raise ValueError(f"{campo} é obrigatório.")
    return texto


def validar_cpf(valor):
    if valor is None:
        raise ValueError("CPF é obrigatório.")
    texto = str(valor).strip()
    if not re.fullmatch(r"(?:[0-9]{11}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2})", texto):
        raise ValueError("CPF inválido. Use 11 dígitos ou 999.999.999-99.")
    cpf = re.sub(r"\D", "", texto)
    if cpf == cpf[0] * 11:
        raise ValueError("CPF inválido.")
    for posicao in (10, 11):
        soma = sum(int(cpf[indice]) * (posicao - indice) for indice in range(posicao - 1))
        digito = (soma * 10) % 11
        digito = 0 if digito == 10 else digito
        if int(cpf[posicao - 1]) != digito:
            raise ValueError("CPF inválido.")
    return cpf


def validar_data(valor):
    if valor is None:
        raise ValueError("Data de nascimento é obrigatória.")
    if isinstance(valor, datetime):
        data = valor.date()
    elif isinstance(valor, date):
        data = valor
    else:
        data = None
        for formato in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                data = datetime.strptime(str(valor).strip(), formato).date()
                break
            except ValueError:
                continue
        if data is None:
            raise ValueError("Data inválida. Use DD/MM/AAAA ou AAAA-MM-DD.")
    if data > date.today():
        raise ValueError("Data de nascimento não pode ser futura.")
    return data


def validar_telefone(valor):
    if valor is None:
        raise ValueError("Telefone é obrigatório.")
    texto = str(valor).strip()
    padrao = r"(?:[0-9]{10,11}|\([0-9]{2}\) ?[0-9]{4,5}-[0-9]{4}|[0-9]{2} ?[0-9]{4,5}-[0-9]{4})"
    if not re.fullmatch(padrao, texto):
        raise ValueError("Telefone inválido. Informe DDD e número em formato válido.")
    telefone = re.sub(r"\D", "", texto)
    if telefone == telefone[0] * len(telefone):
        raise ValueError("Telefone inválido.")
    return telefone


def validar_tipo_sanguineo(valor):
    if valor is None or not str(valor).strip():
        return None
    tipo = str(valor).strip().upper()
    if tipo not in TIPOS_SANGUINEOS:
        raise ValueError("Tipo sanguíneo inválido.")
    return tipo


def validar_status(valor):
    status = str(valor).strip().lower() if valor is not None else ""
    if status not in {STATUS_ATIVO, STATUS_INATIVO}:
        raise ValueError("Status deve ser 'ativo' ou 'inativo'.")
    return status


def validar_inteiro(valor):
    texto = str(valor).strip()
    if not re.fullmatch(r"[0-9]+", texto) or int(texto) <= 0:
        raise ValueError("Informe um número inteiro positivo.")
    return int(texto)


class Paciente:
    # Agrupa os dados validados e fornece representações para tela e banco.
    def __init__(self, paciente_id, nome, cpf, data_nascimento, telefone, endereco,
                 tipo_sanguineo=None, status=STATUS_ATIVO):
        self.id = validar_inteiro(paciente_id)
        self.nome = validar_texto(nome, "Nome completo")
        self.cpf = validar_cpf(cpf)
        self.data_nascimento = validar_data(data_nascimento)
        self.telefone = validar_telefone(telefone)
        self.endereco = validar_texto(endereco, "Endereço")
        self.tipo_sanguineo = validar_tipo_sanguineo(tipo_sanguineo)
        self.status = validar_status(status)

    @property
    def idade(self):
        hoje = date.today()
        idade = hoje.year - self.data_nascimento.year
        if (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day):
            idade -= 1
        return idade

    def to_dict(self):
        return {
            "id": self.id, "nome": self.nome, "cpf": self.cpf,
            "data_nascimento": self.data_nascimento.strftime("%d/%m/%Y"),
            "telefone": self.telefone, "endereco": self.endereco,
            "tipo_sanguineo": self.tipo_sanguineo, "status": self.status,
            "idade": self.idade,
        }

    def to_record(self):
        return {
            "id": self.id, "nome": self.nome, "cpf": self.cpf,
            "data_nascimento": self.data_nascimento.isoformat(),
            "telefone": self.telefone, "endereco": self.endereco,
            "tipo_sanguineo": self.tipo_sanguineo, "status": self.status,
        }


class SQLitePacienteRepository:
    # Persiste pacientes e registra uma trilha das operações realizadas.
    def __init__(self, caminho=None):
        self.caminho = caminho
        self._inicializar()

    def _conectar(self):
        return database_connection(caminho=self.caminho)

    def _inicializar(self):
        with self._conectar() as conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS pacientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL, cpf TEXT NOT NULL UNIQUE,
                    data_nascimento TEXT NOT NULL, telefone TEXT NOT NULL,
                    endereco TEXT NOT NULL, tipo_sanguineo TEXT,
                    status TEXT NOT NULL CHECK (status IN ('ativo', 'inativo'))
                )
            """)
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS transacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER NOT NULL,
                    operacao TEXT NOT NULL,
                    registrada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def listar(self):
        with self._conectar() as conexao:
            return [dict(registro) for registro in conexao.execute("SELECT * FROM pacientes ORDER BY id")]

    def listar_transacoes(self):
        with self._conectar() as conexao:
            return [dict(registro) for registro in conexao.execute(
                "SELECT id, paciente_id, operacao, registrada_em FROM transacoes ORDER BY id"
            )]

    def ultimo_id(self):
        with self._conectar() as conexao:
            registro = conexao.execute("SELECT COALESCE(MAX(seq), 0) FROM sqlite_sequence WHERE name = 'pacientes'").fetchone()
            return registro[0]

    def salvar(self, registro, operacao):
        with self._conectar() as conexao:
            if operacao == "CADASTRO":
                conexao.execute("""
                    INSERT INTO pacientes (id, nome, cpf, data_nascimento, telefone, endereco, tipo_sanguineo, status)
                    VALUES (:id, :nome, :cpf, :data_nascimento, :telefone, :endereco, :tipo_sanguineo, :status)
                """, registro)
            else:
                cursor = conexao.execute("""
                    UPDATE pacientes SET nome=:nome, cpf=:cpf, data_nascimento=:data_nascimento,
                    telefone=:telefone, endereco=:endereco, tipo_sanguineo=:tipo_sanguineo, status=:status
                    WHERE id=:id
                """, registro)
                if cursor.rowcount == 0:
                    raise ValueError("Paciente não encontrado para persistir a alteração.")
            conexao.execute("INSERT INTO transacoes (paciente_id, operacao) VALUES (?, ?)", (registro["id"], operacao))

    def excluir(self, paciente_id):
        with self._conectar() as conexao:
            conexao.execute("INSERT INTO transacoes (paciente_id, operacao) VALUES (?, 'EXCLUSAO')", (paciente_id,))
            conexao.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))


class PacienteManager:
    # Coordena validação, regras de negócio e chamadas ao repositório.
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or SQLitePacienteRepository()
        self.pacientes = [Paciente(r["id"], r["nome"], r["cpf"], r["data_nascimento"], r["telefone"], r["endereco"], r["tipo_sanguineo"], r["status"]) for r in self.repositorio.listar()] 

    def _novo_id(self):
        ids = {paciente.id for paciente in self.pacientes}
        id = 1
        while id in ids:
            id += 1
        return id

    def buscar_por_id(self, paciente_id, incluir_inativos=True):
        try:
            id = validar_inteiro(paciente_id)
        except ValueError:
            return None
        return next((p for p in self.pacientes if p.id == id and (incluir_inativos or p.status == STATUS_ATIVO)), None)

    def buscar_por_cpf(self, cpf, incluir_inativos=True):
        try:
            cpf = validar_cpf(cpf)
        except ValueError:
            return None
        return next((p for p in self.pacientes if p.cpf == cpf and (incluir_inativos or p.status == STATUS_ATIVO)), None)

    def buscar(self, identificador, incluir_inativos=True):
        texto = str(identificador).strip()
        if texto.upper().startswith("ID:"):
            return self.buscar_por_id(texto[3:].strip(), incluir_inativos)
        if texto.upper().startswith("CPF:"):
            return self.buscar_por_cpf(texto[4:].strip(), incluir_inativos)
        if re.fullmatch(r"[0-9]{11}", texto):
            return self.buscar_por_cpf(texto, incluir_inativos)
        if re.fullmatch(r"[0-9]+", texto):
            return self.buscar_por_id(texto, incluir_inativos)
        return self.buscar_por_cpf(texto, incluir_inativos)

    def verificar_paciente_cadastrado(self, cpf, incluir_inativos=True):
        return self.buscar_por_cpf(validar_cpf(cpf), incluir_inativos) is not None

    def cadastrar_paciente(self, dados=None, **kwargs):
        dados = dados or {}
        dados = {**dados, **kwargs}
        if not isinstance(dados, dict):
            return {"sucesso": False, "mensagem": "Os dados devem ser informados em um dicionário."}
        desconhecidos = set(dados) - CAMPOS_CADASTRO
        if desconhecidos:
            return {"sucesso": False, "mensagem": f"Campo desconhecido: {next(iter(desconhecidos))}"}
        try:
            dados = {
                "nome": validar_texto(dados.get("nome"), "Nome completo"),
                "cpf": validar_cpf(dados.get("cpf")),
                "data_nascimento": validar_data(dados.get("data_nascimento")),
                "telefone": validar_telefone(dados.get("telefone")),
                "endereco": validar_texto(dados.get("endereco"), "Endereço"),
                "tipo_sanguineo": validar_tipo_sanguineo(dados.get("tipo_sanguineo")),
            }
            if self.verificar_paciente_cadastrado(dados["cpf"]):
                return {"sucesso": False, "mensagem": f"O CPF {dados['cpf']} já está cadastrado."}
            paciente = Paciente(self._novo_id(), **dados)
            self.repositorio.salvar(paciente.to_record(), "CADASTRO")
            self.pacientes.append(paciente)
            return {"sucesso": True, "mensagem": "Paciente cadastrado com sucesso.", "paciente": paciente.to_dict()}
        except (ValueError, sqlite3.IntegrityError) as erro:
            mensagem = "O CPF informado já está cadastrado." if isinstance(erro, sqlite3.IntegrityError) else str(erro)
            return {"sucesso": False, "mensagem": mensagem}

    def consultar_paciente(self, identificador, incluir_inativos=True):
        paciente = self.buscar(identificador, incluir_inativos)
        return paciente.to_dict() if paciente else None

    def listar_pacientes(self, incluir_inativos=False):
        return [p.to_dict() for p in self.pacientes if incluir_inativos or p.status == STATUS_ATIVO]

    def listar_pacientes_inativos(self):
        return [p.to_dict() for p in self.pacientes if p.status == STATUS_INATIVO]

    def atualizar_paciente(self, paciente_id, novos_dados=None, **kwargs):
        paciente = self.buscar_por_id(paciente_id)
        if paciente is None:
            return {"sucesso": False, "mensagem": "Paciente não encontrado."}
        dados = {**(novos_dados or {}), **kwargs}
        if not dados:
            return {"sucesso": False, "mensagem": "Nenhuma alteração foi informada."}
        desconhecidos = set(dados) - CAMPOS_ATUALIZACAO
        if desconhecidos:
            return {"sucesso": False, "mensagem": f"Campo desconhecido: {next(iter(desconhecidos))}"}
        validadores = {"nome": lambda v: validar_texto(v, "Nome completo"), "cpf": validar_cpf,
                       "data_nascimento": validar_data, "telefone": validar_telefone,
                       "endereco": lambda v: validar_texto(v, "Endereço"),
                       "tipo_sanguineo": validar_tipo_sanguineo, "status": validar_status}
        try:
            alteracoes = {campo: validadores[campo](valor) for campo, valor in dados.items()}
            novo_cpf = alteracoes.get("cpf", paciente.cpf)
            if novo_cpf != paciente.cpf and self.buscar_por_cpf(novo_cpf, True):
                return {"sucesso": False, "mensagem": f"O CPF {novo_cpf} já está cadastrado."}
            anteriores = {campo: getattr(paciente, campo) for campo in alteracoes}
            status_anterior = paciente.status
            for campo, valor in alteracoes.items():
                setattr(paciente, campo, valor)
            try:
                operacao = "INATIVACAO" if status_anterior == STATUS_ATIVO and paciente.status == STATUS_INATIVO else "ATUALIZACAO"
                self.repositorio.salvar(paciente.to_record(), operacao)
            except Exception:
                for campo, valor in anteriores.items():
                    setattr(paciente, campo, valor)
                raise
            return {"sucesso": True, "mensagem": "Paciente atualizado com sucesso.", "paciente": paciente.to_dict()}
        except (ValueError, sqlite3.IntegrityError) as erro:
            mensagem = "O CPF informado já está cadastrado." if isinstance(erro, sqlite3.IntegrityError) else str(erro)
            return {"sucesso": False, "mensagem": mensagem}

    def desativar_paciente(self, paciente_id):
        paciente = self.buscar_por_id(paciente_id)
        if paciente is None:
            return {"sucesso": False, "mensagem": "Paciente não encontrado."}
        if paciente.status == STATUS_INATIVO:
            return {"sucesso": False, "mensagem": "O paciente já está inativo."}
        paciente.status = STATUS_INATIVO
        try:
            self.repositorio.salvar(paciente.to_record(), "INATIVACAO")
        except Exception:
            paciente.status = STATUS_ATIVO
            raise
        return {"sucesso": True, "mensagem": "Paciente desativado com sucesso.", "paciente": paciente.to_dict()}

    def excluir_paciente_inativo(self, paciente_id):
        paciente = self.buscar_por_id(paciente_id)
        if paciente is None:
            return {"sucesso": False, "mensagem": "Paciente não encontrado."}
        if paciente.status != STATUS_INATIVO:
            return {"sucesso": False, "mensagem": "Somente pacientes inativos podem ser excluídos."}
        dados = paciente.to_dict()
        self.repositorio.excluir(paciente.id)
        self.pacientes.remove(paciente)
        return {"sucesso": True, "mensagem": "Paciente excluído permanentemente.", "paciente": dados}
