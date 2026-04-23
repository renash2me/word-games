"""
Gerador de palavras cruzadas estilo Coquetel Diretas.

Mantém o algoritmo clássico (backtracking greedy) do v9, que é rápido e
confiável. As mudanças estão em como apresentamos o resultado ao frontend:

- Uma palavra é escolhida como REVELADA (âncora inicial para o jogador).
  Preferimos a palavra com mais cruzamentos, pois suas letras aparecem em
  mais palavras perpendiculares, distribuindo dicas indiretas.

- Cada bloco preto que fica IMEDIATAMENTE à esquerda de uma H ou acima de
  uma V vira uma "célula-dica" (clue_cell). Essas células não têm letra;
  carregam a dica da(s) palavra(s) que começa(m) depois delas.

- Células pretas "mortas" (sem palavra começando ao lado/abaixo) são
  reportadas como padding; o frontend pode escondê-las ou pintá-las
  igual ao fundo para dar o efeito "grid totalmente preenchido".

Formato do grid: retangular (trimado a partir do 22x22 inicial).
Palavras: tamanhos variados de 3 a 10 letras (vindos do banco).
"""
import random
from typing import List, Dict, Tuple, Optional

GRID_SIZE = 22
BLOCK = '#'


def create_grid() -> List[List[str]]:
    return [[BLOCK] * GRID_SIZE for _ in range(GRID_SIZE)]


def can_place(grid: List[List[str]], word: str, row: int, col: int, direction: str) -> bool:
    size = len(grid)
    length = len(word)

    # Boundary + separation checks
    if direction == 'H':
        if row < 0 or row >= size or col < 0 or col + length > size:
            return False
        if col > 0 and grid[row][col - 1] != BLOCK:
            return False
        if col + length < size and grid[row][col + length] != BLOCK:
            return False
    else:
        if col < 0 or col >= size or row < 0 or row + length > size:
            return False
        if row > 0 and grid[row - 1][col] != BLOCK:
            return False
        if row + length < size and grid[row + length][col] != BLOCK:
            return False

    has_intersection = False
    for i, letter in enumerate(word):
        r = row + (i if direction == 'V' else 0)
        c = col + (0 if direction == 'V' else i)
        cell = grid[r][c]

        if cell == letter:
            has_intersection = True
        elif cell == BLOCK:
            # Check perpendicular neighbors to prevent unintended adjacency
            if direction == 'H':
                if (r > 0 and grid[r - 1][c] != BLOCK) or \
                   (r < size - 1 and grid[r + 1][c] != BLOCK):
                    return False
            else:
                if (c > 0 and grid[r][c - 1] != BLOCK) or \
                   (c < size - 1 and grid[r][c + 1] != BLOCK):
                    return False
        else:
            return False  # letter conflict

    return has_intersection


def place_word(grid: List[List[str]], word: str, row: int, col: int, direction: str):
    for i, letter in enumerate(word):
        r = row + (i if direction == 'V' else 0)
        c = col + (0 if direction == 'V' else i)
        grid[r][c] = letter


def find_placements(grid: List[List[str]], placed: List[Dict], word: str) -> List[Tuple]:
    placements = []
    seen = set()

    for pw in placed:
        pw_word = pw['word']
        pw_row = pw['row']
        pw_col = pw['col']
        pw_dir = pw['direction']

        for i, pl in enumerate(pw_word):
            for j, wl in enumerate(word):
                if pl != wl:
                    continue

                if pw_dir == 'H':
                    nr, nc, nd = pw_row - j, pw_col + i, 'V'
                else:
                    nr, nc, nd = pw_row + i, pw_col - j, 'H'

                key = (nr, nc, nd)
                if key not in seen and can_place(grid, word, nr, nc, nd):
                    placements.append(key)
                    seen.add(key)

    return placements


def _count_crossings(pw: Dict, placed: List[Dict]) -> int:
    """Conta quantas palavras cruzam pw."""
    count = 0
    for i, _ in enumerate(pw['word']):
        r = pw['row'] + (i if pw['direction'] == 'V' else 0)
        c = pw['col'] + (0 if pw['direction'] == 'V' else i)
        for other in placed:
            if other is pw:
                continue
            if other['direction'] == pw['direction']:
                continue
            # Other é perpendicular; verifica se ocupa (r, c)
            for j in range(len(other['word'])):
                orr = other['row'] + (j if other['direction'] == 'V' else 0)
                occ = other['col'] + (0 if other['direction'] == 'V' else j)
                if orr == r and occ == c:
                    count += 1
                    break
    return count


def generate_crossword(word_data: List[Dict], target: int = 12) -> Dict:
    words = sorted(word_data, key=lambda x: len(x['word']), reverse=True)

    best_grid = None
    best_placed = []

    for attempt in range(8):
        if attempt > 0:
            random.shuffle(words[1:min(30, len(words))])

        grid = create_grid()
        placed = []

        # Place first word at center
        first = words[0]
        fw = first['word']
        first_dir = random.choice(['H', 'V'])
        if first_dir == 'H':
            fr = GRID_SIZE // 2
            fc = (GRID_SIZE - len(fw)) // 2
        else:
            fr = (GRID_SIZE - len(fw)) // 2
            fc = GRID_SIZE // 2

        place_word(grid, fw, fr, fc, first_dir)
        placed.append({**first, 'row': fr, 'col': fc, 'direction': first_dir})

        for wd in words[1:]:
            if len(placed) >= target:
                break
            placements = find_placements(grid, placed, wd['word'])
            if placements:
                random.shuffle(placements)
                r, c, d = placements[0]
                place_word(grid, wd['word'], r, c, d)
                placed.append({**wd, 'row': r, 'col': c, 'direction': d})

        if len(placed) > len(best_placed):
            best_placed = placed
            best_grid = [row[:] for row in grid]

        if len(best_placed) >= target:
            break

    if best_grid is None or not best_placed:
        return {"error": "Failed to generate crossword"}

    grid = best_grid
    placed = best_placed

    # Trim grid to bounding box with 1 cell of padding
    min_r = min_c = GRID_SIZE
    max_r = max_c = 0
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] != BLOCK:
                min_r, max_r = min(min_r, r), max(max_r, r)
                min_c, max_c = min(min_c, c), max(max_c, c)

    pad = 1
    min_r = max(0, min_r - pad)
    min_c = max(0, min_c - pad)
    max_r = min(GRID_SIZE - 1, max_r + pad)
    max_c = min(GRID_SIZE - 1, max_c + pad)

    trimmed = [[grid[r][c] for c in range(min_c, max_c + 1)]
               for r in range(min_r, max_r + 1)]
    rows_n = len(trimmed)
    cols_n = len(trimmed[0])

    for pw in placed:
        pw['row'] -= min_r
        pw['col'] -= min_c

    # ─── Numeração das palavras (top-to-bottom, left-to-right) ───
    start_positions = {}
    for pw in placed:
        key = (pw['row'], pw['col'])
        start_positions.setdefault(key, []).append(pw['direction'])

    cell_numbers = {}
    for num, pos in enumerate(sorted(start_positions.keys()), 1):
        cell_numbers[pos] = num

    for pw in placed:
        pw['number'] = cell_numbers[(pw['row'], pw['col'])]

    # ─── Escolhe a palavra REVELADA (mais cruzamentos) ───
    # Desempate: palavra mais longa > número mais baixo
    scored = [(pw, _count_crossings(pw, placed)) for pw in placed]
    scored.sort(key=lambda x: (-x[1], -len(x[0]['word']), x[0]['number']))
    revealed_word = scored[0][0]
    revealed_key = (revealed_word['number'], revealed_word['direction'])

    # ─── Calcula células-dica ───
    # Uma célula (r,c) é célula-dica se:
    #   - É BLOCK no trimmed, E
    #   - existe uma palavra H começando em (r, c+1) OU uma V começando em (r+1, c)
    # A célula-dica carrega as dicas dessas palavras.
    clue_cells: Dict[Tuple[int, int], Dict] = {}
    for pw in placed:
        r, c = pw['row'], pw['col']
        if pw['direction'] == 'H':
            # Célula-dica fica à esquerda (r, c-1)
            cr, cc = r, c - 1
        else:
            cr, cc = r - 1, c
        if 0 <= cr < rows_n and 0 <= cc < cols_n and trimmed[cr][cc] == BLOCK:
            key = (cr, cc)
            clue_cells.setdefault(key, {"h": None, "v": None, "row": cr, "col": cc})
            side = 'h' if pw['direction'] == 'H' else 'v'
            clue_cells[key][side] = {
                "num": pw['number'],
                "clue": pw['clue'],
                "len": len(pw['word']),
            }

    # ─── Monta a saída ───
    clues_h = sorted([pw for pw in placed if pw['direction'] == 'H'],
                     key=lambda x: x['number'])
    clues_v = sorted([pw for pw in placed if pw['direction'] == 'V'],
                     key=lambda x: x['number'])

    return {
        'grid': trimmed,
        'rows': rows_n,
        'cols': cols_n,
        'clues_across': [
            {'num': pw['number'], 'clue': pw['clue'],
             'row': pw['row'], 'col': pw['col'], 'len': len(pw['word'])}
            for pw in clues_h
        ],
        'clues_down': [
            {'num': pw['number'], 'clue': pw['clue'],
             'row': pw['row'], 'col': pw['col'], 'len': len(pw['word'])}
            for pw in clues_v
        ],
        'cell_numbers': {f"{r},{c}": n for (r, c), n in cell_numbers.items()},
        # ── Campos novos estilo Coquetel Diretas ──
        'clue_cells': [
            {
                'row': info['row'],
                'col': info['col'],
                'h': info['h'],   # {num, clue, len} ou None
                'v': info['v'],   # {num, clue, len} ou None
            }
            for info in clue_cells.values()
        ],
        'revealed': {
            'num': revealed_word['number'],
            'direction': revealed_word['direction'],
            'row': revealed_word['row'],
            'col': revealed_word['col'],
            'word': revealed_word['word'],
            'clue': revealed_word['clue'],
        },
    }


if __name__ == "__main__":
    import time
    from words_pt import get_word_list
    # Performance test
    times = []
    for i in range(10):
        bank = get_word_list()
        t0 = time.perf_counter()
        result = generate_crossword(bank, target=12)
        dt = time.perf_counter() - t0
        times.append(dt)
        if 'error' in result:
            print(f'[{i}] ERRO: {result["error"]}')
        else:
            nh = len(result['clues_across'])
            nv = len(result['clues_down'])
            ncc = len(result['clue_cells'])
            rev = result['revealed']
            print(f'[{i}] {result["rows"]}x{result["cols"]} | '
                  f'{nh}H + {nv}V | {ncc} células-dica | '
                  f'revelada: {rev["word"]} ({rev["direction"]}) | '
                  f'{dt*1000:.0f}ms')
    print(f'\nMédia: {sum(times)/len(times)*1000:.0f}ms | '
          f'Max: {max(times)*1000:.0f}ms')
