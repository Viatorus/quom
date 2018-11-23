from typing import List

from .token import Token, TokenType
from .iterator import LineWrapIterator


class RemainingToken(Token):
    def __init__(self, start, end):
        super().__init__(start, end, TokenType.REMAINING)


def scan_for_remaining(tokens: List[Token], it: LineWrapIterator):
    start = it.copy()
    # Stop on whitespace, quotes, comments and dot followed by a digit.
    while it.next() and not (it.curr in ' \t\v\f\n\r' or it.curr in '"\'' or (
            it.curr == '/' and it.lookahead in '/*') or it.curr == '.' and it.lookahead.isnumeric()):
        pass
    tokens.append(RemainingToken(start, it))
    return True
