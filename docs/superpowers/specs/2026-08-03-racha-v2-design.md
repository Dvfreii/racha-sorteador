# RachaLab v2 — Especificação de Design

**Data:** 2026-08-03
**Escopo:** Refatoração do sorteador de society para aplicação completa com persistência, balanceamento avançado e API REST.

---

## 1. Visão Geral

Transformar o RachaLab de um sorteador server-rendered com formulários POST/redirect em uma aplicação com:
- API RESTful (JSON)
- Frontend SPA vanilla JS
- Algoritmo de balanceamento com restrições
- Exportação formatada para WhatsApp

---

## 2. Modelagem do Banco de Dados

### 2.1 Entidade `Jogador`

| Coluna | Tipo | Restrição |
|--------|------|-----------|
| id | Integer | PK, autoincrement |
| nome | String(100) | NOT NULL |
| nota | Float | NOT NULL, default 3.0 (intervalo 1-5) |
| is_goleiro | Boolean | NOT NULL, default false |
| ativo | Boolean | NOT NULL, default true |

### 2.2 Entidade `Posicao`

| Coluna | Tipo | Restrição |
|--------|------|-----------|
| id | Integer | PK, autoincrement |
| nome | String(40) | UNIQUE, NOT NULL |

Posições pré-cadastradas: Goleiro, Zagueiro / Fixo, Lateral, Meio-Campo, Alas, Atacante / Pivô.

### 2.3 Tabelas associativas

**`jogador_posicoes`** — N:N entre Jogador e Posicao.
**`jogador_restricoes`** — N:N self-referential. `jogador_id` + `restrito_id`. Restrição é simétrica.

### 2.4 Entidades de histórico (mantidas com ajustes)

| Entidade | Ajuste |
|----------|--------|
| `Sorteio` | Sem alteração (id, data) |
| `SorteioJogador` | Adiciona `is_goleiro_no_time` (Boolean); coluna `jogador_id` agora aponta para o `Jogador` unificado |
| `SorteioGoleiro` | **Removida** |

### 2.5 O que é eliminado

- `Goleiro` — unificado como flag `Jogador.is_goleiro`
- `Jogador.posicao` (string única) — substituído por `jogador_posicoes` (N:N)

---

## 3. Algoritmo de Sorteio

Três fases encadeadas:

### Fase 1 — Distribuição de goleiros
- Filtra jogadores com `is_goleiro=True` dos selecionados
- Distribui round-robin pelos times
- Times sem goleiro recebem `goleiro=None`

### Fase 2 — Otimização (4000 iterações)
Função de custo (multiplicadores dos pesos visam ordem de grandeza compatível):

| Regra | Tipo | Peso |
|-------|------|------|
| Restrição violada (A e B com restrição mútua no mesmo time) | hard | ∞ (descarta iteração) |
| Desbalanceamento de nota (soma dos quadrados dos desvios da média geral) | soft | ×30 |
| Time sem zagueiro/fixo | soft | +10000 |
| +3 atacantes/pivôs no mesmo time | soft | +3000 por excedente |
| +1 craque (nota=5) por time | soft | +2500 por excedente |
| +1 iniciante (nota≤2) por time | soft | +1200 por excedente |
| Pares repetidos nos últimos 3 sorteios | soft | +4 por repetição |

### Fase 3 — Resultado
Retorna `{times, goleiros, medias}` onde:
- `times`: `{ "Time A": [Jogador, ...], ... }`
- `goleiros`: `{ "Time A": Jogador | None, ... }`
- `medias`: `{ "Time A": float, ... }`

---

## 4. API REST

Base URL: `/api/`

### 4.1 Jogadores — `/api/jogadores`

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/jogadores` | Lista ativos. Query: `?incluir_inativos=true` |
| POST | `/api/jogadores` | Cria. Body: `{nome, nota, posicoes:[id], restricoes:[id], is_goleiro}` |
| GET | `/api/jogadores/<id>` | Detalhe (com posições e restrições populadas) |
| PUT | `/api/jogadores/<id>` | Atualiza. Mesmo body do POST |
| DELETE | `/api/jogadores/<id>` | Soft delete (`ativo=False`) |

### 4.2 Posições — `/api/posicoes`

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/posicoes` | Lista todas as posições |

### 4.3 Sorteios — `/api/sorteios`

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/sorteios/sortear` | Executa sorteio sem salvar. Body: `{jogadores:[id], quantidade_times, tamanhos:null}` |
| POST | `/api/sorteios` | Salva no histórico. Body: `{times:{nome:[id]}, goleiros:{nome:id}}` |
| GET | `/api/sorteios` | Histórico. Query: `?limite=10&offset=0` |
| GET | `/api/sorteios/<id>` | Detalhe do sorteio |
| DELETE | `/api/sorteios/<id>` | Exclui |

### 4.4 WhatsApp — `/api/sorteios/whatsapp`

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/sorteios/whatsapp` | Body: resultado do sortear. Retorna `{texto}` formatado |

### 4.5 Importação — `/api/importar-whatsapp`

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/importar-whatsapp` | Body: `{lista:"..."}` . Retorna `{jogadores, goleiros}` |

### Organização dos blueprints

```
app.py                   → factory + registro de blueprints + rotas legadas
api/
  jogadores_bp.py        → Blueprint "/api/jogadores"
  sorteios_bp.py         → Blueprint "/api/sorteios"
  posicoes_bp.py         → Blueprint "/api/posicoes"
  whatsapp_bp.py         → Blueprint "/api/sorteios/whatsapp" + "/api/importar-whatsapp"
```

Rotas legadas (`/sortear`, `/jogadores`, `/`) mantidas no `app.py` para compatibilidade durante transição.

---

## 5. Frontend (SPA)

### 5.1 Stack
- Vanilla JS (ES modules)
- Bootstrap 5.3 (CDN)
- Hash-based routing

### 5.2 Estrutura de módulos

```
static/js/
  app.js
  config.js
  state.js
  api/
    jogadores.js
    posicoes.js
    sorteios.js
    whatsapp.js
  components/
    jogador-form.js
    jogador-list.js
    posicao-picker.js
    restricao-picker.js
    sorteador-panel.js
    resultado-panel.js
    historico-panel.js
    whatsapp-preview.js
  utils/
    dom.js          (mantido)
    format.js       (novo: formatarNota, iconePosicao)
```

### 5.3 Fluxo de renderização

1. `app.js` carrega jogadores e posições via API
2. Renderiza sidebar + seções (jogadores, sorteio, histórico)
3. Seleção de jogadores → POST sortear → renderiza resultado
4. Botão "Copiar WhatsApp" → POST whatsapp → modal com texto
5. Botão "Salvar" → POST sorteios
6. Histórico carrega via GET e renderiza detalhes expansíveis

### 5.4 Formatação WhatsApp

Emojis por papel no time:
- 🧤 Goleiro
- 🛡️ Zagueiro / Fixo
- ⚽ Linha (demais posições)

Formato de saída:
```
⚽ *RACHALAB — Times da Rodada* ⚽

*Time A* (Média: 3.4)
🧤 João (Goleiro) ★4
⚽ Pedro (Alas) ★3.5
🛡️ Lucas (Zagueiro / Fixo) ★3
...

*Time B* (Média: 3.6)
...
```

### 5.5 O que some do template atual
- Todos os `{% for %}` e `{{ }}` Jinja2
- Modais inline no HTML
- Formulários com action POST + redirect
- `Goleiro` como entidade separada na UI

---

## 6. Migração

### 6.1 Migração do banco
Script `migrate.py` para:
1. Criar tabela `Posicao` com seeds
2. Adicionar colunas `is_goleiro` ao `Jogador`
3. Migrar dados de `Goleiro` → `Jogador` (com `is_goleiro=True`)
4. Criar tabelas associativas `jogador_posicoes` e `jogador_restricoes`
5. Migrar `Jogador.posicao` (string) → `jogador_posicoes` (N:N) via match por nome
6. Criar coluna `is_goleiro_no_time` em `SorteioJogador`
7. Migrar `SorteioGoleiro` → `SorteioJogador.is_goleiro_no_time=True`
8. Remover tabelas `Goleiro` e `SorteioGoleiro`

### 6.2 Rollback
Rotas legadas preservadas. Frontend antigo permanece funcional como fallback até o novo SPA estar completo.

---

## 7. Verificação

- [ ] API: CRUD de jogadores com posições e restrições
- [ ] API: sorteio respeita as 4 regras (goleiros, posições, balanceamento, restrições)
- [ ] API: formato WhatsApp com emojis corresponde ao especificado
- [ ] Frontend: grid de jogadores renderiza da API
- [ ] Frontend: resultado mostra times com média e goleiro
- [ ] Frontend: botão copiar WhatsApp gera texto formatado
- [ ] Migração: dados existentes preservados após rodar `migrate.py`
