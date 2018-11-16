from enum import Enum

from quom.utils.iterable import Iterator
from .quote_tokenizer import scan_for_quote_double
from .token import Token, TokenType


class IdentifierType(Enum):
    IDENTIFIER = 0
    LITERAL_ENCODING = 1


class IdentifierToken(Token):
    def __init__(self, start, end, type: IdentifierType, identifier):
        super().__init__(start, end, TokenType.IDENTIFIER)
        self.identifier_type = type
        self.identifier = identifier


def scan_for_name(it: Iterator, it_end: Iterator):
    if not it[0].isalpha() and it[0] != '_':
        return
    name = [it[0]]
    it += 1

    while it[0].isalnum() or it[0] == '_':
        name.append(it[0])
        it += 1

    return ''.join(name)


def scan_for_identifier(it: Iterator, it_end: Iterator):
    start = it
    identifier = scan_for_name(it, it_end)
    if identifier:
        end = it
        if it[0] == '"':
            scan_for_quote_double(it, it_end, identifier)

        return IdentifierToken(start, end, IdentifierType.IDENTIFIER, identifier)
    return None
