from datetime import datetime

from backend.extensions import db


class Jogador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    estrelas = db.Column(db.Float, nullable=False, default=3.0)
    posicao = db.Column(db.String(60), nullable=False, default="")
    ativo = db.Column(db.Boolean, default=True, nullable=False)


class Goleiro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    fixo = db.Column(db.Boolean, default=False, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)


class Sorteio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    itens = db.relationship("SorteioJogador", backref="sorteio", cascade="all, delete-orphan")
    goleiros = db.relationship("SorteioGoleiro", backref="sorteio", cascade="all, delete-orphan")


class SorteioGoleiro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sorteio_id = db.Column(db.Integer, db.ForeignKey("sorteio.id"), nullable=False)
    goleiro_id = db.Column(db.Integer, db.ForeignKey("goleiro.id"), nullable=False)
    goleiro = db.relationship("Goleiro")


class SorteioJogador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sorteio_id = db.Column(db.Integer, db.ForeignKey("sorteio.id"), nullable=False)
    jogador_id = db.Column(db.Integer, db.ForeignKey("jogador.id"), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    jogador = db.relationship("Jogador")
    
