"""Ponto de entrada da aplicação Flask do sistema hospitalar."""

import os

from flask import Flask, render_template, request

from config import Config
from models.usuario import UsuarioRepository
from models.paciente import PacienteManager, SQLitePacienteRepository
from routes import register_routes
from routes.auth import gerar_csrf, validar_csrf


# Factory central: define caminhos, configurações, repositórios e handlers da aplicação.
def create_app(test_config=None):
    # Define a pasta de templates e a pasta pública de arquivos estáticos.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "interface", "templates"),
        static_folder=os.path.join(base_dir, "interface", "static"),
        static_url_path="/static",
    )
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = app.config.get("SECRET_KEY") or os.environ.get("FLASK_SECRET_KEY")
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = "chave-local-apenas-para-testes" if app.config.get("TESTING") else "chave-local-apenas-para-desenvolvimento"

    repositorio = test_config.get("USUARIO_REPOSITORY") if test_config else None
    app.config["USUARIO_REPOSITORY"] = repositorio or UsuarioRepository(app.config["DATABASE"])

    manager = test_config.get("PACIENTE_MANAGER") if test_config else None
    app.config["PACIENTE_MANAGER"] = manager or PacienteManager(
        repositorio=SQLitePacienteRepository(app.config["DATABASE"])
    )

    register_routes(app)
    app.jinja_env.globals["csrf_token"] = gerar_csrf

    @app.before_request
    def verificar_csrf():
        # POST, PUT, PATCH e DELETE precisam possuir um token válido da sessão.
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            validar_csrf()

    @app.errorhandler(403)
    def erro_403(_erro):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def erro_404(_erro):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def erro_500(_erro):
        return render_template("errors/500.html"), 500

    return app


app = create_app() if os.environ.get("FLASK_SECRET_KEY") or os.environ.get("FLASK_ENV") == "development" else None


if __name__ == "__main__":
    # O modo debug deve ficar restrito ao ambiente de desenvolvimento local.
    os.environ.setdefault("FLASK_SECRET_KEY", "chave-local-apenas-para-desenvolvimento")
    application = create_app()
    application.run(debug=os.environ.get("FLASK_ENV") == "development", use_reloader=False)
