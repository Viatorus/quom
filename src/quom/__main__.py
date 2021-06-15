import argparse
import sys
from pathlib import Path
from typing import List

from quom import Quom

try:
    from quom import __version__
except ImportError:
    __version__ = 'unknown'


def main(args: List[str]):
    parser = argparse.ArgumentParser(prog='quom', description='Single header generator for C/C++ libraries.')
    parser.add_argument('--version', action='version', version='quom {ver}'.format(ver=__version__))
    parser.add_argument('input_path', metavar='input', type=Path, help='Input file path of the main file.')
    parser.add_argument('output_path', metavar='output', type=Path,
                        help='Output file path of the generated single header file.')
    parser.add_argument('--stitch', '-s', metavar='format', type=str, default=None,
                        help='Format of the comment where the source files should be placed (e.g. // ~> stitch <~). \
                        Default: %(default)s (at the end of the main file)')
    parser.add_argument('--include_guard', '-g', metavar='format', type=str, default=None,
                        help='Regex format of the include guard. Default: %(default)s')
    parser.add_argument('--trim', '-t', action='store_true', default=True,
                        help='Reduce continuous line breaks to one. Default: %(default)s')
    parser.add_argument('--include_directory', '-I', type=Path, action='append', default=[],
                        help='Add include directories for header files.')
    parser.add_argument('--source_directory', '-S', type=str, action='append', default=['.'],
                        help='Set the source directories for source files. '
                             'Use ./ or .\\ in front of a path to mark as relative to the header file.')
    parser.add_argument('--encoding', '-e', type=str, default='utf-8',
                        help='The encoding used to read and write all files.')

    args = parser.parse_args(args)

    # Transform source directories to distingue between:
    # - relative from header file (starting with dot)
    # - relative from workdir
    # - absolute path
    relative_source_directories = []
    source_directories = []
    for src in args.source_directory:
        path = Path(src)
        if src == '.' or src.startswith('./') or src.startswith('.\\'):
            relative_source_directories.append(path)
        else:
            source_directories.append(path.resolve())

    with args.output_path.open('w+', encoding=args.encoding) as file:
        Quom(args.input_path, file, args.stitch, args.include_guard, args.trim, args.include_directory,
             relative_source_directories, source_directories, args.encoding)


def run():
    main(sys.argv[1:])


if __name__ == '__main__':
    run()
