from .iterator import Span, RawIterator


class Token:
    def __init__(self, start, end):
        self.start = start.copy()
        self.end = end.copy()

    @property
    def raw(self):
        return str(Span(RawIterator(self.start), RawIterator(self.end)))

    def __str__(self):
        return str(Span(self.start, self.end))


class StartToken(Token):
    pass


class EndToken(Token):
    pass
