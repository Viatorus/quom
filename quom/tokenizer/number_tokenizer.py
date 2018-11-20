from enum import Enum
from typing import List

from .token import Token, TokenType
from .tokenize_error import TokenizeError
from quom.tokenizer.iterator import Iterator


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


def scan_for_digit(it: Iterator, it_end: Iterator):
    if not it[0].isnumeric():
        return False

    it += 1
    while it[0].isnumeric() or it[0] == '\'':
        it += 1

    if it[-1] == '\'':
        raise TokenizeError("Digit separator does not adjacent to digit!", it)

    return True


def scan_for_hexadecimal(it: Iterator, it_end: Iterator):
    if not it[0].isnumeric() and 'a' > it[0] > 'f' and 'A' > it[0] > 'F':
        return False

    it += 1
    while it[0].isnumeric() or 'a' <= it[0] <= 'f' or 'A' <= it[0] <= 'F' or it[0] == '\'':
        it += 1

    if it[-1] == '\'':
        raise TokenizeError("Digit separator does not adjacent to digit!", it)

    return True


def scan_for_binary(it: Iterator, it_end: Iterator):
    if it[0] not in ['0', '1']:
        return False
    it += 1

    while it[0] in ['0', '1', '\'']:
        it += 1

    if it[-1] == '\'':
        raise TokenizeError("Digit separator does not adjacent to digit!", it)

    return True


def scan_for_number(tokens: List[Token], it: Iterator, it_end: Iterator):
    if not it[0].isdigit() and (it[0] != '.' or not it[1].isdigit()):
        return False
    start = it.copy()
    it += 1

    number_type = NumberType.DECIMAL
    precision = Precision.INTEGER

    if it[-1] == '0' and it[0] in ['x', 'X']:
        it += 1
        number_type = NumberType.HEX

        scan_for_hexadecimal(it, it_end)

        # Check for radix separator.
        if it[0] == '.':
            it += 1
            precision = Precision.FLOATING_POINT

            scan_for_hexadecimal(it, it_end)

            if it[0] not in ['p', 'P']:
                raise TokenizeError('Hexadecimal floating constants require an exponent!', it)

        if it[0] in ['p', 'P']:
            it += 1
            precision = Precision.FLOATING_POINT

            # Check for sign.
            if it[0] in ['+', '-']:
                it += 1

            scan_for_hexadecimal(it, it_end)

    elif it[-1] == '0' and it[0] in ['b', 'B']:
        it += 1
        number_type = NumberType.BINARY

        scan_for_binary(it, it_end)
    else:
        number_type = NumberType.DECIMAL

        maybe_ocal = False
        if it[-1] == '0':
            maybe_ocal = True

        if it[0] != '.':
            scan_for_digit(it, it_end)

        # Check for radix separator.
        if it[0] == '.':
            it += 1
            precision = Precision.FLOATING_POINT
        elif maybe_ocal and it[0] not in ['e', 'E']:
            number_type = NumberType.OCTAL

        scan_for_digit(it, it_end)

        # Check for exponent.
        if it[0] in ['e', 'E']:
            it += 1
            precision = Precision.FLOATING_POINT

            # Check for sign.
            if it[0] in ['+', '-']:
                it += 1

            scan_for_digit(it, it_end)

    tokens.append(NumberToken(start, it, number_type, precision))
    return True
