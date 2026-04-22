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


def _try_column(secret, theme, pool, target_size, hl_col):
    """
    Tenta montar com todas as linhas tendo destaque na MESMA coluna hl_col.
    Para cada letra da secreta, procura uma palavra do tamanho alvo que
    tenha aquela letra exatamente na coluna hl_col.
    """
    used = set()
    rows = []

    for letter in secret:
        candidates = [w for w in pool
                      if w["word"] not in used
                      and w["word"][hl_col] == letter]
        if not candidates:
            return None
        chosen = random.choice(candidates)
        used.add(chosen["word"])
        rows.append({
            "word": chosen["word"],
            "clue": chosen["clue"],
            "highlight_pos": hl_col,
        })

    # Cifra única para todas as letras
    all_letters = set(secret)
    for r in rows:
        all_letters.update(r["word"])

    letters = sorted(all_letters)
    if len(letters) > len(SYMBOL_POOL):
        return None

    symbols = random.sample(SYMBOL_POOL, len(letters))
    letter_to_symbol = dict(zip(letters, symbols))

    out_rows = []
    for r in rows:
        out_rows.append({
            "clue":          r["clue"],
            "symbols":       [letter_to_symbol[ch] for ch in r["word"]],
            "highlight_idx": r["highlight_pos"],
        })

    return {
        "theme":         theme,
        "secret_length": len(secret),
        "word_size":     target_size,
        "highlight_col": hl_col,
        "rows":          out_rows,
        "symbols_used":  list(letter_to_symbol.values()),
        "mapping":       {v: k for k, v in letter_to_symbol.items()},
        "secret":        secret,
    }


def _try_build_with_size(secret_obj, bank, target_size):
    """
    Tenta montar um criptograma de tamanho fixo com coluna destacada única
    (todas as linhas compartilham a mesma coluna destacada → palavra secreta
    vertical perfeitamente alinhada).
    """
    secret = secret_obj["word"]
    theme  = secret_obj["theme"]

    pool = [w for w in bank if w["word"] != secret and len(w["word"]) == target_size]
    if not pool:
        return None

    # Tenta cada coluna possível, em ordem aleatória
    columns = list(range(target_size))
    random.shuffle(columns)

    for hl_col in columns:
        # Várias tentativas de randomização para cada coluna
        for _ in range(3):
            result = _try_column(secret, theme, pool, target_size, hl_col)
            if result:
                return result
    return None


def generate_cryptogram(word_size=7):
    """
    Gera criptograma com palavras todas do tamanho word_size.
    word_size: 7 (fácil), 8 (médio), 9 (difícil), 10 (expert).
    """
    if word_size not in (7, 8, 9, 10):
        word_size = 7

    bank = get_word_list()
    # Ordem de fallback se tamanho alvo falhar: tenta o exato, depois próximos
    fallback_order = [word_size]
    for delta in (1, -1, 2, -2):
        cand = word_size + delta
        if 6 <= cand <= 10 and cand not in fallback_order:
            fallback_order.append(cand)

    for target_size in fallback_order:
        attempts = random.sample(SECRETS, len(SECRETS))
        for secret in attempts:
            for _ in range(4):
                result = _try_build_with_size(secret, bank, target_size)
                if result:
                    return result
    return {"error": "Não foi possível gerar o criptograma"}
