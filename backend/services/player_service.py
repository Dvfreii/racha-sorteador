from sqlalchemy.orm import joinedload
from backend.models.entities import Jogador, Posicao


def listar_ativos(db, incluir_inativos=False):
    q = Jogador.query
    if not incluir_inativos:
        q = q.filter_by(ativo=True)
    return q.order_by(Jogador.nome).all()


def criar(db, nome, nota, posicoes_ids, restricoes_ids, is_goleiro):
    jogador = Jogador(nome=nome, nota=nota, is_goleiro=is_goleiro)
    db.session.add(jogador)
    db.session.flush()
    if posicoes_ids:
        jogador.posicoes = Posicao.query.filter(Posicao.id.in_(posicoes_ids)).all()
    if restricoes_ids:
        jogador.restricoes = Jogador.query.filter(Jogador.id.in_(restricoes_ids)).all()
    db.session.commit()
    return jogador


def editar(db, jogador_id, nome, nota, posicoes_ids, restricoes_ids, is_goleiro):
    jogador = db.get_or_404(Jogador, jogador_id)
    jogador.nome = nome
    jogador.nota = nota
    jogador.is_goleiro = is_goleiro
    jogador.posicoes = Posicao.query.filter(Posicao.id.in_(posicoes_ids)).all() if posicoes_ids else []
    jogador.restricoes = Jogador.query.filter(Jogador.id.in_(restricoes_ids)).all() if restricoes_ids else []
    db.session.commit()
    return jogador


def desativar(db, jogador_id):
    jogador = db.get_or_404(Jogador, jogador_id)
    jogador.ativo = False
    db.session.commit()
    return jogador


def buscar_selecionados(ids):
    return Jogador.query.filter(Jogador.id.in_(ids), Jogador.ativo.is_(True)).options(
        joinedload(Jogador.posicoes),
        joinedload(Jogador.restricoes),
    ).all()


def validar_formulario(nome, nota):
    if not nome:
        return "Informe o nome do jogador."
    if not 1 <= nota <= 5:
        return "A nota deve estar entre 1 e 5 estrelas."
    return None


def validar_selecao(ids):
    if len(ids) < 2 or len(set(ids)) != len(ids):
        return "Selecione pelo menos 2 jogadores diferentes."
    return None
