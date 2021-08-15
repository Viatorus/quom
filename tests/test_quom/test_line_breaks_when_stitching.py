from io import StringIO
from pathlib import Path

from quom import Quom

FILE_MAIN_CPP = """\
#include "a.hpp"
int main() {
    return 0;
}
// Stitch Begin
// End
"""

FILE_A_HPP = 'int a;'

FILE_A_CPP = """\
#include "b.hpp"
#include "c.hpp"
void mid() {}"""

FILE_B_HPP = 'int b;'
FILE_C_HPP = 'int c;'

FILE_B_CPP = """\
#include <b>"""

FILE_C_CPP = """\
#include <c>"""

RESULT = """\
int a;
int main() {
    return 0;
}
// Stitch Begin
// End
int b;
int c;
void mid() {}
#include <b>
#include <c>
"""

RESULT_STITCH = """\
int a;
int main() {
    return 0;
}
int b;
int c;
void mid() {}
#include <b>
#include <c>

// End
"""


def init():
    with open('main.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_MAIN_CPP)

    with open('a.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_A_HPP)

    with open('a.cpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_A_CPP)

    with open('b.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_B_HPP)

    with open('b.cpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_B_CPP)

    with open('c.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_C_HPP)

    with open('c.cpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_C_CPP)


def test_add_line_break_in_stitched_files_if_missing(fs):
    init()

    dst = StringIO()
    Quom(Path('main.hpp'), dst)

    assert dst.getvalue() == RESULT


def test_add_line_break_in_stitched_files_if_missing_at_stitch_location(fs):
    init()

    dst = StringIO()
    Quom(Path('main.hpp'), dst, stitch_format='Stitch Begin')

    assert dst.getvalue() == RESULT_STITCH
