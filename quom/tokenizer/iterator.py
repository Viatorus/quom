from typing import Union


class Iterator:
    pass


class Span:
    def __init__(self, start: 'RawIterator', end: 'RawIterator' = None):
        self.it = start.copy()
        if end and end._it.curr_pos < len(self.it):
            self._length = end._it.curr_pos
        else:
            self._length = len(self.it)

    def __len__(self):
        return self._length

    def __iter__(self):
        tmp = Span(self.it)
        tmp._length = self._length
        return tmp

    def __next__(self):
        if self.it._it.curr_pos >= len(self):
            raise StopIteration()
        tmp = self.it.curr
        self.it.next()
        return tmp

    def __str__(self):
        return ''.join(self)


class Iterable:
    def __init__(self, src):
        self.src = src
        self.length = len(src)
        self.prev = '\0'
        self.curr = '\0'
        self.curr_pos = -1

    def copy(self):
        tmp = Iterable(self.src)
        tmp.prev = self.prev
        tmp.curr = self.curr
        tmp.curr_pos = self.curr_pos
        return tmp


class RawIterator:
    def __init__(self, it: Union[Iterable, 'RawIterator', str]):
        if isinstance(it, Iterable):
            self._it = it
        elif isinstance(it, RawIterator):
            self._it = it._it
        else:
            self._it = Iterable(it)
        # Init iterator if not already done.
        if self._it.curr_pos == -1:
            self.__step()

    @property
    def prev(self):
        return self._it.prev

    @property
    def curr(self):
        return self._it.curr

    @property
    def lookahead(self):
        if self._it.curr_pos + 1 >= self._it.length:
            return '\0'

        nxt = self._step(self._it.src, self._it.curr_pos + 1)
        if 0 <= nxt < self._it.length:
            return self._it.src[nxt]
        return '\0'

    def copy(self):
        return self.__class__(self._it.copy())

    def __len__(self):
        return self._it.length

    def __iter__(self):
        return Span(self)

    def next(self):
        self.__step()
        return True if self._it.curr != '\0' else False

    def __step(self):
        self._it.prev = self._it.curr

        if self._it.curr_pos + 1 >= self._it.length:
            self._it.curr_pos = self._it.length
            self._it.curr = '\0'
            return

        src = self._it.src
        nxt = self._it.curr_pos + 1

        self._it.curr_pos = self._step(src, nxt)

        if 0 <= self._it.curr_pos < self._it.length:
            self._it.curr = self._it.src[self._it.curr_pos]
        else:
            self._it.curr = '\0'

    def _step(self, src, nxt):
        # Get next character.
        return nxt


class LineWrapIterator(RawIterator):
    def _step(self, src, nxt):
        # Get next character, but:
        # * do line wrapping (backslash followed by \r and/or \n)
        while nxt < self._it.length:
            if src[nxt] == '\\':
                if nxt + 1 >= self._it.length:
                    break
                if src[nxt + 1] == '\n':
                    nxt += 2
                    continue
                elif src[nxt + 1] == '\r':
                    nxt += 2
                    if nxt < self._it.length and src[nxt] == '\n':
                        nxt += 1
                    continue
            break
        return nxt
