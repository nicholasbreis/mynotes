from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.sessao import iniciar_sessao, login_obrigatorio
from app.validacao import erros_da_senha, erros_do_perfil, normalizar_email

bp = Blueprint("perfil", __name__, url_prefix="/perfil")


def _formulario(nome: str, email: str) -> str:
    return render_template("perfil/editar.html", nome=nome, email=email)


@bp.route("", methods=["GET", "POST"])
@login_obrigatorio
def editar():
    if request.method == "GET":
        return _formulario(g.usuario.nome, g.usuario.email)

    nome = request.form.get("nome", "").strip()
    email = normalizar_email(request.form.get("email", ""))
    erros = erros_do_perfil(nome, email)

    if not erros:
        g.usuario.nome = nome
        g.usuario.email = email
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            erros.append("Este e-mail já está cadastrado.")
        else:
            flash("Perfil atualizado.", "success")
            return redirect(url_for("perfil.editar"))

    for erro in erros:
        flash(erro, "danger")
    return _formulario(nome, email), 422


@bp.post("/senha")
@login_obrigatorio
def trocar_senha():
    nova = request.form.get("nova_senha", "")
    erros = erros_da_senha(nova, request.form.get("confirmacao", ""))
    if not g.usuario.senha_confere(request.form.get("senha_atual", "")):
        erros.insert(0, "A senha atual está incorreta.")

    if erros:
        for erro in erros:
            flash(erro, "danger")
        return _formulario(g.usuario.nome, g.usuario.email), 422

    g.usuario.definir_senha(nova)
    db.session.commit()
    iniciar_sessao(g.usuario)
    flash("Senha alterada.", "success")
    return redirect(url_for("perfil.editar"))
