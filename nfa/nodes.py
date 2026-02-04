"""
Node definition for NFA.
"""
from typing import List, Set, Tuple
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
