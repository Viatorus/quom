class Iterator(object):
    def __init__(self, base, pos=0):
        self.base = base
        self.pos = pos

    def __getitem__(self, pos=0):
        return self.base[self.pos + pos]

    def __setitem__(self, pos, value):
        self.base[self.pos + pos] = value

    def __add__(self, increment):
        return Iterator(self.base, self.pos + increment)

    def __sub__(self, decrement):
        return Iterator(self.base, self.pos - decrement)

    def __iadd__(self, increment):
        self.pos += increment
        return self

    def __isub__(self, decrement):
        self.pos -= decrement
        return self

    def __ne__(self, other):
        return self.base != other.base or self.pos != other.pos

    def __eq__(self, other):
        return not (self != other)


class Iterable(list):
    def begin(self):
        return Iterator(self)

    def end(self):
        return Iterator(self, len(self))
