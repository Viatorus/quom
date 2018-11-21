from enum import Enum
from typing import List

from .token import Token, TokenType
from .iterator import CodeIterator, Span


class IdentifierType(Enum):
    IDENTIFIER = 0
    LITERAL_ENCODING = 1


class IdentifierToken(Token):
    def __init__(self, it, identifier_type: IdentifierType):
        super().__init__(it, TokenType.IDENTIFIER)
        self.identifier_type = identifier_type

    @property
    def identifier_name(self) -> str:
        return ''.join(self.it)


def scan_for_name(it: CodeIterator):
    if not it.curr.isalpha() and it.curr != '_':
        return None
    start = it.copy()

    while next(it, None) and it.curr and (it.curr.isalnum() or it.curr == '_'):
        pass
    return Span(start, it)


def scan_for_identifier(tokens: List[Token], it: CodeIterator):
    start = it.copy()
    identifier = scan_for_name(it)
    if identifier:
        tokens.append(IdentifierToken(Span(start, it), IdentifierType.IDENTIFIER))
        return True
    return False
