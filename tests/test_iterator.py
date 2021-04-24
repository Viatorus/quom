from quom.tokenizer.iterator import RawIterator, LineWrapIterator, Span


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

    it = RawIterator('a\\\r\\\r\nb')
    check_iterator(it, 'a\\\r\\\r\nb')

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
    it = LineWrapIterator('ab')
    check_iterator(it, 'ab')

    it = LineWrapIterator('a\rb')
    check_iterator(it, 'a\rb')

    it = LineWrapIterator('a\r\nb')
    check_iterator(it, 'a\r\nb')

    it = LineWrapIterator('a\\\r\nb')
    check_iterator(it, 'ab')

    it = LineWrapIterator('a\\\nb')
    check_iterator(it, 'ab')

    it = LineWrapIterator('a\\\rb')
    check_iterator(it, 'ab')

    it = LineWrapIterator('a\\\\\nb')
    check_iterator(it, 'a\\b')

    it = LineWrapIterator('a\\\r\\\r\nb')
    check_iterator(it, 'ab')

    it = LineWrapIterator('a\\b')
    check_iterator(it, 'a\\b')

    it = LineWrapIterator('"\\a')
    check_iterator(it, '"\\a')

    it = LineWrapIterator('\\\\')
    check_iterator(it, '\\\\')

    it = LineWrapIterator('\\')
    check_iterator(it, '\\')

    it = LineWrapIterator('\\\n')
    check_iterator(it, '\0')

    it = LineWrapIterator('a')
    assert it.lookahead == '\0'

    it = LineWrapIterator('\\')
    assert it.lookahead == '\0'

    it = LineWrapIterator('\\\na')
    assert it.lookahead == '\0'

    it = LineWrapIterator('')
    assert it.lookahead == '\0'

    it = LineWrapIterator('a\\\n')
    assert it.lookahead == '\0'


def test_copy():
    it1 = LineWrapIterator('ab')
    assert it1.curr == 'a'

    it2 = it1.copy()
    it2.next()
    assert it1.curr == 'a'
    assert it2.curr == 'b'

    it1.next()
    assert it1.curr == 'b'
    assert it2.curr == 'b'


def test_iterator_casting():
    it = LineWrapIterator('a\\\r\\b\\\nc')
    assert it.curr == 'a'

    it = LineWrapIterator(it)
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
    it1 = LineWrapIterator('abc')
    assert ''.join(it1) == 'abc'
    assert ''.join(it1) == 'abc'

    it2 = it1.copy()
    it2.next()
    assert ''.join(it2) == 'bc'
    assert ''.join(it2) == 'bc'

    it1 = LineWrapIterator('a ')
    it2 = it1.copy()
    it2.next()

    span = Span(it1, it2)
    assert ''.join(span) == 'a'
    assert ''.join(span) == 'a'
