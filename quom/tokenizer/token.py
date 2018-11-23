from enum import Enum

from .iterator import Span


class TokenType(Enum):
    START = 0
    WHITESPACE = 1
    COMMENT = 2
    QUOTE = 3
    NUMBER = 4
    PREPROCESSOR = 5
    REMAINING = 6
    END = 7


class Token:
    def __init__(self, start, end, token_type: TokenType):
        self.span = Span(start, end) if start and end else None
        self.token_type: TokenType = token_type

    def __str__(self):
        return ''.join(self.span)
