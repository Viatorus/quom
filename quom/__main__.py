import argparse
import sys
from pathlib import Path

from .quom import Quom


def main():
    parser = argparse.ArgumentParser(prog='quom', description='Single header only library generator for C/C++.')
    parser.add_argument('path', metavar='path', type=Path, help='File path of the main header file.')

    args = parser.parse_args()
    Quom(args.path)



if __name__ == '__main__':
    sys.exit(main())
