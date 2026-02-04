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
