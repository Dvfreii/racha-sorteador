from backend.services.whatsapp_formatter import formatar_whatsapp


class FakeJogador:
    def __init__(self, nome, nota, is_goleiro=False, posicoes=None):
        self.nome = nome
        self.nota = nota
        self.is_goleiro = is_goleiro
        self.posicoes = posicoes or []


class FakePosicao:
    def __init__(self, nome):
        self.nome = nome


def test_formatar_whatsapp():
    times = {
        "Time A": [
            FakeJogador("Joao", 4, is_goleiro=True, posicoes=[FakePosicao("Goleiro")]),
            FakeJogador("Pedro", 3.5, posicoes=[FakePosicao("Alas")]),
            FakeJogador("Lucas", 3, posicoes=[FakePosicao("Zagueiro / Fixo")]),
        ],
        "Time B": [
            FakeJogador("Maria", 4, is_goleiro=True, posicoes=[FakePosicao("Goleiro")]),
            FakeJogador("Ana", 3, posicoes=[FakePosicao("Meio-Campo")]),
            FakeJogador("Carla", 2.5, posicoes=[FakePosicao("Atacante / Pivo")]),
        ],
    }
    goleiros = {"Time A": times["Time A"][0], "Time B": times["Time B"][0]}
    medias = {"Time A": 3.5, "Time B": 3.17}

    texto = formatar_whatsapp(times, goleiros, medias)

    assert "Times da Rodada" in texto
    assert "Time 1" in texto
    assert "Time 2" in texto
    assert "Comeca com a bola" in texto
    assert "Escolhe o lado" in texto
    assert "Joao" in texto
    assert "Pedro" in texto
    assert "Goleiro: Joao" in texto
    assert "Goleiro: Maria" in texto
    assert "listrado" in texto
    assert "azul" in texto
    assert "\u2605" not in texto
    assert "RACHALAB" not in texto
