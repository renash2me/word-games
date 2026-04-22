import random
from typing import List, Dict, Tuple, Optional

GRID_SIZE = 22
BLOCK = '#'


def create_grid() -> List[List[str]]:
    return [[BLOCK] * GRID_SIZE for _ in range(GRID_SIZE)]


def can_place(grid: List[List[str]], word: str, row: int, col: int, direction: str) -> bool:
    size = len(grid)
    length = len(word)

    # Boundary check
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
            # Check perpendicular neighbors for unintended adjacency
            if direction == 'H':
                if (r > 0 and grid[r - 1][c] != BLOCK) or \
                   (r < size - 1 and grid[r + 1][c] != BLOCK):
                    return False
            else:
                if (c > 0 and grid[r][c - 1] != BLOCK) or \
                   (c < size - 1 and grid[r][c + 1] != BLOCK):
                    return False
        else:
            return False  # Letter conflict

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


def generate_crossword(word_data: List[Dict], target: int = 12) -> Dict:
    words = sorted(word_data, key=lambda x: len(x['word']), reverse=True)

    best_grid = None
    best_placed = []

    for attempt in range(8):
        if attempt > 0:
            random.shuffle(words[1:min(30, len(words))])

        grid = create_grid()
        placed = []

        # Place first word
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

    # Trim grid to bounding box
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

    for pw in placed:
        pw['row'] -= min_r
        pw['col'] -= min_c

    # Assign clue numbers (top-to-bottom, left-to-right)
    start_positions = {}
    for pw in placed:
        key = (pw['row'], pw['col'])
        if key not in start_positions:
            start_positions[key] = []
        start_positions[key].append(pw['direction'])

    cell_numbers = {}
    for num, pos in enumerate(sorted(start_positions.keys()), 1):
        cell_numbers[pos] = num

    for pw in placed:
        pw['number'] = cell_numbers[(pw['row'], pw['col'])]

    clues_h = sorted([pw for pw in placed if pw['direction'] == 'H'],
                     key=lambda x: x['number'])
    clues_v = sorted([pw for pw in placed if pw['direction'] == 'V'],
                     key=lambda x: x['number'])

    return {
        'grid': trimmed,
        'rows': len(trimmed),
        'cols': len(trimmed[0]),
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
        'cell_numbers': {f"{r},{c}": n for (r, c), n in cell_numbers.items()}
    }
