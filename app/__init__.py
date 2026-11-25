from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

from config import Config

from .extensions import csrf, db
from .routes import registrar_rotas
from .sessao import carregar_usuario


def create_app(config: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    app.before_request(carregar_usuario)
    csrf.init_app(app)

    registrar_rotas(app)
    app.register_error_handler(HTTPException, pagina_de_erro)
    return app


def pagina_de_erro(erro: HTTPException) -> tuple[str, int] | HTTPException:
    if erro.code is None or erro.code < 400:
        return erro
    mensagens = {
        400: "A requisição é inválida ou o formulário expirou. Volte e tente novamente.",
        403: "Você não tem permissão para acessar esta página.",
        404: "A página ou nota não foi encontrada.",
    }
    mensagem = mensagens.get(erro.code, "Não foi possível concluir a operação.")
    return render_template("erro.html", codigo=erro.code, mensagem=mensagem), erro.code
