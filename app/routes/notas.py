from datetime import datetime

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from sqlalchemy import or_

from app.extensions import db
from app.models import Nota
from app.sessao import login_obrigatorio
from app.validacao import erros_da_nota

bp = Blueprint("notas", __name__)


def _nota_do_usuario(nota_id: int) -> Nota:
    nota = db.session.scalar(db.select(Nota).where(Nota.id == nota_id, Nota.usuario_id == g.usuario.id))
    if nota is None:
        abort(404)
    return nota


def _ler_formulario() -> tuple[str, str, list[str]]:
    titulo = request.form.get("titulo", "").strip()
    conteudo = request.form.get("conteudo", "").replace("\r\n", "\n")
    return titulo, conteudo, erros_da_nota(titulo, conteudo)


@bp.get("/")
@login_obrigatorio
def listar():
    termo = request.args.get("q", "").strip()
    consulta = db.select(Nota).where(Nota.usuario_id == g.usuario.id)
    if termo:
        consulta = consulta.where(
            or_(
                Nota.titulo.icontains(termo, autoescape=True),
                Nota.conteudo.icontains(termo, autoescape=True),
            )
        )
    consulta = consulta.order_by(Nota.fixada.desc(), Nota.atualizada_em.desc())
    return render_template("notas/lista.html", notas=db.session.scalars(consulta).all(), termo=termo)


@bp.route("/notas/nova", methods=["GET", "POST"])
@login_obrigatorio
def criar():
    if request.method == "GET":
        return render_template("notas/formulario.html", nota=None, titulo="", conteudo="")

    titulo, conteudo, erros = _ler_formulario()
    if erros:
        for erro in erros:
            flash(erro, "danger")
        return render_template("notas/formulario.html", nota=None, titulo=titulo, conteudo=conteudo), 422

    nota = Nota(usuario_id=g.usuario.id, titulo=titulo, conteudo=conteudo)
    db.session.add(nota)
    db.session.commit()
    flash("Nota criada.", "success")
    return redirect(url_for("notas.ver", nota_id=nota.id))


@bp.get("/notas/<int:nota_id>")
@login_obrigatorio
def ver(nota_id: int):
    return render_template("notas/ver.html", nota=_nota_do_usuario(nota_id))


@bp.route("/notas/<int:nota_id>/editar", methods=["GET", "POST"])
@login_obrigatorio
def editar(nota_id: int):
    nota = _nota_do_usuario(nota_id)
    if request.method == "GET":
        return render_template("notas/formulario.html", nota=nota, titulo=nota.titulo, conteudo=nota.conteudo)

    titulo, conteudo, erros = _ler_formulario()
    if erros:
        for erro in erros:
            flash(erro, "danger")
        return render_template("notas/formulario.html", nota=nota, titulo=titulo, conteudo=conteudo), 422

    nota.titulo = titulo
    nota.conteudo = conteudo
    nota.atualizada_em = datetime.now()
    db.session.commit()
    flash("Nota atualizada.", "success")
    return redirect(url_for("notas.ver", nota_id=nota.id))


@bp.post("/notas/<int:nota_id>/fixar")
@login_obrigatorio
def fixar(nota_id: int):
    nota = _nota_do_usuario(nota_id)
    nota.fixada = not nota.fixada
    db.session.commit()
    flash("Nota fixada." if nota.fixada else "Nota desafixada.", "success")
    return redirect(url_for("notas.listar"))


@bp.post("/notas/<int:nota_id>/excluir")
@login_obrigatorio
def excluir(nota_id: int):
    db.session.delete(_nota_do_usuario(nota_id))
    db.session.commit()
    flash("Nota excluída.", "success")
    return redirect(url_for("notas.listar"))
