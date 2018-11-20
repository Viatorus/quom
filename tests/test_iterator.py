import pytest

from quom.tokenizer import TokenizeError
from quom.tokenizer.iterator import Iterator


def check_iterator(it, res):
    prv = None
    crr = res[0] if len(res) > 0 else None
    nxt = res[1] if len(res) > 1 else None

    assert it.prv is None
    assert it.crr == crr
    assert it.nxt == nxt

    for c in res[2:]:
        it.step()

        prv = crr
        crr = nxt
        nxt = c

        assert it.prv == prv
        assert it.crr == crr
        assert it.nxt == nxt

    it.step()

    assert it.prv == crr
    assert it.crr == nxt
    assert it.nxt is None

    it.step()

    assert it.prv == nxt
    assert it.crr is None
    assert it.nxt is None

    it.step()

    assert it.prv is None
    assert it.crr is None
    assert it.nxt is None

    it.step()

    assert it.prv is None
    assert it.crr is None
    assert it.nxt is None


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
    check_iterator(it, "a\\")


def test_escape_sequence():
    it = Iterator("ab\\e")
    with pytest.raises(TokenizeError):
        it.step()

    it = Iterator("ab\\e")
    it.step(escape=True)
    assert it.crr == 'b'
    assert it.nxt == '\\'

    it.step()

    assert it.crr == '\\'
    assert it.nxt == 'e'

    # TODO.
    #with pytest.raises(TokenizeError):
    it = Iterator("\"\\a")
