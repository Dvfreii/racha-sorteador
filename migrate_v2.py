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
from backend.models.entities import Jogador, Posicao  # noqa: E402


def migrate():
    with app.app_context():
        db.create_all()

        for nome in POSICOES:
            if not Posicao.query.filter_by(nome=nome).first():
                db.session.add(Posicao(nome=nome))
        db.session.commit()

        from sqlalchemy import text  # noqa: E402

        # Migrate old posicao string -> N:N (raw SQL — ORM no longer maps old column)
        posicao_map = {p.nome.lower().replace(" / ", "/").replace("-", ""): p for p in Posicao.query.all()}
        try:
            rows = db.session.execute(text("SELECT id, posicao FROM jogador WHERE posicao IS NOT NULL AND posicao != ''")).fetchall()
            for row in rows:
                jid, old = row[0], row[1].strip().lower().replace(" / ", "/").replace("-", "")
                pos = posicao_map.get(old)
                if pos:
                    db.session.execute(text("INSERT OR IGNORE INTO jogador_posicoes (jogador_id, posicao_id) VALUES (:jid, :pid)"), {"jid": jid, "pid": pos.id})
            db.session.commit()
        except Exception:
            db.session.rollback()

        # Migrate SorteioGoleiro -> SorteioJogador.is_goleiro_no_time
        try:
            db.session.execute(text(
                "INSERT INTO sorteio_jogador (sorteio_id, jogador_id, time, is_goleiro_no_time) "
                "SELECT sg.sorteio_id, sg.goleiro_id, 'Goleiro', 1 FROM sorteio_goleiro sg "
                "WHERE NOT EXISTS (SELECT 1 FROM sorteio_jogador sj WHERE sj.sorteio_id = sg.sorteio_id AND sj.jogador_id = sg.goleiro_id)"
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()

        print("Migration complete.")
        print(f"  Jogadores: {Jogador.query.filter_by(ativo=True).count()}")
        print(f"  Posicoes: {Posicao.query.count()}")
        try:
            print(f"  Sorteios: {db.session.execute(text('SELECT COUNT(*) FROM sorteio')).scalar()}")
        except Exception:
            print("  Sorteios: 0")


if __name__ == "__main__":
    migrate()
