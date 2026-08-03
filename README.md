# RachaLab — Sorteador de Times

Aplicacao web para organizar rachas de futebol society. Funciona no computador e no celular.

## O que o sistema faz

- Cadastra, edita e exclui jogadores com nota, posicoes multiplas e restricoes.
- Avaliacao visual com estrelas interativas (0,5 a 5).
- Permite escolher multiplas posicoes e definir a posicao principal (prioridade).
- Define restricoes: jogadores que nao podem cair no mesmo time.
- Goleiro definido por checkbox — nao ocupa espaco na lista de posicoes.
- Importa listas copiadas do WhatsApp.
- Sorteia qualquer quantidade de jogadores com algoritmo de balanceamento em 4 regras:
  1. Distribuicao uniforme de goleiros.
  2. Diversidade de posicoes (todo time tem zagueiro/fixo).
  3. Balanceamento de nota tecnica (menor diferenca possivel entre medias).
  4. Respeito a restricoes mutuas.
- Exporta resultado formatado para WhatsApp com emojis (🧤🛡️⚽).
- Salva historico de sorteios no banco de dados.
- API RESTful JSON para integracao com outros sistemas.
- Frontend SPA em JavaScript vanilla consumindo a API.
- Suporte a SQLite local e PostgreSQL em producao.

## Requisitos

- Python 3.10 ou mais recente.
- Pip.
- Navegador atualizado.

## Como executar

```bash
cd racha-sorteador
python -m pip install -r requirements.txt
python app.py
```

Abra no navegador:

```text
http://127.0.0.1:5000
```

Para abrir no celular conectado na mesma rede Wi-Fi, use o IP da maquina:

```text
http://SEU-IP:5000
```

Para parar o servidor, pressione `Ctrl + C` no terminal.

## Como usar

### 1. Cadastrar jogadores

Informe:
- Nome.
- Nota, clicando nas estrelas (widget interativo de 0,5 a 5).
- Posicoes — marque todas as posicoes que o jogador faz e selecione a principal (circulo preto).
- Goleiro — marque o checkbox 🧤 se for goleiro.
- Restricoes — selecione jogadores com quem nao pode jogar junto.

### 2. Importar uma lista do WhatsApp

Cole a mensagem completa na area **Colar lista do WhatsApp** e clique em **Importar lista**.

O sistema identifica:
- Jogadores numerados antes de `Goleiros`.
- Goleiros numerados depois de `Goleiros`.
- Estrelas no nome (⭐).
- Nomes com emojis e asteriscos.

Exemplo:

```text
1 - Joabe ⭐⭐⭐⭐
2 - Maria ⭐⭐⭐
3 - Pedro ⭐⭐⭐⭐⭐

Goleiros
1 - Dorval ⭐⭐⭐
2 - Joel ⭐⭐
```

Linhas de aviso, observacoes e goleiros vazios sao ignoradas.

### 3. Selecionar os presentes

Marque os jogadores que participarao do racha. Use **Selecionar todos** para marcar ou desmarcar todos. E necessario selecionar pelo menos 2 jogadores.

### 4. Sortear

Escolha a quantidade de times (2 a 8) e, opcionalmente, o tamanho de cada time. Clique em **Sortear times equilibrados**.

O algoritmo testa 4000 combinacoes e escolhe a melhor, respeitando:
- Goleiros distribuidos uniformemente.
- Restricoes entre jogadores (nunca no mesmo time).
- Menor diferenca possivel entre as medias de nota dos times.
- Todo time com pelo menos um zagueiro/fixo.
- Maximo de 3 atacantes/pivos por time.
- Maximo de 1 craque (nota 5) e 1 iniciante (nota <= 2) por time.
- Evita repetir pares dos ultimos 3 sorteios.

### 5. Exportar para WhatsApp

Apos o sorteio, clique em **Copiar para WhatsApp** para gerar o texto formatado com emojis:

```
⚽ *RACHALAB — Times da Rodada* ⚽

*Time A* (Media: 3.5)
🧤 Joao ★★★★
⚽ Pedro (Alas) ★★★★
🛡️ Lucas (Zagueiro / Fixo) ★★★
```

### 6. Historico

Os sorteios salvos aparecem na secao **Historico** com times, jogadores, medias e goleiros. E possivel excluir sorteios individualmente.

## API REST

A API JSON esta disponivel em `/api/`:

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/api/jogadores` | Lista jogadores ativos |
| POST | `/api/jogadores` | Cria jogador |
| GET | `/api/jogadores/<id>` | Detalhe do jogador |
| PUT | `/api/jogadores/<id>` | Atualiza jogador |
| DELETE | `/api/jogadores/<id>` | Remove jogador (soft delete) |
| GET | `/api/posicoes` | Lista posicoes |
| POST | `/api/sorteios/sortear` | Executa sorteio (nao salva) |
| POST | `/api/sorteios` | Salva sorteio no historico |
| GET | `/api/sorteios` | Lista historico |
| GET | `/api/sorteios/<id>` | Detalhe do sorteio |
| DELETE | `/api/sorteios/<id>` | Exclui sorteio |
| POST | `/api/sorteios/whatsapp` | Formata resultado para WhatsApp |
| POST | `/api/importar-whatsapp` | Importa lista do WhatsApp |

Body do POST/PUT jogadores:
```json
{
  "nome": "Joao",
  "nota": 4.0,
  "is_goleiro": false,
  "posicoes": [1, 3],
  "posicao_primaria_id": 1,
  "restricoes": [5, 7]
}
```

## Estrutura do projeto

```text
racha-sorteador/
├── app.py                         # Aplicacao Flask, rotas e seed de posicoes
├── api/
│   ├── index.py                   # Handler WSGI para Vercel
│   ├── jogadores_bp.py            # Blueprint /api/jogadores
│   ├── posicoes_bp.py             # Blueprint /api/posicoes
│   ├── sorteios_bp.py             # Blueprint /api/sorteios
│   └── whatsapp_bp.py             # Blueprint WhatsApp + importacao
├── sorteio_engine.py              # Algoritmo de sorteio v2 (4 regras, 4000 iteracoes)
├── migrate_v2.py                  # Migracao do schema v1 para v2
├── requirements.txt               # Dependencias Python
├── vercel.json                    # Configuracao Vercel
├── README.md                      # Este manual
├── backend/
│   ├── extensions.py              # Instancia SQLAlchemy
│   ├── models/
│   │   └── entities.py            # Jogador (unificado), Posicao, Sorteio
│   └── services/
│       ├── draw_service.py        # Servico de sorteios
│       ├── player_service.py      # CRUD de jogadores
│       ├── whatsapp_formatter.py  # Formatacao WhatsApp com emojis
│       └── whatsapp_parser.py     # Leitor de listas do WhatsApp
├── templates/
│   └── index.html                 # SPA shell
├── static/
│   ├── style.css                  # Estilos responsivos + widget de estrelas
│   └── js/
│       ├── app.js                 # Bootstrap da SPA
│       ├── config.js              # URLs da API
│       ├── state.js               # Estado global
│       ├── api/                   # Clientes HTTP (fetch)
│       ├── components/            # Componentes (form, list, pickers, panels)
│       └── utils/                 # DOM helpers, formatacao
├── tests/
│   ├── test_api.py                # Testes da API
│   ├── test_sorteio_engine.py     # Testes do algoritmo
│   └── test_whatsapp.py           # Testes do formatador
└── instance/
    └── racha.db                   # Banco SQLite criado automaticamente
```

## Banco de dados

Por padrao, o SQLite e criado automaticamente em `instance/racha.db`. As posicoes sao semeadas na primeira execucao.

Ordem de escolha da variavel de banco:
1. `DATABASE_URL` — usada pela Vercel (PostgreSQL Neon).
2. `RACHA_DATABASE_URI` — compativel com Render/Railway.
3. SQLite local (`sqlite:///racha.db`).

Para producao com varios usuarios, use PostgreSQL.

## Hospedagem

### Vercel

1. Suba o codigo para um repositorio no GitHub.
2. Crie uma conta em [vercel.com](https://vercel.com) e conecte seu GitHub.
3. Clique em **Add New → Project** e importe o repositorio.
4. A Vercel detecta o Flask pelo `requirements.txt` e usa `api/index.py` como handler.
5. Em **Settings → Environment Variables**, configure `DATABASE_URL` com as credenciais do PostgreSQL (Neon ou Vercel Postgres).
6. Clique em **Deploy**.

O arquivo `vercel.json` ja esta configurado para rotear todas as requisicoes para `api/index.py`. Para usar o banco PostgreSQL da Vercel:

```text
Settings → Environment Variables:
  DATABASE_URL=postgresql://...
```

Servicos gratuitos compativeis com PostgreSQL:
- [Neon](https://neon.tech) — PostgreSQL serverless gratuito.
- Vercel Postgres — integrado a Vercel.

### Render

1. Suba o codigo para o GitHub.
2. Crie um Web Service em [render.com](https://render.com).
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. Configure `DATABASE_URL` nas variaveis de ambiente.

## Variaveis de ambiente

```text
PORT=5000
DATABASE_URL=postgresql://usuario:senha@host:5432/racha
RACHA_DATABASE_URI=sqlite:///racha.db
SECRET_KEY=mude-esta-chave-em-producao
```

## Testes

```bash
python -m pytest tests/ -v
```

17 testes cobrindo API, algoritmo de sorteio e formatacao WhatsApp.

## Solucao de problemas

### `python` nao e reconhecido

Instale o Python e marque **Add Python to PATH** durante a instalacao.

### Porta 5000 ocupada

```bash
$env:PORT=5001
python app.py
```

### Alteracoes nao aparecem

Atualize com `Ctrl + F5`.

## Versao

2.0.0

Bom racha! ⚽
