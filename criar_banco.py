import argparse
from datetime import datetime, timedelta

from flask import Flask

from app import create_app
from app.extensions import db
from app.models import Nota, Usuario

USUARIOS = [
    {"nome": "Administrador", "email": "admin@mynotes.local", "senha": "Admin@2026", "perfil": "admin"},
    {"nome": "Ana Souza", "email": "ana@mynotes.local", "senha": "Ana@2026!"},
    {"nome": "Bruno Lima", "email": "bruno@mynotes.local", "senha": "Bruno@2026"},
    {"nome": "Carla Dias", "email": "carla@mynotes.local", "senha": "Carla@2026", "ativo": False},
]

NOTAS = {
    "admin@mynotes.local": [
        ("Rotina da administração", "Revisar contas bloqueadas toda segunda-feira.", False),
    ],
    "ana@mynotes.local": [
        ("Lista de compras", "Arroz\nFeijão\nCafé\nPão", True),
        ("Prova de Segurança da Informação", "Revisar controle de acesso, sessões e injeção de SQL.", False),
        ("Ideias de viagem", "Florianópolis no verão ou Gramado no inverno.", False),
    ],
    "bruno@mynotes.local": [
        ("Treino da semana", "Segunda: corrida\nQuarta: musculação\nSexta: natação", False),
        ("Reunião do projeto", "Levar o diagrama ER e a lista de rotas.", True),
    ],
    "carla@mynotes.local": [
        ("Livros para ler", "Dom Casmurro\nVidas Secas", False),
    ],
}


def inserir_dados_de_exemplo() -> None:
    agora = datetime.now()
    for dados in USUARIOS:
        campos = {chave: valor for chave, valor in dados.items() if chave != "senha"}
        usuario = Usuario(**campos)
        usuario.definir_senha(dados["senha"])
        for indice, (titulo, conteudo, fixada) in enumerate(NOTAS[dados["email"]]):
            momento = agora - timedelta(days=indice)
            usuario.notas.append(
                Nota(titulo=titulo, conteudo=conteudo, fixada=fixada, criada_em=momento, atualizada_em=momento)
            )
        db.session.add(usuario)
    db.session.commit()


def inicializar(app: Flask, recriar: bool = False) -> None:
    with app.app_context():
        if recriar:
            db.drop_all()
        db.create_all()
        if db.session.scalar(db.select(Usuario.id).limit(1)) is None:
            inserir_dados_de_exemplo()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cria as tabelas do MyNotes e insere os dados de exemplo.")
    parser.add_argument("--recriar", action="store_true", help="apaga todos os dados antes de criar as tabelas")
    argumentos = parser.parse_args()
    inicializar(create_app(), recriar=argumentos.recriar)
    print("Banco de dados pronto.")
