from typing import List

from .comment_tokenizer import scan_for_comment
from .iterator import LineWrapIterator
from .number_tokenizer import scan_for_number
from .quote_tokenizer import scan_for_quote
from .remaining_tokenizer import scan_for_remaining
from .token import Token
from .tokenize_error import TokenizeError
from .whitespace_tokenizer import scan_for_whitespace, LinebreakWhitespaceToken


class PreprocessorToken(Token):
    def __init__(self, start, end, tokens: List[Token]):
        super().__init__(start, end)
        self.preprocessor_tokens = tokens


class PreprocessorIncludeToken(PreprocessorToken):
    def __init__(self, start, end, tokens: List[Token]):
        super().__init__(start, end, tokens)


class PreprocessorPragmaToken(PreprocessorToken):
    pass


class PreprocessorPragmaOnceToken(PreprocessorPragmaToken):
    pass


class PreprocessorDefineToken(PreprocessorToken):
    pass


class PreprocessorIfNotDefinedToken(PreprocessorToken):
    pass


class PreprocessorEndIfToken(PreprocessorToken):
    pass


def scan_for_whitespaces_and_comments(it: LineWrapIterator, tokens: List[Token]):
    while it.curr != '\0':
        if scan_for_comment(tokens, it):
            continue
        if scan_for_whitespace(tokens, it):
            if isinstance(tokens[-1], LinebreakWhitespaceToken):
                return True
            continue
        break
    return it.curr == '\0'


def scan_for_line_end(it: LineWrapIterator, tokens: List[Token]):
    while it.curr != '\0':
        if scan_for_whitespaces_and_comments(it, tokens):
            return
        succeeded = scan_for_quote(tokens, it)
        if not succeeded:
            succeeded = scan_for_number(tokens, it)
        if not succeeded:
            scan_for_remaining(tokens, it)


def scan_for_preprocessor_include(start: LineWrapIterator, it: LineWrapIterator, tokens: List[Token]):
    if scan_for_whitespaces_and_comments(it, tokens) or it.curr != '"' and it.curr != '<':
        raise TokenizeError("Expected \"FILENAME\" or <FILENAME> after include!", it)

    it = LineWrapIterator(it)

    if it.curr == '"':
        # Parse until non escaped ".
        backslashes = 0
        while it.next() and it.curr != '\n' and (it.curr != '"' or backslashes % 2 != 0):
            if it.curr == '\\':
                backslashes += 1
            else:
                backslashes = 0

        # Check if end of line is reached.
        if it.curr != '"':
            raise TokenizeError("Character sequence not terminated!", it)
        it.next()

    elif it.curr == '<':
        # Scan until terminating >.
        while it.next() and it.curr != '\n' and it.curr != '>':
            pass

        # Check if end of line is reached.
        if it.curr != '>':
            raise TokenizeError("Character sequence not terminated!", it)
        it.next()

    scan_for_line_end(it, tokens)
    return PreprocessorIncludeToken(start, it, tokens)


def scan_for_preprocessor_pragma(start: LineWrapIterator, it: LineWrapIterator, tokens: List[Token]):
    if scan_for_whitespaces_and_comments(it, tokens):
        return PreprocessorPragmaToken(start, it, tokens)

    for c in 'once':
        if it.curr != c:
            return PreprocessorPragmaToken(start, it, tokens)
        it.next()

    if scan_for_whitespaces_and_comments(it, tokens):
        return PreprocessorPragmaOnceToken(start, it, tokens)
    return PreprocessorPragmaToken(start, it, tokens)


def scan_for_preprocessor(tokens: List[Token], it: LineWrapIterator):
    if it.curr != '#':
        return None
    start = it.copy()
    it.next()

    preprocessor_tokens = []
    if scan_for_whitespaces_and_comments(it, preprocessor_tokens):
        tokens.append(PreprocessorToken(start, it, preprocessor_tokens))
        return True

    scan_for_remaining(preprocessor_tokens, it)
    name = ''.join(preprocessor_tokens[-1].span)

    if name == 'include':
        preprocessor_token = scan_for_preprocessor_include(start, it, preprocessor_tokens)
    elif name == 'pragma':
        preprocessor_token = scan_for_preprocessor_pragma(start, it, preprocessor_tokens)
    elif name == 'define':
        scan_for_line_end(it, preprocessor_tokens)
        preprocessor_token = PreprocessorDefineToken(start, it, preprocessor_tokens)
    elif name == 'ifndef':
        scan_for_line_end(it, preprocessor_tokens)
        preprocessor_token = PreprocessorIfNotDefinedToken(start, it, preprocessor_tokens)
    elif name == 'endif':
        scan_for_line_end(it, preprocessor_tokens)
        preprocessor_token = PreprocessorEndIfToken(start, it, preprocessor_tokens)
    else:
        scan_for_line_end(it, preprocessor_tokens)
        preprocessor_token = PreprocessorToken(start, it, preprocessor_tokens)

    tokens.append(preprocessor_token)
    return True
