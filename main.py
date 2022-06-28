import sys
import logging
import argparse

import pyregex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel', '-l', default='INFO')
    parser.add_argument('rest', nargs='*', type=str)
    args = parser.parse_args()

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(args.loglevel)

    print(pyregex.match('abc[a-z]*def', 'abczzdef'))


if __name__ == '__main__':
    main()
