import shutil
from io import StringIO
from pathlib import Path
from typing import List, TextIO

from .tokenizer import tokenize, Token, PreprocessorIncludeToken, PreprocessorPragmaOnceToken, CommentToken


def find_all_local_includes(tokens: List[Token]):
    includes = set()
    for i, token in enumerate(tokens):
        if not isinstance(token, PreprocessorIncludeToken):
            continue
        if token.is_local_include is False:
            continue
        includes.add(i)
    return includes


class Quom:
    def __init__(self, src_file_path: Path, dst: TextIO, stitch_marker: str):
        self.__dst = dst
        self.__stitch_marker = stitch_marker
        self._processed_files = set()
        self.__units = StringIO()

        self.__process_root_file(src_file_path)

    def __process_root_file(self, file_path: Path):
        self._processed_files.add(file_path)

        with file_path.open() as file:
            tokens = tokenize(file.read())

        prev = 0
        for i in find_all_local_includes(tokens):
            # Write all tokens before include.
            self._write(tokens[prev:i])
            prev = i + 1
            # Process include.
            self.__process_file(file_path.parent / str(tokens[i].path))
        # Write all tokens after last include.
        self._write(tokens[prev:])

        unit_file_path = self.__get_compilation_unit(file_path)
        if unit_file_path:
            self.__process_file(unit_file_path, True)

    def _write(self, tokens, is_compilation_unit: bool = False):
        dst = self.__dst if not is_compilation_unit else self.__units

        for token in tokens:
            # Write compilation units.
            if isinstance(token, CommentToken) and str(token.content).strip() == self.__stitch_marker:
                self.__units.seek(0)
                shutil.copyfileobj(self.__units, self.__dst, - 1)
                self.__units = StringIO()
            # Write tokens without pragma once.
            elif not isinstance(token, PreprocessorPragmaOnceToken):
                dst.write(str(token))

    def __get_compilation_unit(self, header_file_path: Path):
        # Check if a equivalent compilation unit exits.
        for extension in ['.c', '.cpp', '.cxx', '.cc', '.c++', '.cp']:
            file_path = header_file_path.with_suffix(extension)
            if file_path.exists():
                return file_path
        return None

    def __process_file(self, file_path: Path, is_compilation_unit: bool = False):
        # Skip already processed files.
        if file_path in self._processed_files:
            return
        self._processed_files.add(file_path)

        with file_path.open() as file:
            tokens = tokenize(file.read())

        prev = 0
        for i in find_all_local_includes(tokens):
            # Write all tokens before include.
            self._write(tokens[prev:i], is_compilation_unit)
            prev = i + 1
            # Process include.
            self.__process_file(file_path.parent / str(tokens[i].path))
        # Write all tokens after last include.
        self._write(tokens[prev:], is_compilation_unit)

        if not is_compilation_unit:
            unit_file_path = self.__get_compilation_unit(file_path)
            if unit_file_path:
                self.__process_file(unit_file_path, True)
