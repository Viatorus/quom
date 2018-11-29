from typing import List

from .iterator import LineWrapIterator
from .token import Token


class WhitespaceToken(Token):
    pass


class WhitespaceWhitespaceToken(WhitespaceToken):
    pass


class LinebreakWhitespaceToken(WhitespaceToken):
    pass


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
