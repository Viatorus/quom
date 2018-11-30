import re
import shutil
from io import StringIO
from pathlib import Path
from typing import TextIO

from .tokenizer import tokenize, Token, CommentToken, PreprocessorToken, PreprocessorIfNotDefinedToken, \
    PreprocessorDefineToken, PreprocessorEndIfToken, PreprocessorIncludeToken, PreprocessorPragmaOnceToken, \
    RemainingToken, LinebreakWhitespaceToken, StartToken, EndToken

CONTINUOUS_LINE_BREAK_START = 0
CONTINUOUS_BREAK_REACHED = 3


class Quom:
    def __init__(self, src_file_path: Path, dst: TextIO, stitch_format: str, include_guards_format: str, trim: bool):
        self.__dst = dst
        self.__dst_units = StringIO()
        self.__stitch_format = stitch_format
        self.__include_guards_format = re.compile(include_guards_format) if include_guards_format else None
        self.__trim = trim
        self.__processed_files = set()

        self.__cont_lb = CONTINUOUS_BREAK_REACHED
        self.__cont_lb_units = CONTINUOUS_BREAK_REACHED

        self.__process_file(src_file_path, False)

    def __process_file(self, file_path: Path, is_compilation_unit: bool):
        # Skip already processed files.
        if file_path in self.__processed_files:
            return
        self.__processed_files.add(file_path)

        with file_path.open() as file:
            tokens = tokenize(file.read())

        for token in tokens:
            # Find local includes.
            if isinstance(token, PreprocessorIncludeToken) and token.is_local_include:
                self.__process_file(file_path.parent / str(token.path), is_compilation_unit)
                # Write includes line break token if any.
                token = token.preprocessor_tokens[-1]
                if isinstance(token, LinebreakWhitespaceToken):
                    self.__write(token, is_compilation_unit)
            else:
                self.__write(token, is_compilation_unit)

        unit_file_path = self.__get_compilation_unit(file_path)
        if unit_file_path:
            self.__process_file(unit_file_path, True)

    def __write(self, token: Token, is_compilation_unit: bool):
        dst = self.__dst if not is_compilation_unit else self.__dst_units

        if isinstance(token, StartToken) or isinstance(token, EndToken):
            return

        if self.__is_pragma_once_or_include_guard(token):
            token = token.preprocessor_tokens[-1]
            if not isinstance(token, LinebreakWhitespaceToken):
                return

        # Write compilation units on stitch position.
        if isinstance(token, CommentToken) and str(token.content).strip() == self.__stitch_format:
            self.__dst_units.seek(0)
            shutil.copyfileobj(self.__dst_units, self.__dst, - 1)
            self.__dst_units = StringIO()
            self.__cont_lb = CONTINUOUS_LINE_BREAK_START
            self.__cont_lb_units = CONTINUOUS_BREAK_REACHED
            return

        if self.__trim and self.__continuous_line_break_reached(token, is_compilation_unit):
            return

        # Write token.
        dst.write(str(token.raw))

    def __is_pragma_once_or_include_guard(self, token: Token):
        if isinstance(token, PreprocessorToken):
            if isinstance(token, PreprocessorPragmaOnceToken):
                return True
            if self.__include_guards_format is None:
                return False
            if isinstance(token, (PreprocessorIfNotDefinedToken, PreprocessorDefineToken)):
                # Find first remaining token matching the include guard format.
                remaining_token = next(
                    (subtoken for subtoken in token.preprocessor_tokens[1:] if isinstance(subtoken, RemainingToken)),
                    None)
                if remaining_token and self.__include_guards_format.match(str(remaining_token).strip()):
                    return True
            if isinstance(token, PreprocessorEndIfToken):
                # Find first comment token matching the include guard format.
                comment_token = next(
                    (subtoken for subtoken in token.preprocessor_tokens[1:] if isinstance(subtoken, CommentToken)),
                    None)
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

    def __continuous_line_break_reached(self, token: Token, is_compilation_unit: bool):
        cont_lb = self.__cont_lb if not is_compilation_unit else self.__cont_lb_units

        if isinstance(token, LinebreakWhitespaceToken):
            cont_lb += 1
        elif isinstance(token, PreprocessorToken) and isinstance(token.preprocessor_tokens[-1],
                                                                 LinebreakWhitespaceToken):
            cont_lb = CONTINUOUS_LINE_BREAK_START + 1
        else:
            cont_lb = CONTINUOUS_LINE_BREAK_START

        if not is_compilation_unit:
            self.__cont_lb = cont_lb
        else:
            self.__cont_lb_units = cont_lb

        return cont_lb >= CONTINUOUS_BREAK_REACHED
