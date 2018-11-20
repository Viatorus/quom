from .tokenize_error import TokenizeError


class Iterator(object):
    def __init__(self, src):
        self._src = src
        self._length = len(src)

        self._prev = -1
        self._curr = -1

        # if self._length == 0 or self._src[-1] != '\n':
        #     self._src += '\n'
        if self._length == 0:
            return

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
        tmp = Iterator(self._src)
        tmp._prev = self._prev
        tmp._curr = self._curr
        tmp._length = self._length
        return next(tmp)

    def __iter__(self):
        return self

    def __next__(self):
        self._step()
        if self._curr >= self._length:
            raise StopIteration()
        return self.curr

    def _step(self, escape_characters=False, ignore_line_wrapping=False):
        self._prev = self._curr

        if self._curr + 1 >= len(self._src):
            self._curr = len(self._src)
            return

        src = self._src
        nxt = self._curr + 1
        self._curr = self._length

        # Get next character, but:
        # * skip \r followed by an \n
        # * skip line wrapping (backslash followed by \r or \n) [ignore_line_wrapping = False]
        # * escape characters followed by \ [escape_characters = True]
        while nxt < self._length:
            if src[nxt] == '\r':
                if src[nxt + 1] == '\n':
                    nxt += 1
                break
            if src[nxt] == '\\':
                # Escaped backslash.
                if not escape_characters and nxt + 1 < self._length and src[nxt + 1] == '\\':
                    nxt += 1
                elif not ignore_line_wrapping and nxt + 1 < self._length and src[nxt + 1] == '\r':
                    nxt += 2
                    if nxt < self._length and src[nxt] == '\n':
                        nxt += 1
                    continue
                elif not ignore_line_wrapping and nxt + 1 < self._length and src[nxt + 1] == '\n':
                    nxt += 2
                    continue
                elif not escape_characters:
                    raise TokenizeError('Stray \'\\\'  in program.')
            break
        self._curr = nxt
