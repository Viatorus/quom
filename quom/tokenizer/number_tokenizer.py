from enum import Enum
from typing import List

from .token import Token, TokenType
from .iterator import CodeIterator
from .tokenize_error import TokenizeError


class NumberType(Enum):
    DECIMAL = 0,
    OCTAL = 1
    HEX = 2
    BINARY = 3


class Precision(Enum):
    INTEGER = 0
    FLOATING_POINT = 1


class NumberToken(Token):
    def __init__(self, start, end, number_type: NumberType, precision: Precision):
        super().__init__(start, end, TokenType.NUMBER)
        self.number_type = number_type
        self.precision = precision


def scan_for_digit(it: CodeIterator):
    if not it.curr or not it.curr.isnumeric():
        return False

    while it.next() and (it.curr.isnumeric() or it.curr == '\''):
        pass

    if it.prev == '\'':
        raise TokenizeError("Digit separator does not adjacent to digit!", it)

    return True


def scan_for_hexadecimal(it: CodeIterator):
    if not it.curr or not it.curr.isnumeric() and 'a' > it.curr > 'f' and 'A' > it.curr > 'F':
        return False

    while it.next() and (it.curr.isnumeric() or 'a' <= it.curr <= 'f' or 'A' <= it.curr <= 'F' or it.curr == '\''):
        pass

    if it.prev == '\'':
        raise TokenizeError("Digit separator does not adjacent to digit!", it)

    return True


def scan_for_binary(it: CodeIterator):
    if it.curr not in '01':
        return False

    while it.next() and it.curr in ['0', '1', '\'']:
        pass

    if it.prev == '\'':
        raise TokenizeError("Digit separator does not adjacent to digit!", it)

    return True


def scan_for_number(tokens: List[Token], it: CodeIterator):
    if not it.curr.isdigit() and (it.curr != '.' or not it.lookahead or not it.lookahead.isdigit()):
        return False
    start = it.copy()
    it.next()

    number_type = NumberType.DECIMAL
    precision = Precision.INTEGER

    if it.prev == '0' and it.curr in 'xX' and it.lookahead and ('0' <= it.lookahead <= '9' or 'a' <= it.lookahead <= 'f' or 'A' <= it.lookahead <= 'F'):
        it.next()
        number_type = NumberType.HEX

        scan_for_hexadecimal(it)

        # Check for radix separator.
        if it.curr == '.':
            it.next()
            precision = Precision.FLOATING_POINT

            scan_for_hexadecimal(it)

            if not it.curr or it.curr not in 'pP':
                raise TokenizeError('Hexadecimal floating constants require an exponent!', it)

        if it.curr in 'pP':
            it.next()
            precision = Precision.FLOATING_POINT

            # Check for sign.
            if it.curr in ['+', '-']:
                it.next()

            scan_for_hexadecimal(it)

    elif it.prev == '0' and it.curr in 'bB' and it.lookahead and '0' <= it.lookahead <= '1':
        number_type = NumberType.BINARY
        it.next()
        scan_for_binary(it)
    elif it.curr:
        number_type = NumberType.DECIMAL

        maybe_ocal = False
        if it.prev == '0':
            maybe_ocal = True

        if it.curr != '.':
            scan_for_digit(it)

        # Check for radix separator.
        if it.curr == '.':
            it.next()
            precision = Precision.FLOATING_POINT
        elif maybe_ocal and (not it.curr or it.curr not in 'eE'):
            number_type = NumberType.OCTAL

        scan_for_digit(it)

        # Check for exponent.
        if it.curr in 'eE':
            it.next()
            precision = Precision.FLOATING_POINT

            # Check for sign.
            if it.curr in '+-':
                it.next()

            scan_for_digit(it)

    tokens.append(NumberToken(start, it, number_type, precision))
    return True
