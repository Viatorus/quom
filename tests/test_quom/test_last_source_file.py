from io import StringIO
from pathlib import Path

from quom import Quom

FILE_MAIN_HPP = """\
#pragma once

#ifndef FOOBAR_HPP
#define FOOBAR_HPP

#include "foo.hpp"

#endif // FOOBAR_HPP
"""

FILE_FOO_HPP = """\
#pragma once

# /* */ ifndef /*123*/ FOOBAR_FOO_HPP
#define FOOBAR_FOO_HPP // abc

#include <iostream>

extern int foo;

#endif // FOOBAR_FOO_HPP
"""

FILE_FOO_CPP = """\
#include "foo.hpp"

#include <algorithm>

int foo = 42;"""

RESULT_NORMAL = """\
#pragma once

#ifndef FOOBAR_HPP
#define FOOBAR_HPP

# /* */ ifndef /*123*/ FOOBAR_FOO_HPP
#define FOOBAR_FOO_HPP // abc

#include <iostream>

extern int foo;

#endif // FOOBAR_FOO_HPP

#endif // FOOBAR_HPP

#include <algorithm>

int foo = 42;
"""

RESULT_NORMAL_WITHOUT_TRIM = """\
#pragma once

#ifndef FOOBAR_HPP
#define FOOBAR_HPP



# /* */ ifndef /*123*/ FOOBAR_FOO_HPP
#define FOOBAR_FOO_HPP // abc

#include <iostream>

extern int foo;

#endif // FOOBAR_FOO_HPP


#endif // FOOBAR_HPP


#include <algorithm>

int foo = 42;
"""


def init():
    with open('main.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_MAIN_HPP)

    with open('foo.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_FOO_HPP)

    with open('foo.cpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_FOO_CPP)


def test_normal(fs):
    init()

    dst = StringIO()
    Quom(Path('main.hpp'), dst)

    assert dst.getvalue() == RESULT_NORMAL


def test_normal_without_trim(fs):
    init()

    dst = StringIO()
    Quom(Path('main.hpp'), dst, trim=False)

    assert dst.getvalue() == RESULT_NORMAL_WITHOUT_TRIM


def test_without_newline_at_end(fs):
    with open('main.hpp', 'w+', encoding='utf-8') as file:
        file.write('int a;')

    dst = StringIO()
    Quom(Path('main.hpp'), dst)

    assert dst.getvalue() == 'int a;'
