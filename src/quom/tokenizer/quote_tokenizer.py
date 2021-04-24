from typing import List

from .iterator import RawIterator, LineWrapIterator
from .remaining_tokenizer import RemainingToken
from .token import Token
from .tokenize_error import TokenizeError


class QuoteToken(Token):
    pass


class SingleQuoteToken(QuoteToken):
    pass


class DoubleQuoteToken(QuoteToken):
    def __init__(self, start, end, is_raw_encdoing):
        super().__init__(start, end)
        self.is_raw_encoding = is_raw_encdoing


def check_is_raw_encoding(token: Token):
    if isinstance(token, RemainingToken):
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

    tokens.append(SingleQuoteToken(start, it))
    return True


def scan_for_quote_double(tokens: List[Token], it: LineWrapIterator):
    if it.curr != '"':
        return None
    start = it.copy()

    is_raw_encoding = check_is_raw_encoding(tokens[-1])
    if not is_raw_encoding:
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
        delimiter = ''

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

    tokens.append(DoubleQuoteToken(start, it, is_raw_encoding))
    return True


def scan_for_quote(tokens: List[Token], it: LineWrapIterator):
    if not scan_for_quote_double(tokens, it):
        return scan_for_quote_single(tokens, it)
    return True
