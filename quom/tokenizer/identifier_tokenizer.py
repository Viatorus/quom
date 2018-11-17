from enum import Enum
from typing import List

from .token import Token, TokenType
from ..utils.iterable import Iterator


class IdentifierType(Enum):
    IDENTIFIER = 0
    LITERAL_ENCODING = 1


class IdentifierToken(Token):
    def __init__(self, start, end, type: IdentifierType):
        super().__init__(start, end, TokenType.IDENTIFIER)
        self.identifier_type = type

    @property
    def name(self) -> str:
        return ''.join(self.start[:self.end.start])


def scan_for_name(it: Iterator, it_end: Iterator):
    if not it[0].isalpha() and it[0] != '_':
        return None
    start = it.copy()
    it += 1

    while it[0].isalnum() or it[0] == '_':
        it += 1

    return Iterator(start.base, start.start, it.start - start.start)


def scan_for_identifier(tokens: List[Token], it: Iterator, it_end: Iterator):
    start = it.copy()
    identifier = scan_for_name(it, it_end)
    if identifier:
        tokens.append(IdentifierToken(start, it, IdentifierType.IDENTIFIER))
        return True
    return False
