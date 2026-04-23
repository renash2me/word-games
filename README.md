# 🔤 Jogos de Palavras

Aplicação web com dois jogos de palavras em Português:

- **Palavras Cruzadas** — formato Coquetel Diretas: grade totalmente preenchida,
  dicas em células embutidas no grid (tooltip ao passar mouse / tocar),
  uma palavra revelada como âncora.
- **Criptograma** — provérbios com letras substituídas por símbolos Unicode.

## Versão

**v10** — Palavras Cruzadas migrada do formato americano (blocos pretos +
lista lateral de dicas) para o formato Coquetel Diretas (células-dica
com tooltip, palavra revelada).

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
    ports:
      - "8080:8000"
    restart: unless-stopped
```

```bash
# Primeira vez
docker compose up -d

# Atualizar após novo push no GitHub
docker compose pull && docker compose up -d
```

Acesse em: `http://IP-DO-PI:8080`

---

## Desenvolvimento local

```bash
git clone https://github.com/SEU_USUARIO/word-games.git
cd word-games
pip install -r requirements.txt
uvicorn main:app --reload
# Acesse: http://localhost:8000
```

---

## CI/CD

A cada `git push` na branch `main`, o GitHub Actions:

1. Builda a imagem para `linux/amd64` e `linux/arm64`
2. Publica em `ghcr.io/SEU_USUARIO/word-games:latest`

O Pi só precisa rodar `docker compose pull` para pegar a versão mais nova.

---

## Estrutura

```
word-games/
├── .github/
│   └── workflows/
│       └── docker.yml   ← GitHub Actions (build + push GHCR)
├── static/
│   └── index.html       ← SPA completo
├── main.py              ← FastAPI
├── crossword.py         ← Gerador de palavras cruzadas
├── cryptogram.py        ← Gerador de criptograma
├── words_pt.py          ← Vocabulário PT (~90 palavras + dicas)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml   ← Para build local/dev
└── compose.pi.yml       ← Para o Pi (só pull da imagem)
```
