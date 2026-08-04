import os
import tempfile
import pytest

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["RACHA_DATABASE_URI"] = f"sqlite:///{_db_path}"
from app import app


@pytest.fixture(scope="session", autouse=True)
def _cleanup_tempdb():
    yield
    os.close(_db_fd)
    try:
        os.unlink(_db_path)
    except PermissionError:
        pass


@pytest.fixture
def client():
    app.config["TESTING"] = True
    from backend.extensions import db
    from backend.models.entities import Posicao

    with app.app_context():
        db.create_all()
        Posicao.query.delete()
        for nome in ["Goleiro", "Zagueiro / Fixo", "Lateral", "Meio-Campo", "Alas", "Atacante / Pivo"]:
            db.session.add(Posicao(nome=nome))
        db.session.commit()

    with app.test_client() as c:
        yield c

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_get_jogadores_vazio(client):
    r = client.get("/api/jogadores")
    assert r.status_code == 200
    assert r.get_json() == []


def test_create_jogador(client):
    posicoes = client.get("/api/posicoes").get_json()
    data = {
        "nome": "Joao",
        "nota": 4.0,
        "posicoes": [posicoes[1]["id"]],
        "restricoes": [],
        "is_goleiro": False,
    }
    r = client.post("/api/jogadores", json=data)
    assert r.status_code == 201
    j = r.get_json()
    assert j["nome"] == "Joao"
    assert j["nota"] == 4.0
    assert len(j["posicoes"]) == 1


def test_update_jogador(client):
    r = client.post("/api/jogadores", json={"nome": "Pedro", "nota": 3.0})
    assert r.status_code == 201
    jid = r.get_json()["id"]
    r = client.put(f"/api/jogadores/{jid}", json={"nome": "Pedro Silva", "nota": 5.0})
    assert r.status_code == 200
    assert r.get_json()["nome"] == "Pedro Silva"
    assert r.get_json()["nota"] == 5.0


def test_delete_jogador(client):
    r = client.post("/api/jogadores", json={"nome": "A", "nota": 3.0})
    jid = r.get_json()["id"]
    r = client.delete(f"/api/jogadores/{jid}")
    assert r.status_code == 200
    r = client.get("/api/jogadores")
    assert r.get_json() == []


def test_validate_missing_nome(client):
    r = client.post("/api/jogadores", json={"nome": "", "nota": 3})
    assert r.status_code == 400


def test_validate_nota_range(client):
    r = client.post("/api/jogadores", json={"nome": "A", "nota": 6})
    assert r.status_code == 400


def test_get_posicoes(client):
    r = client.get("/api/posicoes")
    assert r.status_code == 200
    assert len(r.get_json()) == 6


def test_sortear_sem_salvar(client):
    ids = []
    for nome in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]:
        r = client.post("/api/jogadores", json={"nome": nome, "nota": 3.0})
        ids.append(r.get_json()["id"])

    r = client.post("/api/sorteios/sortear", json={
        "jogadores": ids,
        "quantidade_times": 3,
    })
    assert r.status_code == 200
    data = r.get_json()
    assert "times" in data
    assert "goleiros" in data
    assert "medias" in data
    assert len(data["times"]) == 3


def test_salvar_sorteio(client):
    ids = []
    for nome in ["A", "B", "C", "D", "E", "F"]:
        r = client.post("/api/jogadores", json={"nome": nome, "nota": 3.0})
        ids.append(r.get_json()["id"])

    r = client.post("/api/sorteios/sortear", json={"jogadores": ids, "quantidade_times": 2})
    data = r.get_json()
    times_ids = {}
    for nome, jogadores in data["times"].items():
        times_ids[nome] = [j["id"] for j in jogadores]

    r = client.post("/api/sorteios", json={"times": times_ids, "goleiros": {}})
    assert r.status_code == 201


def test_historico_sorteios(client):
    r = client.get("/api/sorteios")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_whatsapp_format(client):
    r = client.post("/api/sorteios/whatsapp", json={
        "times": {
            "Time A": [
                {"nome": "Joao", "nota": 4, "is_goleiro": True, "posicoes": [{"nome": "Goleiro"}]},
                {"nome": "Pedro", "nota": 3, "is_goleiro": False, "posicoes": [{"nome": "Alas"}]},
            ],
        },
        "goleiros": {"Time A": {"nome": "Joao", "nota": 4, "is_goleiro": True, "posicoes": [{"nome": "Goleiro"}]}},
        "medias": {"Time A": 3.5},
    })
    assert r.status_code == 200
    assert "Times da Rodada" in r.get_json()["texto"]
