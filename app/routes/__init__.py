from flask import Flask

from . import admin, auth, notas, perfil


def registrar_rotas(app: Flask) -> None:
    for modulo in (auth, notas, perfil, admin):
        app.register_blueprint(modulo.bp)
