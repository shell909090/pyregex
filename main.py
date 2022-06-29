import sys
import logging
import argparse

import regex


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

    print(regex.match('abc.*def', 'abczzdef'))
    print(regex.match('abc[a-z]*def', 'abczzdef'))

    # print(list(regex.compile('abc*def')))
    # print(list(regex.compile('abc.*def')))
    # print(list(regex.compile('abc.+def')))
    # print(list(regex.compile('abc.?def')))
    # print(list(regex.compile('abc.*def.*hij')))
    # print(list(regex.compile('abc\.\*def')))
    # print(list(regex.compile('abc.\*def')))
    # print(list(regex.compile('abc\.*def')))
    # print(list(regex.compile('abc\ddef')))
    # print(list(regex.compile('abc.{2,3}def')))
    # print(list(regex.compile('abc.{2}def')))
    # print(list(regex.compile('abc.*?def.*')))
    # print(list(regex.compile('abc[a-z]*def')))


if __name__ == '__main__':
    main()
