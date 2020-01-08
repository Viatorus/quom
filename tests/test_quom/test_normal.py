from io import StringIO
from pathlib import Path

import pytest

from quom import Quom, QuomError

FILE_MAIN_HPP = """\
#pragma once

#ifndef FOOBAR_HPP
#define FOOBAR_HPP

#include "foo.hpp"

#endif // FOOBAR_HPP

// ~> stitch <~
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

int foo = 42;
"""

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

RESULT_NORMAL_WITHOUT_SOURCES = """\
#pragma once

#ifndef FOOBAR_HPP
#define FOOBAR_HPP

# /* */ ifndef /*123*/ FOOBAR_FOO_HPP
#define FOOBAR_FOO_HPP // abc

#include <iostream>

extern int foo;

#endif // FOOBAR_FOO_HPP

#endif // FOOBAR_HPP
"""

RESULT_WITH_INCLUDE_GUARD_FORMAT = """\
#pragma once

#ifndef FOOBAR_HPP
#define FOOBAR_HPP

#include <iostream>

extern int foo;

#endif // FOOBAR_HPP

#include <algorithm>

int foo = 42;
"""


def init():
    with open('main.hpp', 'w+') as file:
        file.write(FILE_MAIN_HPP)

    with open('foo.hpp', 'w+') as file:
        file.write(FILE_FOO_HPP)

    with open('foo.cpp', 'w+') as file:
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


def test_with_include_guard_format(fs):
    init()

    dst = StringIO()
    Quom(Path('main.hpp'), dst, include_guard_format='FOOBAR_.+_HPP')

    assert dst.getvalue() == RESULT_WITH_INCLUDE_GUARD_FORMAT


def test_with_mismatching_include_guard_format(fs):
    init()

    dst = StringIO()
    Quom(Path('main.hpp'), dst, include_guard_format='FOOBAR_.+_HP')

    assert dst.getvalue() == RESULT_NORMAL


def test_with_mismatching_stitch(fs):
    init()

    dst = StringIO()
    with pytest.raises(QuomError):
        Quom(Path('main.hpp'), dst, stitch_format='~ stitch ~')


def test_with_missing_header_file(fs):
    init()
    Path('foo.hpp').unlink()

    dst = StringIO()
    with pytest.raises(QuomError):
        Quom(Path('main.hpp'), dst)


def test_with_missing_source_file(fs):
    init()
    Path('foo.cpp').unlink()

    dst = StringIO()
    Quom(Path('main.hpp'), dst)

    assert dst.getvalue() == RESULT_NORMAL_WITHOUT_SOURCES
