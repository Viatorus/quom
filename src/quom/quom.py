import os
import re
from pathlib import Path
from queue import Queue
from typing import TextIO, Union, List

from .quom_error import QuomError
from .tokenizer import tokenize, Token, CommentToken, PreprocessorToken, PreprocessorIfNotDefinedToken, \
    PreprocessorDefineToken, PreprocessorEndIfToken, PreprocessorIncludeToken, PreprocessorPragmaOnceToken, \
    RemainingToken, LinebreakWhitespaceToken, EmptyToken, StartToken, EndToken, WhitespaceToken

CONTINUOUS_LINE_BREAK_START = 0
CONTINUOUS_BREAK_REACHED = 3
SOURCE_FILE_EXTENSIONS = ['.c', '.cpp', '.cxx', '.cc', '.c++', '.cp', '.C']


def find_token(tokens: List[Token], token_type: any):
    for i, token in enumerate(tokens):
        if isinstance(token, token_type):
            return i, token
    return None, None


def contains_only_whitespace_and_comment_tokens(tokens: List[Token]):
    for token in tokens:
        if not isinstance(token, (WhitespaceToken, CommentToken, EndToken)):
            return False
    return True


class Quom:
    def __init__(self, src_file_path: Union[Path, str], dst: TextIO, stitch_format: str = None,
                 include_guard_format: str = None, trim: bool = True,
                 include_directories: List[Union[Path, str]] = None,
                 relative_source_directories: List[Union[Path]] = None,
                 source_directories: List[Union[Path]] = None,
                 encoding: str = 'utf-8'):
        self.__dst = dst
        self.__stitch_format = stitch_format
        self.__include_guard_format = re.compile('^{}$'.format(include_guard_format)) if include_guard_format else None
        self.__trim = trim
        self.__include_directories = [Path(x) for x in include_directories] if include_directories else []
        self.__relative_source_directories = relative_source_directories if relative_source_directories else [] \
            if source_directories else [Path('.')]
        self.__source_directories = source_directories if source_directories else [Path('.')]
        self.__encoding = encoding

        self.__processed_files = set()
        self.__source_files = Queue()
        self.__cont_lb = CONTINUOUS_LINE_BREAK_START
        self.__used_linesep = None
        self.__prev_token = EmptyToken()

        self.__process_file(Path(), src_file_path, False, True)

        if not self.__source_files.empty():
            if stitch_format is not None:
                raise QuomError('Couldn\'t stitch source files. The stitch location "{}" was not found.'
                                .format(stitch_format))
            while not self.__source_files.empty():
                self.__process_file(Path(), self.__source_files.get(), True)
                self.__write_line_break_if_missing()

    def __process_file(self, relative_path: Path, include_path: Path, is_source_file: bool,
                       is_main_header=False):
        # First check if file exists relative.
        file_path = relative_path / include_path
        if not file_path.exists():
            # Otherwise search in include directories.
            for include_directory in self.__include_directories:
                file_path = include_directory / include_path
                if file_path.exists():
                    break
            else:
                raise QuomError('Include not found: "{}"'.format(include_path))

        # Skip already processed files.
        file_path = file_path.resolve()
        if file_path in self.__processed_files:
            return

        # Tokenize the file.
        tokens = tokenize(file_path.read_text(encoding=self.__encoding))

        # Add to processed files.
        if is_main_header or self.__has_guard(tokens):
            self.__processed_files.add(file_path)

        for token in tokens:
            # Find local includes.
            token = self.__scan_for_include(file_path, token, is_source_file)
            if not token or self.__scan_for_source_files_stitch(token):
                continue

            self.__write_token(token, is_main_header)

        file_path = self.__find_possible_source_file(file_path)
        if file_path:
            self.__source_files.put(file_path)

    def __write_token(self, token: Token, is_main_header: bool):
        if isinstance(token, StartToken) or isinstance(token, EndToken):
            return

        if (not is_main_header and self.__is_pragma_once(token)) or self.__is_include_guard(token):
            token = token.preprocessor_tokens[-2]
            if not isinstance(token, LinebreakWhitespaceToken):
                return

        if self.__is_cont_line_break(token):
            return

        # Write token and store.
        self.__dst.write(str(token.raw))
        self.__prev_token = token

    def __has_guard(self, tokens: List[Token]):
        for token in tokens:
            if self.__is_pragma_once(token) or self.__is_include_guard(token):
                return True
        return False

    @staticmethod
    def __is_pragma_once(token: Token):
        if isinstance(token, PreprocessorPragmaOnceToken):
            return True
        return False

    def __is_include_guard(self, token: Token):
        if self.__include_guard_format is None:
            return False

        if isinstance(token, (PreprocessorIfNotDefinedToken, PreprocessorDefineToken)):
            # Find first remaining token matching the include guard format.
            i, remaining_token = find_token(token.preprocessor_arguments, RemainingToken)
            if remaining_token and self.__include_guard_format.match(str(remaining_token).strip()) and \
                    contains_only_whitespace_and_comment_tokens(token.preprocessor_arguments[i + 1:]):
                return True
        elif isinstance(token, PreprocessorEndIfToken):
            # Find first comment token matching the include guard format.
            i, comment_token = find_token(token.preprocessor_arguments, CommentToken)
            if comment_token and self.__include_guard_format.match(str(comment_token.content).strip()) and \
                    contains_only_whitespace_and_comment_tokens(token.preprocessor_arguments[i + 1:]):
                return True
        return False

    def __find_possible_source_file(self, header_file_path: Path) -> Union[Path, None]:
        if header_file_path.suffix in SOURCE_FILE_EXTENSIONS:
            return

        # Checks if a equivalent compilation unit exits.
        for extension in SOURCE_FILE_EXTENSIONS:
            for src_dir in self.__relative_source_directories:
                file_path = (header_file_path.parent / src_dir / header_file_path.name).with_suffix(extension)
                if file_path.exists():
                    return file_path
            for src_dir in self.__source_directories:
                file_path = (src_dir / header_file_path.name).with_suffix(extension).resolve()
                if file_path.exists():
                    return file_path
        return None

    def __scan_for_include(self, file_path: Path, token: Token, is_source_file: bool) -> Union[Token, None]:
        if not isinstance(token, PreprocessorIncludeToken) or not token.is_local_include:
            return token

        self.__process_file(file_path.parent, Path(str(token.path)), is_source_file)
        # Take include tokens line break token if any.
        token = token.preprocessor_tokens[-2]
        if isinstance(token, LinebreakWhitespaceToken):
            return token

        return None

    def __scan_for_source_files_stitch(self, token: Token) -> bool:
        if not isinstance(token, CommentToken) or str(token.content).strip() != self.__stitch_format:
            return False

        while not self.__source_files.empty():
            self.__process_file(Path(), self.__source_files.get(), True)
            self.__write_line_break_if_missing()

        return True

    def __is_cont_line_break(self, token: Token) -> bool:
        # Save a used line break for later.
        if self.__used_linesep is None and isinstance(token, LinebreakWhitespaceToken):
            self.__used_linesep = token.raw

        if not self.__trim:
            return False

        if isinstance(token, LinebreakWhitespaceToken):
            self.__cont_lb += 1
        elif isinstance(token, PreprocessorToken) and isinstance(token.preprocessor_tokens[-2],
                                                                 LinebreakWhitespaceToken):
            self.__cont_lb = CONTINUOUS_LINE_BREAK_START + 1
        else:
            self.__cont_lb = CONTINUOUS_LINE_BREAK_START

        return self.__cont_lb >= CONTINUOUS_BREAK_REACHED

    def __write_line_break_if_missing(self):
        if not isinstance(self.__prev_token, LinebreakWhitespaceToken):
            if self.__used_linesep is None:
                self.__used_linesep = os.linesep  # fallback
            self.__dst.write(self.__used_linesep)
