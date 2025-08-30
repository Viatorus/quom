from typing import List

from .token import Token
from .iterator import LineWrapIterator


class RemainingToken(Token):
    pass


def is_symbol(c: str) -> bool:
    return c in '+-*/%<>&!=?.,[]{}():|;~^'


def scan_for_remaining(tokens: List[Token], it: LineWrapIterator):
    start = it.copy()

    if is_symbol(it.curr):
        it.next()
        tokens.append(RemainingToken(start, it))
        return True

    # Stop on whitespace, quotes, comments, dot followed by a digit, or numeric after a symbol.
    while it.next() and not (it.curr in ' \t\v\f\n\r' or it.curr in '"\'' or (
            it.curr == '/' and it.lookahead in '/*') or (it.curr == '.' and it.lookahead.isnumeric()) or
                             it.curr.isnumeric() and is_symbol(it.prev)):
        pass
    tokens.append(RemainingToken(start, it))
    return True
