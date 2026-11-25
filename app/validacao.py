import re

EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
NOME_MAX = 100
EMAIL_MAX = 100
SENHA_MIN = 8
SENHA_MAX = 128
TITULO_MAX = 150
CONTEUDO_MAX = 20_000


def normalizar_email(email: str) -> str:
    return email.strip().lower()


def erros_do_perfil(nome: str, email: str) -> list[str]:
    erros = []
    if not nome or len(nome) > NOME_MAX:
        erros.append(f"Informe um nome com até {NOME_MAX} caracteres.")
    if len(email) > EMAIL_MAX or not EMAIL_RE.fullmatch(email):
        erros.append(f"Informe um e-mail válido com até {EMAIL_MAX} caracteres.")
    return erros


def erros_da_senha(senha: str, confirmacao: str) -> list[str]:
    erros = []
    if not SENHA_MIN <= len(senha) <= SENHA_MAX:
        erros.append(f"A senha deve ter entre {SENHA_MIN} e {SENHA_MAX} caracteres.")
    if senha != confirmacao:
        erros.append("A confirmação não confere com a senha.")
    return erros


def erros_da_nota(titulo: str, conteudo: str) -> list[str]:
    erros = []
    if not titulo or len(titulo) > TITULO_MAX:
        erros.append(f"Informe um título com até {TITULO_MAX} caracteres.")
    if not conteudo.strip() or len(conteudo) > CONTEUDO_MAX:
        erros.append(f"Informe um conteúdo com até {CONTEUDO_MAX} caracteres.")
    return erros
