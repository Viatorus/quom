class Iterator(object):
    def __init__(self, base, pos, length):
        self.base = base
        self.pos = pos
        self.length = length

    def __len__(self):
        return self.length

    def __getitem__(self, pos):
        if isinstance(pos, slice):
            start = self.pos + pos.start if pos.start is not None else self.pos
            length = pos.stop if pos.stop is not None else self.length - 1
            if pos.step and pos.step != 1:
                raise Exception('Slicing steps other than 1 is not supported')
            return Iterator(self.base, start, length)
        if pos >= self.length:
            raise IndexError()
        return self.base[self.pos + pos]

    def __setitem__(self, pos, value):
        self.base[self.pos + pos] = value

    def __add__(self, increment):
        return Iterator(self.base, self.pos + increment, self.length)

    def __sub__(self, decrement):
        return Iterator(self.base, self.pos - decrement, self.length)

    def __iadd__(self, increment):
        self.pos += increment
        return self

    def __isub__(self, decrement):
        self.pos -= decrement
        return self

    def __ne__(self, other: 'Iterator'):
        return self.base != other.base or self.pos != other.pos

    def __eq__(self, other: 'Iterator'):
        return not (self != other)

    def copy(self) -> 'Iterator':
        return Iterator(self.base, self.pos, self.length)


class Iterable(list):
    def begin(self):
        return Iterator(self, 0, len(self))

    def end(self):
        return Iterator(self, len(self), len(self))
