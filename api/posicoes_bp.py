from flask import Blueprint, jsonify
from backend.models.entities import Posicao

posicoes_bp = Blueprint("posicoes", __name__, url_prefix="/api/posicoes")


@posicoes_bp.route("", methods=["GET"])
def listar():
    posicoes = Posicao.query.order_by(Posicao.id).all()
    return jsonify([{"id": p.id, "nome": p.nome} for p in posicoes])
