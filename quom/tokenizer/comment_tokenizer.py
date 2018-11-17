from enum import Enum
from typing import List

from .token import Token, TokenType
from ..utils.iterable import Iterator


class CommentType(Enum):
    CPP_STYLE = 0
    C_STYLE = 1


class CommentToken(Token):
    def __init__(self, start, end, type: CommentType):
        super().__init__(start, end, TokenType.COMMENT)
        self.comment_type = type


def scan_for_comment_cpp_style(tokens: List[Token], it: Iterator, _: Iterator):
    # C++-style comment: //
    if it[0] != '/' or it[1] != '/':
        return False
    start = it.copy()
    it += 2

    # Parse until \n.
    while it[0] != '\n':
        it += 1

    tokens.append(CommentToken(start, it, CommentType.CPP_STYLE))
    return True


def scan_for_comment_c_style(tokens: List[Token], it: Iterator, it_end: Iterator):
    # C-style comment: /*
    if it[0] != '/' or it[1] != '*':
        return False
    start = it.copy()
    it += 2

    # Parse until file end or */.
    while (it - 1) != it_end and (it[0] != '*' or it[1] != '/'):
        it += 1

    if (it - 1) == it_end:
        raise Exception("C-style comment not terminated!")
    it += 2

    tokens.append(CommentToken(start, it, CommentType.C_STYLE))
    return True


def scan_for_comment(tokens: List[Token], it: Iterator, it_end: Iterator):
    if not scan_for_comment_cpp_style(tokens, it, it_end):
        return scan_for_comment_c_style(tokens, it, it_end)
    return True
