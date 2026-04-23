"""Layout v2 - greedy com would-violate check."""
import random
from typing import List, Optional

MIN_LEN = 3
MAX_LEN = 6


def run_length_at(grid, r, c, direction, rows, cols):
    if grid[r][c] == '#':
        return 0
    if direction == 'H':
        l = c
        while l > 0 and grid[r][l-1] == '.':
            l -= 1
        rt = c
        while rt < cols-1 and grid[r][rt+1] == '.':
            rt += 1
        return rt - l + 1
    else:
        u = r
        while u > 0 and grid[u-1][c] == '.':
            u -= 1
        d = r
        while d < rows-1 and grid[d+1][c] == '.':
            d += 1
        return d - u + 1


def would_violate(grid, r, c, rows, cols, min_len, max_len):
    """Marcar (r,c) como '#' cria algum run em (0, min_len) excluindo 1?"""
    l_run = 0
    cc = c - 1
    while cc >= 0 and grid[r][cc] == '.':
        l_run += 1
        cc -= 1
    r_run = 0
    cc = c + 1
    while cc < cols and grid[r][cc] == '.':
        r_run += 1
        cc += 1
    if 0 < l_run < min_len and l_run != 1:
        return True
    if 0 < r_run < min_len and r_run != 1:
        return True

    u_run = 0
    rr = r - 1
    while rr >= 0 and grid[rr][c] == '.':
        u_run += 1
        rr -= 1
    d_run = 0
    rr = r + 1
    while rr < rows and grid[rr][c] == '.':
        d_run += 1
        rr += 1
    if 0 < u_run < min_len and u_run != 1:
        return True
    if 0 < d_run < min_len and d_run != 1:
        return True
    return False


def _has_valid_perp(grid, r, c, direction, rows, cols, min_len, max_len):
    if direction == 'H':
        l = c
        while l > 0 and grid[r][l-1] == '.':
            l -= 1
        rt = c
        while rt < cols-1 and grid[r][rt+1] == '.':
            rt += 1
        length = rt - l + 1
    else:
        u = r
        while u > 0 and grid[u-1][c] == '.':
            u -= 1
        d = r
        while d < rows-1 and grid[d+1][c] == '.':
            d += 1
        length = d - u + 1
    return min_len <= length <= max_len


def validate_final(grid, rows, cols, min_len, max_len):
    # H
    for r in range(rows):
        c = 0
        while c < cols:
            if grid[r][c] == '#':
                c += 1; continue
            start = c
            while c < cols and grid[r][c] == '.':
                c += 1
            length = c - start
            if length == 1:
                if not _has_valid_perp(grid, r, start, 'V', rows, cols, min_len, max_len):
                    return False
            elif not (min_len <= length <= max_len):
                return False
    # V
    for c in range(cols):
        r = 0
        while r < rows:
            if grid[r][c] == '#':
                r += 1; continue
            start = r
            while r < rows and grid[r][c] == '.':
                r += 1
            length = r - start
            if length == 1:
                if not _has_valid_perp(grid, start, c, 'H', rows, cols, min_len, max_len):
                    return False
            elif not (min_len <= length <= max_len):
                return False
    return True


def generate_layout(rows=10, cols=8, target_clue_ratio=0.18,
                    min_len=MIN_LEN, max_len=MAX_LEN, max_attempts=500):
    for attempt in range(max_attempts):
        grid = [['.' for _ in range(cols)] for _ in range(rows)]
        candidates = [(r, c) for r in range(rows) for c in range(cols)]
        random.shuffle(candidates)

        target_clues = int(rows * cols * target_clue_ratio)
        placed = 0

        for (r, c) in candidates:
            if grid[r][c] == '#':
                continue
            h_run = run_length_at(grid, r, c, 'H', rows, cols)
            v_run = run_length_at(grid, r, c, 'V', rows, cols)
            needs_break = h_run > max_len or v_run > max_len

            if not needs_break and placed >= target_clues:
                continue

            if would_violate(grid, r, c, rows, cols, min_len, max_len):
                continue

            grid[r][c] = '#'
            placed += 1

        if validate_final(grid, rows, cols, min_len, max_len):
            return grid

    return None


def render(grid):
    return '\n'.join(' '.join('■' if c == '#' else '·' for c in row)
                     for row in grid)


def count_slots(grid, min_len, max_len):
    rows = len(grid); cols = len(grid[0])
    count = 0
    by_len = {}
    for r in range(rows):
        c = 0
        while c < cols:
            if grid[r][c] == '#':
                c += 1; continue
            start = c
            while c < cols and grid[r][c] == '.':
                c += 1
            l = c - start
            if min_len <= l <= max_len:
                count += 1
                by_len[l] = by_len.get(l, 0) + 1
    for c in range(cols):
        r = 0
        while r < rows:
            if grid[r][c] == '#':
                r += 1; continue
            start = r
            while r < rows and grid[r][c] == '.':
                r += 1
            l = r - start
            if min_len <= l <= max_len:
                count += 1
                by_len[l] = by_len.get(l, 0) + 1
    return count, by_len


if __name__ == '__main__':
    random.seed(1)
    ok = 0
    for i in range(10):
        g = generate_layout(rows=10, cols=8)
        if g:
            ok += 1
            n, by_len = count_slots(g, MIN_LEN, MAX_LEN)
            print(f'[{i}] {n} slots, dist={by_len}')
            print(render(g))
            print()
    print(f'{ok}/10 sucessos')
