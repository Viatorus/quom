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
    def __init__(self, start, token_type: TokenType):
        self.it = start
        self.token_type: TokenType = token_type
