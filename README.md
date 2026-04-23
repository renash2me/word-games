# 🔤 Jogos de Palavras

Aplicação web com dois jogos de palavras em Português:

- **Palavras Cruzadas Diretas** — formato Coquetel: grade preenchida com
  palavras, dicas em células embutidas (tooltip), dificuldade ajustável
  (8×10 até 11×16), uma palavra revelada como âncora.
- **Criptograma** — provérbios com letras substituídas por símbolos Unicode.

## Versão

**v11** — Palavras Cruzadas migradas pra formato Coquetel Diretas de verdade:
- Solver CSP com forward-checking + MRV
- Layout generator dedicado (grids 100% preenchidos)
- Banco expandido de 1635 → 2310 palavras com dicas
- Endpoint aceita `?difficulty=1..5`

---

## Stack

| Camada    | Tecnologia                  |
|-----------|-----------------------------|
| Backend   | Python 3.11 + FastAPI       |
| Frontend  | HTML/CSS/JS (SPA, sem deps) |
| Container | Docker (multi-arch: amd64 + arm64) |
| Registry  | GitHub Container Registry (GHCR) |

---

## Deploy no Raspberry Pi / OMV

Crie um arquivo `compose.yml` no Pi com o conteúdo abaixo
(substitua `SEU_USUARIO` pelo seu username do GitHub):

```yaml
services:
  word-games:
    image: ghcr.io/SEU_USUARIO/word-games:latest
    container_name: word-games
    restart: unless-stopped
    ports:
      - "8000:8000"
```

Depois:

```bash
docker compose pull
docker compose up -d
```

## Desenvolvimento local

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# http://localhost:8000
```

## Arquitetura do crossword (v11)

- `crossword.py` — orquestrador; chama layout_generator, solver, monta JSON
- `layout_generator.py` — gera grid NxM com clue-cells posicionadas
- `solver.py` — CSP backtracking + forward-checking + MRV
- `grid.py`, `slot.py`, `heuristics.py`, `dictionary.py` — módulos de apoio
- `words_pt.py` — banco de 2310 palavras com dicas estilo Coquetel

Dificuldades:

| Nível | Grid (cols × linhas) |
|-------|----------------------|
| 1     | 8 × 10               |
| 2     | 9 × 11               |
| 3     | 10 × 13              |
| 4     | 11 × 14              |
| 5     | 11 × 16              |
