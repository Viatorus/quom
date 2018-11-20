from enum import Enum
from typing import List

from .token import Token, TokenType
from quom.tokenizer.iterator import Iterator


class WhitespaceType(Enum):
    SPACE = 0
    LINE_BREAK = 1
    WRAPPED = 2


class WhitespaceToken(Token):
    def __init__(self, start, end, whitespace_type: WhitespaceType):
        super().__init__(start, end, TokenType.WHITESPACE)
        self.whitespace_type = whitespace_type

0
WHITESPACE_CHARACTERS = ' \t\v\f'


def scan_for_whitespace(tokens: List[Token], it: Iterator, it_end: Iterator):
    if it[0] in WHITESPACE_CHARACTERS:
        start = it.copy()
        it += 1
        while it != it_end and it[0] in WHITESPACE_CHARACTERS:
            it += 1

        tokens.append(WhitespaceToken(start, it, WhitespaceType.SPACE))
        return True
    elif it[0] == '\n':
        start = it.copy()
        it += 1

        tokens.append(WhitespaceToken(start, it, WhitespaceType.LINE_BREAK))
        return True
    return False
