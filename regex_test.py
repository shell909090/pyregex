import string
import unittest

import regex


# class TestCompile(unittest.TestCase):
#     def test_compile(self):
#         pass


class TestRegex(unittest.TestCase):

    def test_asterisk(self):
        self.assertEqual(regex.match('abc.*def', 'abcdef'), True)
        self.assertEqual(regex.match('abc.*def', 'abczdef'), True)

    def test_add(self):
        self.assertEqual(regex.match('abc.+def', 'abcdef'), False)
        self.assertEqual(regex.match('abc.+def', 'abczdef'), True)

    def test_question_mark(self):
        self.assertEqual(regex.match('abc.?def', 'abcdef'), True)
        self.assertEqual(regex.match('abc.?def', 'abczdef'), True)
        self.assertEqual(regex.match('abc.?def', 'abczzdef'), False)

    def test_two_searches(self):
        self.assertEqual(regex.match('abc.*def.*hij', 'abczdefzhij'), True)
        self.assertEqual(regex.match('abc.*def.*hij', 'abczdezhij'), False)
        self.assertEqual(regex.match('abc.*def.*hij', 'abczdefzhi'), False)
        self.assertEqual(regex.match('abc.*def.*fghij', 'abcdefdefghij'), True)

    def test_quote(self):
        self.assertEqual(regex.match('abc\.\*def', 'abcdef'), False)
        self.assertEqual(regex.match('abc\.\*def', 'abc.*def'), True)
        self.assertEqual(regex.match('abc\.\*def', 'abcz*def'), False)
        self.assertEqual(regex.match('abc.\*def', 'abcz*def'), True)
        self.assertEqual(regex.match('abc\.*def', 'abc..def'), True)

    def test_special_quote(self):
        self.assertEqual(regex.match('abc\ddef', 'abc0def'), True)
        self.assertEqual(regex.match('abc\ddef', 'abczdef'), False)
        self.assertEqual(regex.match('abc\Ddef', 'abc0def'), False)
        self.assertEqual(regex.match('abc\sdef', 'abc def'), True)
        self.assertEqual(regex.match('abc\wdef', 'abc_def'), True)

    def test_repeat(self):
        self.assertEqual(regex.match('abc.{2,3}def', 'abcdef'), False)
        self.assertEqual(regex.match('abc.{2,3}def', 'abczzdef'), True)
        self.assertEqual(regex.match('abc.{2}def', 'abczzdef'), True)

    def test_nongreedy(self):
        self.assertEqual(regex.match('abc.*?def.*', 'abcdefdef'), True)
        self.assertEqual(regex.match('abc.*?def.*', 'abczzzzzz'), False)
        self.assertEqual(regex.match('abc.*?def.*', 'abczzzdef'), True)

    def test_charset(self):
        self.assertEqual(regex.match('abc[a-z]*def', 'abczzdef'), True)
        self.assertEqual(regex.match('abc[a-z]*def', 'abcZZdef'), False)
        self.assertEqual(regex.match('abc[^a-z]*def', 'abcZZdef'), True)
        self.assertEqual(regex.match('abc[a-zA-Z]*def', 'abczZdef'), True)
        self.assertEqual(regex.match('abc[a-zA-Z]*def', 'abc00def'), False)
        self.assertEqual(regex.match('abc[a-zA-Z\s]*def', 'abcz zdef'), True)
