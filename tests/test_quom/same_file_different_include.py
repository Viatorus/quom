import os
from io import StringIO

from quom import Quom

FILE_FOO_HPP = """
#include "../b/bar.hpp"
"""

FILE_BAR_HPP = """
int foo();
"""

FILE_MAIN_CPP = """
#include "a/foo.hpp"
#include "b/bar.hpp"
"""

RESULT = """

int foo();
"""


def test_same_file_different_include(fs):
    os.makedirs('a')
    os.makedirs('b')

    with open('main.cpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_MAIN_CPP)

    with open('a/foo.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_FOO_HPP)

    with open('b/bar.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_BAR_HPP)

    dst = StringIO()
    Quom('main.cpp', dst)

    assert dst.getvalue() == RESULT
