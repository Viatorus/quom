from enum import Enum
from typing import List

from .iterator import RawIterator, LineWrapIterator
from .token import Token, TokenType
from .tokenize_error import TokenizeError


class QuoteType(Enum):
    SINGLE = 0
    Double = 1


class QuoteToken(Token):
    def __init__(self, start, end, quote_type: QuoteType, raw_encdoing):
        super().__init__(start, end, TokenType.QUOTE)
        self.quote_type = quote_type
        self.raw_encoding = raw_encdoing


def is_raw_encoding(token: Token):
    if token.token_type == TokenType.REMAINING:
        return str(token) in ['R', 'u8R', 'LR', 'uR', 'UR']
    return False


def scan_for_quote_single(tokens: List[Token], it: LineWrapIterator):
    if it.curr != '\'':
        return False
    start = it.copy()

    # Parse until non escaped '.
    backslashes = 0
    while it.next() and (it.curr != '\'' or backslashes % 2 != 0):
        if it.curr == '\\':
            backslashes += 1
        else:
            backslashes = 0

    # Check if end of file is reached.
    if it.curr != '\'':
        raise TokenizeError("Character sequence not terminated!", it)
    it.next()

    tokens.append(QuoteToken(start, it, QuoteType.SINGLE, False))
    return True


def scan_for_quote_double(tokens: List[Token], it: LineWrapIterator):
    if it.curr != '"':
        return None
    start = it.copy()

    raw_encoding = is_raw_encoding(tokens[-1])
    if not raw_encoding:
        # Parse until end of line or non escaped ".
        backslashes = 0
        while it.next() and (it.curr != '"' or backslashes % 2 != 0):
            if it.curr == '\\':
                backslashes += 1
            else:
                backslashes = 0

        # Check if end of file is reached.
        if it.curr != '"':
            raise TokenizeError("Character sequence not terminated!", it)
        it.next()
    else:
        delimiter = ""

        # Parse until end of introductory delimiter.
        while it.next() and it.curr != '(' and it.curr:
            delimiter += it.curr

        if it.curr != '(':
            raise TokenizeError('No introductory delimiter inside raw string literal found!', it)

        # Define terminating delimiter.
        delimiter = ')' + delimiter + '"'
        it = RawIterator(it)

        # Parse until delimiter occours again.
        # TODO: Please optimize me.
        string = ''
        while it.next():
            string += it.curr
            if len(string) > len(delimiter) and string.endswith(delimiter):
                break

        if it.curr != '"':
            raise TokenizeError('No terminating delimiter inside raw string literal found!', it)
        it.next()

    tokens.append(QuoteToken(start, it, QuoteType.Double, raw_encoding))
    return True


def scan_for_quote(tokens: List[Token], it: LineWrapIterator):
    if not scan_for_quote_double(tokens, it):
        return scan_for_quote_single(tokens, it)
    return True
