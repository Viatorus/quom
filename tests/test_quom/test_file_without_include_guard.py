from pathlib import Path

from quom.__main__ import main

FILE_FOO_HPP = """
int VAR_NAME;
#undef VAR_NAME
"""

FILE_MAIN_CPP = """
#define VAR_NAME a
#include "foo.hpp"
#define VAR_NAME b
#include "foo.hpp"
"""

RESULT = """
#define VAR_NAME a

int VAR_NAME;
#undef VAR_NAME

#define VAR_NAME b

int VAR_NAME;
#undef VAR_NAME

"""


def test_file_without_include_guard(fs):
    with open('main.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_MAIN_CPP)

    with open('foo.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_FOO_HPP)

    main(['main.hpp', 'result.hpp'])
    assert Path('result.hpp').read_text() == RESULT
