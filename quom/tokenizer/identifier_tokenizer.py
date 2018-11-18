from enum import Enum
from typing import List

from .token import Token, TokenType
from ..utils.iterable import Iterator


class IdentifierType(Enum):
    IDENTIFIER = 0
    LITERAL_ENCODING = 1


class IdentifierToken(Token):
    def __init__(self, start, end, identifier_type: IdentifierType):
        super().__init__(start, end, TokenType.IDENTIFIER)
        self.identifier_type = identifier_type

    @property
    def identifier_name(self) -> str:
        return ''.join(self.start[:(self.end.pos - self.start.pos)])


def scan_for_name(it: Iterator, it_end: Iterator):
    if not it[0].isalpha() and it[0] != '_':
        return None
    start = it.copy()
    it += 1

    while it[0].isalnum() or it[0] == '_':
        it += 1
    return start[:(it.pos - start.pos)]


def scan_for_identifier(tokens: List[Token], it: Iterator, it_end: Iterator):
    start = it.copy()
    identifier = scan_for_name(it, it_end)
    if identifier:
        tokens.append(IdentifierToken(start, it, IdentifierType.IDENTIFIER))
        return True
    return False
