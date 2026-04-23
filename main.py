from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from words_pt import get_word_list
from crossword import generate_crossword
from cryptogram import generate_cryptogram

app = FastAPI(title="Jogos de Palavras")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        with open("static/index.html", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>static/index.html not found</h1>", status_code=404)


@app.get("/api/crossword")
def api_crossword(difficulty: int = 1):
    words = get_word_list()
    difficulty = max(1, min(5, difficulty))
    result = generate_crossword(words, difficulty=difficulty)
    return JSONResponse(result)


@app.get("/api/cryptogram")
def api_cryptogram(size: int = 7):
    result = generate_cryptogram(word_size=size)
    return JSONResponse(result)


@app.get("/health")
def health():
    return {"status": "ok"}
