import unittest

from .nodes import Node
from .edges import Empty, Char, Any, Charset


class TestNode(unittest.TestCase):

    def test_init_without_name(self):
        """Test node initialization without name"""
        node = Node()
        self.assertIsNone(node.name)
        self.assertEqual(node.outs, [])

    def test_init_with_name(self):
        """Test node initialization with name"""
        node = Node('start')
        self.assertEqual(node.name, 'start')
        self.assertEqual(node.outs, [])

    def test_repr_without_name(self):
        """Test __repr__ without name returns id"""
        node = Node()
        repr_str = repr(node)
        self.assertEqual(repr_str, str(id(node)))

    def test_repr_with_name(self):
        """Test __repr__ with name returns name"""
        node = Node('test_node')
        self.assertEqual(repr(node), 'test_node')

    def test_add_single_edge(self):
        """Test adding a single edge to node"""
        node1 = Node('node1')
        node2 = Node('node2')
        edge = Char('a')

        node1.outs.append((edge, node2))

        self.assertEqual(len(node1.outs), 1)
        self.assertEqual(node1.outs[0][0], edge)
        self.assertEqual(node1.outs[0][1], node2)

    def test_add_multiple_edges(self):
        """Test adding multiple edges to node"""
        node1 = Node('node1')
        node2 = Node('node2')
        node3 = Node('node3')

        edge1 = Char('a')
        edge2 = Char('b')

        node1.outs.append((edge1, node2))
        node1.outs.append((edge2, node3))

        self.assertEqual(len(node1.outs), 2)
        self.assertEqual(node1.outs[0][1], node2)
        self.assertEqual(node1.outs[1][1], node3)

    def test_graph2dot_single_node(self):
        """Test DOT generation for single node"""
        node = Node('start')
        dot = node.graph2dot()

        self.assertIn('digraph G {', dot)
        self.assertIn('"start" [label=""]', dot)
        self.assertIn('}', dot)

    def test_graph2dot_two_nodes(self):
        """Test DOT generation for two connected nodes"""
        node1 = Node('n1')
        node2 = Node('n2')
        edge = Char('a')

        node1.outs.append((edge, node2))

        dot = node1.graph2dot()

        self.assertIn('digraph G {', dot)
        self.assertIn('"n1" [label=""]', dot)
        self.assertIn('"n2" [label=""]', dot)
        self.assertIn('"n1" -> "n2" [label="a"]', dot)
        self.assertIn('}', dot)

    def test_graph2dot_chain(self):
        """Test DOT generation for a chain of nodes"""
        node1 = Node('n1')
        node2 = Node('n2')
        node3 = Node('n3')

        node1.outs.append((Char('a'), node2))
        node2.outs.append((Char('b'), node3))

        dot = node1.graph2dot()

        self.assertIn('"n1" -> "n2" [label="a"]', dot)
        self.assertIn('"n2" -> "n3" [label="b"]', dot)

    def test_graph2dot_with_epsilon(self):
        """Test DOT generation with epsilon edge"""
        node1 = Node('n1')
        node2 = Node('n2')

        node1.outs.append((Empty(), node2))

        dot = node1.graph2dot()

        self.assertIn('"n1" -> "n2" [label="ε"]', dot)

    def test_graph2dot_branching(self):
        """Test DOT generation with branching (multiple outgoing edges)"""
        node1 = Node('n1')
        node2 = Node('n2')
        node3 = Node('n3')

        node1.outs.append((Char('a'), node2))
        node1.outs.append((Char('b'), node3))

        dot = node1.graph2dot()

        self.assertIn('"n1" -> "n2" [label="a"]', dot)
        self.assertIn('"n1" -> "n3" [label="b"]', dot)

    def test_graph2dot_cycle(self):
        """Test DOT generation with a cycle (loop back to earlier node)"""
        node1 = Node('n1')
        node2 = Node('n2')

        node1.outs.append((Char('a'), node2))
        node2.outs.append((Char('b'), node1))  # Cycle back

        dot = node1.graph2dot()

        # Both edges should be present
        self.assertIn('"n1" -> "n2" [label="a"]', dot)
        self.assertIn('"n2" -> "n1" [label="b"]', dot)
        # Each node should appear only once in node definitions
        node_defs = [line for line in dot.split('\n') if '[label=""]' in line]
        self.assertEqual(len(node_defs), 2)

    def test_graph2dot_with_any(self):
        """Test DOT generation with Any edge"""
        node1 = Node('n1')
        node2 = Node('n2')

        node1.outs.append((Any(), node2))

        dot = node1.graph2dot()

        self.assertIn('"n1" -> "n2" [label="."]', dot)

    def test_graph2dot_with_charset(self):
        """Test DOT generation with Charset edge"""
        node1 = Node('n1')
        node2 = Node('n2')

        charset = Charset(set('abc'), True)
        node1.outs.append((charset, node2))

        dot = node1.graph2dot()

        self.assertIn('"n1" -> "n2"', dot)
        self.assertIn('[abc]', dot)


class TestMatchBasic(unittest.TestCase):
    """Test basic matching scenarios"""

    def test_empty_nfa_empty_string(self):
        """Test empty NFA matches empty string"""
        node = Node('end')
        self.assertTrue(node.match(''))

    def test_empty_nfa_non_empty_string(self):
        """Test empty NFA does not match non-empty string"""
        node = Node('end')
        self.assertFalse(node.match('a'))

    def test_single_char_match(self):
        """Test single character match"""
        end = Node('end')
        start = Node('start')
        start.outs.append((Char('a'), end))

        self.assertTrue(start.match('a'))
        self.assertFalse(start.match('b'))
        self.assertFalse(start.match(''))
        self.assertFalse(start.match('aa'))

    def test_two_char_sequence(self):
        """Test two character sequence"""
        end = Node('end')
        mid = Node('mid')
        start = Node('start')

        start.outs.append((Char('a'), mid))
        mid.outs.append((Char('b'), end))

        self.assertTrue(start.match('ab'))
        self.assertFalse(start.match('a'))
        self.assertFalse(start.match('b'))
        self.assertFalse(start.match('ba'))
        self.assertFalse(start.match('abc'))

    def test_three_char_sequence(self):
        """Test three character sequence"""
        end = Node('end')
        n2 = Node('n2')
        n1 = Node('n1')
        start = Node('start')

        start.outs.append((Char('a'), n1))
        n1.outs.append((Char('b'), n2))
        n2.outs.append((Char('c'), end))

        self.assertTrue(start.match('abc'))
        self.assertFalse(start.match('ab'))
        self.assertFalse(start.match('abcd'))


class TestMatchEpsilon(unittest.TestCase):
    """Test epsilon (Empty) transitions"""

    def test_epsilon_transition(self):
        """Test epsilon transition between nodes"""
        end = Node('end')
        mid = Node('mid')
        start = Node('start')

        start.outs.append((Empty(), mid))
        mid.outs.append((Char('a'), end))

        self.assertTrue(start.match('a'))
        self.assertFalse(start.match(''))
        self.assertFalse(start.match('b'))

    def test_multiple_epsilon_transitions(self):
        """Test multiple epsilon transitions"""
        end = Node('end')
        n2 = Node('n2')
        n1 = Node('n1')
        start = Node('start')

        start.outs.append((Empty(), n1))
        n1.outs.append((Empty(), n2))
        n2.outs.append((Char('a'), end))

        self.assertTrue(start.match('a'))

    def test_epsilon_to_end(self):
        """Test epsilon transition to end (optional pattern)"""
        end = Node('end')
        start = Node('start')

        start.outs.append((Empty(), end))
        start.outs.append((Char('a'), end))

        self.assertTrue(start.match(''))
        self.assertTrue(start.match('a'))
        self.assertFalse(start.match('b'))


class TestMatchAny(unittest.TestCase):
    """Test Any (.) edge matching"""

    def test_any_single_char(self):
        """Test Any matches any single character"""
        end = Node('end')
        start = Node('start')
        start.outs.append((Any(), end))

        self.assertTrue(start.match('a'))
        self.assertTrue(start.match('b'))
        self.assertTrue(start.match('1'))
        self.assertTrue(start.match(' '))
        self.assertFalse(start.match(''))
        self.assertFalse(start.match('ab'))

    def test_any_in_sequence(self):
        """Test Any in a sequence"""
        end = Node('end')
        n2 = Node('n2')
        n1 = Node('n1')
        start = Node('start')

        start.outs.append((Char('a'), n1))
        n1.outs.append((Any(), n2))
        n2.outs.append((Char('c'), end))

        self.assertTrue(start.match('abc'))
        self.assertTrue(start.match('axc'))
        self.assertTrue(start.match('a1c'))
        self.assertFalse(start.match('ac'))


class TestMatchCharset(unittest.TestCase):
    """Test Charset edge matching"""

    def test_charset_include(self):
        """Test positive character class"""
        end = Node('end')
        start = Node('start')
        start.outs.append((Charset(set('abc'), True), end))

        self.assertTrue(start.match('a'))
        self.assertTrue(start.match('b'))
        self.assertTrue(start.match('c'))
        self.assertFalse(start.match('d'))
        self.assertFalse(start.match(''))

    def test_charset_exclude(self):
        """Test negative character class"""
        end = Node('end')
        start = Node('start')
        start.outs.append((Charset(set('abc'), False), end))

        self.assertTrue(start.match('d'))
        self.assertTrue(start.match('x'))
        self.assertTrue(start.match('1'))
        self.assertFalse(start.match('a'))
        self.assertFalse(start.match('b'))


class TestMatchBranching(unittest.TestCase):
    """Test branching (alternation) patterns"""

    def test_simple_alternation(self):
        """Test simple alternation (a|b)"""
        end = Node('end')
        start = Node('start')

        start.outs.append((Char('a'), end))
        start.outs.append((Char('b'), end))

        self.assertTrue(start.match('a'))
        self.assertTrue(start.match('b'))
        self.assertFalse(start.match('c'))
        self.assertFalse(start.match(''))

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

        self.assertTrue(start.match('ab'))
        self.assertTrue(start.match('cd'))
        self.assertFalse(start.match('a'))
        self.assertFalse(start.match('c'))
        self.assertFalse(start.match('ac'))


class TestMatchLoops(unittest.TestCase):
    """Test loop patterns (*, +, ?)"""

    def test_zero_or_more_star(self):
        """Test zero or more pattern (a*)"""
        end = Node('end')
        start = Node('start')

        # a* pattern: start can go to end (epsilon) or loop back
        start.outs.append((Empty(), end))  # Zero a's
        start.outs.append((Char('a'), start))  # One or more a's

        self.assertTrue(start.match(''))
        self.assertTrue(start.match('a'))
        self.assertTrue(start.match('aa'))
        self.assertTrue(start.match('aaa'))
        self.assertFalse(start.match('b'))
        self.assertFalse(start.match('ab'))

    def test_one_or_more_plus(self):
        """Test one or more pattern (a+)"""
        end = Node('end')
        loop = Node('loop')
        start = Node('start')

        # a+ pattern: must match at least one 'a'
        start.outs.append((Char('a'), loop))
        loop.outs.append((Empty(), end))  # End after one or more
        loop.outs.append((Char('a'), loop))  # Loop for more

        self.assertFalse(start.match(''))
        self.assertTrue(start.match('a'))
        self.assertTrue(start.match('aa'))
        self.assertTrue(start.match('aaa'))
        self.assertFalse(start.match('b'))

    def test_optional_question(self):
        """Test optional pattern (a?)"""
        end = Node('end')
        start = Node('start')

        # a? pattern: can match zero or one 'a'
        start.outs.append((Empty(), end))  # Zero a's
        start.outs.append((Char('a'), end))  # One a

        self.assertTrue(start.match(''))
        self.assertTrue(start.match('a'))
        self.assertFalse(start.match('aa'))
        self.assertFalse(start.match('b'))

    def test_any_star(self):
        """Test .* pattern"""
        end = Node('end')
        start = Node('start')

        # .* pattern: match any characters zero or more times
        start.outs.append((Empty(), end))
        start.outs.append((Any(), start))

        self.assertTrue(start.match(''))
        self.assertTrue(start.match('a'))
        self.assertTrue(start.match('abc'))
        self.assertTrue(start.match('123'))


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

        self.assertTrue(start.match('ac'))
        self.assertTrue(start.match('abc'))
        self.assertTrue(start.match('abbc'))
        self.assertTrue(start.match('abbbc'))
        self.assertFalse(start.match('a'))
        self.assertFalse(start.match('ab'))
        self.assertFalse(start.match('c'))

    def test_a_or_b_star(self):
        """Test pattern (a|b)*"""
        end = Node('end')
        start = Node('start')

        # Pattern: (a|b)*
        start.outs.append((Empty(), end))  # Zero matches
        start.outs.append((Char('a'), start))  # Match 'a' and loop
        start.outs.append((Char('b'), start))  # Match 'b' and loop

        self.assertTrue(start.match(''))
        self.assertTrue(start.match('a'))
        self.assertTrue(start.match('b'))
        self.assertTrue(start.match('ab'))
        self.assertTrue(start.match('ba'))
        self.assertTrue(start.match('aabb'))
        self.assertTrue(start.match('abab'))
        self.assertFalse(start.match('c'))
        self.assertFalse(start.match('abc'))

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

        self.assertTrue(start.match('a'))
        self.assertTrue(start.match('aa'))
        self.assertTrue(start.match('b'))
        self.assertTrue(start.match('bb'))
        self.assertFalse(start.match(''))
        self.assertFalse(start.match('ab'))
        self.assertFalse(start.match('ba'))


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
        self.assertFalse(start.match('a'))

    def test_self_loop(self):
        """Test self-looping node"""
        end = Node('end')
        start = Node('start')

        # Self loop on 'a', then to end
        start.outs.append((Char('a'), start))
        start.outs.append((Empty(), end))

        self.assertTrue(start.match(''))
        self.assertTrue(start.match('a'))
        self.assertTrue(start.match('aa'))
        self.assertTrue(start.match('aaaa'))

    def test_partial_match_fails(self):
        """Test that partial matches fail (must consume entire string)"""
        end = Node('end')
        start = Node('start')
        start.outs.append((Char('a'), end))

        # 'a' matches, but 'ab' should fail because 'b' is not consumed
        self.assertTrue(start.match('a'))
        self.assertFalse(start.match('ab'))
        self.assertFalse(start.match('abc'))

    def test_multiple_paths_to_end(self):
        """Test NFA with multiple paths to accept state"""
        end = Node('end')
        n1 = Node('n1')
        start = Node('start')

        # Two paths: start->n1->end (via 'a','b')
        #            start->end (via 'c')
        start.outs.append((Char('a'), n1))
        n1.outs.append((Char('b'), end))
        start.outs.append((Char('c'), end))

        self.assertTrue(start.match('ab'))
        self.assertTrue(start.match('c'))
        self.assertFalse(start.match('a'))
        self.assertFalse(start.match('b'))
