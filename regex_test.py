import string
import unittest

import regex

from matcher import Str, any, Charset, SPECIAL_QUOTES


DIGITS = SPECIAL_QUOTES['d']

class TestSearch(unittest.TestCase):

    def test_scan_simple(self):
        s = regex.Search(DIGITS, '*', True)
        s1 = 'a0123bc'
        self.assertEqual(list(s.scan(s1, 1, 1, len(s1))),
                         list(range(1, 6)))

    def test_scan_start(self):
        s = regex.Search(DIGITS, '*', True)
        s1 = 'a0123bc'
        self.assertEqual(list(s.scan(s1, 1, 2, len(s1))),
                         list(range(2, 6)))
        s1 = 'ab123c'  # failed
        self.assertEqual(list(s.scan(s1, 1, 2, len(s1))), [])

    def test_scan_end(self):
        s = regex.Search(DIGITS, '*', True)
        s1 = 'a0123bc'
        self.assertEqual(list(s.scan(s1, 1, 1, 1)), [1])

    def test_search_asterisk(self):
        s = regex.Search(DIGITS, '*', False)
        s1 = 'a0123bc'
        self.assertEqual(list(s.search(s1, 1)),
                         list(range(1, 6)))

    def test_search_add(self):
        s = regex.Search(DIGITS, '+', False)
        s1 = 'a0123bc'
        self.assertEqual(list(s.search(s1, 1)),
                         list(range(2, 6)))

    def test_search_question_mark(self):
        s = regex.Search(DIGITS, '?', False)
        s1 = 'a0123bc'
        self.assertEqual(list(s.search(s1, 1)),
                         list(range(1, 3)))

    def test_search_repeat1(self):
        s = regex.Search(DIGITS, '{2}', False)
        s1 = 'a0123bc'
        self.assertEqual(list(s.search(s1, 1)), [3])

    def test_search_repeat2(self):
        s = regex.Search(DIGITS, '{2,3}', False)
        s1 = 'a0123bc'
        self.assertEqual(list(s.search(s1, 1)), [3, 4])

    def test_search_greedy(self):
        s = regex.Search(DIGITS, '*', True)
        s1 = 'a0123bc'
        self.assertEqual(list(s.search(s1, 1)),
                         list(range(5, 0, -1)))


class TestCompile(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(list(regex.compile('abc*def')),
                         ['ab', regex.Search('c', '*', True), 'def'])

    def test_asterisk(self):
        self.assertEqual(list(regex.compile('abc.*def')),
                         ['abc', regex.Search(any, '*', True), 'def'])

    def test_add(self):
        self.assertEqual(list(regex.compile('abc.+def')),
                         ['abc', regex.Search(any, '+', True), 'def'])

    def test_question_mark(self):
        self.assertEqual(list(regex.compile('abc.?def')),
                         ['abc', regex.Search(any, '?', True), 'def'])

    def test_two_searches(self):
        self.assertEqual(list(regex.compile('abc.*def.*hij')),
                         ['abc', regex.Search(any, '*', True), 'def', regex.Search(any, '*', True), 'hij'])

    def test_quote(self):
        self.assertEqual(list(regex.compile('abc\.\*def')),
                         ['abc.*def'])
        self.assertEqual(list(regex.compile('abc.\*def')),
                         ['abc', any, '*def'])
        self.assertEqual(list(regex.compile('abc\.*def')),
                         ['abc', regex.Search('.', '*', True), 'def'])

    def test_special_quote(self):
        self.assertEqual(list(regex.compile('abc\ddef')),
                         ['abc', SPECIAL_QUOTES['d'], 'def'])

    def test_repeat(self):
        self.assertEqual(list(regex.compile('abc.{2,3}def')),
                         ['abc', regex.Search(any, '{2,3}', True), 'def'])
        self.assertEqual(list(regex.compile('abc.{2}def')),
                         ['abc', regex.Search(any, '{2}', True), 'def'])

    def test_greedy(self):
        self.assertEqual(list(regex.compile('abc.*?def.*')),
                         ['abc', regex.Search(any, '*', False), 'def', regex.Search(any, '*', True)])

    def test_charset1(self):
        self.assertEqual(list(regex.compile('abc[a-z]*def')),
                         ['abc', regex.Search(Charset.eval('a-z', 0)[0], '*', True), 'def'])
        self.assertEqual(list(regex.compile('abc[^a-z]*def')),
                         ['abc', regex.Search(Charset.eval('^a-z', 0)[0], '*', True), 'def'])
        self.assertEqual(list(regex.compile('abc[a-zA-Z]*def')),
                         ['abc', regex.Search(Charset.eval('a-zA-Z', 0)[0], '*', True), 'def'])
        self.assertEqual(list(regex.compile('abc[a-zA-Z\s]*def')),
                         ['abc', regex.Search(Charset.eval('a-zA-Z\s', 0)[0], '*', True), 'def'])


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
