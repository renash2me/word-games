"""
Palavras Cruzadas Diretas — gerador v11.

Arquitetura:
- layout_generator.py: cria grid com posições de clue-cells (#).
- solver.py (CSP com forward-checking + MRV): preenche os slots.
- dictionary.py, grid.py, slot.py, heuristics.py: apoio.

Este módulo orquestra e serializa no formato JSON que o frontend v10
espera (campos: grid, rows, cols, clues_across, clues_down,
cell_numbers, clue_cells, revealed).

Dificuldade (1-5) controla o grid:
  1: 10x8   2: 11x9   3: 13x10   4: 14x11   5: 16x11
"""
from __future__ import annotations

import random
import time
from typing import Dict, List, Optional, Tuple

from dictionary import Dictionary
from grid import extract_slots
from layout_generator import generate_layout
from solver import Solver


DIFFICULTY_DIMS = {
    1: (10, 8),
    2: (11, 9),
    3: (13, 10),
    4: (14, 11),
    5: (16, 11),
}


def _build_dictionary(word_data, min_len, max_len):
    clues_by_word = {}
    words = []
    for entry in word_data:
        w = entry['word'].upper()
        if not (min_len <= len(w) <= max_len):
            continue
        if w in clues_by_word:
            continue
        clues_by_word[w] = entry['clue']
        words.append(w)
    return Dictionary(words), clues_by_word


def _number_slots(solved_slots):
    starts = {}
    for s in solved_slots:
        starts[s.positions[0]] = None
    return {pos: num for num, pos in enumerate(sorted(starts.keys()), 1)}


def _direction(slot):
    """'H' se horizontal (row constante), 'V' se vertical."""
    (r0, _), (r1, _) = slot.positions[0], slot.positions[1]
    return 'H' if r0 == r1 else 'V'


def _build_clue_cells(grid, solved_slots, clues_by_word, cell_numbers):
    rows = len(grid)
    cols = len(grid[0])
    clue_cells = {}

    for s in solved_slots:
        r, c = s.positions[0]
        direction = _direction(s)
        if direction == 'H':
            cr, cc = r, c - 1
        else:
            cr, cc = r - 1, c
        if 0 <= cr < rows and 0 <= cc < cols and grid[cr][cc] == '#':
            key = (cr, cc)
            if key not in clue_cells:
                clue_cells[key] = {'row': cr, 'col': cc, 'h': None, 'v': None}
            side = 'h' if direction == 'H' else 'v'
            clue_cells[key][side] = {
                'num': cell_numbers.get((r, c)),
                'clue': clues_by_word.get(s.assigned, ''),
                'len': s.length,
            }

    return list(clue_cells.values())


def _choose_revealed(solved_slots, clues_by_word, cell_numbers):
    scored = []
    for s in solved_slots:
        num = cell_numbers.get(s.positions[0], 0)
        score = (len(s.crossings), s.length, -num)
        scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]
    r, c = best.positions[0]
    return {
        'num': cell_numbers.get((r, c)),
        'direction': _direction(best),
        'row': r,
        'col': c,
        'word': best.assigned,
        'clue': clues_by_word.get(best.assigned, ''),
    }


def generate_crossword(word_data, difficulty=1, max_attempts=8,
                       time_per_attempt=2.5, target=None):
    """Gera crossword Diretas. `target` é ignorado (compat v10)."""
    rows, cols = DIFFICULTY_DIMS.get(difficulty, DIFFICULTY_DIMS[1])
    min_len = 3
    max_len = min(max(rows, cols), 10)
    dictionary, clues_by_word = _build_dictionary(word_data, min_len, max_len)

    for attempt in range(max_attempts):
        grid_layout = generate_layout(rows=rows, cols=cols,
                                      min_len=3, max_len=min(6, max_len))
        if grid_layout is None:
            continue

        slots = extract_slots(grid_layout)
        if not slots:
            continue
        solver = Solver(slots, dictionary)
        result = solver.solve(max_time=time_per_attempt)

        if not all(s.assigned for s in result):
            continue

        final_grid = [row[:] for row in grid_layout]
        for s in result:
            for (r, c), letter in zip(s.positions, s.assigned):
                final_grid[r][c] = letter

        cell_numbers = _number_slots(result)

        clues_h = sorted(
            [s for s in result if _direction(s) == 'H'],
            key=lambda s: cell_numbers[s.positions[0]]
        )
        clues_v = sorted(
            [s for s in result if _direction(s) == 'V'],
            key=lambda s: cell_numbers[s.positions[0]]
        )

        clue_cells = _build_clue_cells(final_grid, result, clues_by_word, cell_numbers)
        revealed = _choose_revealed(result, clues_by_word, cell_numbers)

        return {
            'grid': final_grid,
            'rows': rows,
            'cols': cols,
            'clues_across': [
                {
                    'num': cell_numbers[s.positions[0]],
                    'clue': clues_by_word.get(s.assigned, ''),
                    'row': s.positions[0][0],
                    'col': s.positions[0][1],
                    'len': s.length,
                }
                for s in clues_h
            ],
            'clues_down': [
                {
                    'num': cell_numbers[s.positions[0]],
                    'clue': clues_by_word.get(s.assigned, ''),
                    'row': s.positions[0][0],
                    'col': s.positions[0][1],
                    'len': s.length,
                }
                for s in clues_v
            ],
            'cell_numbers': {f'{r},{c}': n for (r, c), n in cell_numbers.items()},
            'clue_cells': clue_cells,
            'revealed': revealed,
            'difficulty': difficulty,
        }

    return {'error': 'Failed to generate crossword (Diretas)'}


if __name__ == '__main__':
    from words_pt import get_word_list
    bank = get_word_list()
    print(f'Banco: {len(bank)} palavras\n')

    for diff in [1, 2, 3]:
        rows, cols = DIFFICULTY_DIMS[diff]
        print(f'═══ DIFICULDADE {diff} — {cols}×{rows} ═══')
        success = 0
        times = []
        sample = None
        for i in range(5):
            random.seed(i * 17 + diff)
            t0 = time.perf_counter()
            r = generate_crossword(bank, difficulty=diff, max_attempts=6)
            dt = time.perf_counter() - t0
            times.append(dt)
            if 'error' in r:
                print(f'  [{i}] ERRO em {dt:.1f}s')
                continue
            success += 1
            if sample is None:
                sample = r
            n_h = len(r['clues_across'])
            n_v = len(r['clues_down'])
            n_cc = len(r['clue_cells'])
            rev = r['revealed']
            print(f"  [{i}] ✓ rev={rev['word']:<10} ({rev['direction']}) | "
                  f"{n_h}H+{n_v}V | {n_cc} clue-cells | {dt:.2f}s")
        print(f'  → {success}/5 | média {sum(times)/len(times):.2f}s')
        print()

        if diff == 1 and sample:
            print('  Exemplo grid:')
            for row in sample['grid']:
                print('    ' + ' '.join('■' if c == '#' else c for c in row))
            print(f"  Revelada: {sample['revealed']['word']} = \"{sample['revealed']['clue']}\"")
            print(f"  Célula-dica exemplo: {sample['clue_cells'][0]}")
            print()
