import string
import unittest

import pyregex


class TestCharset(unittest.TestCase):

    def test_single(self):
        self.assertEqual(pyregex.gen_charset('abc')[0], (True, set('abc')))

    def test_range1(self):
        self.assertEqual(pyregex.gen_charset('a-z')[0], (True, set(string.ascii_lowercase)))

    def test_range2(self):
        self.assertEqual(pyregex.gen_charset('A-Z')[0], (True, set(string.ascii_uppercase)))

    def test_range3(self):
        self.assertEqual(pyregex.gen_charset('0-9')[0], (True, set(string.digits)))

    def test_ranges(self):
        self.assertEqual(pyregex.gen_charset('0-9a-zA-Z')[0], (True, set(string.ascii_letters+string.digits)))


class TestRegex(unittest.TestCase):

    def test_asterisk(self):
        self.assertEqual(pyregex.match('abc.*def', 'abcdef'), True)
        self.assertEqual(pyregex.match('abc.*def', 'abczdef'), True)

    def test_add(self):
        self.assertEqual(pyregex.match('abc.+def', 'abcdef'), False)
        self.assertEqual(pyregex.match('abc.+def', 'abczdef'), True)

    def test_question_mark(self):
        self.assertEqual(pyregex.match('abc.?def', 'abcdef'), True)
        self.assertEqual(pyregex.match('abc.?def', 'abczdef'), True)
        self.assertEqual(pyregex.match('abc.?def', 'abczzdef'), False)

    def test_two_searches(self):
        self.assertEqual(pyregex.match('abc.*def.*hij', 'abczdefzhij'), True)
        self.assertEqual(pyregex.match('abc.*def.*hij', 'abczdezhij'), False)
        self.assertEqual(pyregex.match('abc.*def.*hij', 'abczdefzhi'), False)
        self.assertEqual(pyregex.match('abc.*def.*fghij', 'abcdefdefghij'), True)

    def test_quote(self):
        self.assertEqual(pyregex.match('abc\.\*def', 'abcdef'), False)
        self.assertEqual(pyregex.match('abc\.\*def', 'abc.*def'), True)
        self.assertEqual(pyregex.match('abc\.\*def', 'abcz*def'), False)
        self.assertEqual(pyregex.match('abc.\*def', 'abcz*def'), True)
        self.assertEqual(pyregex.match('abc\.*def', 'abc..def'), True)

    def test_special_quote(self):
        self.assertEqual(pyregex.match('abc\ddef', 'abc0def'), True)
        self.assertEqual(pyregex.match('abc\ddef', 'abczdef'), False)
        self.assertEqual(pyregex.match('abc\Ddef', 'abc0def'), False)
        self.assertEqual(pyregex.match('abc\sdef', 'abc def'), True)
        self.assertEqual(pyregex.match('abc\wdef', 'abc_def'), True)

    def test_repeat(self):
        self.assertEqual(pyregex.match('abc.{2,3}def', 'abcdef'), False)
        self.assertEqual(pyregex.match('abc.{2,3}def', 'abczzdef'), True)
        self.assertEqual(pyregex.match('abc.{2}def', 'abczzdef'), True)

    def test_nongreedy(self):
        self.assertEqual(pyregex.match('abc.*?def.*', 'abcdefdef'), True)
        self.assertEqual(pyregex.match('abc.*?def.*', 'abczzzzzz'), False)
        self.assertEqual(pyregex.match('abc.*?def.*', 'abczzzdef'), True)

    def test_charset(self):
        self.assertEqual(pyregex.match('abc[a-z]*def', 'abczzdef'), True)
        self.assertEqual(pyregex.match('abc[a-z]*def', 'abcZZdef'), False)
        self.assertEqual(pyregex.match('abc[^a-z]*def', 'abcZZdef'), True)
        self.assertEqual(pyregex.match('abc[a-zA-Z]*def', 'abczZdef'), True)
        self.assertEqual(pyregex.match('abc[a-zA-Z]*def', 'abc00def'), False)
        self.assertEqual(pyregex.match('abc[a-zA-Z\s]*def', 'abcz zdef'), True)
