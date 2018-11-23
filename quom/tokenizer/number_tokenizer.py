from enum import Enum
from typing import List

from .token import Token, TokenType
from .iterator import LineWrapIterator


class NumberType(Enum):
    DECIMAL = 0,
    OCTAL = 1
    HEX = 2
    BINARY = 3


class NumberToken(Token):
    def __init__(self, start, end):
        super().__init__(start, end, TokenType.NUMBER)


def scan_for_number(tokens: List[Token], it: LineWrapIterator):
    if not it.curr.isdigit() and (it.curr != '.' or not it.lookahead.isdigit()):
        return False
    start = it.copy()

    # Parse until not
    # * alphanumeric, _, .
    # * ' followed by another '
    # * ' followed by an alphanumeric and _
    while it.next() and (it.curr.isalnum() or it.curr in '_+-.' or (
            it.curr == '\'' and (it.lookahead == '\'' or it.lookahead.isalnum() or it.lookahead in '_.'))):
        pass

    tokens.append(NumberToken(start, it))
    return True
