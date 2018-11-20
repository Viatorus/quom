from .tokenize_error import TokenizeError


class Iterator(object):
    def __init__(self, src):
        self._src = src
        self._length = len(src)

        self._prv = -1
        self._crr = -1
        self._nxt = -1

        if self._length == 0 or self._src[-1] != '\n':
            self._src += '\n'
        if self._length == 0:
            return

        # Initialize curr and next.
        self.step()

        if self.crr == '"' or self.crr == '\'':
            self.step(escape=True)
        else:
            self.step()

    @property
    def prv(self):
        if 0 <= self._prv < self._length:
            c = self._src[self._prv]
            return c if c != '\r' else '\n'
        return None

    @property
    def crr(self):
        if self._crr < self._length:
            c = self._src[self._crr]
            return c if c != '\r' else '\n'

    @property
    def nxt(self):
        if self._nxt < self._length:
            c = self._src[self._nxt]
            return c if c != '\r' else '\n'
        return None

    def step(self, escape=False, ignore_line_wrapping=False):
        if ignore_line_wrapping:
            pass
            return

        self._prv = self._crr
        self._crr = self._nxt

        if self._nxt + 1 >= len(self._src):
            self._nxt = len(self._src)
            return

        src = self._src
        nxt = self._nxt + 1
        self._nxt = self._length

        # Get next character, but:
        # * skip \r followed by an \n
        # * skip line wrapping (single \\ followed by \r or \n)
        while nxt < self._length:
            if src[nxt] == '\r':
                if src[nxt + 1] == '\n':
                    nxt += 1
                break
            if src[nxt] == '\\':
                # Escaped \\.
                if src[nxt + 1] == '\\':
                    nxt += 1
                elif src[nxt + 1] == '\r':
                    nxt += 2
                    if src[nxt] == '\n':
                        nxt += 1
                    continue
                elif src[nxt + 1] == '\n':
                    nxt += 2
                    continue
                elif not escape:
                    raise TokenizeError('Stray \'\\\'  in program.')
            break
        self._nxt = nxt
