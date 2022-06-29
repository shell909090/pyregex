import string
import unittest

from matcher import SPECIAL_QUOTES
from searcher import Search


DIGITS = SPECIAL_QUOTES['d']

class TestSearch(unittest.TestCase):

    def test_longest(self):
        s = Search(DIGITS, '*', True)
        self.assertEqual(s.get_end('a0123bc', 1), 5)
