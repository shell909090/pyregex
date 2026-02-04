import string
import unittest

from .compile import tokenizer, tok_to_set, compile, scan_brackets


class TestScanBrackets(unittest.TestCase):
    """Test scan_brackets function

    Note: scan_brackets assumes the closing ')' has already been popped from the list.
    It scans backwards to find the matching '(' for that popped ')'.
    """

    def test_simple_brackets(self):
        """Test simple bracket matching"""
        # Pattern: (a) - after popping ')', toks = ['(', 'a']
        toks = ['(', 'a']
        self.assertEqual(scan_brackets(toks), 0)

    def test_nested_brackets(self):
        """Test nested bracket matching"""
        # Pattern: ((a)) - after popping outer ')', toks = ['(', '(', 'a', ')']
        toks = ['(', '(', 'a', ')']
        self.assertEqual(scan_brackets(toks), 0)

    def test_multiple_groups(self):
        """Test multiple groups - should match the last group"""
        # Pattern: (a)(b) - after popping ')', toks = ['(', 'a', ')', '(', 'b']
        toks = ['(', 'a', ')', '(', 'b']
        self.assertEqual(scan_brackets(toks), 3)

    def test_deeply_nested(self):
        """Test deeply nested brackets"""
        # Pattern: (((a))) - after popping ')', toks = ['(', '(', '(', 'a', ')', ')']
        toks = ['(', '(', '(', 'a', ')', ')']
        self.assertEqual(scan_brackets(toks), 0)

    def test_complex_nesting(self):
        """Test complex nesting with multiple levels"""
        # Pattern: (a(b)c) - after popping ')', toks = ['(', 'a', '(', 'b', ')', 'c']
        toks = ['(', 'a', '(', 'b', ')', 'c']
        self.assertEqual(scan_brackets(toks), 0)

    def test_multiple_at_same_level(self):
        """Test multiple brackets at the same level"""
        # Pattern: ((a)(b)) - after popping ')', toks = ['(', '(', 'a', ')', '(', 'b', ')']
        toks = ['(', '(', 'a', ')', '(', 'b', ')']
        self.assertEqual(scan_brackets(toks), 0)

    def test_unmatched_opening(self):
        """Test unmatched opening bracket"""
        # Missing closing bracket for the opening '('
        toks = ['(', 'a', 'b']
        self.assertEqual(scan_brackets(toks), 0)  # Still finds the '('

    def test_no_opening(self):
        """Test no opening bracket"""
        toks = ['a', 'b']
        self.assertEqual(scan_brackets(toks), -1)

    def test_empty_group(self):
        """Test empty group"""
        # Pattern: () - after popping ')', toks = ['(']
        toks = ['(']
        self.assertEqual(scan_brackets(toks), 0)

    def test_with_operators(self):
        """Test brackets with operators inside"""
        # Pattern: (a*b+) - after popping ')', toks = ['(', 'a', '*', 'b', '+']
        toks = ['(', 'a', '*', 'b', '+']
        self.assertEqual(scan_brackets(toks), 0)

    def test_alternation_in_group(self):
        """Test group with alternation"""
        # Pattern: (a|b) - after popping ')', toks = ['(', 'a', '|', 'b']
        toks = ['(', 'a', '|', 'b']
        self.assertEqual(scan_brackets(toks), 0)

    def test_three_nested_groups(self):
        """Test three nested groups"""
        # Pattern: (((a))) - after popping ')', toks = ['(', '(', '(', 'a', ')', ')']
        toks = ['(', '(', '(', 'a', ')', ')']
        self.assertEqual(scan_brackets(toks), 0)

    def test_inner_group(self):
        """Test finding inner group match"""
        # Pattern: (a(b)) - after popping inner ')', toks = ['(', 'a', '(', 'b']
        toks = ['(', 'a', '(', 'b']
        self.assertEqual(scan_brackets(toks), 2)  # Should find the inner '('

    def test_complex_sequence(self):
        """Test complex sequence with multiple nesting levels"""
        # Pattern: (a)(b(c))  - after popping outer ')', toks = ['(', 'a', ')', '(', 'b', '(', 'c', ')']
        toks = ['(', 'a', ')', '(', 'b', '(', 'c', ')']
        self.assertEqual(scan_brackets(toks), 3)


class TestTokenizer(unittest.TestCase):
    """Test tokenizer function"""

    def test_single_char(self):
        """Test tokenizing single character"""
        self.assertEqual(list(tokenizer('a')), ['a'])
        self.assertEqual(list(tokenizer('x')), ['x'])

    def test_multiple_chars(self):
        """Test tokenizing multiple characters"""
        self.assertEqual(list(tokenizer('abc')), ['a', 'b', 'c'])
        self.assertEqual(list(tokenizer('hello')), ['h', 'e', 'l', 'l', 'o'])

    def test_dot(self):
        """Test tokenizing dot (any character)"""
        self.assertEqual(list(tokenizer('.')), ['.'])
        self.assertEqual(list(tokenizer('a.b')), ['a', '.', 'b'])

    def test_asterisk(self):
        """Test tokenizing asterisk quantifier"""
        self.assertEqual(list(tokenizer('a*')), ['a', '*'])
        self.assertEqual(list(tokenizer('ab*')), ['a', 'b', '*'])

    def test_plus(self):
        """Test tokenizing plus quantifier"""
        self.assertEqual(list(tokenizer('a+')), ['a', '+'])
        self.assertEqual(list(tokenizer('ab+')), ['a', 'b', '+'])

    def test_question(self):
        """Test tokenizing question quantifier"""
        self.assertEqual(list(tokenizer('a?')), ['a', '?'])
        self.assertEqual(list(tokenizer('ab?')), ['a', 'b', '?'])

    def test_non_greedy_quantifiers(self):
        """Test tokenizing non-greedy quantifiers"""
        self.assertEqual(list(tokenizer('a*?')), ['a', '*?'])
        self.assertEqual(list(tokenizer('a+?')), ['a', '+?'])
        self.assertEqual(list(tokenizer('a??')), ['a', '??'])

    def test_charset_simple(self):
        """Test tokenizing simple character set"""
        self.assertEqual(list(tokenizer('[abc]')), ['[abc]'])
        self.assertEqual(list(tokenizer('[a-z]')), ['[a-z]'])

    def test_charset_negated(self):
        """Test tokenizing negated character set"""
        self.assertEqual(list(tokenizer('[^abc]')), ['[^abc]'])
        self.assertEqual(list(tokenizer('[^0-9]')), ['[^0-9]'])

    def test_charset_in_pattern(self):
        """Test character set within pattern"""
        self.assertEqual(list(tokenizer('a[0-9]b')), ['a', '[0-9]', 'b'])

    def test_escape_sequences(self):
        """Test tokenizing escape sequences"""
        self.assertEqual(list(tokenizer('\\d')), ['\\d'])
        self.assertEqual(list(tokenizer('\\s')), ['\\s'])
        self.assertEqual(list(tokenizer('\\w')), ['\\w'])
        self.assertEqual(list(tokenizer('\\.')), ['\\.'])
        self.assertEqual(list(tokenizer('\\*')), ['\\*'])

    def test_escape_in_pattern(self):
        """Test escape sequences within pattern"""
        self.assertEqual(list(tokenizer('a\\db')), ['a', '\\d', 'b'])
        self.assertEqual(list(tokenizer('\\d+')), ['\\d', '+'])

    def test_parentheses(self):
        """Test tokenizing parentheses"""
        self.assertEqual(list(tokenizer('(ab)')), ['(', 'a', 'b', ')'])
        self.assertEqual(list(tokenizer('a(bc)d')), ['a', '(', 'b', 'c', ')', 'd'])

    def test_pipe(self):
        """Test tokenizing pipe (alternation)"""
        self.assertEqual(list(tokenizer('a|b')), ['a', '|', 'b'])
        self.assertEqual(list(tokenizer('abc|def')), ['a', 'b', 'c', '|', 'd', 'e', 'f'])

    def test_braces(self):
        """Test tokenizing braces (repetition count)"""
        self.assertEqual(list(tokenizer('a{2}')), ['a', '{2}'])
        self.assertEqual(list(tokenizer('a{2,5}')), ['a', '{2,5}'])

    def test_complex_pattern(self):
        """Test tokenizing complex pattern"""
        tokens = list(tokenizer('a[0-9]+\\d*'))
        self.assertEqual(tokens, ['a', '[0-9]', '+', '\\d', '*'])

    def test_error_unmatched_bracket(self):
        """Test error on unmatched bracket"""
        with self.assertRaises(Exception) as ctx:
            list(tokenizer('[abc'))
        self.assertIn('Unmatched bracket', str(ctx.exception))

    def test_error_unmatched_brace(self):
        """Test error on unmatched brace"""
        with self.assertRaises(Exception) as ctx:
            list(tokenizer('{2'))
        self.assertIn('Unmatched brace', str(ctx.exception))

    def test_error_incomplete_escape(self):
        """Test error on incomplete escape sequence"""
        with self.assertRaises(Exception) as ctx:
            list(tokenizer('a\\'))
        self.assertIn('Incomplete escape sequence', str(ctx.exception))


class TestTokToSet(unittest.TestCase):
    """Test tok_to_set function"""

    def test_simple_chars(self):
        """Test parsing simple character set"""
        charset, include = tok_to_set('[abc]')
        self.assertEqual(charset, set('abc'))
        self.assertTrue(include)

    def test_single_char(self):
        """Test parsing single character"""
        charset, include = tok_to_set('[a]')
        self.assertEqual(charset, set('a'))
        self.assertTrue(include)

    def test_range_lowercase(self):
        """Test parsing lowercase range"""
        charset, include = tok_to_set('[a-z]')
        self.assertEqual(charset, set(string.ascii_lowercase))
        self.assertTrue(include)

    def test_range_uppercase(self):
        """Test parsing uppercase range"""
        charset, include = tok_to_set('[A-Z]')
        self.assertEqual(charset, set(string.ascii_uppercase))
        self.assertTrue(include)

    def test_range_digits(self):
        """Test parsing digit range"""
        charset, include = tok_to_set('[0-9]')
        self.assertEqual(charset, set(string.digits))
        self.assertTrue(include)

    def test_multiple_ranges(self):
        """Test parsing multiple ranges"""
        charset, include = tok_to_set('[a-zA-Z]')
        self.assertEqual(charset, set(string.ascii_letters))
        self.assertTrue(include)

    def test_range_and_chars(self):
        """Test parsing range with individual characters"""
        charset, include = tok_to_set('[a-z0-9_]')
        expected = set(string.ascii_lowercase + string.digits + '_')
        self.assertEqual(charset, expected)
        self.assertTrue(include)

    def test_negated_simple(self):
        """Test parsing negated character set"""
        charset, include = tok_to_set('[^abc]')
        self.assertEqual(charset, set('abc'))
        self.assertFalse(include)

    def test_negated_range(self):
        """Test parsing negated range"""
        charset, include = tok_to_set('[^0-9]')
        self.assertEqual(charset, set(string.digits))
        self.assertFalse(include)

    def test_special_chars_in_set(self):
        """Test parsing special characters in set"""
        charset, include = tok_to_set('[.+*]')
        self.assertEqual(charset, set('.+*'))
        self.assertTrue(include)


class TestCompileBasic(unittest.TestCase):
    """Test compile function with basic patterns"""

    def test_single_char(self):
        """Test compiling single character"""
        nfa = compile('a')
        self.assertTrue(nfa.match('a'))
        self.assertFalse(nfa.match('b'))
        self.assertFalse(nfa.match(''))
        self.assertFalse(nfa.match('aa'))

    def test_two_chars(self):
        """Test compiling two character sequence"""
        nfa = compile('ab')
        self.assertTrue(nfa.match('ab'))
        self.assertFalse(nfa.match('a'))
        self.assertFalse(nfa.match('b'))
        self.assertFalse(nfa.match('ba'))

    def test_three_chars(self):
        """Test compiling three character sequence"""
        nfa = compile('abc')
        self.assertTrue(nfa.match('abc'))
        self.assertFalse(nfa.match('ab'))
        self.assertFalse(nfa.match('abcd'))

    def test_dot(self):
        """Test compiling dot (any character)"""
        nfa = compile('.')
        self.assertTrue(nfa.match('a'))
        self.assertTrue(nfa.match('x'))
        self.assertTrue(nfa.match('1'))
        self.assertFalse(nfa.match(''))
        self.assertFalse(nfa.match('ab'))

    def test_dot_in_pattern(self):
        """Test dot within pattern"""
        nfa = compile('a.c')
        self.assertTrue(nfa.match('abc'))
        self.assertTrue(nfa.match('axc'))
        self.assertTrue(nfa.match('a1c'))
        self.assertFalse(nfa.match('ac'))


class TestCompileEscape(unittest.TestCase):
    """Test compile function with escape sequences"""

    def test_escaped_dot(self):
        """Test escaped dot (literal dot)"""
        nfa = compile('\\.')
        self.assertTrue(nfa.match('.'))
        self.assertFalse(nfa.match('a'))

    def test_escaped_asterisk(self):
        """Test escaped asterisk (literal asterisk)"""
        nfa = compile('\\*')
        self.assertTrue(nfa.match('*'))
        self.assertFalse(nfa.match('a'))

    def test_digit_d(self):
        """Test \\d (digit)"""
        nfa = compile('\\d')
        self.assertTrue(nfa.match('0'))
        self.assertTrue(nfa.match('9'))
        self.assertFalse(nfa.match('a'))

    def test_non_digit_D(self):
        """Test \\D (non-digit)"""
        nfa = compile('\\D')
        self.assertTrue(nfa.match('a'))
        self.assertTrue(nfa.match('Z'))
        self.assertFalse(nfa.match('0'))

    def test_whitespace_s(self):
        """Test \\s (whitespace)"""
        nfa = compile('\\s')
        self.assertTrue(nfa.match(' '))
        self.assertTrue(nfa.match('\t'))
        self.assertFalse(nfa.match('a'))

    def test_non_whitespace_S(self):
        """Test \\S (non-whitespace)"""
        nfa = compile('\\S')
        self.assertTrue(nfa.match('a'))
        self.assertTrue(nfa.match('1'))
        self.assertFalse(nfa.match(' '))

    def test_word_w(self):
        """Test \\w (word character)"""
        nfa = compile('\\w')
        self.assertTrue(nfa.match('a'))
        self.assertTrue(nfa.match('Z'))
        self.assertTrue(nfa.match('0'))
        self.assertTrue(nfa.match('_'))
        self.assertFalse(nfa.match(' '))

    def test_non_word_W(self):
        """Test \\W (non-word character)"""
        nfa = compile('\\W')
        self.assertTrue(nfa.match(' '))
        self.assertTrue(nfa.match('-'))
        self.assertFalse(nfa.match('a'))


class TestCompileCharset(unittest.TestCase):
    """Test compile function with character sets"""

    def test_simple_charset(self):
        """Test simple character set"""
        nfa = compile('[abc]')
        self.assertTrue(nfa.match('a'))
        self.assertTrue(nfa.match('b'))
        self.assertTrue(nfa.match('c'))
        self.assertFalse(nfa.match('d'))

    def test_charset_range(self):
        """Test character set with range"""
        nfa = compile('[a-z]')
        self.assertTrue(nfa.match('a'))
        self.assertTrue(nfa.match('z'))
        self.assertTrue(nfa.match('m'))
        self.assertFalse(nfa.match('A'))
        self.assertFalse(nfa.match('0'))

    def test_charset_digits(self):
        """Test character set with digit range"""
        nfa = compile('[0-9]')
        self.assertTrue(nfa.match('0'))
        self.assertTrue(nfa.match('9'))
        self.assertFalse(nfa.match('a'))

    def test_negated_charset(self):
        """Test negated character set"""
        nfa = compile('[^abc]')
        self.assertTrue(nfa.match('d'))
        self.assertTrue(nfa.match('x'))
        self.assertFalse(nfa.match('a'))
        self.assertFalse(nfa.match('b'))

    def test_charset_in_pattern(self):
        """Test character set within pattern"""
        nfa = compile('a[0-9]b')
        self.assertTrue(nfa.match('a0b'))
        self.assertTrue(nfa.match('a5b'))
        self.assertFalse(nfa.match('aab'))


class TestCompileQuantifiers(unittest.TestCase):
    """Test compile function with quantifiers"""

    def test_asterisk(self):
        """Test * (zero or more) with context"""
        nfa = compile('xa*y')
        self.assertTrue(nfa.match('xy'))
        self.assertTrue(nfa.match('xay'))
        self.assertTrue(nfa.match('xaay'))
        self.assertTrue(nfa.match('xaaay'))
        self.assertFalse(nfa.match('xby'))

    def test_plus(self):
        """Test + (one or more) with context"""
        nfa = compile('xa+y')
        self.assertFalse(nfa.match('xy'))
        self.assertTrue(nfa.match('xay'))
        self.assertTrue(nfa.match('xaay'))
        self.assertTrue(nfa.match('xaaay'))
        self.assertFalse(nfa.match('xby'))

    def test_question(self):
        """Test ? (zero or one)"""
        nfa = compile('a?')
        self.assertTrue(nfa.match(''))
        self.assertTrue(nfa.match('a'))
        self.assertFalse(nfa.match('aa'))
        self.assertFalse(nfa.match('b'))

    def test_question_in_pattern(self):
        """Test ? (zero or one) in pattern"""
        nfa = compile('xa?y')
        self.assertTrue(nfa.match('xy'))
        self.assertTrue(nfa.match('xay'))
        self.assertFalse(nfa.match('xaay'))

    def test_non_greedy_asterisk(self):
        """Test *? (non-greedy zero or more) with context"""
        nfa = compile('xa*?y')
        self.assertTrue(nfa.match('xy'))
        self.assertTrue(nfa.match('xay'))
        self.assertTrue(nfa.match('xaay'))

    def test_non_greedy_plus(self):
        """Test +? (non-greedy one or more) with context"""
        nfa = compile('xa+?y')
        self.assertFalse(nfa.match('xy'))
        self.assertTrue(nfa.match('xay'))
        self.assertTrue(nfa.match('xaay'))

    def test_non_greedy_question(self):
        """Test ?? (non-greedy zero or one) with context"""
        nfa = compile('xa??y')
        self.assertTrue(nfa.match('xy'))
        self.assertTrue(nfa.match('xay'))
        self.assertFalse(nfa.match('xaay'))

    def test_quantifier_in_pattern(self):
        """Test quantifiers within pattern"""
        nfa = compile('ab*c')
        self.assertTrue(nfa.match('ac'))
        self.assertTrue(nfa.match('abc'))
        self.assertTrue(nfa.match('abbc'))
        self.assertFalse(nfa.match('a'))


class TestCompileAlternation(unittest.TestCase):
    """Test compile function with alternation"""

    def test_simple_alternation(self):
        """Test simple alternation (a|b)"""
        nfa = compile('a|b')
        self.assertTrue(nfa.match('a'))
        self.assertTrue(nfa.match('b'))
        self.assertFalse(nfa.match('c'))
        self.assertFalse(nfa.match(''))

    def test_alternation_sequences(self):
        """Test alternation with sequences"""
        nfa = compile('ab|cd')
        self.assertTrue(nfa.match('ab'))
        self.assertTrue(nfa.match('cd'))
        self.assertFalse(nfa.match('a'))
        self.assertFalse(nfa.match('ac'))

    def test_three_way_alternation(self):
        """Test three-way alternation"""
        nfa = compile('a|b|c')
        self.assertTrue(nfa.match('a'))
        self.assertTrue(nfa.match('b'))
        self.assertTrue(nfa.match('c'))
        self.assertFalse(nfa.match('d'))


class TestCompileGroups(unittest.TestCase):
    """Test compile function with groups"""

    def test_simple_group(self):
        """Test simple group"""
        nfa = compile('(ab)')
        self.assertTrue(nfa.match('ab'))
        self.assertFalse(nfa.match('a'))

    def test_group_with_quantifier(self):
        """Test group with quantifier"""
        nfa = compile('x(ab)*y')
        self.assertTrue(nfa.match('xy'))
        self.assertTrue(nfa.match('xaby'))
        self.assertTrue(nfa.match('xababy'))
        self.assertTrue(nfa.match('xabababy'))
        self.assertFalse(nfa.match('xay'))

    def test_group_alternation(self):
        """Test alternation within group"""
        nfa = compile('(a|b)c')
        self.assertTrue(nfa.match('ac'))
        self.assertTrue(nfa.match('bc'))
        self.assertFalse(nfa.match('c'))


class TestCompileComplex(unittest.TestCase):
    """Test compile function with complex patterns"""

    def test_dot_asterisk(self):
        """Test .* pattern with context"""
        nfa = compile('a.*b')
        self.assertTrue(nfa.match('ab'))
        self.assertTrue(nfa.match('axb'))
        self.assertTrue(nfa.match('abcb'))
        self.assertTrue(nfa.match('a123b'))

    def test_dot_plus(self):
        """Test .+ pattern with context"""
        nfa = compile('a.+b')
        self.assertFalse(nfa.match('ab'))
        self.assertTrue(nfa.match('axb'))
        self.assertTrue(nfa.match('abcb'))

    def test_pattern_with_anchors(self):
        """Test pattern a.*b"""
        nfa = compile('a.*b')
        self.assertTrue(nfa.match('ab'))
        self.assertTrue(nfa.match('axb'))
        self.assertTrue(nfa.match('axxxb'))
        self.assertFalse(nfa.match('a'))
        self.assertFalse(nfa.match('b'))

    def test_alternation_with_quantifiers(self):
        """Test x(a|b)*y pattern"""
        nfa = compile('x(a|b)*y')
        self.assertTrue(nfa.match('xy'))
        self.assertTrue(nfa.match('xay'))
        self.assertTrue(nfa.match('xaby'))
        self.assertTrue(nfa.match('xababy'))
        self.assertTrue(nfa.match('xbay'))
        self.assertFalse(nfa.match('xcy'))

    def test_complex_pattern_1(self):
        """Test complex pattern xa[0-9]+by"""
        nfa = compile('xa[0-9]+by')
        self.assertTrue(nfa.match('xa0by'))
        self.assertTrue(nfa.match('xa123by'))
        self.assertFalse(nfa.match('xaby'))
        self.assertFalse(nfa.match('xaaby'))

    def test_complex_pattern_2(self):
        """Test complex pattern x\\d+\\.\\d+y"""
        nfa = compile('x\\d+\\.\\d+y')
        self.assertTrue(nfa.match('x1.0y'))
        self.assertTrue(nfa.match('x123.456y'))
        self.assertFalse(nfa.match('x1y'))
        self.assertFalse(nfa.match('x.5y'))

    def test_complex_pattern_3(self):
        """Test complex pattern x[a-z]+@[a-z]+y"""
        nfa = compile('x[a-z]+@[a-z]+y')
        self.assertTrue(nfa.match('xuser@hosty'))
        self.assertTrue(nfa.match('xabc@xyzy'))
        self.assertFalse(nfa.match('xuser@y'))
        self.assertFalse(nfa.match('x@hosty'))
