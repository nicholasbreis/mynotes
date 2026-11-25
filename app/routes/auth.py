from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Usuario
from app.sessao import encerrar_sessao, iniciar_sessao
from app.validacao import erros_da_senha, erros_do_perfil, normalizar_email

bp = Blueprint("auth", __name__)


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if g.usuario:
        return redirect(url_for("notas.listar"))
    if request.method == "GET":
        return render_template("auth/cadastro.html")

    nome = request.form.get("nome", "").strip()
    email = normalizar_email(request.form.get("email", ""))
    senha = request.form.get("senha", "")
    erros = erros_do_perfil(nome, email) + erros_da_senha(senha, request.form.get("confirmacao", ""))

    if not erros:
        usuario = Usuario(nome=nome, email=email)
        usuario.definir_senha(senha)
        db.session.add(usuario)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            erros.append("Este e-mail já está cadastrado.")
        else:
            flash("Conta criada. Faça login para continuar.", "success")
            return redirect(url_for("auth.login"))

    for erro in erros:
        flash(erro, "danger")
    return render_template("auth/cadastro.html", nome=nome, email=email), 422


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.usuario:
        return redirect(url_for("notas.listar"))
    if request.method == "GET":
        return render_template("auth/login.html")

    email = normalizar_email(request.form.get("email", ""))
    usuario = db.session.scalar(db.select(Usuario).where(Usuario.email == email))
    if usuario is None or not usuario.senha_confere(request.form.get("senha", "")):
        flash("E-mail ou senha inválidos.", "danger")
        return render_template("auth/login.html", email=email), 401
    if not usuario.ativo:
        flash("Esta conta está bloqueada. Procure o administrador.", "danger")
        return render_template("auth/login.html", email=email), 403

    iniciar_sessao(usuario)
    return redirect(url_for("notas.listar"))


@bp.post("/logout")
def logout():
    encerrar_sessao()
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("auth.login"))
