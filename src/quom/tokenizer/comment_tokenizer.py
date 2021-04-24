from typing import List

from .iterator import LineWrapIterator, Span
from .token import Token
from .tokenize_error import TokenizeError


class CommentToken(Token):
    def __init__(self, start, end, content_start, content_end):
        super().__init__(start, end)
        self.content_start = content_start.copy()
        self.content_end = content_end.copy()

    @property
    def content(self):
        return Span(self.content_start, self.content_end)


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
    it.next()
    content_start = it.copy()

    # Parse until line break.
    while it.curr not in '\n\r' and it.next():
        pass

    content_end = it.copy()

    tokens.append(CppCommentToken(start, it, content_start, content_end))
    return True


def scan_for_comment_c_style(tokens: List[Token], it: LineWrapIterator):
    # C-style comment: /*
    if it.curr != '/' or it.lookahead != '*':
        return False
    it = LineWrapIterator(it)
    start = it.copy()
    it.next()
    it.next()
    content_start = it.copy()

    # Parse until file end or */.
    while (it.curr != '*' or it.lookahead != '/') and it.next():
        pass

    if it.curr != '*':
        raise TokenizeError("C-style comment not terminated!", it)
    content_end = it.copy()
    it.next()
    it.next()

    tokens.append(CCommentToken(start, it, content_start, content_end))
    return True


def scan_for_comment(tokens: List[Token], it: LineWrapIterator):
    if not scan_for_comment_cpp_style(tokens, it):
        return scan_for_comment_c_style(tokens, it)
    return True
