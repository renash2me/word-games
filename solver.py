import random
import time

from heuristics import select_slot, score_grid


class Solver:
    def __init__(self, slots, dictionary):
        self.slots = slots
        self.dictionary = dictionary
        self._initial_domains = {
            id(s): dictionary.get_words(s.length) for s in slots
        }

    def reset(self):
        for s in self.slots:
            s.domain = list(self._initial_domains[id(s)])
            s.assigned = None

    def consistent(self, slot, word):
        for other, i, j in slot.crossings:
            if other.assigned and word[i] != other.assigned[j]:
                return False
        return True

    def forward_check(self, slot, word):
        removed = []
        for other, i, j in slot.crossings:
            if other.is_filled():
                continue
            new_domain = [w for w in other.domain if w[j] == word[i]]
            if not new_domain:
                for s, d in removed:
                    s.domain = d
                return None
            removed.append((other, other.domain))
            other.domain = new_domain
        return removed

    def restore(self, removed):
        for slot, domain in removed:
            slot.domain = domain

    def backtrack(self, deadline=None):
        if deadline and time.time() > deadline:
            return False
        if all(s.is_filled() for s in self.slots):
            return True

        slot = select_slot(self.slots)
        if slot is None:
            return True
        words = list(slot.domain)
        random.shuffle(words)

        for word in words[:50]:
            if not self.consistent(slot, word):
                continue

            slot.assigned = word
            removed = self.forward_check(slot, word)

            if removed is not None:
                if self.backtrack(deadline):
                    return True
                self.restore(removed)

            slot.assigned = None

        return False

    def solve(self, max_time=10):
        start = time.time()
        deadline = start + max_time
        best_filled = 0
        best_snapshot = None

        while time.time() < deadline:
            self.reset()
            success = self.backtrack(deadline)
            filled = sum(1 for s in self.slots if s.is_filled())

            if filled > best_filled:
                best_filled = filled
                best_snapshot = [(id(s), s.assigned) for s in self.slots]

            if success:
                return self.slots

        if best_snapshot:
            by_id = {id(s): s for s in self.slots}
            for sid, assigned in best_snapshot:
                by_id[sid].assigned = assigned
        return self.slots
