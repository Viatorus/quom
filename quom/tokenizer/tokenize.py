from typing import List

from .remaining_tokenizer import scan_for_remaining
from .comment_tokenizer import scan_for_comment
from .iterator import LineWrapIterator
from .number_tokenizer import scan_for_number
from .preprocessor_tokenizer import scan_for_preprocessor
from .quote_tokenizer import scan_for_quote
from .token import Token
from .whitespace_tokenizer import scan_for_whitespace


def tokenize(src) -> List[Token]:
    it = LineWrapIterator(src)

    tokens = [Token(None, None)]

    while it.curr != '\0':
        succeeded = scan_for_whitespace(tokens, it)
        if not succeeded:
            succeeded = scan_for_comment(tokens, it)
        if not succeeded:
            succeeded = scan_for_quote(tokens, it)
        if not succeeded:
            succeeded = scan_for_number(tokens, it)
        if not succeeded:
            succeeded = scan_for_preprocessor(tokens, it)
        if not succeeded:
            scan_for_remaining(tokens, it)

    tokens.append(Token(None, None))

    return tokens
