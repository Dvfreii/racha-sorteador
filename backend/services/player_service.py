from backend.models.entities import Goleiro, Jogador


def listar_ativos(db):
    return Jogador.query.filter_by(ativo=True).order_by(Jogador.nome).all()


def listar_goleiros():
    return Goleiro.query.filter_by(ativo=True).order_by(Goleiro.nome).all()


def criar(db, nome, estrelas, posicao):
    jogador = Jogador(nome=nome, estrelas=estrelas, posicao=posicao)
    db.session.add(jogador)
    db.session.commit()
    return jogador


def editar(db, jogador_id, nome, estrelas, posicao):
    jogador = db.get_or_404(Jogador, jogador_id)
    jogador.nome, jogador.estrelas, jogador.posicao = nome, estrelas, posicao
    db.session.commit()
    return jogador


def editar_goleiro(db, goleiro_id, nome):
    goleiro = db.get_or_404(Goleiro, goleiro_id)
    goleiro.nome = nome
    db.session.commit()
    return goleiro


def criar_goleiro(db, nome):
    goleiro = Goleiro(nome=nome)
    db.session.add(goleiro)
    db.session.commit()
    return goleiro


def desativar(db, jogador_id):
    jogador = db.get_or_404(Jogador, jogador_id)
    jogador.ativo = False
    db.session.commit()
    return jogador


def desativar_goleiro(db, goleiro_id):
    goleiro = db.get_or_404(Goleiro, goleiro_id)
    goleiro.ativo = False
    db.session.commit()
    return goleiro


def buscar_selecionados(ids):
    return Jogador.query.filter(Jogador.id.in_(ids), Jogador.ativo.is_(True)).all()


def validar_formulario(nome, estrelas):
    if not nome:
        return "Informe o nome do jogador."
    if not 0.5 <= estrelas <= 5:
        return "A nota deve estar entre 0,5 e 5 estrelas."
    return None


def validar_selecao(ids):
    if len(ids) < 2 or len(set(ids)) != len(ids):
        return "Selecione pelo menos 2 jogadores diferentes."
    return None
