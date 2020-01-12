import re
from pathlib import Path
from queue import Queue
from typing import TextIO, Union, List

from .quom_error import QuomError
from .tokenizer import tokenize, Token, CommentToken, PreprocessorToken, PreprocessorIfNotDefinedToken, \
    PreprocessorDefineToken, PreprocessorEndIfToken, PreprocessorIncludeToken, PreprocessorPragmaOnceToken, \
    RemainingToken, LinebreakWhitespaceToken, StartToken, EndToken, WhitespaceToken

CONTINUOUS_LINE_BREAK_START = 0
CONTINUOUS_BREAK_REACHED = 3


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
                 include_guard_format: str = None, trim: bool = True):
        self.__dst = dst
        self.__stitch_format = stitch_format
        self.__include_guard_format = re.compile('^{}$'.format(include_guard_format)) if include_guard_format else None
        self.__trim = trim

        self.__processed_files = set()
        self.__source_files = Queue()
        self.__cont_lb = CONTINUOUS_BREAK_REACHED
        self.__prev_token = None

        self.__process_file(Path(src_file_path), False, True)

        if not self.__source_files.empty():
            if stitch_format is not None:
                raise QuomError('Couldn\'t stitch source files. The stitch location "{}" was not found.'
                                .format(stitch_format))
            while not self.__source_files.empty():
                self.__process_file(self.__source_files.get(), True)
            # Write last token.
            self.__write_token(self.__prev_token, True)

        # Write last token, if not a continuous line break.
        if self.__cont_lb == CONTINUOUS_LINE_BREAK_START or not isinstance(self.__prev_token, LinebreakWhitespaceToken):
            self.__write_token(self.__prev_token, True)

    def __process_file(self, file_path: Path, is_source_file: bool, is_main_header=False):
        # Skip already processed files.
        if file_path in self.__processed_files:
            return
        self.__processed_files.add(file_path)

        try:
            with file_path.open() as file:
                tokens = tokenize(file.read())
        except FileNotFoundError:
            raise QuomError('File not found: \'{}\''.format(file_path))

        for token in tokens:
            # Find local includes.
            token = self.__scan_for_include(file_path, token, is_source_file)
            if not token or self.__scan_for_source_files_stitch(token):
                continue

            self.__write_token(token, is_main_header)

        self.__find_possible_source_file(file_path)

    def __write_token(self, token: Token, is_main_header: bool):
        if isinstance(token, StartToken) or isinstance(token, EndToken):
            return

        if (not is_main_header and self.__is_pragma_once(token)) or self.__is_include_guard(token):
            token = token.preprocessor_tokens[-2]
            if not isinstance(token, LinebreakWhitespaceToken):
                return

        if self.__is_cont_line_break(token):
            return

        # Write previous token, store current.
        if self.__prev_token:
            self.__dst.write(str(self.__prev_token.raw))
        self.__prev_token = token

    def __is_pragma_once(self, token: Token):
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

    def __find_possible_source_file(self, header_file_path: Path):
        if header_file_path.suffix in ['.c', '.cpp', '.cxx', '.cc', '.c++', '.cp', '.C']:
            return

        # Checks if a equivalent compilation unit exits.
        for extension in ['.c', '.cpp', '.cxx', '.cc', '.c++', '.cp', '.C']:
            file_path = header_file_path.with_suffix(extension)
            if file_path.exists():
                self.__source_files.put(file_path)
                break

    def __scan_for_include(self, file_path: Path, token: Token, is_source_file: bool) -> Union[Token, None]:
        if not isinstance(token, PreprocessorIncludeToken) or not token.is_local_include:
            return token

        self.__process_file(file_path.parent / str(token.path), is_source_file)
        # Take include tokens line break token if any.
        token = token.preprocessor_tokens[-2]
        if isinstance(token, LinebreakWhitespaceToken):
            return token

        return None

    def __scan_for_source_files_stitch(self, token: Token) -> bool:
        if not isinstance(token, CommentToken) or str(token.content).strip() != self.__stitch_format:
            return False

        while not self.__source_files.empty():
            self.__process_file(self.__source_files.get(), True)

        return True

    def __is_cont_line_break(self, token: Token) -> bool:
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
