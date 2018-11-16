from enum import Enum


class TokenType(Enum):
    IDENTIFIER = 0
    SYMBOL = 1
    NUMBER = 2
    WHITESPACE = 3
    PREPROCESSOR = 4
    COMMENT = 5
    QUOTE = 6


class Token:
    def __init__(self, start, end, type: TokenType):
        self.start = start
        self.end = end
        self.type = type
