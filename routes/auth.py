"""Rotas de autenticação, proteção de sessão e cadastro administrativo."""

import hmac
import secrets
from functools import wraps
from urllib.parse import urlsplit

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for


auth_bp = Blueprint("auth", __name__)


def login_required(view):
    # Impede o acesso direto do navegador a páginas que exigem sessão autenticada.
    @wraps(view)
    def protegido(*args, **kwargs):
        if not session.get("usuario_id"):
            flash("Faça login para acessar o sistema.", "aviso")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return protegido


def gerar_csrf():
    # Usa um token persistente durante a sessão para validar formulários enviados.
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def validar_csrf():
    recebido = request.form.get("csrf_token", "")
    esperado = session.get("csrf_token", "")
    if not recebido or not esperado or not hmac.compare_digest(recebido, esperado):
        abort(400, description="Token CSRF inválido.")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Primeiro acesso: o sistema direciona à criação do usuário inicial.
    if session.get("usuario_id"):
        return redirect(url_for("dashboard.dashboard"))
    repositorio = current_app.config["USUARIO_REPOSITORY"]
    sem_usuarios = repositorio.contar_usuarios() == 0
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        if not usuario or not senha:
            flash("Informe usuário e senha.", "erro")
            return render_template("login_flask.html", sem_usuarios=sem_usuarios), 400
        autenticado = repositorio.verificar_senha(usuario, senha)
        if not autenticado:
            flash("Usuário ou senha inválidos.", "erro")
            return render_template("login_flask.html"), 401
        session.clear()
        session.permanent = True
        session["usuario_id"] = autenticado["id"]
        session["usuario"] = autenticado["usuario"]
        session["nome"] = autenticado["nome"]
        gerar_csrf()
        destino = request.args.get("next") or ""
        partes = urlsplit(destino)
        if partes.scheme or partes.netloc or not partes.path.startswith("/"):
            destino = url_for("dashboard.dashboard")
        return redirect(destino)
    return render_template("login_flask.html", sem_usuarios=sem_usuarios)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Você saiu do sistema.", "aviso")
    return redirect(url_for("auth.login"))


@auth_bp.route("/usuarios/cadastrar", methods=["GET", "POST"])
def cadastrar_usuario():
    # Permite o primeiro cadastro público; novas contas não ficam abertas sem sessão.
    repositorio = current_app.config["USUARIO_REPOSITORY"]
    if repositorio.contar_usuarios() > 0 and not session.get("usuario_id"):
        flash("Faça login para criar uma conta com acesso ao sistema.", "aviso")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar_senha", "")
        if not nome or not usuario or not senha or not confirmar:
            flash("Preencha todos os campos obrigatórios.", "erro")
        elif senha != confirmar:
            flash("As senhas não coincidem.", "erro")
        else:
            try:
                repositorio.criar_usuario(nome, usuario, senha)
                flash("Usuário cadastrado com sucesso. Faça login para continuar.", "sucesso")
                return redirect(url_for("auth.login") if not session.get("usuario_id") else url_for("dashboard.dashboard"))
            except ValueError as erro:
                flash(str(erro), "erro")
    return render_template("cadastro_usuario_flask.html")


@auth_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    repositorio = current_app.config["USUARIO_REPOSITORY"]
    usuario_id = session["usuario_id"]
    perfil_usuario = repositorio.buscar_por_id(usuario_id)
    if not perfil_usuario:
        session.clear()
        flash("A conta não existe mais.", "aviso")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar_senha", "")
        if senha and senha != confirmar:
            flash("As senhas não coincidem.", "erro")
        else:
            try:
                repositorio.atualizar_usuario(usuario_id, nome, usuario, senha or None)
                session["nome"] = nome
                session["usuario"] = usuario
                flash("Perfil atualizado com sucesso.", "sucesso")
                return redirect(url_for("auth.perfil"))
            except ValueError as erro:
                flash(str(erro), "erro")
        perfil_usuario = {"id": usuario_id, "nome": nome, "usuario": usuario, "ativo": 1}
    return render_template("perfil_flask.html", perfil=perfil_usuario)


@auth_bp.route("/perfil/excluir", methods=["POST"])
@login_required
def excluir_perfil():
    repositorio = current_app.config["USUARIO_REPOSITORY"]
    repositorio.excluir_usuario(session["usuario_id"])
    session.clear()
    flash("Sua conta foi excluída.", "sucesso")
    return redirect(url_for("auth.login"))
