from typing import List

from .identifier_tokenizer import scan_for_identifier
from .comment_tokenizer import scan_for_comment
from .number_tokenizer import scan_for_number
from .preprocessor_tokenizer import scan_for_preprocessor
from .quote_tokenizer import scan_for_quote
from .token import Token, TokenType
from .tokenize_error import TokenizeError
from .symbol_tokenizer import scan_for_symbol
from .whitespace_tokenizer import scan_for_whitespace
from quom.tokenizer.iterator import Iterable


class Tokenizer:
    def __init__(self, src: str):
        self._src: Iterable = None
        self._line_lengths: List[int] = []
        self._wrapped_position: List[int] = []
        self._tokens: List[Token] = []
        self._correct_line_ending(Iterable(list(src)))

    def tokenize(self) -> None:
        it = self._src.begin()
        it_end = self._src.end()

        tokens = [Token(None, None, TokenType.START)]

        while it != it_end:
            succeeded = scan_for_whitespace(tokens, it, it_end)
            if not succeeded:
                succeeded = scan_for_comment(tokens, it, it_end)
            if not succeeded:
                succeeded = scan_for_identifier(tokens, it, it_end)
            if not succeeded:
                succeeded = scan_for_quote(tokens, it, it_end)
            if not succeeded:
                succeeded = scan_for_number(tokens, it, it_end)
            if not succeeded:
                succeeded = scan_for_preprocessor(tokens, it, it_end)
            if not succeeded:
                succeeded = scan_for_symbol(tokens, it, it_end)
            if not succeeded:
                raise TokenizeError('Unknown syntax.', it)

        tokens.append([Token(None, None, TokenType.END)])

    def get_source_code(self):
        return ''.join(self._src)

    def _correct_line_ending(self, src: Iterable) -> None:
        number_of_back_slashes = 0
        line_length = 0

        src.append(None)
        it = src.begin()
        it_end = src.end() - 1
        write_it = src.begin()
        while it != it_end:
            if it[0] == '\r':
                # Check if next character is a line feed.
                if it[1] == '\n':
                    it += 1
                else:
                    # Convert line ending.
                    it[0] = '\n'
            if it[0] == '\n':
                # Save and reset line length.
                self._line_lengths.append(line_length)
                line_length = 0

                # Check for trailing backslash (wrap line).
                if number_of_back_slashes % 2 == 1:
                    # Reset the number of backslashes.
                    number_of_back_slashes = 0
                    # Go back two characters (to the backslash).
                    write_it -= 2
                    # Save wrapped line position.
                    self._wrapped_position.append(write_it.pos + 1)
                else:
                    it[0] = '\n'

                # Skip character copy.
                it += 1
                write_it += 1
                continue
            elif it[0] == '\\':
                #  Count the number of continuous backlashes.
                number_of_back_slashes += 1
            else:
                # Reset the number of backslashes if any other character was found.
                number_of_back_slashes = 0

            write_it[0] = it[0]
            line_length += 1

            it += 1
            write_it += 1

        self._line_lengths.append(line_length)

        # Set iterator to last character.
        if write_it != src.begin():
            write_it -= 1

        # Check if last line should be wrapped.
        if number_of_back_slashes % 2 == 1:
            # Add new line instead.
            write_it[0] = '\n'

        # Check if last character is not a new line.
        if write_it[0] != '\n':
            if write_it[0] is not None:
                write_it += 1
            write_it[0] = '\n'

        self._src = Iterable(src[:write_it.pos + 1])
