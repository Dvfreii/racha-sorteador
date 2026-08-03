from datetime import datetime

from backend.extensions import db

jogador_posicoes = db.Table(
    "jogador_posicoes",
    db.Column("jogador_id", db.Integer, db.ForeignKey("jogador.id"), primary_key=True),
    db.Column("posicao_id", db.Integer, db.ForeignKey("posicao.id"), primary_key=True),
)

jogador_restricoes = db.Table(
    "jogador_restricoes",
    db.Column("jogador_id", db.Integer, db.ForeignKey("jogador.id"), primary_key=True),
    db.Column("restrito_id", db.Integer, db.ForeignKey("jogador.id"), primary_key=True),
)


class Jogador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nota = db.Column(db.Float, nullable=False, default=3.0)
    is_goleiro = db.Column(db.Boolean, default=False, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    posicoes = db.relationship("Posicao", secondary=jogador_posicoes, lazy="joined")
    restricoes = db.relationship(
        "Jogador",
        secondary=jogador_restricoes,
        primaryjoin=(id == jogador_restricoes.c.jogador_id),
        secondaryjoin=(id == jogador_restricoes.c.restrito_id),
        lazy="joined",
    )


class Posicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), unique=True, nullable=False)


class Sorteio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    itens = db.relationship("SorteioJogador", backref="sorteio", cascade="all, delete-orphan")


class SorteioJogador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sorteio_id = db.Column(db.Integer, db.ForeignKey("sorteio.id"), nullable=False)
    jogador_id = db.Column(db.Integer, db.ForeignKey("jogador.id"), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    is_goleiro_no_time = db.Column(db.Boolean, default=False, nullable=False)
    jogador = db.relationship("Jogador")
