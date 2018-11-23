from typing import List

import pytest

from quom.tokenizer import tokenize, TokenizeError, Token, TokenType


def check_tokens(tokens: List[Token], res):
    res = [TokenType.START] + res + [TokenType.END]

    for token, token_type in zip(tokens, res):
        assert token.token_type == token_type


def test_comments_cpp_style():
    tokens = tokenize('//abc')
    check_tokens(tokens, [TokenType.COMMENT])
    assert str(tokens[1]) == '//abc'

    tokens = tokenize(' //abc\n')
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.WHITESPACE])
    assert str(tokens[2]) == '//abc'

    tokens = tokenize('//abc \\\n \\b')
    check_tokens(tokens, [TokenType.COMMENT])


def test_comments_c_style():
    tokens = tokenize('/*ab*/')
    check_tokens(tokens, [TokenType.COMMENT])
    assert str(tokens[1]) == '/*ab*/'

    tokens = tokenize(' /*ab*/ ')
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.WHITESPACE])
    assert str(tokens[2]) == '/*ab*/'

    tokens = tokenize('/*ab\n*/')
    check_tokens(tokens, [TokenType.COMMENT])

    tokens = tokenize('/*ab\\\n*/')
    check_tokens(tokens, [TokenType.COMMENT])

    tokens = tokenize('/*ab\\b*/')
    check_tokens(tokens, [TokenType.COMMENT])

    with pytest.raises(TokenizeError):
        tokenize('/*a')

    with pytest.raises(TokenizeError):
        tokenize('/*a*')

    with pytest.raises(TokenizeError):
        tokenize('/*a* /')


def test_whitespace():
    tokens = tokenize(' ')
    check_tokens(tokens, [TokenType.WHITESPACE])

    tokens = tokenize(' \t')
    check_tokens(tokens, [TokenType.WHITESPACE])

    tokens = tokenize('\t')
    check_tokens(tokens, [TokenType.WHITESPACE])

    tokens = tokenize('\v')
    check_tokens(tokens, [TokenType.WHITESPACE])

    tokens = tokenize('\f')
    check_tokens(tokens, [TokenType.WHITESPACE])

    tokens = tokenize('\r')
    check_tokens(tokens, [TokenType.WHITESPACE])

    tokens = tokenize('\n')
    check_tokens(tokens, [TokenType.WHITESPACE])

    tokens = tokenize('\r\n')
    check_tokens(tokens, [TokenType.WHITESPACE])

    tokens = tokenize('\r\n\r')
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.WHITESPACE])

    tokens = tokenize('\r\n\n')
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.WHITESPACE])

    tokens = tokenize('\r\n\r\n\n')
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.WHITESPACE, TokenType.WHITESPACE])

    tokens = tokenize('\n\r\r')
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.WHITESPACE, TokenType.WHITESPACE])

    tokens = tokenize(' \n ')
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.WHITESPACE, TokenType.WHITESPACE])


def test_quote_single():
    tokens = tokenize('\'abc\'')
    check_tokens(tokens, [TokenType.QUOTE])
    assert str(tokens[1]) == '\'abc\''

    tokens = tokenize(' \'abc\' ')
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.QUOTE, TokenType.WHITESPACE])
    assert str(tokens[2]) == '\'abc\''

    tokens = tokenize('\'a\\bc\'')
    check_tokens(tokens, [TokenType.QUOTE])

    tokens = tokenize('\'a\\\'bc\'')
    check_tokens(tokens, [TokenType.QUOTE])

    with pytest.raises(TokenizeError):
        tokenize('\'a')

    with pytest.raises(TokenizeError):
        tokenize('\'')


def test_quote_double():
    tokens = tokenize('"abc"')
    check_tokens(tokens, [TokenType.QUOTE])
    assert str(tokens[1]) == '"abc"'

    tokens = tokenize(' "abc" ')
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.QUOTE, TokenType.WHITESPACE])
    assert str(tokens[2]) == '"abc"'

    tokens = tokenize('"abc\\""')
    check_tokens(tokens, [TokenType.QUOTE])
    assert str(tokens[1]) == '"abc\\""'

    tokens = tokenize('R"(abc)"')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.QUOTE])
    assert str(tokens[2]) == '"(abc)"'

    tokens = tokenize('R"(a\b\\r\\abc)"')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.QUOTE])
    assert str(tokens[2]) == '"(a\b\\r\\abc)"'

    tokens = tokenize('R"1=#(abc)1=#abc)1=#"')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.QUOTE])

    tokens = tokenize('u8R"(abc)"')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.QUOTE])

    tokens = tokenize('uR"(abc)"')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.QUOTE])

    tokens = tokenize('UR"(a)bc)"')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.QUOTE])

    tokens = tokenize('LR"=(a)bc)="')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.QUOTE])

    tokens = tokenize('u"abc"')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.QUOTE])

    tokens = tokenize('u8"abc"')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.QUOTE])

    tokens = tokenize('U"abc"')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.QUOTE])

    tokens = tokenize('L"abc"')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.QUOTE])

    with pytest.raises(TokenizeError):
        tokenize('"a')

    with pytest.raises(TokenizeError):
        tokenize('a"a')

    with pytest.raises(TokenizeError):
        tokenize('R"a"')

    with pytest.raises(TokenizeError):
        tokenize('R"(a"')


def test_number():
    tokens = tokenize('0')
    check_tokens(tokens, [TokenType.NUMBER])
    assert str(tokens[1]) == '0'

    tokens = tokenize('123')
    check_tokens(tokens, [TokenType.NUMBER])
    assert str(tokens[1]) == '123'

    tokens = tokenize('1\'23')
    check_tokens(tokens, [TokenType.NUMBER])
    assert str(tokens[1]) == '1\'23'

    tokens = tokenize(' 1234567890 ')
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.NUMBER, TokenType.WHITESPACE])
    assert str(tokens[2]) == "1234567890"

    tokens = tokenize("001.1")
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize("001e1")
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0x')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('1xx13b')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize(".1")
    check_tokens(tokens, [TokenType.NUMBER])
    assert str(tokens[1]) == ".1"

    tokens = tokenize('.123')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('123.345')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('123.345e3')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('123e+4')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('123e-4')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('12\'3.345')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('01e1')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('01.1')
    check_tokens(tokens, [TokenType.NUMBER])

    with pytest.raises(TokenizeError):
        tokenize('12\'')

    tokens = tokenize('0x1')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0xFp1')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0x02\'3')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0x023p+1')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0xABCDEFabcdef')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0x0.123p-1')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0x0.e2\'3p-1\'0')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0x0.p1')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0xa.Ap1')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0xA.ap1')
    check_tokens(tokens, [TokenType.NUMBER])

    with pytest.raises(TokenizeError):
        tokenize('0x12\'')

    tokens = tokenize('0x0.123')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0x0.123p-A')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0b1')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0b01')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0b010101')
    check_tokens(tokens, [TokenType.NUMBER])

    with pytest.raises(TokenizeError):
        tokenize('0b01\'')

    tokens = tokenize('01')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0\'1')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0012345\'67')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('01x')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('0012345\'68')
    check_tokens(tokens, [TokenType.NUMBER])

    tokens = tokenize('12\'d.z\'.x1.\'1')
    check_tokens(tokens, [TokenType.NUMBER])


def test_preprocessor():
    tokens = tokenize("#")
    check_tokens(tokens, [TokenType.PREPROCESSOR])

    tokens = tokenize("#\n ")
    check_tokens(tokens, [TokenType.PREPROCESSOR, TokenType.WHITESPACE])

    tokens = tokenize("# /**/\n")
    check_tokens(tokens, [TokenType.PREPROCESSOR])

    tokens = tokenize("#pragma")
    check_tokens(tokens, [TokenType.PREPROCESSOR])

    tokens = tokenize(" #pragma")
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.PREPROCESSOR])

    tokens = tokenize('#define')
    check_tokens(tokens, [TokenType.PREPROCESSOR])

    tokens = tokenize('#include "abc" ')
    check_tokens(tokens, [TokenType.PREPROCESSOR])

    tokens = tokenize('#include "abc\\"" ')
    check_tokens(tokens, [TokenType.PREPROCESSOR])

    tokens = tokenize('#include /*123*/ <abc> ')
    check_tokens(tokens, [TokenType.PREPROCESSOR])

    tokens = tokenize('#define a(x) auto a##x = #x')
    check_tokens(tokens, [TokenType.PREPROCESSOR])

    tokens = tokenize('#define eprintf(format, ...) fprintf (stderr, format, __VA_ARGS__)')
    check_tokens(tokens, [TokenType.PREPROCESSOR])

    tokens = tokenize('# /* abc */ define  /* test */')
    check_tokens(tokens, [TokenType.PREPROCESSOR])

    with pytest.raises(TokenizeError):
        tokenize('#include "abc\\" ')

    with pytest.raises(TokenizeError):
        tokenize('#include <abc')

    with pytest.raises(TokenizeError):
        tokenize('#include ')


def test_remaining():
    tokens = tokenize('abc')
    check_tokens(tokens, [TokenType.REMAINING])
    assert str(tokens[1]) == 'abc'

    tokens = tokenize('abc ')
    check_tokens(tokens, [TokenType.REMAINING, TokenType.WHITESPACE])
    assert str(tokens[1]) == 'abc'

    tokens = tokenize(' abc ')
    check_tokens(tokens, [TokenType.WHITESPACE, TokenType.REMAINING, TokenType.WHITESPACE])
    assert str(tokens[2]) == 'abc'

    tokens = tokenize('_ab_c')
    check_tokens(tokens, [TokenType.REMAINING])
    assert str(tokens[1]) == '_ab_c'

    for symbol in "+-*/%<>&!=?.,[]{}():|;~^":
        tokens = tokenize(symbol)
        check_tokens(tokens, [TokenType.REMAINING])

    tokens = tokenize('kwqjj8a8gja98gj9\b\1\¹23')
    check_tokens(tokens, [TokenType.REMAINING])
