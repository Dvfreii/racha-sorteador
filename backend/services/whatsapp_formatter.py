"""Formatador de resultado para WhatsApp com emojis."""


def _icone(jogador):
    pos_nomes = [p.nome.lower() for p in getattr(jogador, "posicoes", [])]
    if getattr(jogador, "is_goleiro", False):
        return "\U0001F9E4"
    if any("zagueiro" in p or "fixo" in p for p in pos_nomes):
        return "\U0001F6E1\uFE0F"
    return "\u26BD"


def _estrelas(jogador):
    nota = getattr(jogador, "nota", 3)
    inteiro = int(nota)
    resto = nota - inteiro
    if resto == 0.5:
        return "\u2605" * inteiro + "\u00BD"
    return "\u2605" * inteiro


def _posicoes_str(jogador):
    posicoes = getattr(jogador, "posicoes", [])
    if posicoes:
        nomes = [getattr(p, "nome", str(p)) for p in posicoes]
        if nomes:
            return " (" + ", ".join(nomes) + ")"
    return ""


def formatar_whatsapp(times, goleiros, medias):
    linhas = ["\u26BD *RACHALAB \u2014 Times da Rodada* \u26BD", ""]

    for nome, time in times.items():
        media = medias.get(nome, 0)
        linhas.append(f"*{nome}* (Media: {media:.1f})")

        for jogador in time:
            icone = _icone(jogador)
            est = _estrelas(jogador)
            pos = _posicoes_str(jogador)
            linhas.append(f"{icone} {jogador.nome}{pos} {est}")

        g = goleiros.get(nome)
        if g and hasattr(g, "nome"):
            linhas.append(f"\U0001F9E4 Goleiro: {g.nome}")
        elif g is None:
            linhas.append("\U0001F9E4 Goleiro: Improvisado")

        linhas.append("")

    return "\n".join(linhas)
