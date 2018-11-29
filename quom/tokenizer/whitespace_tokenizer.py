from typing import List

from .iterator import LineWrapIterator
from .token import Token


class WhitespaceToken(Token):
    def __init__(self, start, end):
        super().__init__(start, end)


class WhitespaceWhitespaceToken(WhitespaceToken):
    def __init__(self, start, end):
        super().__init__(start, end)


class LinebreakWhitespaceToken(WhitespaceToken):
    def __init__(self, start, end, ):
        super().__init__(start, end)


WHITESPACE_CHARACTERS = ' \t\v\f'


def scan_for_whitespace(tokens: List[Token], it: LineWrapIterator):
    if it.curr in WHITESPACE_CHARACTERS:
        start = it.copy()
        while it.next() and it.curr in WHITESPACE_CHARACTERS:
            pass

        tokens.append(WhitespaceWhitespaceToken(start, it))
        return True
    elif it.curr in '\n\r':
        start = it.copy()
        it.next()

        if it.prev == '\r' and it.curr == '\n':
            it.next()

        tokens.append(LinebreakWhitespaceToken(start, it))
        return True
    return False
