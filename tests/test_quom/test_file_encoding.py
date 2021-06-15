from pathlib import Path

import pytest

from quom.__main__ import main

FILE_MAIN_HPP = """
int foo(); // qθομ"""


def test_file_encoding_default_encoding(fs):
    with open('main.hpp', 'w+', encoding='utf-8') as file:
        file.write(FILE_MAIN_HPP)

    main(['main.hpp', 'result.hpp'])
    assert Path('result.hpp').read_text('utf-8') == FILE_MAIN_HPP

    with pytest.raises(UnicodeDecodeError):
        Path('result.hpp').read_text('ascii')

    with pytest.raises(UnicodeDecodeError):
        Path('result.hpp').read_text('utf-32')


def test_file_encoding_custom_encoding(fs):
    with open('main.hpp', 'w+', encoding='utf-32') as file:
        file.write(FILE_MAIN_HPP)

    main(['main.hpp', 'result.hpp', '--encoding=utf-32'])

    assert Path('result.hpp').read_text('utf-32') == FILE_MAIN_HPP

    with pytest.raises(UnicodeDecodeError):
        Path('result.hpp').read_text('utf-8')

    with pytest.raises(UnicodeDecodeError):
        main(['main.hpp', 'result.hpp'])

    with pytest.raises(UnicodeDecodeError):
        main(['main.hpp', 'result.hpp', '--encoding=utf-8'])
