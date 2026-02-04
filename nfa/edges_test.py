import string
import unittest

from .edges import Edge, Empty, Any, Char, Charset, SPECIAL_QUOTES


class TestEmpty(unittest.TestCase):
    """Test Empty (epsilon) edge"""

    def test_repr(self):
        """Test __repr__ returns epsilon symbol"""
        edge = Empty()
        self.assertEqual(repr(edge), 'ε')

    def test_match_at_start(self):
        """Test match at start of string"""
        edge = Empty()
        self.assertEqual(edge.match('abc', 0), 0)

    def test_match_at_middle(self):
        """Test match in middle of string"""
        edge = Empty()
        self.assertEqual(edge.match('abc', 1), 1)

    def test_match_at_end(self):
        """Test match at end of string"""
        edge = Empty()
        self.assertEqual(edge.match('abc', 3), 3)

    def test_match_empty_string(self):
        """Test match on empty string"""
        edge = Empty()
        self.assertEqual(edge.match('', 0), 0)


class TestAny(unittest.TestCase):
    """Test Any (.) edge"""

    def test_repr(self):
        """Test __repr__ returns dot"""
        edge = Any()
        self.assertEqual(repr(edge), '.')

    def test_match_single_char(self):
        """Test match single character"""
        edge = Any()
        self.assertEqual(edge.match('a', 0), 1)

    def test_match_at_middle(self):
        """Test match in middle of string"""
        edge = Any()
        self.assertEqual(edge.match('abc', 1), 2)

    def test_match_various_chars(self):
        """Test match various characters"""
        edge = Any()
        self.assertEqual(edge.match('x', 0), 1)
        self.assertEqual(edge.match('1', 0), 1)
        self.assertEqual(edge.match(' ', 0), 1)
        self.assertEqual(edge.match('\n', 0), 1)

    def test_no_match_at_end(self):
        """Test no match when at end of string"""
        edge = Any()
        self.assertIsNone(edge.match('abc', 3))

    def test_no_match_empty_string(self):
        """Test no match on empty string"""
        edge = Any()
        self.assertIsNone(edge.match('', 0))

    def test_no_match_beyond_end(self):
        """Test no match when position beyond string length"""
        edge = Any()
        self.assertIsNone(edge.match('abc', 5))


class TestChar(unittest.TestCase):
    """Test Char edge"""

    def test_repr(self):
        """Test __repr__ returns the character"""
        edge = Char('a')
        self.assertEqual(repr(edge), 'a')

    def test_match_single_char(self):
        """Test match specific character"""
        edge = Char('a')
        self.assertEqual(edge.match('a', 0), 1)
        self.assertEqual(edge.match('abc', 0), 1)

    def test_match_at_middle(self):
        """Test match in middle of string"""
        edge = Char('b')
        self.assertEqual(edge.match('abc', 1), 2)

    def test_match_at_end(self):
        """Test match at end of string"""
        edge = Char('c')
        self.assertEqual(edge.match('abc', 2), 3)

    def test_no_match_different_char(self):
        """Test no match when character differs"""
        edge = Char('a')
        self.assertIsNone(edge.match('b', 0))
        self.assertIsNone(edge.match('bcd', 0))

    def test_no_match_at_end(self):
        """Test no match when at end of string"""
        edge = Char('a')
        self.assertIsNone(edge.match('abc', 3))

    def test_no_match_empty_string(self):
        """Test no match on empty string"""
        edge = Char('a')
        self.assertIsNone(edge.match('', 0))

    def test_match_special_chars(self):
        """Test match special characters"""
        edge1 = Char(' ')
        self.assertEqual(edge1.match(' ', 0), 1)

        edge2 = Char('.')
        self.assertEqual(edge2.match('.', 0), 1)

        edge3 = Char('\n')
        self.assertEqual(edge3.match('\n', 0), 1)


class TestCharset(unittest.TestCase):
    """Test Charset edge"""

    def test_repr_include(self):
        """Test __repr__ for positive character class"""
        edge = Charset(set('abc'), True)
        repr_str = repr(edge)
        self.assertIn('a', repr_str)
        self.assertIn('b', repr_str)
        self.assertIn('c', repr_str)
        self.assertNotIn('^', repr_str)

    def test_repr_exclude(self):
        """Test __repr__ for negative character class"""
        edge = Charset(set('abc'), False)
        repr_str = repr(edge)
        self.assertIn('^', repr_str)
        self.assertIn('a', repr_str)

    def test_match_include_single(self):
        """Test match with positive character class"""
        edge = Charset(set('abc'), True)
        self.assertEqual(edge.match('a', 0), 1)
        self.assertEqual(edge.match('b', 0), 1)
        self.assertEqual(edge.match('c', 0), 1)

    def test_match_include_at_middle(self):
        """Test match in middle of string"""
        edge = Charset(set('abc'), True)
        self.assertEqual(edge.match('xax', 1), 2)

    def test_no_match_include(self):
        """Test no match with positive character class"""
        edge = Charset(set('abc'), True)
        self.assertIsNone(edge.match('x', 0))
        self.assertIsNone(edge.match('d', 0))

    def test_match_exclude_single(self):
        """Test match with negative character class"""
        edge = Charset(set('abc'), False)
        self.assertEqual(edge.match('x', 0), 1)
        self.assertEqual(edge.match('d', 0), 1)
        self.assertEqual(edge.match('1', 0), 1)

    def test_no_match_exclude(self):
        """Test no match with negative character class"""
        edge = Charset(set('abc'), False)
        self.assertIsNone(edge.match('a', 0))
        self.assertIsNone(edge.match('b', 0))
        self.assertIsNone(edge.match('c', 0))

    def test_match_range(self):
        """Test match with character range"""
        edge = Charset(set(string.ascii_lowercase), True)
        self.assertEqual(edge.match('a', 0), 1)
        self.assertEqual(edge.match('z', 0), 1)
        self.assertIsNone(edge.match('A', 0))
        self.assertIsNone(edge.match('1', 0))

    def test_no_match_at_end(self):
        """Test no match when at end of string"""
        edge = Charset(set('abc'), True)
        self.assertIsNone(edge.match('abc', 3))

    def test_no_match_empty_string(self):
        """Test no match on empty string"""
        edge = Charset(set('abc'), True)
        self.assertIsNone(edge.match('', 0))


class TestSpecialQuotes(unittest.TestCase):
    """Test SPECIAL_QUOTES definitions"""

    def test_digit_d(self):
        """Test \\d matches digits"""
        charset_set, include = SPECIAL_QUOTES['d']
        self.assertEqual(charset_set, set(string.digits))
        self.assertTrue(include)

        edge = Charset(*SPECIAL_QUOTES['d'])
        self.assertEqual(edge.match('0', 0), 1)
        self.assertEqual(edge.match('9', 0), 1)
        self.assertIsNone(edge.match('a', 0))

    def test_non_digit_D(self):
        """Test \\D matches non-digits"""
        charset_set, include = SPECIAL_QUOTES['D']
        self.assertEqual(charset_set, set(string.digits))
        self.assertFalse(include)

        edge = Charset(*SPECIAL_QUOTES['D'])
        self.assertEqual(edge.match('a', 0), 1)
        self.assertEqual(edge.match('Z', 0), 1)
        self.assertIsNone(edge.match('0', 0))
        self.assertIsNone(edge.match('9', 0))

    def test_whitespace_s(self):
        """Test \\s matches whitespace"""
        charset_set, include = SPECIAL_QUOTES['s']
        self.assertEqual(charset_set, set(string.whitespace))
        self.assertTrue(include)

        edge = Charset(*SPECIAL_QUOTES['s'])
        self.assertEqual(edge.match(' ', 0), 1)
        self.assertEqual(edge.match('\t', 0), 1)
        self.assertEqual(edge.match('\n', 0), 1)
        self.assertIsNone(edge.match('a', 0))

    def test_non_whitespace_S(self):
        """Test \\S matches non-whitespace"""
        charset_set, include = SPECIAL_QUOTES['S']
        self.assertEqual(charset_set, set(string.whitespace))
        self.assertFalse(include)

        edge = Charset(*SPECIAL_QUOTES['S'])
        self.assertEqual(edge.match('a', 0), 1)
        self.assertEqual(edge.match('1', 0), 1)
        self.assertIsNone(edge.match(' ', 0))
        self.assertIsNone(edge.match('\t', 0))

    def test_word_w(self):
        """Test \\w matches word characters"""
        charset_set, include = SPECIAL_QUOTES['w']
        expected = set('_' + string.ascii_letters + string.digits)
        self.assertEqual(charset_set, expected)
        self.assertTrue(include)

        edge = Charset(*SPECIAL_QUOTES['w'])
        self.assertEqual(edge.match('a', 0), 1)
        self.assertEqual(edge.match('Z', 0), 1)
        self.assertEqual(edge.match('0', 0), 1)
        self.assertEqual(edge.match('_', 0), 1)
        self.assertIsNone(edge.match(' ', 0))
        self.assertIsNone(edge.match('-', 0))

    def test_non_word_W(self):
        """Test \\W matches non-word characters"""
        charset_set, include = SPECIAL_QUOTES['W']
        expected = set('_' + string.ascii_letters + string.digits)
        self.assertEqual(charset_set, expected)
        self.assertFalse(include)

        edge = Charset(*SPECIAL_QUOTES['W'])
        self.assertEqual(edge.match(' ', 0), 1)
        self.assertEqual(edge.match('-', 0), 1)
        self.assertEqual(edge.match('.', 0), 1)
        self.assertIsNone(edge.match('a', 0))
        self.assertIsNone(edge.match('0', 0))
        self.assertIsNone(edge.match('_', 0))

    def test_all_special_quotes_keys(self):
        """Test all expected special quote keys exist"""
        expected_keys = ['d', 'D', 's', 'S', 'w', 'W']
        self.assertEqual(sorted(SPECIAL_QUOTES.keys()), sorted(expected_keys))


class TestEdgeInterface(unittest.TestCase):
    """Test Edge abstract base class"""

    def test_all_edges_implement_match(self):
        """Test all edge types implement match method"""
        edges = [Empty(), Any(), Char('a'), Charset(set('a'), True)]
        for edge in edges:
            self.assertTrue(hasattr(edge, 'match'))
            self.assertTrue(callable(edge.match))

    def test_all_edges_are_edges(self):
        """Test all edge types inherit from Edge"""
        edges = [Empty(), Any(), Char('a'), Charset(set('a'), True)]
        for edge in edges:
            self.assertIsInstance(edge, Edge)
