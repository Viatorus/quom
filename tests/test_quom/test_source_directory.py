import os
from io import StringIO
from pathlib import Path

import pytest

from quom import Quom, QuomError

FILE_MAIN_HPP = """
int foo = 3;

int foo();
"""

FILE_MAIN_CPP = """
int foo() { return 42; }
"""

RESULT = """
int foo = 3;

int foo();

int foo() { return 42; }
"""


def test_source_directory(fs):
    os.makedirs('include/')
    os.makedirs('src/')

    with open('include/main.hpp', 'w+') as file:
        file.write(FILE_MAIN_HPP)

    with open('src/main.cpp', 'w+') as file:
        file.write(FILE_MAIN_CPP)

    dst = StringIO()
    Quom(Path('include/main.hpp'), dst, source_directories=[Path('src').resolve()])
    assert dst.getvalue() == RESULT

    dst = StringIO()
    Quom(Path('include/main.hpp'), dst, source_directories=[Path('../src')])
    assert dst.getvalue() == RESULT
