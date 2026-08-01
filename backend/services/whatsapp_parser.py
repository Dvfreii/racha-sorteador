import re

LINE_RE = re.compile(r"^\s*\d+\s*[-.)]\s*(.+?)\s*$")
STAR_RE = re.compile(r"(⭐|★|☆)")


def limpar_nome(nome):
    nome = re.sub(r"[*_`]+", "", nome)
    nome = re.sub(r"[^\wÀ-ÿ .'-]", "", nome, flags=re.UNICODE)
    return re.sub(r"\s+", " ", nome).strip(" .-")


def ler_nota(texto):
    estrelas = len(STAR_RE.findall(texto))
    return float(estrelas or 3)


def importar_lista(texto):
    jogadores, goleiros = [], []
    secao_goleiros = False
    for linha in texto.splitlines():
        if linha.strip().lower().startswith("goleiros"):
            secao_goleiros = True
            continue
        match = LINE_RE.match(linha)
        if not match:
            continue
        bruto = match.group(1)
        nota = ler_nota(bruto)
        nome = limpar_nome(STAR_RE.sub("", bruto))
        if not nome:
            continue
        (goleiros if secao_goleiros else jogadores).append({"nome": nome, "estrelas": nota})
    return jogadores, goleiros
