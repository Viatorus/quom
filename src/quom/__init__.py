# flake8: noqa Q003
from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

from . import tokenizer
from .quom import Quom
from .quom_error import QuomError

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'quom'
    __version__ = version(dist_name)
except PackageNotFoundError:
    __version__ = 'unknown'  # pragma: no cover
finally:
    del version, PackageNotFoundError
