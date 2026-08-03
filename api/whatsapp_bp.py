from flask import Blueprint, jsonify, request
from backend.services.whatsapp_formatter import formatar_whatsapp
from backend.services.whatsapp_parser import importar_lista
from backend.models.entities import Jogador

whatsapp_bp = Blueprint("whatsapp", __name__, url_prefix="/api")


class JogadorProxy:
    def __init__(self, data):
        self.nome = data.get("nome", "")
        self.nota = data.get("nota", 3)
        self.is_goleiro = data.get("is_goleiro", False)
        self.posicoes = [PosicaoProxy(p) for p in data.get("posicoes", [])]


class PosicaoProxy:
    def __init__(self, data):
        self.nome = data.get("nome", "")


@whatsapp_bp.route("/sorteios/whatsapp", methods=["POST"])
def formatar():
    data = request.get_json(silent=True) or {}
    times_raw = data.get("times", {})
    goleiros_raw = data.get("goleiros", {})
    medias = data.get("medias", {})

    times = {}
    goleiros = {}
    for nome, jogadores in times_raw.items():
        times[nome] = [JogadorProxy(j) for j in jogadores]
    for nome, g in goleiros_raw.items():
        goleiros[nome] = JogadorProxy(g) if g else None

    texto = formatar_whatsapp(times, goleiros, medias)
    return jsonify({"texto": texto})


@whatsapp_bp.route("/importar-whatsapp", methods=["POST"])
def importar():
    from backend.extensions import db
    data = request.get_json(silent=True) or {}
    jogadores, goleiros_novo = importar_lista(data.get("lista", ""))

    adicionados = 0
    for item in jogadores:
        if not Jogador.query.filter_by(nome=item["nome"], ativo=True).first():
            j = Jogador(nome=item["nome"], nota=item["estrelas"])
            db.session.add(j)
            adicionados += 1

    for item in goleiros_novo:
        exists = Jogador.query.filter_by(nome=item["nome"], is_goleiro=True, ativo=True).first()
        if not exists:
            j = Jogador(nome=item["nome"], nota=item["estrelas"], is_goleiro=True)
            db.session.add(j)
            adicionados += 1

    db.session.commit()
    return jsonify({"adicionados": adicionados})
