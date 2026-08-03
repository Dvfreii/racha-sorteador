from flask import Blueprint, jsonify, request

jogadores_bp = Blueprint("jogadores", __name__, url_prefix="/api/jogadores")


def _get_db():
    from backend.extensions import db
    return db


@jogadores_bp.route("", methods=["GET"])
def listar():
    db = _get_db()
    from backend.services.player_service import listar_ativos
    incluir = request.args.get("incluir_inativos", "false").lower() == "true"
    jogadores = listar_ativos(db, incluir_inativos=incluir)
    return jsonify([_serializar(j) for j in jogadores])


@jogadores_bp.route("", methods=["POST"])
def criar_jogador():
    data = request.get_json(silent=True) or {}
    db = _get_db()
    from backend.services.player_service import validar_formulario, criar

    erro = validar_formulario(data.get("nome", "").strip(), float(data.get("nota", 0)))
    if erro:
        return jsonify({"erro": erro}), 400

    jogador = criar(
        db,
        data.get("nome", "").strip(),
        float(data.get("nota", 3)),
        data.get("posicoes", []),
        data.get("restricoes", []),
        data.get("is_goleiro", False),
        data.get("posicao_primaria_id"),
    )
    return jsonify(_serializar(jogador)), 201


@jogadores_bp.route("/<int:jogador_id>", methods=["GET"])
def detalhe(jogador_id):
    from backend.models.entities import Jogador
    from sqlalchemy.orm import joinedload
    jogador = Jogador.query.options(
        joinedload(Jogador.posicoes), joinedload(Jogador.restricoes)
    ).get_or_404(jogador_id)
    return jsonify(_serializar(jogador))


@jogadores_bp.route("/<int:jogador_id>", methods=["PUT"])
def editar_jogador(jogador_id):
    data = request.get_json(silent=True) or {}
    db = _get_db()
    from backend.services.player_service import validar_formulario, editar

    erro = validar_formulario(data.get("nome", "").strip(), float(data.get("nota", 0)))
    if erro:
        return jsonify({"erro": erro}), 400

    jogador = editar(
        db, jogador_id,
        data.get("nome", "").strip(),
        float(data.get("nota", 3)),
        data.get("posicoes", []),
        data.get("restricoes", []),
        data.get("is_goleiro", False),
        data.get("posicao_primaria_id"),
    )
    return jsonify(_serializar(jogador))


@jogadores_bp.route("/<int:jogador_id>", methods=["DELETE"])
def excluir_jogador(jogador_id):
    db = _get_db()
    from backend.services.player_service import desativar
    desativar(db, jogador_id)
    return jsonify({"ok": True})


def _serializar(jogador):
    return {
        "id": jogador.id,
        "nome": jogador.nome,
        "nota": jogador.nota,
        "is_goleiro": jogador.is_goleiro,
        "ativo": jogador.ativo,
        "posicao_primaria_id": jogador.posicao_primaria_id,
        "posicoes": [{"id": p.id, "nome": p.nome} for p in (jogador.posicoes or [])],
        "restricoes": [{"id": r.id, "nome": r.nome} for r in (jogador.restricoes or [])],
    }
