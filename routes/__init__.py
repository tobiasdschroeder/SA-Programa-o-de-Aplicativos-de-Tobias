"""Registro dos blueprints da aplicação.

Centraliza o registro dos grupos de rotas da aplicação."""

from .auth import auth_bp
from .dashboard import dashboard_bp
from .pacientes import pacientes_bp


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(pacientes_bp)
