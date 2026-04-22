"""
Criptograma estilo Coquetel:
- Um tema/dica no topo
- Cada linha = uma palavra horizontal com dica textual
- Uma coluna comum em destaque → forma a palavra secreta verticalmente
- A palavra secreta responde ao tema
"""

import random
from words_pt import get_word_list

SYMBOL_POOL = [
    '◆', '▲', '★', '♠', '♣', '♥', '◉', '▼', '◈', '⬟',
    '⬡', '⬢', '◇', '△', '▽', '◁', '▷', '⬤', '⊕', '⊗',
    '⊘', '⊙', '⊛', '✦', '✧', '❖', '⬦', '⬧', '⬨', '⬩',
    '⬪', '⬫', '⬬', '⬭',
]

# Palavras secretas (tema → palavra). Só A-Z, sem acentos.
SECRETS = [
    {"theme": "Capital federal do Brasil",                    "word": "BRASILIA"},
    {"theme": "Maior mamífero terrestre do planeta",          "word": "ELEFANTE"},
    {"theme": "Valor fundamental das democracias",            "word": "LIBERDADE"},
    {"theme": "Inseto colorido que era lagarta",              "word": "BORBOLETA"},
    {"theme": "Festa popular mais famosa do Brasil",          "word": "CARNAVAL"},
    {"theme": "Grande corpo de água salgada",                 "word": "OCEANO"},
    {"theme": "Grande elevação natural do terreno",           "word": "MONTANHA"},
    {"theme": "Corpo celeste que orbita uma estrela",         "word": "PLANETA"},
    {"theme": "Corpo celeste luminoso no céu noturno",        "word": "ESTRELA"},
    {"theme": "Ritmo musical patrimônio cultural brasileiro", "word": "SAMBA"},
    {"theme": "Instrumento de cordas elétrico",               "word": "GUITARRA"},
    {"theme": "Ciência que cuida da saúde humana",            "word": "MEDICINA"},
    {"theme": "Primeiro mês do calendário",                   "word": "JANEIRO"},
    {"theme": "Sétima arte, indústria dos filmes",            "word": "CINEMA"},
    {"theme": "Grande extensão de árvores",                   "word": "FLORESTA"},
    {"theme": "Gênero literário em prosa longa",              "word": "ROMANCE"},
    {"theme": "Arte de criar imagens com tinta",              "word": "PINTURA"},
    {"theme": "Local onde se tratam os enfermos",             "word": "HOSPITAL"},
    {"theme": "Tubérculo base de muitas cozinhas",            "word": "BATATA"},
    {"theme": "Vertebrado aquático que respira por brânquias","word": "PEIXE"},
]


def _try_build(secret_obj, bank):
    """Tenta montar um criptograma para uma palavra secreta. Retorna None se falhar."""
    secret = secret_obj["word"]
    theme  = secret_obj["theme"]

    pool = [w for w in bank if w["word"] != secret and 4 <= len(w["word"]) <= 11]
    random.shuffle(pool)

    used = set()
    rows = []

    for letter in secret:
        candidates = [w for w in pool if letter in w["word"] and w["word"] not in used]
        if not candidates:
            return None
        # Prefere palavras menores para layout compacto, com alguma variedade
        candidates.sort(key=lambda w: len(w["word"]))
        pick_from = candidates[:max(4, len(candidates) // 2)]
        chosen = random.choice(pick_from)
        used.add(chosen["word"])

        # Escolhe uma ocorrência aleatória da letra
        positions = [i for i, ch in enumerate(chosen["word"]) if ch == letter]
        pos = random.choice(positions)

        rows.append({
            "word": chosen["word"],
            "clue": chosen["clue"],
            "highlight_pos": pos,
        })

    # Gera cifra única para TODAS as letras usadas (nas linhas + na secreta)
    all_letters = set(secret)
    for r in rows:
        all_letters.update(r["word"])

    letters = sorted(all_letters)
    if len(letters) > len(SYMBOL_POOL):
        return None

    symbols = random.sample(SYMBOL_POOL, len(letters))
    letter_to_symbol = dict(zip(letters, symbols))

    # Monta linhas de saída com símbolos + alinhamento
    out_rows = []
    for r in rows:
        row_symbols = [letter_to_symbol[ch] for ch in r["word"]]
        out_rows.append({
            "clue": r["clue"],
            "symbols": row_symbols,
            "highlight_idx": r["highlight_pos"],
            "word_length": len(r["word"]),
        })

    # Alinhamento vertical: todas as posições destacadas caem na mesma coluna
    max_left  = max(r["highlight_idx"] for r in out_rows)
    max_right = max(r["word_length"] - r["highlight_idx"] - 1 for r in out_rows)
    total_cols = max_left + 1 + max_right

    for r in out_rows:
        r["start_col"] = max_left - r["highlight_idx"]

    return {
        "theme":          theme,
        "secret_length":  len(secret),
        "total_cols":     total_cols,
        "highlight_col":  max_left,
        "rows":           out_rows,
        "symbols_used":   list(letter_to_symbol.values()),
        "mapping":        {v: k for k, v in letter_to_symbol.items()},
        "secret":         secret,
    }


def generate_cryptogram():
    bank = get_word_list()
    attempts = random.sample(SECRETS, len(SECRETS))
    for secret in attempts:
        for _ in range(4):  # algumas tentativas de randomização por secreta
            result = _try_build(secret, bank)
            if result:
                return result
    return {"error": "Não foi possível gerar o criptograma"}
