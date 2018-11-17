from enum import Enum
from typing import List

from .token import Token, TokenType
from ..utils.iterable import Iterator


class SymbolType(Enum):
    UNDEFINED = 0


class SymbolToken(Token):
    def __init__(self, start, end, type: SymbolType):
        super().__init__(start, end, TokenType.SYMBOL)
        self.comment_type = type


def scan_for_symbol(tokens: List[Token], it: Iterator, it_end: Iterator):
    if it[0] not in '+-*/.,:?%!=<>(){}[]&|':
        return False
    start = it.copy()
    it += 1
    tokens.append(SymbolToken(start, it, SymbolType.UNDEFINED))
    return True
