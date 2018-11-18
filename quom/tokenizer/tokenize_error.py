from ..utils.iterable import Iterator


class TokenizeError(Exception):
    def __init__(self, msg: str, it: Iterator):
        super().__init__(msg)
        self.it = it
