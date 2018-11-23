from enum import Enum

from .iterator import Span


class TokenType(Enum):
    START = 0
    IDENTIFIER = 1
    SYMBOL = 2
    NUMBER = 3
    WHITESPACE = 4
    PREPROCESSOR = 5
    COMMENT = 6
    QUOTE = 7
    END = 8


class Token:
    def __init__(self, start, end, token_type: TokenType):
        self.span = Span(start, end) if start and end else None
        self.token_type: TokenType = token_type

    def __str__(self):
        return ''.join(self.span)
