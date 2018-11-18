from enum import Enum

from ..utils.iterable import Iterator


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
    def __init__(self, start: Iterator, end: Iterator, token_type: TokenType):
        self.start: Iterator = start.copy() if start is not None else None
        self.end: Iterator = end.copy() if end is not None else None
        self.token_type: TokenType = token_type