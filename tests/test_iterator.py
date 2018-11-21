import pytest

from quom.tokenizer import TokenizeError
from quom.tokenizer.iterator import RawIterator, EscapeIterator, CodeIterator


def check_iterator(it, res):
    crr = None

    assert it.prev is None
    assert it.curr is None

    for c in res:
        next(it)

        prv = crr
        crr = c

        assert it.prev == prv
        assert it.curr == crr

    with pytest.raises(StopIteration):
        next(it)


def test_raw_iterator():
    it = RawIterator('ab')
    check_iterator(it, 'ab')

    it = RawIterator('a\rb')
    check_iterator(it, 'a\nb')

    it = RawIterator('a\r\nb')
    check_iterator(it, 'a\nb')

    it = RawIterator('a\\\r\nb')
    check_iterator(it, 'a\\\nb')

    it = RawIterator('a\\\nb')
    check_iterator(it, 'a\\\nb')

    it = RawIterator('a\\\rb')
    check_iterator(it, 'a\\\nb')

    it = RawIterator("a\\\r\\\r\nb")
    check_iterator(it, "a\\\n\\\nb")

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

    it = RawIterator('a')
    assert it.lookahead == 'a'

    it = RawIterator('\\')
    assert it.lookahead == '\\'

    it = RawIterator('\\\na')
    assert it.lookahead == '\\'


def test_escape_iterator():
    it = EscapeIterator('ab')
    check_iterator(it, 'ab')

    it = EscapeIterator('a\rb')
    check_iterator(it, 'a\nb')

    it = EscapeIterator('a\r\nb')
    check_iterator(it, 'a\nb')

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
    check_iterator(it, '')

    it = EscapeIterator('a')
    assert it.lookahead == 'a'

    it = EscapeIterator('\\')
    assert it.lookahead == '\\'

    it = EscapeIterator('\\\na')
    assert it.lookahead == 'a'


def test_source_iterator():
    it = CodeIterator('ab')
    check_iterator(it, 'ab')

    it = CodeIterator('a\rb')
    check_iterator(it, 'a\nb')

    it = CodeIterator('a\r\nb')
    check_iterator(it, 'a\nb')

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

    it = CodeIterator('\\\\')
    with pytest.raises(TokenizeError):
        check_iterator(it, ' ')

    it = CodeIterator('\\')
    with pytest.raises(TokenizeError):
        check_iterator(it, ' ')

    it = CodeIterator('\\\n')
    check_iterator(it, '')

    it = CodeIterator('a')
    assert it.lookahead == 'a'

    it = CodeIterator('\\\na')
    assert it.lookahead == 'a'

    it = CodeIterator('\\a')
    with pytest.raises(TokenizeError):
        assert it.lookahead == 'a'
