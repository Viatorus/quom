import re
import shutil
from io import StringIO
from pathlib import Path
from typing import TextIO

from .tokenizer import tokenize, Token, CommentToken, PreprocessorToken, PreprocessorIfNotDefinedToken, \
    PreprocessorDefineToken, PreprocessorEndIfToken, PreprocessorIncludeToken, PreprocessorPragmaOnceToken, \
    RemainingToken


class Quom:
    def __init__(self, src_file_path: Path, dst: TextIO, stitch_format: str, include_guards_format: str):
        self.__dst = dst
        self.__stitch_marker = stitch_format
        self.__include_guards_format = re.compile(include_guards_format) if include_guards_format else None
        self.__processed_files = set()
        self.__units = StringIO()

        self.__process_file(src_file_path)

    def __process_file(self, file_path: Path, is_compilation_unit: bool = False):
        # Skip already processed files.
        if file_path in self.__processed_files:
            return
        self.__processed_files.add(file_path)

        with file_path.open() as file:
            tokens = tokenize(file.read())

        for token in tokens:
            # Find local includes.
            if isinstance(token, PreprocessorIncludeToken) and token.is_local_include:
                self.__process_file(file_path.parent / str(token.path))
            else:
                self._write(token, is_compilation_unit)

        if not is_compilation_unit:
            unit_file_path = self.__get_compilation_unit(file_path)
            if unit_file_path:
                self.__process_file(unit_file_path, True)

    def _write(self, token: Token, is_compilation_unit: bool = False):
        dst = self.__dst if not is_compilation_unit else self.__units

        if self.__is_pragma_once_or_include_quard(token):
            return

        # Write compilation units on stitch position.
        if isinstance(token, CommentToken) and str(token.content).strip() == self.__stitch_marker:
            self.__units.seek(0)
            shutil.copyfileobj(self.__units, self.__dst, - 1)
            self.__units = StringIO()
            return

        # Write token.
        dst.write(str(token.raw))

    def __is_pragma_once_or_include_quard(self, token: Token):
        if isinstance(token, PreprocessorToken):
            if isinstance(token, PreprocessorPragmaOnceToken):
                return True
            if self.__include_guards_format is None:
                return False
            if isinstance(token, (PreprocessorIfNotDefinedToken, PreprocessorDefineToken)):
                # Find first remaining token matching the include guard format.
                remaining_token = next(
                    subtoken for subtoken in token.preprocessor_tokens if isinstance(subtoken, RemainingToken))
                if remaining_token and self.__include_guards_format.match(str(remaining_token).strip()):
                    return True
            if isinstance(token, PreprocessorEndIfToken):
                # Find first comment token matching the include guard format.
                comment_token = next(
                    subtoken for subtoken in token.preprocessor_tokens if isinstance(subtoken, CommentToken))
                if comment_token and self.__include_guards_format.match(str(comment_token.content).strip()):
                    return True
        return False

    def __get_compilation_unit(self, header_file_path: Path):
        # Checks if a equivalent compilation unit exits.
        for extension in ['.c', '.cpp', '.cxx', '.cc', '.c++', '.cp']:
            file_path = header_file_path.with_suffix(extension)
            if file_path.exists():
                return file_path
        return None
