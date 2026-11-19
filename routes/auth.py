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
    if repositorio.contar_usuarios() == 0:
        return redirect(url_for("auth.cadastrar_usuario"))
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        if not usuario or not senha:
            flash("Informe usuário e senha.", "erro")
            return render_template("login_flask.html"), 400
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
    return render_template("login_flask.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Você saiu do sistema.", "aviso")
    return redirect(url_for("auth.login"))


@auth_bp.route("/usuarios/cadastrar", methods=["GET", "POST"])
def cadastrar_usuario():
    # Permite cadastro público apenas enquanto não existir nenhuma conta.
    repositorio = current_app.config["USUARIO_REPOSITORY"]
    if repositorio.contar_usuarios() > 0 and not session.get("usuario_id"):
        flash("Faça login para cadastrar novos usuários.", "aviso")
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
