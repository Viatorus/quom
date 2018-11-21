from typing import List

from .identifier_tokenizer import scan_for_identifier
from .comment_tokenizer import scan_for_comment
from .iterator import CodeIterator
from .number_tokenizer import scan_for_number
from .preprocessor_tokenizer import scan_for_preprocessor
from .quote_tokenizer import scan_for_quote
from .token import Token, TokenType
from .tokenize_error import TokenizeError
from .symbol_tokenizer import scan_for_symbol
from .whitespace_tokenizer import scan_for_whitespace


def tokenize(src) -> List[Token]:
    it = CodeIterator(src)

    tokens = [Token(None, TokenType.START)]

    if it.lookahead:
        next(it)

    while it.curr:
        succeeded = scan_for_whitespace(tokens, it)
        if not succeeded:
            succeeded = scan_for_comment(tokens, it)
        if not succeeded:
            succeeded = scan_for_identifier(tokens, it)
        if not succeeded:
            succeeded = scan_for_quote(tokens, it)
        if not succeeded:
            succeeded = scan_for_number(tokens, it)
        if not succeeded:
            succeeded = scan_for_preprocessor(tokens, it)
        if not succeeded:
            succeeded = scan_for_symbol(tokens, it)
        if not succeeded:
            raise TokenizeError('Unknown syntax.', it)

    tokens.append(Token(None, TokenType.END))

    return tokens
