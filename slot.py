class Slot:
    def __init__(self, positions):
        self.positions = positions
        self.length = len(positions)
        self.domain = []
        self.assigned = None
        self.crossings = []

    def is_filled(self):
        return self.assigned is not None

    def __repr__(self):
        return f"<Slot len={self.length} filled={self.assigned is not None}>"
