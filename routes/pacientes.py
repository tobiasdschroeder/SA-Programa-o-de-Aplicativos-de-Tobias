"""Rotas HTTP para cadastro, consulta, atualização, exclusão e verificação."""

from flask import Blueprint, current_app, flash, render_template, request

from .auth import login_required


pacientes_bp = Blueprint("pacientes", __name__, url_prefix="/pacientes")


def obter_manager():
    return current_app.config["PACIENTE_MANAGER"]


@pacientes_bp.route("/cadastrar", methods=["GET", "POST"])
@login_required
def cadastrar():
    # Recebe os dados do formulário, chama as regras de negócio e informa o resultado.
    resultado = None
    if request.method == "POST":
        dados = {campo: request.form.get(campo, "").strip()
                 for campo in ("nome", "cpf", "data_nascimento", "telefone", "endereco", "tipo_sanguineo")}
        resultado = obter_manager().cadastrar_paciente(dados)
        flash(resultado["mensagem"], "sucesso" if resultado["sucesso"] else "erro")
    return render_template("pacientes_flask.html", modo="cadastrar", resultado=resultado)


@pacientes_bp.route("/consultar", methods=["GET", "POST"])
@login_required
def consultar():
    # Localiza um paciente por ID ou CPF e mantém o filtro de inativos opcional.
    paciente = None
    if request.method == "POST":
        identificador = request.form.get("identificador", "").strip()
        incluir = request.form.get("incluir_inativos") == "true"
        paciente = obter_manager().consultar_paciente(identificador, incluir)
        if paciente is None:
            flash("Paciente não encontrado.", "erro")
    return render_template("pacientes_flask.html", modo="consultar", paciente=paciente)


@pacientes_bp.route("/inativos")
@login_required
def listar():
    # Separa pacientes ativos e inativos para apresentação nas duas listas.
    manager = obter_manager()
    return render_template("pacientes_flask.html", modo="listar",
                           ativos=manager.listar_pacientes(),
                           inativos=manager.listar_pacientes_inativos())


@pacientes_bp.route("/atualizar", methods=["GET", "POST"])
@login_required
def atualizar():
    # Localiza o registro pelo ID e aplica somente alterações validadas pelo gerenciador.
    paciente = None
    resultado = None
    paciente_id = request.args.get("paciente_id", "")
    if request.method == "POST":
        paciente_id = request.form.get("paciente_id", "").strip()
        try:
            paciente_id_int = int(paciente_id)
        except (TypeError, ValueError):
            paciente_id_int = 0
        alteracoes = {}
        for campo in ("nome", "cpf", "data_nascimento", "telefone", "endereco", "tipo_sanguineo", "status"):
            valor = request.form.get(campo)
            if valor is not None and str(valor).strip():
                alteracoes[campo] = str(valor).strip()
        resultado = obter_manager().atualizar_paciente(paciente_id_int, alteracoes)
        flash(resultado["mensagem"], "sucesso" if resultado["sucesso"] else "erro")
        paciente = resultado.get("paciente")
    elif paciente_id:
        try:
            paciente_obj = obter_manager().buscar_por_id(int(paciente_id), True)
            paciente = paciente_obj.to_dict() if paciente_obj else None
        except (TypeError, ValueError):
            paciente = None
    return render_template("pacientes_flask.html", modo="atualizar", paciente=paciente, resultado=resultado)


@pacientes_bp.route("/excluir", methods=["GET", "POST"])
@login_required
def excluir():
    # Solicita a exclusão definitiva; o gerente rejeita pacientes que ainda estão ativos.
    paciente = None
    resultado = None
    if request.method == "POST":
        try:
            paciente_id = int(request.form.get("paciente_id", "").strip())
        except (TypeError, ValueError):
            paciente_id = 0
        paciente_obj = obter_manager().buscar_por_id(paciente_id, True)
        paciente = paciente_obj.to_dict() if paciente_obj else None
        resultado = obter_manager().excluir_paciente_inativo(paciente_id)
        flash(resultado["mensagem"], "sucesso" if resultado["sucesso"] else "erro")
    return render_template("pacientes_flask.html", modo="excluir", paciente=paciente, resultado=resultado)


@pacientes_bp.route("/verificar", methods=["GET", "POST"])
@login_required
def verificar():
    # Normaliza e verifica o CPF entre os cadastros ativos e inativos.
    cadastrado = None
    cpf = ""
    if request.method == "POST":
        cpf = request.form.get("cpf", "").strip()
        try:
            cadastrado = obter_manager().verificar_paciente_cadastrado(cpf, True)
        except ValueError as erro:
            flash(str(erro), "erro")
        else:
            flash("CPF já cadastrado no sistema." if cadastrado else "CPF disponível para cadastro.",
                  "sucesso" if cadastrado else "aviso")
    return render_template("pacientes_flask.html", modo="verificar", cadastrado=cadastrado, cpf=cpf)
