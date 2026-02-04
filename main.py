import sys
import logging
import argparse

import regex
import nfa


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
    print(regex.match('abc(?P<pp>.*)def', 'abczzdef'))
    print(regex.match('(abc)*end', 'abcabcend'))

    print(nfa.compile('ab*c').match('abbc'))
    print(nfa.compile('abc.*def').match('abczzdef'))
    print(nfa.compile('abc[a0-9b]*def').match('abc00def'))
    print(nfa.compile('abc.{2,4}def').match('abc00def'))
    print(nfa.compile('abc\\d+def').match('abc00def'))
    print(nfa.compile('(abc)*end').match('abcabcend'))


if __name__ == '__main__':
    main()
