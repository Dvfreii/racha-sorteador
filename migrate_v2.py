"""Migrate DB from v1 to v2 (Jogador unified + Posicao N:N)."""
import os
from flask import Flask
from backend.extensions import db

POSICOES = [
    "Goleiro",
    "Zagueiro / Fixo",
    "Lateral",
    "Meio-Campo",
    "Alas",
    "Atacante / Pivo",
]


def _normalizar_uri(uri):
    if uri and uri.startswith("postgres://"):
        return uri.replace("postgres://", "postgresql://", 1)
    return uri


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = _normalizar_uri(
    os.getenv("DATABASE_URL") or os.getenv("RACHA_DATABASE_URI") or "sqlite:///../instance/racha.db"
)
db.init_app(app)

import backend.models.entities  # noqa: E402
from backend.models.entities import Jogador, Posicao, SorteioJogador  # noqa: E402


def migrate():
    with app.app_context():
        db.create_all()

        for nome in POSICOES:
            if not Posicao.query.filter_by(nome=nome).first():
                db.session.add(Posicao(nome=nome))
        db.session.commit()

        from sqlalchemy import text  # noqa: E402

        print("Migration complete.")
        print(f"  Jogadores: {Jogador.query.filter_by(ativo=True).count()}")
        print(f"  Posicoes: {Posicao.query.count()}")
        try:
            print(f"  Sorteios: {db.session.execute(text('SELECT COUNT(*) FROM sorteio')).scalar()}")
        except Exception:
            print("  Sorteios: 0")


if __name__ == "__main__":
    migrate()
