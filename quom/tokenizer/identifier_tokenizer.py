from enum import Enum
from typing import List

from .token import Token, TokenType
from .iterator import CodeIterator


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


def scan_for_name(it: CodeIterator):
    if not it.curr.isalpha() and it.curr != '_':
        return None
    start = it.copy()

    while next(it, None) and (it.curr.isalnum() or it.curr == '_'):
        pass
    return start


def scan_for_identifier(tokens: List[Token], it: CodeIterator):
    start = it.copy()
    identifier = scan_for_name(it)
    if identifier:
        tokens.append(IdentifierToken(start, it, IdentifierType.IDENTIFIER))
        return True
    return False
