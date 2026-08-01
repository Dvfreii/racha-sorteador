from sorteio_engine import historico_para_engine, sortear_times
from backend.models.entities import Sorteio, SorteioGoleiro, SorteioJogador


def salvar(db, ids, times, goleiros=None):
    sorteio = Sorteio()
    db.session.add(sorteio)
    db.session.flush()
    for jogador_id, time in zip(ids, times):
        db.session.add(SorteioJogador(
            sorteio_id=sorteio.id,
            jogador_id=int(jogador_id),
            time=time,
        ))
    for goleiro_id in goleiros or []:
        if goleiro_id:
            db.session.add(SorteioGoleiro(sorteio_id=sorteio.id, goleiro_id=int(goleiro_id)))
    db.session.commit()
    return sorteio



def gerar(jogadores, quantidade=3, tamanhos=None):
    historico = Sorteio.query.order_by(Sorteio.data.desc()).limit(3).all()
    return sortear_times(jogadores, historico_para_engine(historico), quantidade=quantidade, tamanhos=tamanhos)

