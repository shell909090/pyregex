import string
import unittest

from matcher import Str, any, Any, Charset, eval


class TestStr(unittest.TestCase):

    def test_match(self):
        s = Str('abc')
        self.assertEqual(s.slip('abcde', 0), (True, 3))
        self.assertEqual(s.slip('zabcd', 1), (True, 4))

    def test_short(self):
        s = Str('abcde')
        self.assertEqual(s.slip('abc', 0), (False, 0))
        self.assertEqual(s.slip('zabc', 1), (False, 1))

    def test_dismatch(self):
        s = Str('abc')
        self.assertEqual(s.slip('abz', 0), (False, 0))
        self.assertEqual(s.slip('zabz', 1), (False, 1))


class TestAny(unittest.TestCase):

    def test_match(self):
        self.assertEqual(any.slip('a', 0), (True, 1))
        self.assertEqual(any.slip('ab', 1), (True, 2))

    def test_short(self):
        self.assertEqual(any.slip('', 0), (False, 0))
        self.assertEqual(any.slip('a', 1), (False, 1))


class TestCharset(unittest.TestCase):

    def test_single(self):
        cs, cur = Charset.eval('abc', 0)
        self.assertEqual(cs.charset, set('abc'))
        self.assertEqual(cs.include, True)

    def test_range1(self):
        cs, cur = Charset.eval('a-z', 0)
        self.assertEqual(cs.charset, set(string.ascii_lowercase))
        self.assertEqual(cs.include, True)

    def test_range2(self):
        cs, cur = Charset.eval('A-Z', 0)
        self.assertEqual(cs.charset, set(string.ascii_uppercase))
        self.assertEqual(cs.include, True)

    def test_range3(self):
        cs, cur = Charset.eval('0-9', 0)
        self.assertEqual(cs.charset, set(string.digits))
        self.assertEqual(cs.include, True)

    def test_ranges(self):
        cs, cur = Charset.eval('0-9a-zA-Z', 0)
        self.assertEqual(cs.charset, set(string.ascii_letters+string.digits))
        self.assertEqual(cs.include, True)

    def test_eval(self):
        cs, cur = Charset.eval('a[0-9]b', 2)
        self.assertEqual(cur, 6)
        self.assertEqual(cs.charset, set(string.digits))
        self.assertEqual(cs.include, True)

    def test_match(self):
        cs, cur = Charset.eval('a-z', 0)
        self.assertEqual(cs.slip('abc', 0), (True, 1))
        self.assertEqual(cs.slip('abc', 1), (True, 2))

    def test_short(self):
        cs, cur = Charset.eval('a-z', 0)
        self.assertEqual(cs.slip('', 0), (False, 0))
        self.assertEqual(cs.slip('a', 1), (False, 1))

    def test_dismatch(self):
        cs, cur = Charset.eval('a-z', 0)
        self.assertEqual(cs.slip('Abc', 0), (False, 0))
        self.assertEqual(cs.slip('aBc', 1), (False, 1))


class TestEval(unittest.TestCase):

    def test_str(self):
        self.assertEqual(eval('a', 0), ('a', 1))
        self.assertEqual(eval('zb', 1), ('b', 2))

    def test_any(self):
        self.assertEqual(eval('.', 0), (any, 1))
        self.assertEqual(eval('z.', 1), (any, 2))

    def test_charset(self):
        cs, cur = eval('[0-9]a', 0)
        self.assertEqual((cs.include, cs.charset, cur), (True, set(string.digits), 5))
        cs, cur = eval('z[0-9]a', 1)
        self.assertEqual((cs.include, cs.charset, cur), (True, set(string.digits), 6))
