import random

SYMBOL_POOL = [
    '◆', '▲', '★', '♠', '♣', '♥', '◉', '▼', '◈', '⬟',
    '⬡', '⬢', '◇', '△', '▽', '◁', '▷', '⬤', '⊕', '⊗',
    '⊘', '⊙', '⊛', '✦', '✧', '❖', '⬦', '⬧', '⬨', '⬩',
    '⬪', '⬫', '⬬', '⬭',
]

PHRASES = [
    "QUEM NAO ARRISCA NAO PETISCA",
    "AGUAS PASSADAS NAO MOVEM MOINHOS",
    "DEVAGAR SE VAI AO LONGE",
    "EM TERRA DE CEGO QUEM TEM UM OLHO E REI",
    "MAIS VALE UM PASSARO NA MAO QUE DOIS VOANDO",
    "CADA CABECA UMA SENTENCA",
    "ANTES TARDE DO QUE NUNCA",
    "A ESPERANCA E A ULTIMA QUE MORRE",
    "CASA DE FERREIRO ESPETO DE PAU",
    "EM BOCA FECHADA NAO ENTRA MOSCA",
    "A PRESSA E INIMIGA DA PERFEICAO",
    "O SILENCIO VALE MAIS DO QUE MIL PALAVRAS",
    "O AMOR MOVE O MUNDO",
    "FILHO DE PEIXE PEIXINHO E",
    "QUEM TUDO QUER TUDO PERDE",
    "NAO DEIXE PARA AMANHA O QUE PODE FAZER HOJE",
    "O SABER NAO OCUPA LUGAR",
    "BURRO VELHO NAO APRENDE LINGUA",
    "DEUS AJUDA QUEM CEDO MADRUGA",
    "A UNIAO FAZ A FORCA",
    "QUEM SEMEIA VENTO COLHE TEMPESTADE",
    "AGUA MOLE EM PEDRA DURA TANTO BAT ATE QUE FURA",
    "NAO E SO DE PAO QUE VIVE O HOMEM",
    "A OCASIAO FAZ O LADRAO",
    "OLHO POR OLHO DENTE POR DENTE",
]


def generate_cryptogram() -> dict:
    phrase = random.choice(PHRASES)
    words = phrase.split()

    # Unique letters in phrase
    letters = sorted(set(ch for ch in phrase if ch != ' '))

    if len(letters) > len(SYMBOL_POOL):
        letters = letters[:len(SYMBOL_POOL)]

    # Random symbol assignment
    symbols = random.sample(SYMBOL_POOL, len(letters))
    letter_to_symbol = dict(zip(letters, symbols))
    symbol_to_letter = {v: k for k, v in letter_to_symbol.items()}

    # Encode phrase
    encoded_words = []
    for word in words:
        encoded_words.append([letter_to_symbol[ch] for ch in word if ch in letter_to_symbol])

    # One free hint: pick a common letter (E, A, O) if available, else random
    common = [l for l in ['E', 'A', 'O', 'S', 'R'] if l in letter_to_symbol]
    hint_letter = random.choice(common) if common else random.choice(letters)
    hint_symbol = letter_to_symbol[hint_letter]

    return {
        'phrase': phrase,
        'encoded_words': encoded_words,
        'mapping': symbol_to_letter,   # symbol → letter (used for checking)
        'symbols_used': list(letter_to_symbol.values()),
        'hint': {'symbol': hint_symbol, 'letter': hint_letter},
    }
