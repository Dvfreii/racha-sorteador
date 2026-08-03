from sorteio_engine import historico_para_engine, sortear_times
from backend.models.entities import Sorteio, SorteioJogador
from sqlalchemy.orm import joinedload


def salvar(db, times, goleiros):
    sorteio = Sorteio()
    db.session.add(sorteio)
    db.session.flush()

    for nome_time, ids in times.items():
        goleiro_id = goleiros.get(nome_time)
        for jogador_id in ids:
            db.session.add(SorteioJogador(
                sorteio_id=sorteio.id,
                jogador_id=jogador_id,
                time=nome_time,
                is_goleiro_no_time=(jogador_id == goleiro_id),
            ))
    db.session.commit()
    return sorteio


def gerar(jogadores, quantidade=3, tamanhos=None):
    """Legacy: returns {nome: [jogadores]} dict for old frontend compat."""
    historico = Sorteio.query.options(
        joinedload(Sorteio.itens).joinedload(SorteioJogador.jogador)
    ).order_by(Sorteio.data.desc()).limit(3).all()
    times, _, _ = sortear_times(jogadores, historico=historico_para_engine(historico), quantidade=quantidade, tamanhos=tamanhos)
    return times


def gerar_v2(jogadores, quantidade=3, tamanhos=None):
    """Returns (times, goleiros, medias) tuple."""
    historico = Sorteio.query.options(
        joinedload(Sorteio.itens).joinedload(SorteioJogador.jogador)
    ).order_by(Sorteio.data.desc()).limit(3).all()
    return sortear_times(jogadores, historico=historico_para_engine(historico), quantidade=quantidade, tamanhos=tamanhos)


def listar_historico(limite=10, offset=0):
    sorteios = Sorteio.query.options(
        joinedload(Sorteio.itens).joinedload(SorteioJogador.jogador)
    ).order_by(Sorteio.data.desc()).offset(offset).limit(limite).all()
    return sorteios
