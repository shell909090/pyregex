"""
Node definition for NFA.
"""
import logging
from typing import List, Set, Tuple, Dict, Optional
from .edges import Edge


class Node(object):
    """
    NFA state node.

    Each node contains a list of outgoing transitions, where each transition
    is a tuple of (edge, target_node). The edge determines the matching logic,
    while the target_node specifies where to go next.

    This design decouples the edge matching logic from the graph structure.
    """

    def __init__(self, name=None) -> None:
        """Initialize empty node with no outgoing edges."""
        self.name = name
        self.outs: List[Tuple[Edge, 'Node']] = []

    def __repr__(self) -> str:
        if self.name:
            return self.name
        return str(id(self))

    def clone(self, mapping: Dict['Node', 'Node']) -> 'Node':
        """
        Clone this node and all its descendants, using a mapping to handle shared nodes.

        This method performs a deep copy of the node graph structure while preserving
        the topology. The mapping parameter tracks already-cloned nodes to ensure that
        shared nodes in the original graph remain shared in the cloned graph.

        Args:
            mapping: Dictionary mapping original nodes to their clones. This is used
                    to handle cycles and shared nodes correctly.

        Returns:
            The cloned node corresponding to this node
        """
        if self in mapping:
            return mapping[self]
        nn = Node(self.name)
        mapping[self] = nn
        for e, n in self.outs:
            nn.outs.append((e, n.clone(mapping)))
        return nn

    def graph2dot(self) -> str:
        """
        Generate Graphviz DOT format representation of the NFA.

        Returns:
            DOT format string for visualization
        """
        nodes: List['Node'] = [self]
        done: Set['Node'] = set()
        dot_content = "digraph G {\n"
        while nodes:
            p = nodes.pop(0)
            if p in done:
                continue
            dot_content += f'    "{p}" [label=""];\n'
            for e, next_node in p.outs:
                next_id: str = str(next_node) if next_node else 'end'
                dot_content += f'    "{p}" -> "{next_id}" [label="{e}"];\n'
                if next_node:
                    nodes.append(next_node)
            done.add(p)
        dot_content += "}"
        return dot_content

    def match(self, s: str) -> bool:
        """
        Match string against NFA using breadth-first search.

        The algorithm maintains a queue of states (position, node) and explores
        all possible paths through the NFA. A state is accepted if we reach a
        node with no outgoing edges and have consumed the entire input string.

        Args:
            r: Start node of the NFA
            s: String to match

        Returns:
            True if string matches the NFA, False otherwise
        """
        # Queue of (position, node) states to explore
        sts: List[Tuple[int, Node]] = [(0, self)]

        # Set of (position, node_id) to avoid revisiting same state
        history: Set[Tuple[int, int]] = set()

        while sts:
            logging.debug(sts)
            cur, node = sts.pop(0)

            # Accept state: no outgoing edges and consumed entire input
            if not node.outs and cur == len(s):
                return True

            # Explore all outgoing edges
            for e, next_node in node.outs:
                # Mark epsilon transitions in history before matching
                history.add((cur, id(node)))

                # Try to match the edge
                new_cur: Optional[int] = e.match(s, cur)
                if new_cur is None:
                    continue

                # Check if we've seen this state before
                state_key = (new_cur, id(next_node))
                if state_key in history:
                    continue

                # Add new state to queue
                sts.append((new_cur, next_node))

        return False
