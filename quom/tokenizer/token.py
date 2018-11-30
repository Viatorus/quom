from .iterator import Span


class Token:
    def __init__(self, start, end):
        self.start = start.copy() if start else None
        self.end = end.copy() if end else None

    def __str__(self):
        return str(Span(self.start, self.end)) if self.start else ''
