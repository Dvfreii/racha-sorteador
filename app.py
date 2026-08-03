from datetime import datetime
import os
from flask import Flask, flash, redirect, render_template, request, url_for
from backend.extensions import db


def _normalizar_uri(uri):
    if uri and uri.startswith("postgres://"):
        return uri.replace("postgres://", "postgresql://", 1)
    return uri


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "racha-local")
app.config["SQLALCHEMY_DATABASE_URI"] = _normalizar_uri(
    os.getenv("DATABASE_URL") or os.getenv("RACHA_DATABASE_URI") or "sqlite:///racha.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

from api.jogadores_bp import jogadores_bp
from api.posicoes_bp import posicoes_bp
app.register_blueprint(jogadores_bp)
app.register_blueprint(posicoes_bp)
from api.sorteios_bp import sorteios_bp
from api.whatsapp_bp import whatsapp_bp
app.register_blueprint(sorteios_bp)
app.register_blueprint(whatsapp_bp)

from backend.models.entities import Jogador, Sorteio
from backend.services.player_service import (
    buscar_selecionados, criar, desativar, editar,
    listar_ativos, validar_formulario, validar_selecao,
)
from backend.services.draw_service import gerar, salvar
from backend.services.whatsapp_parser import importar_lista

with app.app_context():
    db.create_all()
    from backend.models.entities import Posicao
    for nome in ["Goleiro", "Zagueiro / Fixo", "Lateral", "Meio-Campo", "Alas", "Atacante / Pivo"]:
        if not Posicao.query.filter_by(nome=nome).first():
            db.session.add(Posicao(nome=nome))
    db.session.commit()


def _listar_goleiros():
    """Helper: list active goleiros using is_goleiro flag."""
    return Jogador.query.filter_by(is_goleiro=True, ativo=True).order_by(Jogador.nome).all()


@app.route("/")
def index():
    return render_template("index.html")


# -- Legacy form routes (backward compat) --


@app.post("/sorteios/<int:sorteio_id>/excluir")
def excluir_sorteio(sorteio_id):
    sorteio = db.get_or_404(Sorteio, sorteio_id)
    db.session.delete(sorteio)
    db.session.commit()
    flash("Sorteio excluido.", "ok")
    return redirect(url_for("index"))


@app.post("/sorteios/excluir-todos")
def excluir_todos_sorteios():
    Sorteio.query.delete()
    db.session.commit()
    flash("Historico de sorteios excluido.", "ok")
    return redirect(url_for("index"))


@app.post("/jogadores")
def criar_jogador():
    nome = request.form.get("nome", "").strip()
    try:
        nota = float(request.form.get("estrelas", 3).replace(",", "."))
    except ValueError:
        nota = 0
    erro = validar_formulario(nome, nota)
    if erro:
        flash(erro, "erro")
    else:
        criar(db, nome, nota, [], [], False)
        flash("Jogador cadastrado.", "ok")
    return redirect(url_for("index"))


@app.post("/jogadores/<int:jogador_id>/excluir")
def excluir_jogador(jogador_id):
    desativar(db, jogador_id)
    flash("Jogador removido.", "ok")
    return redirect(url_for("index"))


@app.post("/jogadores/excluir-todos")
def excluir_todos_jogadores():
    Jogador.query.filter_by(ativo=True).update({"ativo": False})
    db.session.commit()
    flash("Todos os jogadores foram excluidos.", "ok")
    return redirect(url_for("index"))


@app.post("/jogadores/<int:jogador_id>/editar")
def editar_jogador(jogador_id):
    nome = request.form.get("nome", "").strip()
    try:
        nota = float(request.form.get("estrelas", 3).replace(",", "."))
    except ValueError:
        nota = 0
    erro = validar_formulario(nome, nota)
    if erro:
        flash(erro, "erro")
    else:
        editar(db, jogador_id, nome, nota, [], [], False)
        flash("Jogador atualizado.", "ok")
    return redirect(url_for("index"))


@app.post("/goleiros")
def adicionar_goleiro():
    nome = request.form.get("nome", "").strip()
    if not nome:
        flash("Informe o nome do goleiro.", "erro")
    else:
        criar(db, nome, 3.0, [], [], True)
        flash("Goleiro adicionado.", "ok")
    return redirect(url_for("index"))


@app.post("/goleiros/<int:goleiro_id>/editar")
def editar_goleiro_route(goleiro_id):
    nome = request.form.get("nome", "").strip()
    if nome:
        editar(db, goleiro_id, nome, 3.0, [], [], True)
        flash("Goleiro atualizado.", "ok")
    return redirect(url_for("index"))


@app.post("/goleiros/<int:goleiro_id>/excluir")
def excluir_goleiro(goleiro_id):
    desativar(db, goleiro_id)
    flash("Goleiro removido.", "ok")
    return redirect(url_for("index"))


@app.post("/importar-whatsapp")
def importar_whatsapp():
    jogadores, goleiros_novo = importar_lista(request.form.get("lista", ""))
    adicionados = 0
    for item in jogadores:
        if not Jogador.query.filter_by(nome=item["nome"], ativo=True).first():
            criar(db, item["nome"], item["estrelas"], [], [], False)
            adicionados += 1
    for item in goleiros_novo:
        if not Jogador.query.filter_by(nome=item["nome"], is_goleiro=True, ativo=True).first():
            criar(db, item["nome"], item["estrelas"], [], [], True)
            adicionados += 1
    flash(f"Importados {adicionados} jogadores/goleiros.", "ok")
    return redirect(url_for("index"))


@app.post("/sortear")
def sortear():
    try:
        ids = [int(item) for item in request.form.getlist("jogadores")]
    except ValueError:
        ids = []
    erro = validar_selecao(ids)
    jogadores = buscar_selecionados(ids) if not erro else []
    if erro or len(jogadores) != len(ids):
        flash(erro or "Ha jogadores invalidos na selecao.", "erro")
        return redirect(url_for("index"))
    try:
        quantidade = int(request.form.get("quantidade_times", 3))
        tam = request.form.get("jogadores_por_time", "").strip()
        tamanhos = str(int(tam)) if tam else None
        times = gerar(jogadores, quantidade, tamanhos)
        disponiveis = _listar_goleiros()
        import random
        embaralhados = list(disponiveis)
        random.shuffle(embaralhados)
        goleiros_por_time = {}
        for indice, nome_time in enumerate(times):
            goleiros_por_time[nome_time] = embaralhados[indice] if indice < len(embaralhados) else None
    except ValueError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("index"))
    return render_template("index.html", jogadores=listar_ativos(db), goleiros=_listar_goleiros(), times=times, goleiros_por_time=goleiros_por_time, selecionados=ids, historico=Sorteio.query.order_by(Sorteio.data.desc()).all())


@app.post("/sorteios/salvar")
def salvar_sorteio():
    ids = request.form.getlist("jogador_id")
    times = request.form.getlist("time")
    if len(ids) != len(times) or not ids:
        flash("Sorteio invalido.", "erro")
        return redirect(url_for("index"))
    times_dict = {}
    for jogador_id, time in zip(ids, times):
        times_dict.setdefault(time, []).append(int(jogador_id))
    goleiros_ids = {t: None for t in times_dict}
    salvar(db, times_dict, goleiros_ids)
    flash("Sorteio salvo no historico.", "ok")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
