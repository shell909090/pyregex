"""
Match strings using NFA.
"""
import logging
from typing import List, Set, Tuple, Optional
from .edges import Empty
from .nodes import Node


def match(r: Node, s: str) -> bool:
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
    sts: List[Tuple[int, Node]] = [(0, r)]

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
            if isinstance(e, Empty):
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
