class Iterator(object):
    def __init__(self, base, start, length):
        self.base = base
        self.start = start
        self.length = length

    def __len__(self):
        return self.length

    def __getitem__(self, pos=0):
        if isinstance(pos, slice):
            start = self.start + pos.start if pos.start is not None else self.start
            stop = self.start + pos.stop if pos.stop is not None else self.length - 1
            if pos.step and pos.step != 1:
                raise Exception('Slicing steps other than 1 is not supported')
            return Iterator(self.base, start, stop)
        if pos >= self.length:
            raise IndexError()
        return self.base[self.start + pos]

    def __setitem__(self, pos, value):
        self.base[self.start + pos] = value

    def __add__(self, increment):
        return Iterator(self.base, self.start + increment, self.length)

    def __sub__(self, decrement):
        return Iterator(self.base, self.start - decrement, self.length)

    def __iadd__(self, increment):
        self.start += increment
        return self

    def __isub__(self, decrement):
        self.start -= decrement
        return self

    def __ne__(self, other):
        return self.base != other.base or self.start != other.start

    def __eq__(self, other):
        return not (self != other)

    def copy(self):
        return Iterator(self.base, self.start, self.length)


class Iterable(list):
    def begin(self):
        return Iterator(self, 0, len(self))

    def end(self):
        return Iterator(self, len(self), len(self))
