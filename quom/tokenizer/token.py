from .iterator import Span


class Token:
    def __init__(self, start, end):
        self.span = Span(start, end) if start and end else None

    def __str__(self):
        return str(self.span)
