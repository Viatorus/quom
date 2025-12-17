from io import StringIO
from pathlib import Path

from quom import Quom

FILE_SIMPLE_FOO_HPP = """\
#ifndef FOOBAR_FOO_HPP
#define FOOBAR_FOO_HPP

int i;

#endif
"""

FILE_SIMPLE_HPP = """\
#ifndef FOOBAR_HPP
#define FOOBAR_HPP

#include "foo.hpp"

#endif
"""

RESULT_SIMPLE = """\
#ifndef FOOBAR_HPP
#define FOOBAR_HPP

int i;

#endif
"""


def test_simple_include_guards(fs):
    with open('foo.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_SIMPLE_FOO_HPP)

    with open('main.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_SIMPLE_HPP)

    dst = StringIO()
    Quom(Path('main.hpp'), dst, include_guard_format='FOOBAR_.+_HPP.*')

    assert dst.getvalue() == RESULT_SIMPLE


FILE_MAIN_HPP = """\
#pragma once

#ifndef FOOBAR_HPP
#define FOOBAR_HPP

#if 1

#include "foo.hpp"

#endif // # if 1

#endif // FOOBAR_HPP
"""

FILE_FOO_HPP = """\
#pragma once

# /* */ ifndef /*123*/ FOOBAR_FOO_HPP
#define FOOBAR_FOO_HPP // abc

#ifndef FOOBAR_BAR_HPP
#define FOOBAR_BAR_HPP

#ifdef 1

#include <iostream>

#endif // # ifdef 1

#endif // not kept

extern int foo;

#endif // not kept
"""

RESULT_COMPLEX = """\
#pragma once

#ifndef FOOBAR_HPP
#define FOOBAR_HPP

#if 1

#ifdef 1

#include <iostream>

#endif // # ifdef 1

extern int foo;

#endif // # if 1

#endif // FOOBAR_HPP
"""


def test_complex_include_guards(fs):
    with open('main.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_MAIN_HPP)

    with open('foo.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_FOO_HPP)

    dst = StringIO()
    Quom(Path('main.hpp'), dst, include_guard_format='FOOBAR_.+_HPP')

    assert dst.getvalue() == RESULT_COMPLEX
