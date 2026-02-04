"""
Node definition for NFA.
"""
from typing import List, Tuple, Any


class Node(object):
    """
    NFA state node.
    Each node has a list of outgoing edges (transitions).
    """

    def __init__(self) -> None:
        """Initialize empty node with no outgoing edges."""
        self.outs: List[Tuple[Any, 'Node']] = []

    def __repr__(self) -> str:
        return '|'.join(f'{e} {e.next if e.next else ""}' for e in self.outs)
            


def to_list(li):
    p = None
    for e in reversed(li):
        e.next = p
        n = Node()
        n.outs.append(e)
        p = n
    return p


def graph2dot(node: Node) -> str:
    nodes = [node]
    done = set()
    dot_content = "digraph G {\n"
    while nodes:
        p = nodes.pop(0)
        if p in done:
            continue
        dot_content += f'    "{id(p)}" [label=""];\n'
        for e in p.outs:
            next = id(e.next) if e.next else 'end'
            dot_content += f'    "{id(p)}" -> "{next}" [label="{e}"];\n'
            if e.next:
                nodes.append(e.next)
        done.add(p)
    dot_content += "}"
    return dot_content
