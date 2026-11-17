import os
import re
from datetime import date, datetime

# CONSTANTES: centralizam valores utilizados pelo sistema.
STATUS_ATIVO, STATUS_INATIVO = "ativo", "inativo"
OPCOES_MENU = {"0", "1", "2", "3", "4", "5", "6", "7"}
TIPOS_SANGUINEOS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
CAMPOS_CADASTRO = {"nome", "cpf", "data_nascimento", "telefone", "endereco", "tipo_sanguineo"}
CAMPOS_ATUALIZACAO = CAMPOS_CADASTRO | {"status"}

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def limpar_terminal():
    # Identifica o sistema operacional para executar o comando correto.
    os.system("cls" if os.name == "nt" else "clear")

def perguntar(mensagem=""):
    # Centraliza a entrada de dados pelo terminal.
    return input(mensagem)

def perguntar_valido(mensagem, validador):
    # Repete a pergunta até que o valor passe pela validação.
    while True:
        try:
            return validador(perguntar(mensagem))
        except ValueError as erro:
            print(f"Erro: {erro}")

def validar_sim_nao(valor):
    # Normaliza a resposta e aceita somente "s" ou "n".
    resposta = valor.strip().lower()
    if resposta not in {"s", "n"}:
        raise ValueError("Digite apenas s ou n.")
    return resposta

def perguntar_sim_nao(mensagem):
    # Reutiliza a validação de respostas binárias.
    return perguntar_valido(mensagem, validar_sim_nao)

def validar_inteiro(valor):
    # Aceita somente números inteiros positivos.
    texto = str(valor).strip()
    if not re.fullmatch(r"[0-9]+", texto) or int(texto) <= 0:
        raise ValueError("Informe um número inteiro positivo.")
    return int(texto)

def ler_inteiro(mensagem):
    # Solicita um número inteiro utilizando a validação centralizada.
    return perguntar_valido(mensagem, validar_inteiro)

def resultado(sucesso, mensagem, paciente=None):
    # Padroniza o retorno das operações do gerenciador.
    resposta = {"sucesso": sucesso, "mensagem": mensagem}
    if paciente is not None:
        resposta["paciente"] = paciente
    return resposta

# ============================================================
# VALIDAÇÕES DOS DADOS
# ============================================================

def validar_texto(valor, campo):
    # Remove espaços externos e impede o envio de campos vazios.
    texto = str(valor).strip() if valor is not None else ""
    if not texto:
        raise ValueError(f"{campo} é obrigatório.")
    return texto

def validar_cpf(valor):
    # Verifica o formato do CPF antes de calcular seus dígitos verificadores.
    if valor is None:
        raise ValueError("CPF é obrigatório.")
    texto = str(valor).strip()
    padrao = r"(?:[0-9]{11}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2})"
    if not re.fullmatch(padrao, texto):
        raise ValueError("CPF inválido. Use 11 dígitos ou 999.999.999-99.")
    # Remove a pontuação para realizar os cálculos.
    cpf = re.sub(r"\D", "", texto)
    # Rejeita CPFs formados por um único algarismo repetido.
    if cpf == cpf[0] * 11:
        raise ValueError("CPF inválido.")
    # Calcula e confere os dois dígitos verificadores.
    for posicao in (10, 11):
        soma = sum(int(cpf[i]) * (posicao - i) for i in range(posicao - 1))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if int(cpf[posicao - 1]) != digito:
            raise ValueError("CPF inválido.")
    # Retorna o CPF sem pontuação para padronizar o armazenamento.
    return cpf

def validar_data(valor):
    # Aceita objetos date, datetime e datas em dois formatos de texto.
    if valor is None:
        raise ValueError("Data de nascimento é obrigatória.")
    # datetime é tratado antes de date por ser uma subclasse de date.
    if isinstance(valor, datetime):
        data = valor.date()
    elif isinstance(valor, date):
        data = valor
    else:
        texto = str(valor).strip()
        data = None
        # Tenta interpretar a data em cada formato permitido.
        for formato in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                data = datetime.strptime(texto, formato).date()
                break
            except ValueError:
                pass
        if data is None:
            raise ValueError("Data inválida. Use DD/MM/AAAA ou AAAA-MM-DD.")
    # Impede o cadastro de datas futuras.
    if data > date.today():
        raise ValueError("Data de nascimento não pode ser futura.")
    return data

def validar_telefone(valor):
    # Aceita telefone com DDD, com ou sem formatação.
    if valor is None:
        raise ValueError("Telefone é obrigatório.")
    texto = str(valor).strip()
    padrao = r"(?:[0-9]{10,11}|\([0-9]{2}\) ?[0-9]{4,5}-[0-9]{4}|[0-9]{2} ?[0-9]{4,5}-[0-9]{4})"
    if not re.fullmatch(padrao, texto):
        raise ValueError("Telefone inválido. Informe DDD e número em formato válido.")
    # Remove espaços, parênteses e hífens.
    telefone = re.sub(r"\D", "", texto)
    # Rejeita números compostos pelo mesmo algarismo repetido.
    if telefone == telefone[0] * len(telefone):
        raise ValueError("Telefone inválido.")
    return telefone

def validar_tipo_sanguineo(valor):
    # Permite ausência de informação, mas restringe os tipos informados.
    if valor is None or not str(valor).strip():
        return None
    tipo = str(valor).strip().upper()
    if tipo not in TIPOS_SANGUINEOS:
        raise ValueError("Tipo sanguíneo inválido.")
    return tipo

def validar_status(valor):
    # Garante que o status seja ativo ou inativo.
    status = str(valor).strip().lower() if valor is not None else ""
    if status not in {STATUS_ATIVO, STATUS_INATIVO}:
        raise ValueError("Status deve ser 'ativo' ou 'inativo'.")
    return status

# ============================================================
# MODELO PACIENTE
# ============================================================

class Paciente:
    # Representa um paciente e armazena seus dados validados.
    def __init__(self, paciente_id, nome, cpf, data_nascimento, telefone, endereco, tipo_sanguineo=None, status=STATUS_ATIVO):
        # Valida os dados antes de atribuí-los aos atributos do objeto.
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
        # Calcula a idade considerando se o aniversário já ocorreu no ano atual.
        hoje = date.today()
        idade = hoje.year - self.data_nascimento.year
        if (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day):
            idade -= 1
        return idade

    def to_dict(self):
        # Converte o objeto em dicionário para facilitar sua exibição e utilização.
        return {
            "id": self.id, "nome": self.nome, "cpf": self.cpf,
            "data_nascimento": self.data_nascimento.strftime("%d/%m/%Y"),
            "telefone": self.telefone, "endereco": self.endereco,
            "tipo_sanguineo": self.tipo_sanguineo,
            "status": self.status, "idade": self.idade
        }

# ============================================================
# GERENCIADOR DE PACIENTES
# ============================================================

class PacienteManager:
    # Centraliza as operações realizadas sobre os pacientes.
    def __init__(self):
        # Mantém os pacientes em memória e controla a sequência dos IDs.
        self.pacientes = []
        self._ultimo_id = 0

    def _novo_id(self):
        # Gera o próximo ID sem reutilizar identificadores anteriores.
        return self._ultimo_id + 1

    def buscar_por_id(self, paciente_id, incluir_inativos=True):
        # Procura um paciente pelo ID e permite filtrar os inativos.
        try:
            identificador = validar_inteiro(paciente_id)
        except ValueError:
            return None
        return next((p for p in self.pacientes if p.id == identificador and (incluir_inativos or p.status == STATUS_ATIVO)), None)

    def buscar_por_cpf(self, cpf, incluir_inativos=True):
        # Procura um paciente pelo CPF já normalizado.
        try:
            cpf = validar_cpf(cpf)
        except ValueError:
            return None
        return next((p for p in self.pacientes if p.cpf == cpf and (incluir_inativos or p.status == STATUS_ATIVO)), None)

    def buscar(self, identificador, incluir_inativos=True):
        # Identifica se a pesquisa utiliza ID ou CPF.
        # Os prefixos ID: e CPF: permitem resolver possíveis ambiguidades.
        texto = str(identificador).strip()
        if texto.upper().startswith("ID:"):
            return self.buscar_por_id(texto[3:].strip(), incluir_inativos)
        if texto.upper().startswith("CPF:"):
            return self.buscar_por_cpf(texto[4:].strip(), incluir_inativos)
        # Por convenção, uma sequência de 11 dígitos é considerada CPF.
        if re.fullmatch(r"[0-9]{11}", texto):
            return self.buscar_por_cpf(texto, incluir_inativos)
        if re.fullmatch(r"[0-9]+", texto):
            return self.buscar_por_id(texto, incluir_inativos)
        return self.buscar_por_cpf(texto, incluir_inativos)

    def verificar_paciente_cadastrado(self, cpf, incluir_inativos=True):
        # Confirma se o CPF já pertence a algum paciente cadastrado.
        cpf = validar_cpf(cpf)
        return self.buscar_por_cpf(cpf, incluir_inativos) is not None

    def cadastrar_paciente(self, dados=None, **kwargs):
        # Recebe os dados, valida os campos e cria um novo paciente.
        if dados is None:
            dados = {}
        if not isinstance(dados, dict):
            return resultado(False, "Os dados devem ser informados em um dicionário.")
        # Permite receber dados por dicionário ou argumentos nomeados.
        dados = {**dados, **kwargs}
        desconhecidos = set(dados) - CAMPOS_CADASTRO
        if desconhecidos:
            return resultado(False, f"Campo desconhecido: {next(iter(desconhecidos))}")
        try:
            # Valida todos os campos antes de criar o objeto.
            dados_validados = {
                "nome": validar_texto(dados.get("nome"), "Nome completo"),
                "cpf": validar_cpf(dados.get("cpf")),
                "data_nascimento": validar_data(dados.get("data_nascimento")),
                "telefone": validar_telefone(dados.get("telefone")),
                "endereco": validar_texto(dados.get("endereco"), "Endereço"),
                "tipo_sanguineo": validar_tipo_sanguineo(dados.get("tipo_sanguineo"))
            }
            # Impede o cadastro de um CPF que já esteja registrado.
            if self.verificar_paciente_cadastrado(dados_validados["cpf"]):
                return resultado(False, f"O CPF {dados_validados['cpf']} já está cadastrado.")
            # Cria o paciente e atualiza o contador somente após a validação.
            novo_id = self._novo_id()
            paciente = Paciente(novo_id, **dados_validados)
            self.pacientes.append(paciente)
            self._ultimo_id = novo_id
            return resultado(True, "Paciente cadastrado com sucesso.", paciente.to_dict())
        except ValueError as erro:
            return resultado(False, str(erro))

    def consultar_paciente(self, identificador, incluir_inativos=True):
        # Retorna os dados do paciente encontrado em formato de dicionário.
        paciente = self.buscar(identificador, incluir_inativos)
        return paciente.to_dict() if paciente else None

    def listar_pacientes(self, incluir_inativos=False):
        # Lista pacientes ativos por padrão; permite incluir inativos.
        return [p.to_dict() for p in self.pacientes if incluir_inativos or p.status == STATUS_ATIVO]

    def listar_pacientes_inativos(self):
        # Retorna exclusivamente os pacientes com status inativo.
        return [p.to_dict() for p in self.pacientes if p.status == STATUS_INATIVO]

    def atualizar_paciente(self, paciente_id, novos_dados=None, **kwargs):
        # Atualiza os dados de um paciente sem aplicar alterações inválidas parcialmente.
        paciente = self.buscar_por_id(paciente_id)
        if paciente is None:
            return resultado(False, "Paciente não encontrado.")
        if novos_dados is not None and not isinstance(novos_dados, dict):
            return resultado(False, "Os novos dados devem ser informados em um dicionário.")
        dados = {**(novos_dados or {}), **kwargs}
        if not dados:
            return resultado(False, "Nenhuma alteração foi informada.")
        # Rejeita atributos que não fazem parte dos campos permitidos.
        desconhecidos = set(dados) - CAMPOS_ATUALIZACAO
        if desconhecidos:
            return resultado(False, f"Campo desconhecido: {next(iter(desconhecidos))}")
        # Associa cada campo à sua função específica de validação.
        validadores = {
            "nome": lambda v: validar_texto(v, "Nome completo"),
            "cpf": validar_cpf,
            "data_nascimento": validar_data,
            "telefone": validar_telefone,
            "endereco": lambda v: validar_texto(v, "Endereço"),
            "tipo_sanguineo": validar_tipo_sanguineo,
            "status": validar_status
        }
        try:
            # Valida todas as alterações antes de modificar o paciente.
            alteracoes = {campo: validadores[campo](valor) for campo, valor in dados.items()}
            novo_cpf = alteracoes.get("cpf", paciente.cpf)
            # Verifica se o novo CPF já pertence a outro paciente.
            if novo_cpf != paciente.cpf and self.buscar_por_cpf(novo_cpf, True):
                return resultado(False, f"O CPF {novo_cpf} já está cadastrado.")
            # Aplica as alterações somente depois de todas as validações.
            for campo, valor in alteracoes.items():
                setattr(paciente, campo, valor)
            return resultado(True, "Paciente atualizado com sucesso.", paciente.to_dict())
        except ValueError as erro:
            return resultado(False, str(erro))

    def desativar_paciente(self, paciente_id):
        # Altera o status sem remover os dados do paciente.
        paciente = self.buscar_por_id(paciente_id)
        if paciente is None:
            return resultado(False, "Paciente não encontrado.")
        if paciente.status == STATUS_INATIVO:
            return resultado(False, "O paciente já está inativo.")
        paciente.status = STATUS_INATIVO
        return resultado(True, "Paciente desativado com sucesso.", paciente.to_dict())

    def excluir_paciente_inativo(self, paciente_id):
        # Permite excluir permanentemente somente pacientes inativos.
        paciente = self.buscar_por_id(paciente_id)
        if paciente is None:
            return resultado(False, "Paciente não encontrado.")
        if paciente.status != STATUS_INATIVO:
            return resultado(False, "Somente pacientes inativos podem ser excluídos.")
        # Guarda os dados antes de remover o objeto da lista.
        dados = paciente.to_dict()
        self.pacientes.remove(paciente)
        return resultado(True, "Paciente excluído permanentemente.", dados)

# ============================================================
# INTERFACE DO TERMINAL
# ============================================================

def exibir_paciente(paciente):
    # Organiza os dados do paciente para apresentação no terminal.
    print("\n=== Dados do paciente ===")
    campos = [
        ("ID", "id"), ("Nome", "nome"), ("CPF", "cpf"),
        ("Data de nascimento", "data_nascimento"), ("Telefone", "telefone"),
        ("Endereço", "endereco"), ("Tipo sanguíneo", "tipo_sanguineo"),
        ("Status", "status")
    ]
    for descricao, chave in campos:
        print(f"{descricao}: {paciente.get(chave) or 'Não informado'}")
    print(f"Idade: {paciente['idade']} anos\n========================")

def exibir_mensagem(resultado_operacao):
    # Exibe o resultado de uma operação e os dados do paciente, se houver.
    print(f"\n{resultado_operacao['mensagem']}")
    if resultado_operacao["sucesso"]:
        exibir_paciente(resultado_operacao["paciente"])

def menu():
    # Apresenta as opções disponíveis para o usuário.
    print("\n=== Sistema Hospitalar - Pacientes ===\n1. Cadastrar paciente\n2. Consultar paciente\n3. Listar pacientes ativos\n4. Atualizar paciente\n5. Listar pacientes inativos\n6. Excluir paciente inativo\n7. Verificar CPF cadastrado\n0. Sair")

def cadastrar_terminal(manager):
    # Coleta as informações do paciente e envia os dados ao gerenciador.
    print("\n--- Cadastro de paciente ---")
    dados = {
        "nome": perguntar_valido("Nome completo: ", lambda v: validar_texto(v, "Nome completo")),
        "cpf": perguntar_valido("CPF: ", validar_cpf),
        "data_nascimento": perguntar_valido("Data de nascimento (DD/MM/AAAA): ", validar_data),
        "telefone": perguntar_valido("Telefone: ", validar_telefone),
        "endereco": perguntar_valido("Endereço: ", lambda v: validar_texto(v, "Endereço")),
        "tipo_sanguineo": perguntar_valido("Tipo sanguíneo (opcional): ", validar_tipo_sanguineo)
    }
    exibir_mensagem(manager.cadastrar_paciente(dados))

def validar_identificador_terminal(valor):
    # Interpreta a entrada do usuário como ID ou CPF.
    # Permite prefixos explícitos para evitar confusão entre identificadores.
    texto = valor.strip()
    if texto.upper().startswith("ID:"):
        return f"ID:{validar_inteiro(texto[3:])}"
    if texto.upper().startswith("CPF:"):
        return f"CPF:{validar_cpf(texto[4:])}"
    if re.fullmatch(r"[0-9]{11}", texto):
        return validar_cpf(texto)
    if re.fullmatch(r"[0-9]+", texto):
        return validar_inteiro(texto)
    if "." in texto or "-" in texto:
        return validar_cpf(texto)
    raise ValueError("Informe um ID ou CPF válido.")

def consultar_terminal(manager):
    # Solicita um identificador e exibe o cadastro encontrado.
    print("\n--- Consulta de paciente ---")
    identificador = perguntar_valido("Informe o CPF ou ID do paciente: ", validar_identificador_terminal)
    paciente = manager.consultar_paciente(identificador)
    if paciente is None:
        print("\nPaciente não encontrado.")
        return
    exibir_paciente(paciente)

def listar_terminal(manager):
    # Exibe os pacientes ativos cadastrados.
    pacientes = manager.listar_pacientes()
    if not pacientes:
        print("\nNenhum paciente ativo cadastrado.")
        return
    print("\n--- Pacientes ativos ---")
    for p in pacientes:
        print(f"ID: {p['id']} | Nome: {p['nome']} | CPF: {p['cpf']}")

def coletar_alteracoes(paciente, manager):
    # Pergunta quais campos o usuário deseja atualizar.
    campos = {
        "nome": "Nome completo", "cpf": "CPF",
        "data_nascimento": "Data de nascimento", "telefone": "Telefone",
        "endereco": "Endereço", "tipo_sanguineo": "Tipo sanguíneo",
        "status": "Status"
    }
    # Define a validação correspondente a cada campo.
    validadores = {
        "nome": lambda v: validar_texto(v, "Nome completo"),
        "cpf": validar_cpf, "data_nascimento": validar_data,
        "telefone": validar_telefone,
        "endereco": lambda v: validar_texto(v, "Endereço"),
        "tipo_sanguineo": validar_tipo_sanguineo,
        "status": validar_status
    }
    alteracoes = {}
    for campo, descricao in campos.items():
        # Só solicita o novo valor quando o usuário confirma a alteração.
        if perguntar_sim_nao(f"Deseja alterar {descricao}? (s/n): ") == "s":
            alteracoes[campo] = perguntar_valido(
                f"Novo valor para {descricao}: ", validadores[campo]
            )
    return alteracoes

def atualizar_terminal(manager):
    # Localiza o paciente e encaminha as alterações escolhidas.
    print("\n--- Atualização de paciente ---")
    paciente_id = ler_inteiro("ID do paciente: ")
    paciente = manager.buscar_por_id(paciente_id)
    if paciente is None:
        print("Paciente não encontrado.")
        return
    alteracoes = coletar_alteracoes(paciente, manager)
    if not alteracoes:
        print("Nenhuma alteração informada.")
        return
    exibir_mensagem(manager.atualizar_paciente(paciente_id, alteracoes))

def listar_inativos_terminal(manager):
    # Exibe somente os pacientes desativados.
    pacientes = manager.listar_pacientes_inativos()
    if not pacientes:
        print("\nNenhum paciente inativo cadastrado.")
        return
    print("\n--- Pacientes inativos ---")
    for p in pacientes:
        print(f"ID: {p['id']} | Nome: {p['nome']} | CPF: {p['cpf']}")

def excluir_inativo_terminal(manager):
    # Solicita confirmação antes de excluir permanentemente um cadastro.
    print("\n--- Exclusão de paciente inativo ---")
    paciente_id = ler_inteiro("ID do paciente inativo: ")
    if perguntar_sim_nao("Confirmar exclusão permanente? (s/n): ") != "s":
        print("Exclusão cancelada.")
        return
    exibir_mensagem(manager.excluir_paciente_inativo(paciente_id))

def verificar_terminal(manager):
    # Verifica se o CPF informado já está registrado.
    cpf = perguntar_valido("Informe o CPF para verificar: ", validar_cpf)
    print("CPF já cadastrado no sistema." if manager.verificar_paciente_cadastrado(cpf) else "CPF disponível para cadastro.")

# ============================================================
# CONTROLE DO MENU
# ============================================================

def executar_opcao(manager, opcao):
    # Relaciona cada opção do menu à função responsável por executá-la.
    operacoes = {
        "1": cadastrar_terminal, "2": consultar_terminal,
        "3": listar_terminal, "4": atualizar_terminal,
        "5": listar_inativos_terminal, "6": excluir_inativo_terminal,
        "7": verificar_terminal
    }
    operacao = operacoes.get(opcao)
    if operacao:
        operacao(manager)

def validar_opcao_menu(valor):
    # Impede a execução de opções inexistentes.
    if valor not in OPCOES_MENU:
        raise ValueError("Escolha uma opção entre 0 e 7.")
    return valor

def main():
    # Inicializa o gerenciador e mantém o menu em execução.
    manager = PacienteManager()
    print("\nBem-vindo ao Sistema Hospitalar\nMódulo de gerenciamento de pacientes")
    while True:
        menu()
        opcao = perguntar_valido("Escolha uma opção: ", validar_opcao_menu)
        # Encerra o programa quando o usuário seleciona zero.
        if opcao == "0":
            print("\nEncerrando sistema...")
            break
        executar_opcao(manager, opcao)
        # Aguarda o usuário antes de limpar a tela e exibir o menu novamente.
        perguntar("\nPressione Enter para continuar...")
        limpar_terminal()

# Executa o programa somente quando este arquivo é iniciado diretamente.
if __name__ == "__main__":
    main()