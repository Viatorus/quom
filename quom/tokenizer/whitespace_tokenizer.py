from enum import Enum

from quom.utils.iterable import Iterator
from .token import Token, TokenType


class WhitespaceType(Enum):
    SPACE = 0
    LINE_BREAK = 1
    WRAPPED = 2


class WhitespaceToken(Token):
    def __init__(self, start, end, type: WhitespaceType):
        super().__init__(start, end, TokenType.WHITESPACE)
        self.whitespace_type = type


WHITESPACE_CHARACTERS = [' ', '\t', '\v', '\f']


def scan_for_whitespace(it: Iterator, it_end: Iterator):
    if it[0] in WHITESPACE_CHARACTERS:
        start = it
        while it != it_end and it[0] in WHITESPACE_CHARACTERS:
            it += 1

        return WhitespaceToken(start, it, WhitespaceType.SPACE)

    elif it[0] == '\n':
        start = it
        it += 1

        return WhitespaceToken(start, it, WhitespaceType.LINE_BREAK)
    return None
