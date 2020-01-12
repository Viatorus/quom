import argparse
import sys
from pathlib import Path

from .quom import Quom


def main():
    parser = argparse.ArgumentParser(prog='quom', description='Single header generator for C/C++ libraries.')
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

    args = parser.parse_args()

    try:
        with args.output_path.open('w+') as file:
            Quom(args.input_path, file, args.stitch, args.include_guard, args.trim)
    except Exception as e:
        print('Error: {}'.format(e), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
