from enum import Enum
from typing import List

from .token import Token, TokenType
from .iterator import CodeIterator, Span
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
    if not it.curr.isnumeric() and it.curr != '\'':
        return False, False

    found_decimal = False
    while it.next() and (it.curr.isnumeric() or it.curr == '\''):
        found_decimal |= it.curr in '89'

    if it.prev == '\'':
        raise TokenizeError("Digit separator does not adjacent to digit!", it)

    return True, found_decimal


def scan_for_hexadecimal(it: CodeIterator):
    if not it.curr.isnumeric() and it.curr not in 'abcdefABCDEF':
        return False

    while it.next() and (it.curr.isnumeric() or it.curr in 'abcdefABCDEF' or it.curr == '\''):
        pass

    if it.prev == '\'':
        raise TokenizeError("Digit separator does not adjacent to digit!", it)

    return True


def scan_for_binary(it: CodeIterator):
    while it.next() and it.curr in '01\'':
        pass

    if it.prev == '\'':
        raise TokenizeError("Digit separator does not adjacent to digit!", it)

    return True


def scan_for_number(tokens: List[Token], it: CodeIterator):
    if not it.curr.isdigit() and (it.curr != '.' or not it.lookahead.isdigit()):
        return False
    start = it.copy()
    it.next()

    number_type = NumberType.DECIMAL
    precision = Precision.INTEGER

    if it.prev == '0' and it.curr in 'xX' and (it.lookahead.isnumeric() or it.lookahead in 'abcdefABCDEF'):
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
            if it.curr in '+-':
                it.next()

            if not scan_for_digit(it)[0]:
                raise TokenizeError('Exponent has no digits.')

    elif it.prev == '0' and it.curr in 'bB' and it.lookahead in '01':
        number_type = NumberType.BINARY
        it.next()
        scan_for_binary(it)
    elif it.curr:
        number_type = NumberType.DECIMAL

        maybe_ocal = False
        if it.prev == '0' and it.curr in '01234567\'':
            maybe_ocal = True

        found_decimal = False
        if it.curr != '.':
            _, found_decimal = scan_for_digit(it)

        # Check for radix separator.
        if it.curr == '.':
            it.next()
            precision = Precision.FLOATING_POINT
        elif maybe_ocal and it.curr not in 'eE':
            number_type = NumberType.OCTAL

        if number_type != NumberType.OCTAL:
            scan_for_digit(it)

            # Check for exponent.
            if it.curr in 'eE':
                it.next()
                precision = Precision.FLOATING_POINT

                # Check for sign.
                if it.curr in '+-':
                    it.next()

                scan_for_digit(it)
        else:
            if found_decimal:
                raise TokenizeError('Invalid digit in octal constant.')

    tokens.append(NumberToken(start, it, number_type, precision))
    return True
