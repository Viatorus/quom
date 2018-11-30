from .iterator import Span, RawIterator


class Token:
    def __init__(self, start, end):
        self.start = start.copy() if start else None
        self.end = end.copy() if end else None

    @property
    def raw(self):
        return str(Span(RawIterator(self.start), RawIterator(self.end))) if self.start else ''

    def __str__(self):
        return str(Span(self.start, self.end)) if self.start else ''
