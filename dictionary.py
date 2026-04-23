from collections import defaultdict

class Dictionary:
    def __init__(self, words):
        self.by_length = defaultdict(list)
        for w in words:
            w = w.strip().upper()
            if len(w) >= 3:
                self.by_length[len(w)].append(w)

    def get_words(self, length):
        return list(self.by_length[length])
