from enum import Enum
from typing import List

from .iterator import CodeIterator, EscapeIterator, Span
from .token import Token, TokenType
from .tokenize_error import TokenizeError


class CommentType(Enum):
    CPP_STYLE = 0
    C_STYLE = 1


class CommentToken(Token):
    def __init__(self, it, comment_type: CommentType):
        super().__init__(it, TokenType.COMMENT)
        self.comment_type = comment_type


def scan_for_comment_cpp_style(tokens: List[Token], it: CodeIterator):
    # C++-style comment: //
    if it.curr != '/' or it.lookahead != '/':
        return False
    it = EscapeIterator(it)
    start = it.copy()
    next(it)

    # Parse until \n.
    while next(it, None) and it.curr != '\n':
        pass

    tokens.append(CommentToken(Span(start, it), CommentType.CPP_STYLE))
    return True


def scan_for_comment_c_style(tokens: List[Token], it: CodeIterator):
    # C-style comment: /*
    if it.curr != '/' or it.lookahead != '*':
        return False
    it = EscapeIterator(it)
    start = it.copy()
    next(it)

    # Parse until file end or */.
    while next(it, None) and (it.curr != '*' or it.lookahead != '/'):
        pass

    if it.curr is None:
        raise TokenizeError("C-style comment not terminated!", it)
    next(it)
    next(it, None)

    tokens.append(CommentToken(Span(start, it), CommentType.C_STYLE))
    return True


def scan_for_comment(tokens: List[Token], it: CodeIterator):
    if not scan_for_comment_cpp_style(tokens, it):
        return scan_for_comment_c_style(tokens, it)
    return True
