"""Formatador de resultado para WhatsApp."""

ROTULOS = {
    1: "Comeca com a bola",
    2: "Escolhe o lado",
    3: "Comeca fora",
}

CORES = {
    1: "listrado",
    2: "azul",
}


def formatar_whatsapp(times, goleiros, medias):
    linhas = ["*Times da Rodada*", ""]
    nomes = list(times.keys())

    for idx, nome in enumerate(nomes, start=1):
        rotulo = ROTULOS.get(idx, "")
        cabecalho = f"*Time {idx}"
        if rotulo:
            cabecalho += f" ({rotulo})"
        cabecalho += "*"
        linhas.append(cabecalho)

        for jogador in times[nome]:
            linhas.append(jogador.nome)

        g = goleiros.get(nome)
        if g and hasattr(g, "nome"):
            linhas.append(f"Goleiro: {g.nome}")
        elif g is None:
            linhas.append("Goleiro: Improvisado")

        linhas.append("")

    linhas.append("---")
    for idx, nome in enumerate(nomes, start=1):
        rotulo = ROTULOS.get(idx, "")
        cor = CORES.get(idx, "")
        linha = f"*Time {idx}:"
        if rotulo:
            linha += f" {rotulo.lower()}"
        if cor:
            linha += f" e joga de {cor}"
        linha += "*"
        linhas.append(linha)

    return "\n".join(linhas)
