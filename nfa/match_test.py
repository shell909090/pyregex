import unittest

from .match import match
from .nodes import Node
from .edges import Empty, Char, Any, Charset


class TestMatchBasic(unittest.TestCase):
    """Test basic matching scenarios"""

    def test_empty_nfa_empty_string(self):
        """Test empty NFA matches empty string"""
        node = Node('end')
        self.assertTrue(match(node, ''))

    def test_empty_nfa_non_empty_string(self):
        """Test empty NFA does not match non-empty string"""
        node = Node('end')
        self.assertFalse(match(node, 'a'))

    def test_single_char_match(self):
        """Test single character match"""
        end = Node('end')
        start = Node('start')
        start.outs.append((Char('a'), end))

        self.assertTrue(match(start, 'a'))
        self.assertFalse(match(start, 'b'))
        self.assertFalse(match(start, ''))
        self.assertFalse(match(start, 'aa'))

    def test_two_char_sequence(self):
        """Test two character sequence"""
        end = Node('end')
        mid = Node('mid')
        start = Node('start')

        start.outs.append((Char('a'), mid))
        mid.outs.append((Char('b'), end))

        self.assertTrue(match(start, 'ab'))
        self.assertFalse(match(start, 'a'))
        self.assertFalse(match(start, 'b'))
        self.assertFalse(match(start, 'ba'))
        self.assertFalse(match(start, 'abc'))

    def test_three_char_sequence(self):
        """Test three character sequence"""
        end = Node('end')
        n2 = Node('n2')
        n1 = Node('n1')
        start = Node('start')

        start.outs.append((Char('a'), n1))
        n1.outs.append((Char('b'), n2))
        n2.outs.append((Char('c'), end))

        self.assertTrue(match(start, 'abc'))
        self.assertFalse(match(start, 'ab'))
        self.assertFalse(match(start, 'abcd'))


class TestMatchEpsilon(unittest.TestCase):
    """Test epsilon (Empty) transitions"""

    def test_epsilon_transition(self):
        """Test epsilon transition between nodes"""
        end = Node('end')
        mid = Node('mid')
        start = Node('start')

        start.outs.append((Empty(), mid))
        mid.outs.append((Char('a'), end))

        self.assertTrue(match(start, 'a'))
        self.assertFalse(match(start, ''))
        self.assertFalse(match(start, 'b'))

    def test_multiple_epsilon_transitions(self):
        """Test multiple epsilon transitions"""
        end = Node('end')
        n2 = Node('n2')
        n1 = Node('n1')
        start = Node('start')

        start.outs.append((Empty(), n1))
        n1.outs.append((Empty(), n2))
        n2.outs.append((Char('a'), end))

        self.assertTrue(match(start, 'a'))

    def test_epsilon_to_end(self):
        """Test epsilon transition to end (optional pattern)"""
        end = Node('end')
        start = Node('start')

        start.outs.append((Empty(), end))
        start.outs.append((Char('a'), end))

        self.assertTrue(match(start, ''))
        self.assertTrue(match(start, 'a'))
        self.assertFalse(match(start, 'b'))


class TestMatchAny(unittest.TestCase):
    """Test Any (.) edge matching"""

    def test_any_single_char(self):
        """Test Any matches any single character"""
        end = Node('end')
        start = Node('start')
        start.outs.append((Any(), end))

        self.assertTrue(match(start, 'a'))
        self.assertTrue(match(start, 'b'))
        self.assertTrue(match(start, '1'))
        self.assertTrue(match(start, ' '))
        self.assertFalse(match(start, ''))
        self.assertFalse(match(start, 'ab'))

    def test_any_in_sequence(self):
        """Test Any in a sequence"""
        end = Node('end')
        n2 = Node('n2')
        n1 = Node('n1')
        start = Node('start')

        start.outs.append((Char('a'), n1))
        n1.outs.append((Any(), n2))
        n2.outs.append((Char('c'), end))

        self.assertTrue(match(start, 'abc'))
        self.assertTrue(match(start, 'axc'))
        self.assertTrue(match(start, 'a1c'))
        self.assertFalse(match(start, 'ac'))


class TestMatchCharset(unittest.TestCase):
    """Test Charset edge matching"""

    def test_charset_include(self):
        """Test positive character class"""
        end = Node('end')
        start = Node('start')
        start.outs.append((Charset(set('abc'), True), end))

        self.assertTrue(match(start, 'a'))
        self.assertTrue(match(start, 'b'))
        self.assertTrue(match(start, 'c'))
        self.assertFalse(match(start, 'd'))
        self.assertFalse(match(start, ''))

    def test_charset_exclude(self):
        """Test negative character class"""
        end = Node('end')
        start = Node('start')
        start.outs.append((Charset(set('abc'), False), end))

        self.assertTrue(match(start, 'd'))
        self.assertTrue(match(start, 'x'))
        self.assertTrue(match(start, '1'))
        self.assertFalse(match(start, 'a'))
        self.assertFalse(match(start, 'b'))


class TestMatchBranching(unittest.TestCase):
    """Test branching (alternation) patterns"""

    def test_simple_alternation(self):
        """Test simple alternation (a|b)"""
        end = Node('end')
        start = Node('start')

        start.outs.append((Char('a'), end))
        start.outs.append((Char('b'), end))

        self.assertTrue(match(start, 'a'))
        self.assertTrue(match(start, 'b'))
        self.assertFalse(match(start, 'c'))
        self.assertFalse(match(start, ''))

    def test_alternation_with_sequences(self):
        """Test alternation with sequences (ab|cd)"""
        end = Node('end')
        n1 = Node('n1')
        n2 = Node('n2')
        start = Node('start')

        # First branch: ab
        start.outs.append((Char('a'), n1))
        n1.outs.append((Char('b'), end))

        # Second branch: cd
        start.outs.append((Char('c'), n2))
        n2.outs.append((Char('d'), end))

        self.assertTrue(match(start, 'ab'))
        self.assertTrue(match(start, 'cd'))
        self.assertFalse(match(start, 'a'))
        self.assertFalse(match(start, 'c'))
        self.assertFalse(match(start, 'ac'))


class TestMatchLoops(unittest.TestCase):
    """Test loop patterns (*, +, ?)"""

    def test_zero_or_more_star(self):
        """Test zero or more pattern (a*)"""
        end = Node('end')
        start = Node('start')

        # a* pattern: start can go to end (epsilon) or loop back
        start.outs.append((Empty(), end))  # Zero a's
        start.outs.append((Char('a'), start))  # One or more a's

        self.assertTrue(match(start, ''))
        self.assertTrue(match(start, 'a'))
        self.assertTrue(match(start, 'aa'))
        self.assertTrue(match(start, 'aaa'))
        self.assertFalse(match(start, 'b'))
        self.assertFalse(match(start, 'ab'))

    def test_one_or_more_plus(self):
        """Test one or more pattern (a+)"""
        end = Node('end')
        loop = Node('loop')
        start = Node('start')

        # a+ pattern: must match at least one 'a'
        start.outs.append((Char('a'), loop))
        loop.outs.append((Empty(), end))  # End after one or more
        loop.outs.append((Char('a'), loop))  # Loop for more

        self.assertFalse(match(start, ''))
        self.assertTrue(match(start, 'a'))
        self.assertTrue(match(start, 'aa'))
        self.assertTrue(match(start, 'aaa'))
        self.assertFalse(match(start, 'b'))

    def test_optional_question(self):
        """Test optional pattern (a?)"""
        end = Node('end')
        start = Node('start')

        # a? pattern: can match zero or one 'a'
        start.outs.append((Empty(), end))  # Zero a's
        start.outs.append((Char('a'), end))  # One a

        self.assertTrue(match(start, ''))
        self.assertTrue(match(start, 'a'))
        self.assertFalse(match(start, 'aa'))
        self.assertFalse(match(start, 'b'))

    def test_any_star(self):
        """Test .* pattern"""
        end = Node('end')
        start = Node('start')

        # .* pattern: match any characters zero or more times
        start.outs.append((Empty(), end))
        start.outs.append((Any(), start))

        self.assertTrue(match(start, ''))
        self.assertTrue(match(start, 'a'))
        self.assertTrue(match(start, 'abc'))
        self.assertTrue(match(start, '123'))


class TestMatchComplex(unittest.TestCase):
    """Test complex NFA patterns"""

    def test_ab_star_c(self):
        """Test pattern ab*c"""
        end = Node('end')
        loop = Node('loop')
        start = Node('start')

        # Pattern: a b* c
        start.outs.append((Char('a'), loop))
        loop.outs.append((Char('b'), loop))  # b loop
        loop.outs.append((Char('c'), end))  # end with c

        self.assertTrue(match(start, 'ac'))
        self.assertTrue(match(start, 'abc'))
        self.assertTrue(match(start, 'abbc'))
        self.assertTrue(match(start, 'abbbc'))
        self.assertFalse(match(start, 'a'))
        self.assertFalse(match(start, 'ab'))
        self.assertFalse(match(start, 'c'))

    def test_a_or_b_star(self):
        """Test pattern (a|b)*"""
        end = Node('end')
        start = Node('start')

        # Pattern: (a|b)*
        start.outs.append((Empty(), end))  # Zero matches
        start.outs.append((Char('a'), start))  # Match 'a' and loop
        start.outs.append((Char('b'), start))  # Match 'b' and loop

        self.assertTrue(match(start, ''))
        self.assertTrue(match(start, 'a'))
        self.assertTrue(match(start, 'b'))
        self.assertTrue(match(start, 'ab'))
        self.assertTrue(match(start, 'ba'))
        self.assertTrue(match(start, 'aabb'))
        self.assertTrue(match(start, 'abab'))
        self.assertFalse(match(start, 'c'))
        self.assertFalse(match(start, 'abc'))

    def test_complex_branching_with_loops(self):
        """Test complex pattern with branching and loops"""
        end = Node('end')
        n1 = Node('n1')
        n2 = Node('n2')
        start = Node('start')

        # Pattern: a+|b+
        # First branch: a+
        start.outs.append((Char('a'), n1))
        n1.outs.append((Empty(), end))
        n1.outs.append((Char('a'), n1))

        # Second branch: b+
        start.outs.append((Char('b'), n2))
        n2.outs.append((Empty(), end))
        n2.outs.append((Char('b'), n2))

        self.assertTrue(match(start, 'a'))
        self.assertTrue(match(start, 'aa'))
        self.assertTrue(match(start, 'b'))
        self.assertTrue(match(start, 'bb'))
        self.assertFalse(match(start, ''))
        self.assertFalse(match(start, 'ab'))
        self.assertFalse(match(start, 'ba'))


class TestMatchEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios"""

    def test_epsilon_loop_protection(self):
        """Test that epsilon loops don't cause infinite loops"""
        n1 = Node('n1')
        start = Node('start')

        # Create an epsilon loop
        start.outs.append((Empty(), n1))
        n1.outs.append((Empty(), start))

        # Should not hang, should return False
        self.assertFalse(match(start, 'a'))

    def test_self_loop(self):
        """Test self-looping node"""
        end = Node('end')
        start = Node('start')

        # Self loop on 'a', then to end
        start.outs.append((Char('a'), start))
        start.outs.append((Empty(), end))

        self.assertTrue(match(start, ''))
        self.assertTrue(match(start, 'a'))
        self.assertTrue(match(start, 'aa'))
        self.assertTrue(match(start, 'aaaa'))

    def test_partial_match_fails(self):
        """Test that partial matches fail (must consume entire string)"""
        end = Node('end')
        start = Node('start')
        start.outs.append((Char('a'), end))

        # 'a' matches, but 'ab' should fail because 'b' is not consumed
        self.assertTrue(match(start, 'a'))
        self.assertFalse(match(start, 'ab'))
        self.assertFalse(match(start, 'abc'))

    def test_multiple_paths_to_end(self):
        """Test NFA with multiple paths to accept state"""
        end = Node('end')
        n1 = Node('n1')
        n2 = Node('n2')
        start = Node('start')

        # Two paths: start->n1->end (via 'a','b')
        #            start->n2->end (via 'c')
        start.outs.append((Char('a'), n1))
        n1.outs.append((Char('b'), end))
        start.outs.append((Char('c'), end))

        self.assertTrue(match(start, 'ab'))
        self.assertTrue(match(start, 'c'))
        self.assertFalse(match(start, 'a'))
        self.assertFalse(match(start, 'b'))
