"""Rotas do painel principal e compatibilidade de caminhos antigos."""

from flask import Blueprint, current_app, redirect, render_template, session, url_for

from .auth import login_required


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def raiz():
    # Escolhe cadastro inicial, login ou dashboard conforme usuário e sessão.
    if session.get("usuario_id"):
        return redirect(url_for("dashboard.dashboard"))
    repositorio = current_app.config["USUARIO_REPOSITORY"]
    if repositorio.contar_usuarios() == 0:
        return redirect(url_for("auth.cadastrar_usuario"))
    return redirect(url_for("auth.login"))


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard_flask.html")


@dashboard_bp.route("/pacientes")
@login_required
def pacientes():
    return redirect(url_for("pacientes.listar"))


@dashboard_bp.route("/index.html")
@login_required
def index_legado():
    return redirect(url_for("dashboard.dashboard"))
