import hashlib
import hmac
from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import abort, current_app, flash, g, redirect, session, url_for

from .extensions import db
from .models import Usuario


def _marca_da_senha(usuario: Usuario) -> str:
    chave = current_app.config["SECRET_KEY"].encode()
    return hmac.new(chave, usuario.senha.encode(), hashlib.sha256).hexdigest()


def iniciar_sessao(usuario: Usuario) -> None:
    session.clear()
    session["usuario_id"] = usuario.id
    # Trocar a senha muda a marca e derruba as sessões abertas em outros navegadores.
    session["marca"] = _marca_da_senha(usuario)


def encerrar_sessao() -> None:
    session.clear()


def carregar_usuario() -> None:
    g.usuario = None
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return
    usuario = db.session.get(Usuario, usuario_id)
    if (
        usuario is None
        or not usuario.ativo
        or not hmac.compare_digest(session.get("marca", ""), _marca_da_senha(usuario))
    ):
        encerrar_sessao()
        return
    g.usuario = usuario


def login_obrigatorio(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def protegida(*args: Any, **kwargs: Any) -> Any:
        if g.usuario is None:
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return protegida


def admin_obrigatorio(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    @login_obrigatorio
    def protegida(*args: Any, **kwargs: Any) -> Any:
        if not g.usuario.eh_admin:
            abort(403)
        return view(*args, **kwargs)

    return protegida
