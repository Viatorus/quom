from enum import Enum

from quom.utils.iterable import Iterator
from .token import Token, TokenType


class CommentType(Enum):
    CPP_STYLE = 0
    C_STYLE = 1


class CommentToken(Token):
    def __init__(self, start, end, type: CommentType):
        super().__init__(start, end, TokenType.COMMENT)
        self.comment_type = type


def scan_for_comment_cpp_style(it: Iterator, _: Iterator):
    # C++-style comment: //
    if it[0] != '/' or it[1] != '/':
        return None
    start = it
    it += 2

    # Parse until \n.
    while it[0] != '\n':
        it += 1

    return CommentToken(start, it, CommentType.CPP_STYLE)


def scan_for_comment_c_style(it: Iterator, it_end: Iterator):
    # C-style comment: /*
    if it[0] != '/' or it[1] != '*':
        return None
    start = it
    it += 2

    # Parse until file end or */.
    while (it - 1) != it_end and (it[0] != '*' or it[1] != '/'):
        it += 1

    if (it - 1) == it_end:
        raise Exception("C-style comment not terminated!")
    it += 2

    return CommentToken(start, it, CommentType.C_STYLE)


def scan_for_comment(it: Iterator, it_end: Iterator):
    token = scan_for_comment_cpp_style(it, it_end)
    if not token:
        token = scan_for_comment_c_style(it, it_end)
    return token
