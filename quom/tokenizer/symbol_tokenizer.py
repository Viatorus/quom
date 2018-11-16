from enum import Enum

from quom.utils.iterable import Iterator
from .token import Token, TokenType


class SymbolType(Enum):
    UNDEFINED = 0


class SymbolToken(Token):
    def __init__(self, start, end, type: SymbolType):
        super().__init__(start, end, TokenType.SYMBOL)
        self.comment_type = type


def scan_for_symbol(it: Iterator, it_end: Iterator):
    if it[0] not in '+-*/.,:?%!=<>(){}[]&|':
        return

    start = it
    it += 1
    return SymbolToken(start, it, SymbolType.UNDEFINED)
