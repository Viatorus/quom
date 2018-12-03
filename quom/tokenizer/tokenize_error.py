from ..quom_error import QuomError


class TokenizeError(QuomError):
    def __init__(self, msg: str, it=None):
        super().__init__(msg)
        self.it = it
