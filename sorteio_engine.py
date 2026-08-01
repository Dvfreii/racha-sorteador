"""Motor de sorteio equilibrado do racha."""
from collections import Counter
import random

TEAM_NAMES = ["Time A", "Time B", "Time C", "Time D", "Time E", "Time F", "Time G", "Time H"]


def nomes_dos_times(quantidade):
    return [f"Time {chr(65 + i)}" for i in range(quantidade)]


def tamanhos_dos_times(total, quantidade=3, tamanhos=None):
    if quantidade < 2:
        raise ValueError("Escolha pelo menos 2 times.")
    if tamanhos:
        # Formato: um único tamanho por time. Os primeiros times ficam completos;
        # o último recebe o restante (pode ficar menor) e, se ainda sobrar gente,
        # esses jogadores ficam no banco.
        # Ex.: 20 em 3 times de 8 -> 8/8/4 · 25 em 3 times de 8 -> 8/8/8 e 1 no banco.
        if len(tamanhos) != 1 or tamanhos[0] < 1:
            raise ValueError("Digite apenas o tamanho de cada time. Ex.: 8.")
        base = tamanhos[0]
        if base * (quantidade - 1) >= total:
            raise ValueError(
                f"Jogadores insuficientes: para {quantidade} times de {base}, "
                f"é preciso ter mais de {base * (quantidade - 1)} jogadores."
            )
        ultimo = min(total - base * (quantidade - 1), base)
        return [base] * (quantidade - 1) + [ultimo]
    base, sobras = divmod(total, quantidade)
    if base < 1:
        raise ValueError("Não há jogadores suficientes para essa quantidade de times.")
    return [base + (1 if i < sobras else 0) for i in range(quantidade)]


def _parse_tamanhos(tamanhos):
    if tamanhos is None:
        return None
    if isinstance(tamanhos, str):
        try:
            return [int(item.strip()) for item in tamanhos.split(",") if item.strip()]
        except ValueError:
            raise ValueError("Digite apenas o tamanho de cada time. Ex.: 8.")
    return list(tamanhos) if tamanhos else None


def nomes_historico(sorteio):
    grupos = {}
    for item in sorteio.itens:
        grupos.setdefault(item.time, []).append(str(item.jogador_id))
    return list(grupos.values())



def _time_nome(index):
    return f"Time {chr(65 + index)}" if index < 26 else f"Time {index + 1}"


def sortear_times(jogadores, historico=None, tentativas=4000, quantidade=3, tamanhos=None):
    """Sorteia qualquer configuração de times, inclusive times quebrados."""
    if len(jogadores) < 2:
        raise ValueError("Selecione pelo menos 2 jogadores.")
    historico = historico or []
    tamanhos = tamanhos_dos_times(len(jogadores), quantidade, _parse_tamanhos(tamanhos))
    melhor, melhor_pontuacao = None, float("inf")

    for _ in range(tentativas):
        ordem = list(jogadores)
        random.shuffle(ordem)
        times, inicio = [], 0
        for tamanho in tamanhos:
            times.append(ordem[inicio:inicio + tamanho])
            inicio += tamanho
        pontuacao = _pontuar(times, historico)
        if pontuacao < melhor_pontuacao:
            melhor, melhor_pontuacao = times, pontuacao

    return {_time_nome(i): time for i, time in enumerate(melhor)}


def _valor(j, campo, padrao=""):
    return j.get(campo, padrao) if isinstance(j, dict) else getattr(j, campo, padrao)


def _pontuar(times, historico):
    totais = [sum(float(_valor(j, "estrelas", 1)) for j in t) for t in times]
    media = sum(totais) / 3
    score = sum(abs(total - media) ** 2 for total in totais) * 30

    for time in times:
        posicoes = [str(_valor(j, "posicao")).lower() for j in time]
        atacantes = sum("atac" in p for p in posicoes)
        zagueiros = sum("zague" in p or "def" in p for p in posicoes)
        iniciantes = sum(float(_valor(j, "estrelas", 1)) <= 2 for j in time)
        craques = sum(float(_valor(j, "estrelas", 1)) == 5 for j in time)
        score += max(0, 1 - zagueiros) * 10000
        score += max(0, atacantes - 3) * 3000
        score += max(0, iniciantes - 1) * 1200
        score += max(0, craques - 1) * 2500

    # Penaliza pares que estiveram juntos nos últimos 3 sorteios.
    pares = Counter()
    for sorteio in historico[-3:]:
        for time in sorteio:
            for i, jogador in enumerate(time):
                for outro in time[i + 1:]:
                    a, b = sorted((str(jogador), str(outro)))
                    pares[(a, b)] += 4
    for time in times:
        nomes = [str(_valor(j, "id", _valor(j, "nome"))) for j in time]
        for i, a in enumerate(nomes):
            for b in nomes[i + 1:]:
                score += pares[tuple(sorted((a, b)))]
    return score


def historico_para_engine(sorteios):
    return [[ [str(item.jogador_id) for item in sorteio.itens if item.time == nome]
              for nome in TEAM_NAMES] for sorteio in sorteios]
