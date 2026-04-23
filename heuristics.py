def select_slot(slots):
    candidates = [s for s in slots if not s.is_filled()]
    if not candidates:
        return None
    return min(candidates, key=lambda s: len(s.domain))

def score_grid(slots):
    filled = sum(1 for s in slots if s.is_filled())
    total = len(slots)
    penalty = sum(5 for s in slots if not s.domain)
    return (filled / total) * 100 - penalty
