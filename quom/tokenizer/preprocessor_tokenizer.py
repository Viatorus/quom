from typing import List

from .comment_tokenizer import scan_for_comment
from .iterator import LineWrapIterator, Span
from .number_tokenizer import scan_for_number
from .quote_tokenizer import scan_for_quote
from .remaining_tokenizer import scan_for_remaining, RemainingToken
from .token import Token, StartToken, EndToken
from .tokenize_error import TokenizeError
from .whitespace_tokenizer import scan_for_whitespace, LinebreakWhitespaceToken


class PreprocessorToken(Token):
    def __init__(self, start, end):
        super().__init__(start, end)
        self.preprocessor_tokens = None
        self.preprocessor_arguments_idx = None

    @property
    def preprocessor_instruction(self):
        return self.preprocessor_tokens[1:self.preprocessor_arguments_idx]

    @property
    def preprocessor_arguments(self):
        return self.preprocessor_tokens[self.preprocessor_arguments_idx:-1]


class PreprocessorIncludeToken(PreprocessorToken):
    def __init__(self, start, end, is_local_include: bool, path_start, path_end):
        super().__init__(start, end)
        self.is_local_include = is_local_include
        self.path = Span(path_start, path_end)


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
    it.next()
    path_start = it.copy()
    is_local_include = False

    if it.prev == '"':
        is_local_include = True

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
    elif it.prev == '<':
        # Scan until terminating >.
        while it.next() and it.curr != '\n' and it.curr != '>':
            pass

        # Check if end of line is reached.
        if it.curr != '>':
            raise TokenizeError("Character sequence not terminated!", it)

    path_end = it.copy()
    it.next()

    scan_for_line_end(it, tokens)
    return PreprocessorIncludeToken(start, it, is_local_include, path_start, path_end)


def scan_for_preprocessor_pragma(start: LineWrapIterator, it: LineWrapIterator, tokens: List[Token]):
    if scan_for_whitespaces_and_comments(it, tokens):
        return PreprocessorPragmaToken(start, it)

    scan_for_remaining(tokens, it)
    if str(tokens[-1]) != 'once':
        return PreprocessorPragmaToken(start, it)

    if scan_for_whitespaces_and_comments(it, tokens):
        return PreprocessorPragmaOnceToken(start, it)

    scan_for_line_end(it, tokens)
    return PreprocessorPragmaToken(start, it)


def scan_for_preprocessor(tokens: List[Token], it: LineWrapIterator):
    if it.curr != '#':
        return None
    start = it.copy()
    it.next()

    preprocessor_tokens = [StartToken(start, start), RemainingToken(start, it)]
    if scan_for_whitespaces_and_comments(it, preprocessor_tokens):
        preprocessor_token = PreprocessorToken(start, it)
        preprocessor_arguments_idx = len(preprocessor_tokens)
    else:
        scan_for_remaining(preprocessor_tokens, it)
        name = str(preprocessor_tokens[-1])
        preprocessor_arguments_idx = len(preprocessor_tokens)

        if name == 'include':
            preprocessor_token = scan_for_preprocessor_include(start, it, preprocessor_tokens)
        elif name == 'pragma':
            preprocessor_token = scan_for_preprocessor_pragma(start, it, preprocessor_tokens)
        elif name == 'define':
            scan_for_line_end(it, preprocessor_tokens)
            preprocessor_token = PreprocessorDefineToken(start, it)
        elif name == 'ifndef':
            scan_for_line_end(it, preprocessor_tokens)
            preprocessor_token = PreprocessorIfNotDefinedToken(start, it)
        elif name == 'endif':
            scan_for_line_end(it, preprocessor_tokens)
            preprocessor_token = PreprocessorEndIfToken(start, it)
        else:
            scan_for_line_end(it, preprocessor_tokens)
            preprocessor_token = PreprocessorToken(start, it)

    preprocessor_tokens.append(EndToken(it, it))
    preprocessor_token.preprocessor_tokens = preprocessor_tokens
    preprocessor_token.preprocessor_arguments_idx = preprocessor_arguments_idx

    tokens.append(preprocessor_token)
    return True
