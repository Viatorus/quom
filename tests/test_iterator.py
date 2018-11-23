import pytest

from quom.tokenizer import TokenizeError
from quom.tokenizer.iterator import RawIterator, EscapeIterator, CodeIterator, Span


def check_iterator(it, res):
    crr = '\0'

    for c in res:
        prv = crr
        crr = c

        assert it.prev == prv
        assert it.curr == crr

        it.next()

    assert it.next() is False


def test_raw_iterator():
    it = RawIterator('ab')
    check_iterator(it, 'ab')

    it = RawIterator('a\rb')
    check_iterator(it, 'a\rb')

    it = RawIterator('a\r\nb')
    check_iterator(it, 'a\r\nb')

    it = RawIterator('a\\\r\nb')
    check_iterator(it, 'a\\\r\nb')

    it = RawIterator('a\\\nb')
    check_iterator(it, 'a\\\nb')

    it = RawIterator('a\\\rb')
    check_iterator(it, 'a\\\rb')

    it = RawIterator("a\\\r\\\r\nb")
    check_iterator(it, "a\\\r\\\r\nb")

    it = RawIterator('a\\b')
    check_iterator(it, 'a\\b')

    it = RawIterator('"\\a')
    check_iterator(it, '"\\a')

    it = RawIterator('\\\\')
    check_iterator(it, '\\\\')

    it = RawIterator('\\')
    check_iterator(it, '\\')

    it = RawIterator('\\\n')
    check_iterator(it, '\\\n')

    it = RawIterator('\r')
    check_iterator(it, '\r')

    it = RawIterator('a')
    assert it.lookahead == '\0'

    it = RawIterator('\\')
    assert it.lookahead == '\0'

    it = RawIterator('\\\na')
    assert it.lookahead == '\n'

    it = RawIterator('')
    assert it.lookahead == '\0'


def test_escape_iterator():
    it = EscapeIterator('ab')
    check_iterator(it, 'ab')

    it = EscapeIterator('a\rb')
    check_iterator(it, 'a\rb')

    it = EscapeIterator('a\r\nb')
    check_iterator(it, 'a\r\nb')

    it = EscapeIterator('a\\\r\nb')
    check_iterator(it, 'ab')

    it = EscapeIterator('a\\\nb')
    check_iterator(it, 'ab')

    it = EscapeIterator('a\\\rb')
    check_iterator(it, 'ab')

    it = EscapeIterator('a\\\\\nb')
    check_iterator(it, 'a\\b')

    it = EscapeIterator("a\\\r\\\r\nb")
    check_iterator(it, "ab")

    it = EscapeIterator('a\\b')
    check_iterator(it, 'a\\b')

    it = EscapeIterator('"\\a')
    check_iterator(it, '"\\a')

    it = EscapeIterator('\\\\')
    check_iterator(it, '\\\\')

    it = EscapeIterator('\\')
    check_iterator(it, '\\')

    it = EscapeIterator('\\\n')
    check_iterator(it, '\0')

    it = EscapeIterator('a')
    assert it.lookahead == '\0'

    it = EscapeIterator('\\')
    assert it.lookahead == '\0'

    it = EscapeIterator('\\\na')
    assert it.lookahead == '\0'

    it = EscapeIterator('')
    assert it.lookahead == '\0'


def test_code_iterator():
    it = CodeIterator('ab')
    check_iterator(it, 'ab')

    it = CodeIterator('a\rb')
    check_iterator(it, 'a\rb')

    it = CodeIterator('a\r\nb')
    check_iterator(it, 'a\r\nb')

    it = CodeIterator('a\\\r\nb')
    check_iterator(it, 'ab')

    it = CodeIterator('a\\\nb')
    check_iterator(it, 'ab')

    it = CodeIterator('a\\\rb')
    check_iterator(it, 'ab')

    it = CodeIterator("a\\\r\\\r\nb")
    check_iterator(it, "ab")

    it = CodeIterator('a\\b')
    with pytest.raises(TokenizeError):
        check_iterator(it, 'a\\b')

    it = CodeIterator('"\\a')
    with pytest.raises(TokenizeError):
        check_iterator(it, '"\\a')

    with pytest.raises(TokenizeError):
         CodeIterator('\\\\')

    with pytest.raises(TokenizeError):
        CodeIterator('\\')

    it = CodeIterator('\\\n')
    check_iterator(it, '')

    it = CodeIterator('a')
    assert it.lookahead == '\0'

    it = CodeIterator('\\\na')
    assert it.lookahead == '\0'

    with pytest.raises(TokenizeError):
        CodeIterator('\\a')

    it = CodeIterator('')
    assert it.lookahead == '\0'


def test_copy():
    it1 = CodeIterator('ab')
    assert it1.curr == 'a'

    it2 = it1.copy()
    it2.next()
    assert it1.curr == 'a'
    assert it2.curr == 'b'

    it1.next()
    assert it1.curr == 'b'
    assert it2.curr == 'b'


def test_iterator_casting():
    it = CodeIterator('a\\\r\\b\\\nc')
    assert it.curr == 'a'

    it = EscapeIterator(it)
    it.next()
    assert it.curr == '\\'
    it.next()
    assert it.curr == 'b'

    it = RawIterator(it)
    it.next()
    assert it.curr == '\\'
    it.next()
    assert it.curr == '\n'
    it.next()
    assert it.curr == 'c'


def test_span():
    it1 = CodeIterator('abc')
    assert ''.join(it1) == 'abc'
    assert ''.join(it1) == 'abc'

    it2 = it1.copy()
    it2.next()
    assert ''.join(it2) == 'bc'
    assert ''.join(it2) == 'bc'

    it1 = CodeIterator('a ')
    it2 = it1.copy()
    it2.next()

    span = Span(it1, it2)
    assert ''.join(span) == 'a'
    assert ''.join(span) == 'a'
