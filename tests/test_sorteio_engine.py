import pytest
from sorteio_engine import sortear_times, tamanhos_dos_times


class FakeJogador:
    def __init__(self, id, nome, nota, is_goleiro=False, posicoes=None, restricoes=None):
        self.id = id
        self.nome = nome
        self.nota = nota
        self.is_goleiro = is_goleiro
        self.posicoes = posicoes or []
        self.restricoes = restricoes or []


class FakePosicao:
    def __init__(self, nome):
        self.nome = nome


def _make_jogadores(specs):
    return [FakeJogador(
        id=i,
        nome=s["nome"],
        nota=s.get("nota", 3.0),
        is_goleiro=s.get("is_goleiro", False),
        posicoes=[FakePosicao(p) for p in s.get("posicoes", [])],
        restricoes=s.get("restricoes", []),
    ) for i, s in enumerate(specs, 1)]


def test_sortear_distribui_goleiros():
    specs = [
        {"nome": "A", "nota": 3, "is_goleiro": True},
        {"nome": "B", "nota": 3, "is_goleiro": True},
        {"nome": "C", "nota": 3, "is_goleiro": True},
        {"nome": "D", "nota": 3},
        {"nome": "E", "nota": 3},
        {"nome": "F", "nota": 3},
        {"nome": "G", "nota": 3},
        {"nome": "H", "nota": 3},
        {"nome": "I", "nota": 3},
        {"nome": "J", "nota": 3},
        {"nome": "K", "nota": 3},
        {"nome": "L", "nota": 3},
    ]
    jogadores = _make_jogadores(specs)
    times, goleiros, _ = sortear_times(jogadores, quantidade=3)
    assert len(goleiros) == 3
    goleiros_set = set(goleiros.values())
    assert len(goleiros_set) == 3  # all 3 goleiros distributed
    assert None not in goleiros_set  # no team without goleiro


def test_sortear_respeita_restricoes():
    specs = [
        {"nome": "A", "nota": 3, "restricoes": [3]},
        {"nome": "B", "nota": 3},
        {"nome": "C", "nota": 3, "restricoes": [4]},
        {"nome": "D", "nota": 3, "restricoes": [3]},
        {"nome": "E", "nota": 3},
        {"nome": "F", "nota": 3},
        {"nome": "G", "nota": 3},
        {"nome": "H", "nota": 3},
        {"nome": "I", "nota": 3},
        {"nome": "J", "nota": 3},
        {"nome": "K", "nota": 3},
        {"nome": "L", "nota": 3},
    ]
    jogadores = _make_jogadores(specs)
    times, _, _ = sortear_times(jogadores, quantidade=3)

    for time_jogadores in times.values():
        ids = {j.id for j in time_jogadores}
        if 1 in ids:
            assert 3 not in ids, "Jogador 1 tem restricao com 3"
        if 3 in ids:
            assert 4 not in ids, "Jogador 3 tem restricao com 4"


def test_sortear_balanceia_notas():
    specs = [
        {"nome": "A", "nota": 5},
        {"nome": "B", "nota": 5},
        {"nome": "C", "nota": 1},
        {"nome": "D", "nota": 1},
        {"nome": "E", "nota": 5},
        {"nome": "F", "nota": 1},
        {"nome": "G", "nota": 5},
        {"nome": "H", "nota": 1},
        {"nome": "I", "nota": 3},
        {"nome": "J", "nota": 3},
        {"nome": "K", "nota": 3},
        {"nome": "L", "nota": 3},
    ]
    jogadores = _make_jogadores(specs)
    times, _, medias = sortear_times(jogadores, quantidade=3)
    valores = list(medias.values())
    assert max(valores) - min(valores) < 1.5, f"Too unbalanced: {medias}"


def test_sortear_garante_zagueiro_por_time():
    specs = [
        {"nome": "Z1", "nota": 3, "posicoes": ["Zagueiro / Fixo"]},
        {"nome": "Z2", "nota": 3, "posicoes": ["Zagueiro / Fixo"]},
        {"nome": "Z3", "nota": 3, "posicoes": ["Zagueiro / Fixo"]},
        {"nome": "A", "nota": 4, "posicoes": ["Atacante / Pivo"]},
        {"nome": "B", "nota": 4, "posicoes": ["Alas"]},
        {"nome": "C", "nota": 3, "posicoes": ["Meio-Campo"]},
        {"nome": "D", "nota": 5, "posicoes": ["Atacante / Pivo"]},
        {"nome": "E", "nota": 3, "posicoes": ["Meio-Campo"]},
        {"nome": "F", "nota": 2, "posicoes": ["Lateral"]},
        {"nome": "G", "nota": 3, "posicoes": ["Alas"]},
        {"nome": "H", "nota": 4, "posicoes": ["Meio-Campo"]},
        {"nome": "I", "nota": 3, "posicoes": ["Atacante / Pivo"]},
    ]
    jogadores = _make_jogadores(specs)
    times, _, _ = sortear_times(jogadores, quantidade=3)
    for nome, time_jogadores in times.items():
        tem_zagueiro = any(
            any("Zagueiro" in p.nome or "Fixo" in p.nome for p in j.posicoes)
            for j in time_jogadores
        )
        assert tem_zagueiro, f"{nome} has no Zagueiro/Fixo"


def test_tamanhos_dos_times():
    assert tamanhos_dos_times(12, 3) == [4, 4, 4]
    assert tamanhos_dos_times(10, 3) == [4, 3, 3]
    with pytest.raises(ValueError):
        tamanhos_dos_times(1, 3)
