from datetime import datetime
import os
import random
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

from backend.models.entities import Goleiro, Jogador, Sorteio, SorteioGoleiro, SorteioJogador
from backend.services.player_service import (
    buscar_selecionados, criar, criar_goleiro, desativar, desativar_goleiro,
    editar, editar_goleiro, listar_ativos, listar_goleiros,
    validar_formulario, validar_selecao,
)
from backend.services.draw_service import gerar, salvar
from backend.services.whatsapp_parser import importar_lista

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    historico = Sorteio.query.order_by(Sorteio.data.desc()).all()
    return render_template("index.html", jogadores=listar_ativos(db), goleiros=listar_goleiros(), times=None, selecionados=[], historico=historico)


@app.post("/sorteios/<int:sorteio_id>/excluir")
def excluir_sorteio(sorteio_id):
    sorteio = db.get_or_404(Sorteio, sorteio_id)
    db.session.delete(sorteio)
    db.session.commit()
    return redirect(url_for("index"))


@app.post("/sorteios/excluir-todos")
def excluir_todos_sorteios():
    Sorteio.query.delete()
    db.session.commit()
    flash("Histórico de sorteios excluído.", "ok")
    return redirect(url_for("index"))


@app.post("/jogadores")
def criar_jogador():
    nome = request.form.get("nome", "").strip()
    try:
        estrelas = float(request.form.get("estrelas", 3).replace(",", "."))
    except ValueError:
        estrelas = 0
    erro = validar_formulario(nome, estrelas)
    if erro:
        flash(erro, "erro")
    else:
        criar(db, nome, estrelas, request.form.get("posicao", "").strip())
        flash("Jogador cadastrado.", "ok")
    return redirect(url_for("index"))


@app.post("/jogadores/<int:jogador_id>/excluir")
def excluir_jogador(jogador_id):
    desativar(db, jogador_id)
    return redirect(url_for("index"))


@app.post("/jogadores/excluir-todos")
def excluir_todos_jogadores():
    Jogador.query.filter_by(ativo=True).update({"ativo": False})
    db.session.commit()
    flash("Todos os jogadores foram excluídos da lista.", "ok")
    return redirect(url_for("index"))


@app.post("/jogadores/<int:jogador_id>/editar")
def editar_jogador(jogador_id):
    nome = request.form.get("nome", "").strip()
    try:
        estrelas = float(request.form.get("estrelas", 3).replace(",", "."))
    except ValueError:
        estrelas = 0
    erro = validar_formulario(nome, estrelas)
    if erro:
        flash(erro, "erro")
    else:
        editar(db, jogador_id, nome, estrelas, request.form.get("posicao", "").strip())
        flash("Jogador atualizado.", "ok")
    return redirect(url_for("index"))


@app.post("/goleiros")
def adicionar_goleiro():
    nome = request.form.get("nome", "").strip()
    if not nome:
        flash("Informe o nome do goleiro.", "erro")
    else:
        criar_goleiro(db, nome)
        flash("Goleiro adicionado.", "ok")
    return redirect(url_for("index"))


@app.post("/goleiros/<int:goleiro_id>/editar")
def editar_goleiro_route(goleiro_id):
    nome = request.form.get("nome", "").strip()
    if nome:
        editar_goleiro(db, goleiro_id, nome)
        flash("Goleiro atualizado.", "ok")
    return redirect(url_for("index"))


@app.post("/goleiros/<int:goleiro_id>/excluir")
def excluir_goleiro(goleiro_id):
    desativar_goleiro(db, goleiro_id)
    return redirect(url_for("index"))


@app.post("/importar-whatsapp")
def importar_whatsapp():
    jogadores, goleiros = importar_lista(request.form.get("lista", ""))
    adicionados = 0
    for item in jogadores:
        if not Jogador.query.filter_by(nome=item["nome"], ativo=True).first():
            criar(db, item["nome"], item["estrelas"], "")
            adicionados += 1
    goleiros_novos = 0
    for item in goleiros:
        if not Goleiro.query.filter_by(nome=item["nome"], ativo=True).first():
            criar_goleiro(db, item["nome"])
            goleiros_novos += 1
    flash(f"Importados {adicionados} jogadores e {goleiros_novos} goleiros.", "ok")
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
        flash(erro or "Há jogadores inválidos na seleção.", "erro")
        return redirect(url_for("index"))
    try:
        quantidade = int(request.form.get("quantidade_times", 3))
        tam = request.form.get("jogadores_por_time", "").strip()
        if tam:
            por_time = int(tam)
            tamanhos = str(por_time)
        else:
            tamanhos = None
        times = gerar(jogadores, quantidade, tamanhos)
        disponiveis = listar_goleiros()
        embaralhados = list(disponiveis)
        random.shuffle(embaralhados)
        goleiros_por_time = {}
        for indice, nome_time in enumerate(times):
            goleiros_por_time[nome_time] = embaralhados[indice] if indice < len(embaralhados) else None
    except ValueError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("index"))
    return render_template("index.html", jogadores=listar_ativos(db), goleiros=listar_goleiros(), times=times, goleiros_por_time=goleiros_por_time, selecionados=ids, historico=Sorteio.query.order_by(Sorteio.data.desc()).all())


@app.post("/sorteios/salvar")
def salvar_sorteio():
    ids = request.form.getlist("jogador_id")
    times = request.form.getlist("time")
    if len(ids) != len(times) or not ids:
        flash("Sorteio inválido.", "erro")
        return redirect(url_for("index"))
    salvar(db, ids, times, request.form.getlist("goleiro_id"))
    flash("Sorteio salvo no histórico.", "ok")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
