# Sample Test passing with nose and pytest
from quom.tokenizer import Tokenizer


def test_line_ending():
    tkz = Tokenizer('')
    assert tkz.get_source_code() == '\n'

    tkz = Tokenizer('\n')
    assert tkz.get_source_code() == '\n'

    tkz = Tokenizer('\r')
    assert tkz.get_source_code() == '\n'

    tkz = Tokenizer('ab\n')
    assert tkz.get_source_code() == 'ab\n'

    tkz = Tokenizer('ab\r')
    assert tkz.get_source_code() == 'ab\n'

    tkz = Tokenizer('ab')
    assert tkz.get_source_code() == 'ab\n'

    tkz = Tokenizer('ab')
    assert tkz.get_source_code() == 'ab\n'

    tkz = Tokenizer('ab\\')
    assert tkz.get_source_code() == 'ab\n'

    tkz = Tokenizer('ab\\\n')
    assert tkz.get_source_code() == 'ab\n'

    tkz = Tokenizer('ab\\\r')
    assert tkz.get_source_code() == 'ab\n'

    tkz = Tokenizer('ab\\\r\n')
    assert tkz.get_source_code() == 'ab\n'

    tkz = Tokenizer('ab\\\ncd')
    assert tkz.get_source_code() == 'abcd\n'

    tkz = Tokenizer('ab\\\rcd')
    assert tkz.get_source_code() == 'abcd\n'

    tkz = Tokenizer('ab\\\r\ncd')
    assert tkz.get_source_code() == 'abcd\n'


def test_comments_cpp_style():
    tkz = Tokenizer('//abc')
    tkz.tokenize()


def test_comments_c_style():
    tkz = Tokenizer('/*ab*/')
    tkz.tokenize()


def test_whitespace():
    tkz = Tokenizer(' ')
    tkz.tokenize()

    tkz = Tokenizer('\t')
    tkz.tokenize()

    tkz = Tokenizer('\v')
    tkz.tokenize()

    tkz = Tokenizer('\f')
    tkz.tokenize()

    tkz = Tokenizer('\r')
    tkz.tokenize()

    tkz = Tokenizer('\n')
    tkz.tokenize()


def test_identifier():
    tkz = Tokenizer('abc')
    tkz.tokenize()

    tkz = Tokenizer('_abc')
    tkz.tokenize()

    tkz = Tokenizer('_a_bc')
    tkz.tokenize()


def test_quote_single():
    tkz = Tokenizer('\'abc\'')
    tkz.tokenize()

    tkz = Tokenizer('\'a\\\'bc\'')
    tkz.tokenize()


def test_quote_double():
    tkz = Tokenizer("\"abc\"")
    tkz.tokenize()

    tkz = Tokenizer("\"abc\\\"\"")
    tkz.tokenize()

    tkz = Tokenizer("u8R\"(abc)\"")
    tkz.tokenize()

    tkz = Tokenizer("UR\"(a)bc)\"")
    tkz.tokenize()

    tkz = Tokenizer("LR\"=(a)bc)=\"")
    tkz.tokenize()


def test_number():
    tkz = Tokenizer("12")
    tkz.tokenize()

    tkz = Tokenizer(".1")
    tkz.tokenize()


def test_preprocessor():
    tkz = Tokenizer("#pragma")
    tkz.tokenize()

    tkz = Tokenizer('#define')
    tkz.tokenize()

    tkz = Tokenizer('#include "abc" ')
    tkz.tokenize()

    tkz = Tokenizer('#include <abc> ')
    tkz.tokenize()

    tkz = Tokenizer('#define a(x) auto a##x = #x')
    tkz.tokenize()

    tkz = Tokenizer('#define eprintf(format, ...) fprintf (stderr, format, __VA_ARGS__)')
    tkz.tokenize()


def test_symbol():
    tkz = Tokenizer('+')
    tkz.tokenize()


def test_number_decimal():
    tkz = Tokenizer('.123')
    tkz.tokenize()

    tkz = Tokenizer('123')
    tkz.tokenize()

    tkz = Tokenizer('123.345')
    tkz.tokenize()

    tkz = Tokenizer('123.345e3')
    tkz.tokenize()

    tkz = Tokenizer('123e+4')
    tkz.tokenize()

    tkz = Tokenizer('123e-4')
    tkz.tokenize()

    tkz = Tokenizer('12\'3.345')
    tkz.tokenize()

    tkz = Tokenizer('01e1')
    tkz.tokenize()

    tkz = Tokenizer('01.1')
    tkz.tokenize()


def test_number_hexadecimal():
    tkz = Tokenizer('0x1')
    tkz.tokenize()

    tkz = Tokenizer('0xFp1')
    tkz.tokenize()

    tkz = Tokenizer('0x023p+1')
    tkz.tokenize()

    tkz = Tokenizer('0x0.123p-a')
    tkz.tokenize()


def test_number_binary():
    tkz = Tokenizer('0b1')
    tkz.tokenize()

    tkz = Tokenizer('0b01')
    tkz.tokenize()

    tkz = Tokenizer('0b010101')
    tkz.tokenize()


def test_number_octal():
    tkz = Tokenizer('01')
    tkz.tokenize()
