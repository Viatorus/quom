from enum import Enum


# from quom.tokenizer.iterator import


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
        self.start = start.copy() if start is not None else None
        self.end = end.copy() if end is not None else None
        self.token_type: TokenType = token_type
