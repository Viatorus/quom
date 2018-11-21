from enum import Enum
from typing import List

from .identifier_tokenizer import IdentifierToken
from .iterator import CodeIterator, EscapeIterator
from .token import Token, TokenType
from .tokenize_error import TokenizeError


class LiteralEncoding(Enum):
    NONE = 0,
    WIDE = 1,
    UTF8 = 2,
    UTF16 = 3,
    UTF32 = 4,
    RAW = 5,
    RAW_WIDE = 6,
    RAW_UTF8 = 7,
    RAW_UTF16 = 8,
    RAW_UTF32 = 9


class QuoteType(Enum):
    SINGLE = 0
    Double = 1


class QuoteToken(Token):
    def __init__(self, start, end, quote_type: QuoteType, literal_encoding: LiteralEncoding = None):
        super().__init__(start, end, TokenType.QUOTE)
        self.quote_type = quote_type
        self.literal_encoding = literal_encoding


def to_literal_encoding(identifier: IdentifierToken):
    name = identifier.identifier_name
    if name == 'u8':
        return LiteralEncoding.UTF8
    elif name == 'u':
        return LiteralEncoding.UTF16
    elif name == 'U':
        return LiteralEncoding.UTF32
    elif name == 'L':
        return LiteralEncoding.WIDE
    elif name == 'R':
        return LiteralEncoding.RAW
    elif name == 'u8R':
        return LiteralEncoding.RAW_UTF8
    elif name == 'uR':
        return LiteralEncoding.RAW_UTF16
    elif name == 'UR':
        return LiteralEncoding.RAW_UTF32
    elif name == 'LR':
        return LiteralEncoding.RAW_WIDE
    raise TokenizeError('Unknown literal encoding.', identifier.it)


def scan_for_quote_single(tokens: List[Token], it: CodeIterator):
    if it.curr != '\'':
        return False
    it = EscapeIterator(it)
    start = it.copy()

    # Parse until non escaped '.
    backslashes = 0
    while next(it, None) and (it.curr != '\'' or backslashes % 2 != 0):
        if it.curr == '\\':
            backslashes += 1
        else:
            backslashes = 0

    # Check if end of file is reached.
    if it.curr is None:
        raise TokenizeError("Character sequence not terminated!", it)
    next(it, None)

    tokens.append(QuoteToken(start, it, QuoteType.SINGLE))
    return True


def scan_for_quote_double(tokens: List[Token], it: CodeIterator):
    if it.curr != '"':
        return None
    it = EscapeIterator(it)
    start = it.copy()

    literal_encoding = LiteralEncoding.NONE
    if tokens[-1].token_type == TokenType.IDENTIFIER:
        # literal_encoding = to_literal_encoding(tokens[-1])
        pass

    if literal_encoding in [LiteralEncoding.NONE, LiteralEncoding.WIDE, LiteralEncoding.UTF8, LiteralEncoding.UTF16,
                            LiteralEncoding.UTF32]:
        # Parse until end of line or non escaped ".
        backslashes = 0
        while next(it, None) and (it.curr != '"' or backslashes % 2 != 0):
            if it.curr == '\\':
                backslashes += 1
            else:
                backslashes = 0

        # Check if end of file is reached.
        if it.curr is None:
            raise TokenizeError("Character sequence not terminated!", it)
        next(it, None)
    else:
        delimiter = ""

        # Parse until end of introductory delimiter.
        while it != it_end and it[0] != '(':
            delimiter += it[0]
            it += 1

        if it == it_end:
            raise TokenizeError('No introductory delimiter inside raw string literal found!', it)
        it += 1

        # Define terminating delimiter.
        delimiter = ')' + delimiter + '"'

        # Parse until delimiter occours again.
        # TODO: Please optimize me.
        string = ""
        while it != it_end:
            string += it[0]
            it += 1
            if len(string) > len(delimiter) and string.endswith(delimiter):
                break

        if it == it_end:
            raise TokenizeError('No terminating delimiter inside raw string literal found!', it)

    tokens.append(QuoteToken(start, it, QuoteType.Double, literal_encoding))
    return True


def scan_for_quote(tokens: List[Token], it: CodeIterator):
    if not scan_for_quote_double(tokens, it):
        return scan_for_quote_single(tokens, it)
    return True
