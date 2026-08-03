from flask import Blueprint, jsonify, request
from backend.extensions import db
from backend.services.draw_service import gerar_v2, salvar, listar_historico
from backend.services.player_service import buscar_selecionados
from backend.models.entities import Sorteio, SorteioJogador
from sqlalchemy.orm import joinedload

sorteios_bp = Blueprint("sorteios", __name__, url_prefix="/api/sorteios")


@sorteios_bp.route("/sortear", methods=["POST"])
def sortear():
    data = request.get_json(silent=True) or {}
    ids = data.get("jogadores", [])

    if len(ids) < 2:
        return jsonify({"erro": "Selecione pelo menos 2 jogadores."}), 400

    jogadores = buscar_selecionados(ids)
    if len(jogadores) < len(ids):
        return jsonify({"erro": "Ha jogadores invalidos na selecao."}), 400

    quantidade = int(data.get("quantidade_times", 3))
    tamanhos = data.get("tamanhos")

    times, goleiros, medias = gerar_v2(jogadores, quantidade=quantidade, tamanhos=tamanhos)

    result = {
        "times": {},
        "goleiros": {},
        "medias": medias,
    }
    for nome, time in times.items():
        result["times"][nome] = [_serializar_jogador(j) for j in time]
        g = goleiros.get(nome)
        result["goleiros"][nome] = {"id": g.id, "nome": g.nome} if g else None

    return jsonify(result)


@sorteios_bp.route("", methods=["POST"])
def salvar_sorteio():
    data = request.get_json(silent=True) or {}
    times = data.get("times")
    goleiros = data.get("goleiros")

    if not times:
        return jsonify({"erro": "Dados invalidos."}), 400

    goleiros_ids = {k: v for k, v in (goleiros or {}).items() if v}

    sorteio = salvar(db, times, goleiros_ids)
    return jsonify({"id": sorteio.id, "data": sorteio.data.isoformat()}), 201


@sorteios_bp.route("", methods=["GET"])
def historico():
    limite = request.args.get("limite", 10, type=int)
    offset = request.args.get("offset", 0, type=int)
    sorteios = listar_historico(limite=limite, offset=offset)

    result = []
    for s in sorteios:
        times = {}
        goleiros_ids = {}
        for item in s.itens:
            times.setdefault(item.time, []).append({
                "id": item.jogador.id,
                "nome": item.jogador.nome,
                "nota": item.jogador.nota,
            })
            if item.is_goleiro_no_time:
                goleiros_ids[item.time] = item.jogador.nome

        medias = {}
        for nome, t in times.items():
            medias[nome] = round(sum(j["nota"] for j in t) / len(t), 2)

        result.append({
            "id": s.id,
            "data": s.data.isoformat(),
            "times": times,
            "goleiros": goleiros_ids,
            "medias": medias,
        })

    return jsonify(result)


@sorteios_bp.route("/<int:sorteio_id>", methods=["GET"])
def detalhe_sorteio(sorteio_id):
    s = db.get_or_404(Sorteio, sorteio_id)
    _ = [item.jogador.nome for item in s.itens]

    times = {}
    goleiros = {}
    for item in s.itens:
        times.setdefault(item.time, []).append({
            "id": item.jogador.id,
            "nome": item.jogador.nome,
            "nota": item.jogador.nota,
        })
        if item.is_goleiro_no_time:
            goleiros[item.time] = item.jogador.nome

    medias = {}
    for nome, t in times.items():
        medias[nome] = round(sum(j["nota"] for j in t) / len(t), 2)

    return jsonify({
        "id": s.id,
        "data": s.data.isoformat(),
        "times": times,
        "goleiros": goleiros,
        "medias": medias,
    })


@sorteios_bp.route("/<int:sorteio_id>", methods=["DELETE"])
def excluir_sorteio(sorteio_id):
    sorteio = db.get_or_404(Sorteio, sorteio_id)
    db.session.delete(sorteio)
    db.session.commit()
    return jsonify({"ok": True})


def _serializar_jogador(j):
    return {
        "id": j.id,
        "nome": j.nome,
        "nota": j.nota,
        "is_goleiro": j.is_goleiro,
        "posicoes": [{"id": p.id, "nome": p.nome} for p in (j.posicoes or [])],
    }
