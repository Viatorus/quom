import os
from io import StringIO
from pathlib import Path

from quom import Quom
from quom.__main__ import main

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
    os.makedirs('project/')
    os.chdir('project/')
    os.makedirs('include/')
    os.makedirs('src/')

    with open('include/main.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_MAIN_HPP)

    with open('src/main.cpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_MAIN_CPP)

    dst = StringIO()
    Quom(Path('include/main.hpp'), dst)
    assert dst.getvalue() != RESULT

    dst = StringIO()
    Quom(Path('include/main.hpp'), dst, relative_source_directories=[Path('../src')])
    assert dst.getvalue() == RESULT

    dst = StringIO()
    Quom(Path('include/main.hpp'), dst, source_directories=[Path('src').resolve()])
    assert dst.getvalue() == RESULT

    dst = StringIO()
    Quom(Path('include/main.hpp'), dst, source_directories=[Path('/project/src')])
    assert dst.getvalue() == RESULT

    main(['include/main.hpp', 'result.hpp', '-S', './../src'])
    assert Path('result.hpp').read_text() == RESULT

    main(['include/main.hpp', 'result.hpp', '-S', 'src'])
    assert Path('result.hpp').read_text() == RESULT

    main(['include/main.hpp', 'result.hpp', '-S', '/project/src'])
    assert Path('result.hpp').read_text() == RESULT
