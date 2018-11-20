import pytest

from quom.tokenizer import TokenizeError
from quom.tokenizer.iterator import Iterator


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


def test_linefeed():
    it = Iterator("a\nb")
    check_iterator(it, "a\nb")


def test_carriage_return():
    it = Iterator("a\rb")
    check_iterator(it, "a\nb")


def test_carriage_return_line_feed():
    it = Iterator("a\r\nb")
    check_iterator(it, "a\nb")


def test_line_wrap():
    it = Iterator("a\\\nb")
    check_iterator(it, "ab")

    it = Iterator("a\\\rb")
    check_iterator(it, "ab")

    it = Iterator("a\\\r\nb")
    check_iterator(it, "ab")

    it = Iterator("a\\\n\\\nb")
    check_iterator(it, "ab")

    it = Iterator("a\\\r\\\nb")
    check_iterator(it, "ab")

    it = Iterator("a\\\r\\\r\nb")
    check_iterator(it, "ab")

    it = Iterator("a\\\\\\\nb")
    check_iterator(it, "a\\b")

    it = Iterator("a\\\\\\\rb")
    check_iterator(it, "a\\b")

    it = Iterator("a\\\\\\\r\n\nb")
    check_iterator(it, "a\\\nb")

    it = Iterator("a\\\\\\\r\n\rb")
    check_iterator(it, "a\\\nb")

    it = Iterator("a\\\\\\\r\n\r\nb")
    check_iterator(it, "a\\\nb")

    it = Iterator("a\\\\b")
    check_iterator(it, "a\\b")

    # Stray at file end
    it = Iterator("a\\\\\\")
    with pytest.raises(TokenizeError):
        check_iterator(it, "a\\")


def test_stray_sequence():
    it = Iterator("ab\\e")
    next(it)
    next(it)
    with pytest.raises(TokenizeError):
        next(it)

    it = Iterator("ab\\e")
    next(it)
    next(it)
    it._step(escape_characters=True)
    assert it.prev == 'b'
    assert it.curr == '\\'

    next(it)

    assert it.prev == '\\'
    assert it.curr == 'e'

    it = Iterator('\\')
    with pytest.raises(TokenizeError):
        next(it)


def test_escape():
    it = Iterator("\"\\a")
    next(it)
    with pytest.raises(TokenizeError):
        next(it)

    it = Iterator('"\\a')
    next(it)
    it._step(escape_characters=True)

    assert it.prev == '"'
    assert it.curr == '\\'

    next(it)

    assert it.prev == '\\'
    assert it.curr == 'a'

    it = Iterator("//\\\nd")
    next(it)
    next(it)

    assert it.prev == '/'
    assert it.curr == '/'

    it._step(escape_characters=True)

    assert it.prev == '/'
    assert it.curr == 'd'

    it = Iterator("//\\\n\\d")
    next(it)
    next(it)

    assert it.prev == '/'
    assert it.curr == '/'

    it._step(escape_characters=True)

    assert it.prev == '/'
    assert it.curr == '\\'

    next(it)

    assert it.prev == '\\'
    assert it.curr == 'd'


def test_ingore_line_wrapping():
    it = Iterator('a\\\nb')
    check_iterator(it, 'ab')

    it = Iterator('a\\\nb')
    next(it)
    it._step(ignore_line_wrapping=True, escape_characters=True)

    assert it.prev == 'a'
    assert it.curr == '\\'

    next(it)

    assert it.prev == '\\'
    assert it.curr == '\n'

    next(it)

    assert it.prev == '\n'
    assert it.curr == 'b'


def test_ingore_line_wrapping_and_escape():
    it = Iterator('a\\\n\\b')
    next(it)
    it._step(ignore_line_wrapping=True, escape_characters=True)

    assert it.prev == 'a'
    assert it.curr == '\\'

    next(it)

    assert it.prev == '\\'
    assert it.curr == '\n'

    it._step(ignore_line_wrapping=True, escape_characters=True)

    assert it.prev == '\n'
    assert it.curr == '\\'

    next(it)

    assert it.prev == '\\'
    assert it.curr == 'b'
