from enum import Enum
from typing import List

from .comment_tokenizer import scan_for_comment
from .identifier_tokenizer import scan_for_name, scan_for_identifier
from .number_tokenizer import scan_for_number
from .quote_tokenizer import scan_for_quote
from .symbol_tokenizer import scan_for_symbol
from .token import Token, TokenType
from .tokenize_error import TokenizeError
from .whitespace_tokenizer import scan_for_whitespace, WhitespaceType
from quom.tokenizer.iterator import Iterator


class PreprocessorType(Enum):
    UNDEFINED = 0,
    NULL_DIRECTIVE = 1,
    DEFINE = 2,
    UNDEFINE = 3,
    INCLUDE = 4,
    IF = 5,
    IF_DEFINED = 6,
    IF_NOT_DEFINED = 7,
    ELSE = 8,
    ELSE_IF = 9,
    END_IF = 10,
    LINE = 11,
    ERROR = 12,
    PRAGMA = 13,
    WARNING = 14


class PreprocessorToken(Token):
    def __init__(self, start, end, preprocessor_type: PreprocessorType, tokens: List[Token]):
        super().__init__(start, end, TokenType.PREPROCESSOR)
        self.preprocessor_type = preprocessor_type
        self.preprocessor_tokens = tokens


def scan_for_whitespaces_and_comments(tokens: List[Token], it: Iterator, it_end: Iterator):
    while True:
        if scan_for_comment(tokens, it, it_end):
            continue
        if scan_for_whitespace(tokens, it, it_end):
            if tokens[-1].whitespace_type == WhitespaceType.LINE_BREAK:
                return True
            continue
        break
    return False


def scan_for_preprocessor_symbol(tokens: List[Token], it: Iterator, it_end: Iterator):
    if it[0] != '#':
        return
    it += 1
    return True


def scan_for_line_end(tokens: List[Token], it: Iterator, it_end: Iterator):
    while True:
        if scan_for_whitespaces_and_comments(tokens, it, it_end):
            return
        succeeded = scan_for_identifier(tokens, it, it_end)
        if not succeeded:
            succeeded = scan_for_quote(tokens, it, it_end)
        if not succeeded:
            succeeded = scan_for_number(tokens, it, it_end)
        if not succeeded:
            succeeded = scan_for_symbol(tokens, it, it_end)
        if not succeeded:
            succeeded = scan_for_preprocessor_symbol(tokens, it, it_end)
        if not succeeded:
            raise TokenizeError('Unknown syntax.', it)


def scan_for_preprocessor_include(tokens: List[Token], it: Iterator, it_end: Iterator):
    if scan_for_whitespaces_and_comments(tokens, it, it_end) or it[0] != '"' and it[0] != '<':
        raise TokenizeError("Expected \"FILENAME\" or <FILENAME> after include!", it)

    if it[0] == '"':
        it += 1

        # Parse until end of line or non escaped ".
        backslashes = 0
        while it[0] != '\n' and (it[0] != '"' or backslashes % 2 != 0):
            if it[0] == '\\':
                backslashes += 1
            else:
                backslashes = 0
            it += 1

        # Check if end of line is reached.
        if it[0] == '\n':
            raise TokenizeError("Character sequence not terminated!", it)
        it += 1

    elif it[0] == '<':
        it += 1

        # Scan until terminating >.
        while it[0] != '\n' and (it[0] != '>'):
            it += 1

        # Check if end of line is reached.
        if it[0] == '\n':
            raise TokenizeError("Character sequence not terminated!", it)
        it += 1


def scan_for_preprocessor(tokens: List[Token], it: Iterator, it_end: Iterator):
    if it[0] != '#':
        return None
    start = it.copy()
    it += 1

    preprocessor_tokens = []
    if scan_for_whitespaces_and_comments(preprocessor_tokens, it, it_end):
        tokens.append(PreprocessorToken(start, it, PreprocessorType.NULL_DIRECTIVE, preprocessor_tokens))
        return True

    name = scan_for_name(it, it_end)
    if not name:
        raise TokenizeError('Illegal preprocessor instruction.', start + 1)
    name = ''.join(name)

    if name in ['if', 'ifdef', 'ifndef', 'elsif', 'pragma', 'warning', 'error', 'line', 'define', 'undef',
                'else', 'endif']:
        scan_for_line_end(preprocessor_tokens, it, it_end)
    elif name == 'include':
        scan_for_preprocessor_include(preprocessor_tokens, it, it_end)
        scan_for_line_end(preprocessor_tokens, it, it_end)
    else:
        raise TokenizeError('Unknown preprocessor directive: ' + name + '<-', it)

    tokens.append(PreprocessorToken(start, it, PreprocessorType.UNDEFINE, preprocessor_tokens))
    return True