from app import create_app
from criar_banco import inicializar

app = create_app()

if __name__ == "__main__":
    inicializar(app)
    app.run(host="127.0.0.1", port=5000)
