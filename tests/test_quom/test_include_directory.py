import os
from io import StringIO
from pathlib import Path

import pytest

from quom import Quom, QuomError

FILE_MAIN_HPP = """
int foo = 3;

#include "my_lib/core/core.hpp"
#include "my_other_lib/bar.hpp"
"""

FILE_CORE_HPP = """
#pragma once

#include "my_lib/util/foo.hpp"
"""

FILE_CORE_CPP = """
#include "my_lib/core/core.hpp"

int i = 10;
"""

FILE_FOO_HPP = """
#pragma once

int foo();
"""

FILE_FOO_CPP = """
#include "foo.hpp"

int foo() { return 42; }
"""

FILE_BAR_HPP = """
#pragma once

float bar();
"""

FILE_INFO_HPP = """

float f = 0.42;

"""

FILE_BAR_CPP = """
#include "bar.hpp"

#include "info.hpp"

float bar() { return f; }
"""

RESULT = """
int foo = 3;

int foo();

float bar();

int foo() { return 42; }

int i = 10;

float f = 0.42;

float bar() { return f; }
"""


def test_include_directory(fs):
    os.makedirs('include/my_lib/core')
    os.makedirs('include/my_lib/util')
    os.makedirs('include/my_other_lib/')

    with open('include/my_lib/main.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_MAIN_HPP)

    with open('include/my_lib/core/core.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_CORE_HPP)

    with open('include/my_lib/core/core.cpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_CORE_CPP)

    with open('include/my_lib/util/foo.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_FOO_HPP)

    with open('include/my_lib/util/foo.cpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_FOO_CPP)

    with open('include/my_other_lib/bar.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_BAR_HPP)

    with open('include/my_other_lib/bar.cpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_BAR_CPP)

    with open('include/my_other_lib/info.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_INFO_HPP)

    dst = StringIO()

    with pytest.raises(QuomError):
        Quom(Path('include/my_lib/main.hpp'), dst)

    dst = StringIO()

    Quom(Path('include/my_lib/main.hpp'), dst, include_directories=['include/'])

    assert dst.getvalue() == RESULT
