from pathlib import Path
from typing import List

from .tokenizer import tokenize, Token, PreprocessorIncludeToken


def find_all_includes(tokens: List[Token]):
    includes = set()
    for token in tokens:
        if not isinstance(token, PreprocessorIncludeToken):
            continue
        if token.is_local_include is False:
            continue
        includes.add(Path(str(token.path)))
    return includes


class Quom:
    def __init__(self, file_path: Path):
        self._processed_files = set()
        self.__process_root_file(file_path)

    def __process_root_file(self, file_path: Path):
        self._processed_files.add(file_path)

        # Ignore pragma once and include guards in root file.
        with file_path.open() as file:
            tokens = tokenize(file.read())

        for include in find_all_includes(tokens):
            self.__process_file(file_path.parent / include)

    def __process_file(self, file_path: Path):
        if file_path in self._processed_files:
            return
        self._processed_files.add(file_path)

        print(file_path)

        with file_path.open() as file:
            tokens = tokenize(file.read())

        for include in find_all_includes(tokens):
            self.__process_file(file_path.parent / include)

