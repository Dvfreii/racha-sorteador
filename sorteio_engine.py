"""Motor de sorteio equilibrado do racha - v2."""
from collections import Counter
import random


def tamanhos_dos_times(total, quantidade=3, tamanhos=None):
    if quantidade < 2:
        raise ValueError("Escolha pelo menos 2 times.")
    if tamanhos:
        base = tamanhos[0]
        if base * (quantidade - 1) >= total:
            raise ValueError(
                f"Jogadores insuficientes: para {quantidade} times de {base}, "
                f"e preciso ter mais de {base * (quantidade - 1)} jogadores."
            )
        ultimo = min(total - base * (quantidade - 1), base)
        return [base] * (quantidade - 1) + [ultimo]
    base, sobras = divmod(total, quantidade)
    if base < 1:
        raise ValueError("Nao ha jogadores suficientes para essa quantidade de times.")
    return [base + (1 if i < sobras else 0) for i in range(quantidade)]


def _parse_tamanhos(tamanhos):
    if tamanhos is None:
        return None
    if isinstance(tamanhos, str):
        try:
            val = int(tamanhos.strip())
            return [val]
        except ValueError:
            raise ValueError("Digite apenas o tamanho de cada time. Ex.: 8.")
    return list(tamanhos) if tamanhos else None


def _time_nome(index):
    return f"Time {chr(65 + index)}" if index < 26 else f"Time {index + 1}"


def _get(j, attr, default=None):
    val = getattr(j, attr, None)
    if val is not None:
        return val
    if isinstance(j, dict):
        return j.get(attr, default)
    return default


def _tem_posicao(jogador, alvo):
    posicoes = _get(jogador, "posicoes", [])
    if isinstance(posicoes, str):
        return alvo.lower() in posicoes.lower()
    for p in posicoes:
        nome = _get(p, "nome", str(p)).lower()
        if alvo.lower() in nome:
            return True
    return False


def _ids_restritos(jogador):
    restricoes = _get(jogador, "restricoes", [])
    if isinstance(restricoes, (str, int)):
        return []
    ids = set()
    for r in restricoes:
        rid = _get(r, "id", r)
        if rid:
            ids.add(rid)
    return ids


def sortear_times(jogadores, historico=None, tentativas=4000, quantidade=3, tamanhos=None):
    if len(jogadores) < 2:
        raise ValueError("Selecione pelo menos 2 jogadores.")

    goleiros = [j for j in jogadores if _get(j, "is_goleiro", False)]
    jogadores_linha = [j for j in jogadores if not _get(j, "is_goleiro", False)]

    historico = historico or []

    if not goleiros:
        tamanhos_lista = tamanhos_dos_times(len(jogadores), quantidade, _parse_tamanhos(tamanhos))
        gols_por_time = {_time_nome(i): None for i in range(quantidade)}
        melhor, melhor_pontuacao = None, float("inf")
        melhor_gols = None

        for _ in range(tentativas):
            linha = list(jogadores_linha)
            random.shuffle(linha)
            times = {}
            inicio = 0
            for i in range(quantidade):
                nome = _time_nome(i)
                tam = tamanhos_lista[i]
                times[nome] = linha[inicio:inicio + tam]
                inicio += tam
            pontuacao = _pontuar(times, gols_por_time, historico, jogadores)
            if pontuacao < melhor_pontuacao:
                melhor, melhor_pontuacao = times, pontuacao

        medias = {}
        for nome, time in melhor.items():
            notas = [_get(j, "nota", 0) for j in time if not _get(j, "is_goleiro", False)]
            medias[nome] = round(sum(notas) / len(notas) if notas else 0, 2)

        return melhor, gols_por_time, medias

    # Fase 1: distribuir goleiros
    gols = list(goleiros)
    random.shuffle(gols)

    # Se ha goleiros suficientes, distribui round-robin
    nomes_times = [_time_nome(i) for i in range(quantidade)]

    # Se mais goleiros que times, extras viram linha
    if len(gols) > quantidade:
        goleiros_time = gols[:quantidade]
        goleiros_extras = gols[quantidade:]
        todos_linha = jogadores_linha + goleiros_extras
    else:
        goleiros_time = gols
        todos_linha = list(jogadores_linha)

    tamanhos_lista = tamanhos_dos_times(len(todos_linha), quantidade, _parse_tamanhos(tamanhos))

    melhor, melhor_pontuacao = None, float("inf")
    melhor_gols = None

    for _ in range(tentativas):
        # Shuffle goleiro distribution
        gols_shuffled = list(goleiros_time)
        random.shuffle(gols_shuffled)
        gols_por_time = {}
        for i, nome in enumerate(nomes_times):
            gols_por_time[nome] = gols_shuffled[i] if i < len(gols_shuffled) else None

        linha = list(todos_linha)
        random.shuffle(linha)

        times = {nome: [] for nome in nomes_times}
        inicio = 0
        for i, nome in enumerate(nomes_times):
            tam_linha = tamanhos_lista[i]
            times[nome] = linha[inicio:inicio + tam_linha]
            inicio += tam_linha

        pontuacao = _pontuar(times, gols_por_time, historico, jogadores)
        if pontuacao < melhor_pontuacao:
            melhor, melhor_pontuacao = times, pontuacao
            melhor_gols = dict(gols_por_time)

    # Montar resultado
    times_finais = {}
    for nome in nomes_times:
        time = list(melhor[nome])
        g = melhor_gols.get(nome)
        if g:
            time.insert(0, g)
        times_finais[nome] = time

    goleiros_finais = melhor_gols

    medias = {}
    for nome, time in times_finais.items():
        notas = [_get(j, "nota", 0) for j in time if not _get(j, "is_goleiro", False)]
        medias[nome] = round(sum(notas) / len(notas) if notas else 0, 2)

    return times_finais, goleiros_finais, medias


def _pontuar(times, gols_por_time, historico, todos_jogadores):
    score = 0

    times_completos = {}
    for nome in times:
        time = list(times[nome])
        g = gols_por_time.get(nome)
        if g:
            time.insert(0, g)
        times_completos[nome] = time

    # Restricao = infinite
    restricao_map = {}
    for j in todos_jogadores:
        restricao_map[j.id] = _ids_restritos(j)

    for time in times_completos.values():
        ids = {j.id for j in time}
        for j in time:
            restritos = restricao_map.get(j.id, set())
            if ids & restritos:
                return float("inf")

    # Balanceamento
    totais = [sum(_get(j, "nota", 0) for j in t) for t in times_completos.values()]
    if totais:
        media = sum(totais) / len(totais)
        score += sum(abs(t - media) ** 2 for t in totais) * 30

    for time in times_completos.values():
        tem_zagueiro = any(_tem_posicao(j, "Zagueiro") or _tem_posicao(j, "Fixo") for j in time)
        if not tem_zagueiro:
            score += 10000

        atacantes = sum(1 for j in time if _tem_posicao(j, "Atacante") or _tem_posicao(j, "Pivo"))
        score += max(0, atacantes - 3) * 3000

        craques = sum(1 for j in time if _get(j, "nota", 0) == 5)
        score += max(0, craques - 1) * 2500

        iniciantes = sum(1 for j in time if _get(j, "nota", 0) <= 2)
        score += max(0, iniciantes - 1) * 1200

    # Pares repetidos
    pares = Counter()
    for sorteio in historico[-3:]:
        if isinstance(sorteio, dict):
            for t in sorteio.values():
                ids_t = [str(item) for item in t]
                for i, a in enumerate(ids_t):
                    for b in ids_t[i + 1:]:
                        pares[tuple(sorted((a, b)))] += 4
        elif isinstance(sorteio, list):
            for t in sorteio:
                ids_t = [str(item) for item in t]
                for i, a in enumerate(ids_t):
                    for b in ids_t[i + 1:]:
                        pares[tuple(sorted((a, b)))] += 4

    for time in times_completos.values():
        ids_t = [str(j.id) for j in time]
        for i, a in enumerate(ids_t):
            for b in ids_t[i + 1:]:
                score += pares.get(tuple(sorted((a, b))), 0)

    return score


def nomes_historico(sorteio):
    grupos = {}
    for item in sorteio.itens:
        grupos.setdefault(item.time, []).append(str(item.jogador_id))
    return list(grupos.values())


def historico_para_engine(sorteios):
    result = []
    for sorteio in sorteios:
        grupos = {}
        for item in sorteio.itens:
            grupos.setdefault(item.time, []).append(item.jogador_id)
        result.append(grupos)
    return result
