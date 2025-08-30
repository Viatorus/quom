from typing import List

from .token import Token
from .iterator import LineWrapIterator


class SymbolToken(Token):
    pass


def is_symbol(c: str) -> bool:
    return c in '+-*/%<>&!=?.,[]{}():|;~^'


def scan_for_symbol(tokens: List[Token], it: LineWrapIterator):
    if not is_symbol(it.curr):
        return None

    start = it.copy()
    while it.next() and is_symbol(it.curr):
        pass

    tokens.append(SymbolToken(start, it))
    return True
