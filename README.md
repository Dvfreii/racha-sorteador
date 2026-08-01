# RachaLab — Sorteador de Times

Aplicação web para organizar rachas de futebol. Funciona no computador e no celular.

## O que o sistema faz

- Cadastra, edita e exclui jogadores.
- Avaliação visual com exatamente 5 estrelas.
- Cada estrela aceita meia estrela: lado esquerdo = `0,5`, lado direito = valor inteiro.
- Estrelas ficam cinzas no estado inicial e amarelas no hover/seleção.
- Permite digitar qualquer posição.
- Cards mostram nome, estrelas e posição de cada jogador.
- Importa listas copiadas do WhatsApp.
- Cadastra goleiros separados dos jogadores de linha.
- Sorteia qualquer quantidade de jogadores.
- Permite escolher a quantidade de times e o tamanho de cada time.
- Excedente de jogadores fica automaticamente no banco.
- Equilibra estrelas, posições, craques, iniciantes e histórico recente.
- Salva os sorteios no histórico, com os goleiros de cada rodada.
- Salva tudo no banco SQLite.

## Requisitos

- Python 3.10 ou mais recente.
- Pip.
- Navegador atualizado.

## Como executar no Windows

Abra o PowerShell ou Prompt de Comando e execute:

```bash
cd C:\Users\Davi\hermes\racha-sorteador
python -m pip install -r requirements.txt
python app.py
```

Abra no navegador:

```text
http://127.0.0.1:5000
```

Para abrir no celular conectado na mesma rede Wi-Fi, use o IP da máquina:

```text
http://SEU-IP:5000
```

Para parar o servidor, pressione `Ctrl + C` no terminal.

## Como usar

### 1. Cadastrar jogadores

Informe:

- Nome.
- Nota, clicando nas estrelas: clique na metade esquerda da estrela para meia estrela (ex.: `3,5`) e na estrela inteira para o valor cheio (ex.: `4`).
- Posição — pode ser uma posição personalizada.

Também é possível editar ou excluir um jogador no próprio card.

### 2. Importar uma lista do WhatsApp

Cole a mensagem completa na área **Colar lista do WhatsApp**.

O sistema identifica:

- Jogadores numerados antes de `Goleiros`.
- Goleiros numerados depois de `Goleiros`.
- Estrelas no nome.
- Nomes com emojis e asteriscos.

Exemplo:

```text
1 - Joabe ⭐⭐⭐⭐⭐
2 - Maria ⭐⭐⭐

Goleiros
1 - Dorval
2 - Joel
```

Linhas de aviso, observações e goleiros vazios são ignoradas.

### 3. Selecionar os presentes

Marque os jogadores que participarão do racha.

Use **Selecione todos** para marcar ou desmarcar todos de uma vez.

É necessário selecionar pelo menos 2 jogadores.

### 4. Definir os times

Escolha a quantidade de times (de 2 a 8) e, se quiser, o **tamanho de cada time**.

Sem tamanho informado, a divisão é automática:

```text
20 jogadores e 4 times = 5, 5, 5, 5
25 jogadores e 3 times = 9, 8, 8
```

Com tamanho informado (ex.: `8`), os primeiros times ficam completos e o último recebe o restante. Se ainda sobrar gente, o excedente vai para o banco:

```text
20 jogadores, 3 times de 8 = 8, 8, 4
25 jogadores, 3 times de 8 = 8, 8, 8 e 1 jogador no banco
```

Para o sorteio acontecer, é preciso ter mais jogadores do que `tamanho × (times − 1)`. Ex.: para 3 times de 8, é preciso mais de 16 jogadores.

### 5. Definir goleiros

Os goleiros ficam separados do sorteio dos jogadores de linha. Cadastre os goleiros do racha e o sistema sorteia um para cada time; times sem goleiro cadastrado usam goleiro improvisado.

O histórico mostra a seção **Goleiros** com os goleiros de cada sorteio salvo.

## Como o equilíbrio funciona

O algoritmo testa várias combinações e escolhe a melhor pontuação possível considerando:

- Soma de estrelas dos times.
- Distribuição de jogadores de 5 estrelas.
- Distribuição de jogadores com até 2 estrelas.
- Presença de zagueiros, quando cadastrados.
- Limite de atacantes por time, quando possível.
- Repetição de companheiros nos últimos 3 sorteios.
- Tamanho dos times.

Quando uma regra for impossível — por exemplo, menos zagueiros do que times — o sistema continua funcionando e minimiza o problema.

## Estrutura do projeto

```text
racha-sorteador/
├── app.py                         # Aplicação Flask e rotas
├── sorteio_engine.py              # Algoritmo de sorteio
├── requirements.txt               # Dependências Python
├── Procfile                       # Comando para hospedagem
├── README.md                      # Este manual
├── backend/
│   ├── extensions.py              # Banco SQLAlchemy
│   ├── models/entities.py         # Jogador, goleiro e sorteio
│   └── services/
│       ├── draw_service.py        # Serviço de sorteios
│       ├── player_service.py      # Serviço de jogadores
│       └── whatsapp_parser.py     # Leitor de listas do WhatsApp
├── templates/
│   └── index.html                 # Interface web
├── static/
│   ├── style.css                  # Estilos responsivos + widget de estrelas
│   └── js/
│       ├── app.js                 # Entrada do frontend
│       ├── components/             # Componentes da tela
│       ├── hooks/                  # Lógica reutilizável
│       ├── utils/                  # Utilitários DOM
│       ├── api/                    # Cliente HTTP
│       └── services/               # Serviços do frontend
└── instance/
    └── racha.db                   # Banco criado automaticamente
```

## Banco de dados

Por padrão, o SQLite é criado automaticamente em:

```text
instance/racha.db
```

Para usar outro banco, defina a variável `RACHA_DATABASE_URI`.

Exemplo:

```bash
set RACHA_DATABASE_URI=sqlite:///racha.db
python app.py
```

Para produção com vários usuários, prefira PostgreSQL.

## Hospedagem

A aplicação pode ser hospedada como um único serviço Flask.

O arquivo `Procfile` usa:

```bash
gunicorn app:app
```

Plataformas possíveis:

- Render.
- Railway.
- Fly.io.
- VPS.

### Render (passo a passo)

1. Suba o código para um repositório no GitHub.
2. Crie uma conta em [render.com](https://render.com) e conecte seu GitHub.
3. Clique em **New → Web Service** e selecione o repositório.
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Clique em **Create Web Service** e aguarde o deploy.
6. Acesse a URL gerada (ex.: `https://racha-sorteador.onrender.com`) de qualquer celular.

Observação: no plano gratuito do Render, o serviço "dorme" após 15 minutos sem uso e o SQLite é apagado a cada novo deploy. Para manter o histórico, use um disco persistente (Render Disk) ou migre para PostgreSQL.

### Railway (alternativa)

1. Crie um projeto em [railway.app](https://railway.app) e conecte o repositório do GitHub.
2. O Railway instala as dependências pelo `requirements.txt`.
3. Configure o comando de início como `gunicorn app:app`.
4. Gere um domínio público em **Settings → Networking**.

Para dados persistentes em produção, configure PostgreSQL e defina `RACHA_DATABASE_URI`. SQLite em ambientes efêmeros pode ser perdido durante redeploys.

### Variáveis de ambiente

```text
PORT=5000
RACHA_DATABASE_URI=sqlite:///instance/racha.db
```

Não publique senhas, tokens ou arquivos `.env` no GitHub.

## Transformar em aplicativo instalável

O modo web hospedado é o caminho mais simples. Futuramente, o projeto pode virar:

- PWA instalável pelo navegador.
- Aplicativo desktop com Tauri.
- Aplicativo desktop com Electron.

## Verificação rápida

Compilar os arquivos Python:

```bash
python -m py_compile app.py sorteio_engine.py backend/models/entities.py backend/services/*.py
```

Depois, abra o navegador e confirme:

1. A página carrega.
2. Um jogador pode ser cadastrado com nota em estrelas.
3. Uma lista do WhatsApp pode ser importada.
4. Os jogadores podem ser selecionados.
5. A quantidade de times pode ser alterada.
6. Com tamanho `8`, 20 jogadores em 3 times geram `8/8/4` e 25 geram `8/8/8` com 1 no banco.
7. O sorteio exibe todos os jogadores uma única vez.

## Observações

- Os goleiros não recebem nota e não entram na divisão dos jogadores de linha.
- A exclusão é lógica: o jogador deixa de aparecer, mas o histórico é preservado.
- O banco SQLite local não deve ser apagado se você quiser manter o histórico.
- Para uso público, adicione autenticação, proteção CSRF e migrações de banco.

## Solução de problemas

### `python` não é reconhecido

Instale o Python e marque a opção **Add Python to PATH** durante a instalação.

### Porta 5000 ocupada

No Windows PowerShell:

```bash
$env:PORT=5001
python app.py
```

Depois acesse:

```text
http://127.0.0.1:5001
```

### Alterações não aparecem

Atualize a página com:

```text
Ctrl + F5
```

## Licença

Uso privado.

## Versão

1.1.0

Bom racha! ⚽
