from enum import Enum
from typing import List

from .iterator import CodeIterator, Span
from .token import Token, TokenType


class WhitespaceType(Enum):
    SPACE = 0
    LINE_BREAK = 1
    WRAPPED = 2


class WhitespaceToken(Token):
    def __init__(self, it, whitespace_type: WhitespaceType):
        super().__init__(it, TokenType.WHITESPACE)
        self.whitespace_type = whitespace_type


WHITESPACE_CHARACTERS = ' \t\v\f'


def scan_for_whitespace(tokens: List[Token], it: CodeIterator):
    if it.curr in WHITESPACE_CHARACTERS:
        start = it.copy()
        while next(it, None) and it.curr in WHITESPACE_CHARACTERS:
            pass

        tokens.append(WhitespaceToken(Span(start, it), WhitespaceType.SPACE))
        return True
    elif it.curr == '\n':
        start = it.copy()
        next(it, None)

        tokens.append(WhitespaceToken(Span(start, it), WhitespaceType.LINE_BREAK))
        return True
    return False
