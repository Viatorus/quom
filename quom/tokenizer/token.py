from enum import Enum


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
    def __init__(self, start, end, type: TokenType):
        self.start = start
        self.end = end
        self.type = type
