import sys, json
from pathlib import Path
from argparse import ArgumentParser

__dir__ = Path(__file__).absolute().parent
  
def main(args):
    """Empty main function"""
    return 0


if __name__ == "__main__":
    argparse = ArgumentParser()
    argparse.add_argument('--input', default='/', type=str, help='input dir')
    sys.exit(main(argparse.parse_args()))
