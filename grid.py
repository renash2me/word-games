from slot import Slot

def extract_slots(grid):
    slots = []
    rows = len(grid)
    cols = len(grid[0])

    for r in range(rows):
        c = 0
        while c < cols:
            if grid[r][c] == '#':
                c += 1
                continue
            start = c
            while c < cols and grid[r][c] != '#':
                c += 1
            if c - start >= 3:
                slots.append(Slot([(r, i) for i in range(start, c)]))

    for c in range(cols):
        r = 0
        while r < rows:
            if grid[r][c] == '#':
                r += 1
                continue
            start = r
            while r < rows and grid[r][c] != '#':
                r += 1
            if r - start >= 3:
                slots.append(Slot([(i, c) for i in range(start, r)]))

    build_crossings(slots)
    return slots

def build_crossings(slots):
    for s1 in slots:
        for s2 in slots:
            if s1 is s2:
                continue
            for i, p1 in enumerate(s1.positions):
                for j, p2 in enumerate(s2.positions):
                    if p1 == p2:
                        s1.crossings.append((s2, i, j))
