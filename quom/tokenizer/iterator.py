import copy
from typing import Union

from .tokenize_error import TokenizeError


class Iterator:
    pass


class Iterable:
    def __init__(self, src):
        self.src = src
        self.length = len(src)
        self.prev = -1
        self.curr = -1


class RawIterator:
    def __init__(self, it: Union[Iterable, str]):
        if isinstance(it, Iterable):
            self._it = it
        elif isinstance(it, RawIterator):
            self._it = it._it
        else:
            self._it = Iterable(it)

    @property
    def prev(self):
        if 0 <= self._it.prev < len(self):
            c = self._it.src[self._it.prev]
            return c if c != '\r' else '\n'
        return None

    @property
    def curr(self):
        if 0 <= self._it.curr < len(self):
            c = self._it.src[self._it.curr]
            return c if c != '\r' else '\n'
        return None

    @property
    def lookahead(self):
        if self._it.curr + 1 >= len(self):
            return None

        nxt = self._step(self._it.src, self._it.curr + 1)
        if 0 <= nxt < len(self):
            c = self._it.src[nxt]
            return c if c != '\r' else '\n'
        return None

    def copy(self):
        tmp = copy.deepcopy(self)
        return tmp

    def has_next(self):
        return self.lookahead is not None

    def __len__(self):
        return self._it.length

    def __iter__(self):
        return self

    def __next__(self):
        self.__step()
        if self._it.curr >= len(self):
            raise StopIteration()
        return self.curr

    def __step(self):
        self._it.prev = self._it.curr

        if self._it.curr + 1 >= len(self._it.src):
            self._it.curr = len(self._it.src)
            return

        self._it.prev = self._it.curr

        src = self._it.src
        nxt = self._it.curr + 1

        self._it.curr = self._step(src, nxt)

    def _step(self, src, nxt):
        # Get next character, but:
        # * skip \r followed by an \n
        if src[nxt] == '\r':
            if nxt + 1 < len(self) and src[nxt + 1] == '\n':
                nxt += 1
        return nxt


class EscapeIterator(RawIterator):
    def _step(self, src, nxt):
        # Get next character, but:
        # * skip \r followed by an \n
        # * do line wrapping (backslash followed by \r and/or \n)
        while nxt < len(self):
            if src[nxt] == '\r':
                if nxt + 1 < len(self) and src[nxt + 1] == '\n':
                    nxt += 1
                break
            if src[nxt] == '\\':
                if nxt + 1 >= len(self):
                    break
                if src[nxt + 1] == '\n':
                    nxt += 2
                    continue
                elif src[nxt + 1] == '\r':
                    nxt += 2
                    if nxt < len(self) and src[nxt] == '\n':
                        nxt += 1
                    continue
            break
        return nxt


class CodeIterator(RawIterator):
    def _step(self, src, nxt):
        # Get next character, but:
        # * skip \r followed by an \n
        # * do line wrapping (backslash followed by \r and/or \n)
        # * no escape sequence allowed
        while nxt < len(self):
            if src[nxt] == '\r':
                if nxt + 1 < len(self) and src[nxt + 1] == '\n':
                    nxt += 1
                break
            if src[nxt] == '\\':
                if nxt + 1 >= len(self):
                    raise TokenizeError('Stray \'\\\' in program.')
                if src[nxt + 1] == '\n':
                    nxt += 2
                    continue
                elif src[nxt + 1] == '\r':
                    nxt += 2
                    if nxt < len(self) and src[nxt] == '\n':
                        nxt += 1
                    continue
                else:
                    raise TokenizeError('Stray \'\\\' in program.')
            break
        return nxt