from .tokenize_error import TokenizeError


class RawIterator:
    def __init__(self, src):
        self._src = src
        self._length = len(src)

        self._prev = -1
        self._curr = -1

    @property
    def prev(self):
        if 0 <= self._prev < self._length:
            c = self._src[self._prev]
            return c if c != '\r' else '\n'
        return None

    @property
    def curr(self):
        if 0 <= self._curr < self._length:
            c = self._src[self._curr]
            return c if c != '\r' else '\n'
        return None

    @property
    def lookahead(self):
        tmp = self.__class__(self._src)
        tmp._prev = self._prev
        tmp._curr = self._curr
        tmp._length = self._length
        return next(tmp)

    def __iter__(self):
        return self

    def __next__(self):
        self.__step()
        if self._curr >= self._length:
            raise StopIteration()
        return self.curr

    def __step(self):
        self._prev = self._curr

        if self._curr + 1 >= len(self._src):
            self._curr = len(self._src)
            return

        self._prev = self._curr

        src = self._src
        nxt = self._curr + 1

        self._curr = self._length
        self._step(src, nxt)

    def _step(self, src, nxt):
        # Get next character, but:
        # * skip \r followed by an \n
        if src[nxt] == '\r':
            if src[nxt + 1] == '\n':
                nxt += 1
        self._curr = nxt


class EscapeIterator(RawIterator):
    def _step(self, src, nxt):
        # Get next character, but:
        # * skip \r followed by an \n
        # * do line wrapping (backslash followed by \r and/or \n)
        while nxt < self._length:
            if src[nxt] == '\r':
                if src[nxt + 1] == '\n':
                    nxt += 1
                break
            if src[nxt] == '\\':
                if nxt + 1 >= self._length:
                    break
                if src[nxt + 1] == '\n':
                    nxt += 2
                    continue
                elif src[nxt + 1] == '\r':
                    nxt += 2
                    if nxt < self._length and src[nxt] == '\n':
                        nxt += 1
                    continue
            break
        self._curr = nxt


class CodeIterator(RawIterator):
    def _step(self, src, nxt):
        # Get next character, but:
        # * skip \r followed by an \n
        # * do line wrapping (backslash followed by \r and/or \n)
        # * no escape sequence allowed
        while nxt < self._length:
            if src[nxt] == '\r':
                if src[nxt + 1] == '\n':
                    nxt += 1
                break
            if src[nxt] == '\\':
                if nxt + 1 >= self._length:
                    raise TokenizeError('Stray \'\\\' in program.')
                if src[nxt + 1] == '\n':
                    nxt += 2
                    continue
                elif src[nxt + 1] == '\r':
                    nxt += 2
                    if nxt < self._length and src[nxt] == '\n':
                        nxt += 1
                    continue
                else:
                    raise TokenizeError('Stray \'\\\' in program.')
            break
        self._curr = nxt
