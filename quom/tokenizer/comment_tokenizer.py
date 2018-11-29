from typing import List

from .iterator import LineWrapIterator
from .token import Token
from .tokenize_error import TokenizeError


class CommentToken(Token):
    pass


class CppCommentToken(CommentToken):
    pass


class CCommentToken(CommentToken):
    pass


def scan_for_comment_cpp_style(tokens: List[Token], it: LineWrapIterator):
    # C++-style comment: //
    if it.curr != '/' or it.lookahead != '/':
        return False
    it = LineWrapIterator(it)
    start = it.copy()
    it.next()

    # Parse until line break.
    while it.next() and it.curr not in '\n\r':
        pass

    tokens.append(CppCommentToken(start, it))
    return True


def scan_for_comment_c_style(tokens: List[Token], it: LineWrapIterator):
    # C-style comment: /*
    if it.curr != '/' or it.lookahead != '*':
        return False
    it = LineWrapIterator(it)
    start = it.copy()
    it.next()

    # Parse until file end or */.
    while it.next() and (it.curr != '*' or it.lookahead != '/'):
        pass

    if it.curr != '*':
        raise TokenizeError("C-style comment not terminated!", it)
    it.next()
    it.next()

    tokens.append(CCommentToken(start, it))
    return True


def scan_for_comment(tokens: List[Token], it: LineWrapIterator):
    if not scan_for_comment_cpp_style(tokens, it):
        return scan_for_comment_c_style(tokens, it)
    return True
