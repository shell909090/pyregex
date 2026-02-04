"""
Edge types for NFA regex engine.

All edge types inherit from the Edge base class and implement
the match() method for their specific matching logic.
"""
import string
from typing import Set, Optional, Dict, Tuple
from abc import ABC, abstractmethod


class Edge(ABC):
    """
    Abstract base class for NFA edges.

    Each edge represents a transition condition in the NFA.
    Edges are decoupled from nodes - they only determine if
    a transition is possible, not where it leads.
    """

    @abstractmethod
    def match(self, s: str, cur: int) -> Optional[int]:
        """
        Attempt to match the edge condition.

        Args:
            s: Input string
            cur: Current position

        Returns:
            New position if match succeeds, None otherwise
        """
        pass


class Empty(Edge):
    """
    Epsilon edge - transition without consuming characters.

    Always succeeds and returns the current position unchanged.
    """

    def __repr__(self) -> str:
        return 'ε'

    def match(self, s: str, cur: int) -> int:
        """
        Match epsilon transition.

        Args:
            s: Input string (unused)
            cur: Current position

        Returns:
            Current position (unchanged)
        """
        return cur


class Any(Edge):
    """
    Any character edge - matches any single character.

    Succeeds if there is at least one character remaining in the input.
    """

    def __repr__(self) -> str:
        return '.'

    def match(self, s: str, cur: int) -> Optional[int]:
        """
        Match any single character.

        Args:
            s: Input string
            cur: Current position

        Returns:
            New position (cur+1) if match succeeds, None otherwise
        """
        if cur >= len(s):
            return None
        return cur+1


class Char(Edge):
    """
    Character edge - matches a specific character.

    Succeeds only if the current character in the input matches
    the expected character.
    """

    def __init__(self, c: str) -> None:
        """
        Initialize character edge.

        Args:
            c: The character to match
        """
        self.c: str = c

    def __repr__(self) -> str:
        return self.c

    def match(self, s: str, cur: int) -> Optional[int]:
        """
        Match specific character.

        Args:
            s: Input string
            cur: Current position

        Returns:
            New position (cur+1) if character matches, None otherwise
        """
        if cur >= len(s):
            return None
        if s[cur] != self.c:
            return None
        return cur+1


class Charset(Edge):
    """
    Character set edge - matches characters from a set.

    Can be used for both positive character classes (match if in set)
    and negative character classes (match if not in set).
    """

    def __init__(self, s: Set[str], include: bool) -> None:
        """
        Initialize character set edge.

        Args:
            s: Set of characters
            include: If True, match chars in set; if False, match chars not in set
        """
        self.s: Set[str] = set(s)
        self.include: bool = include

    def __repr__(self) -> str:
        return f'[{"^" if not self.include else ""}{"".join(sorted(self.s))}]'

    def match(self, s: str, cur: int) -> Optional[int]:
        """
        Match character against set.

        Args:
            s: Input string
            cur: Current position

        Returns:
            New position (cur+1) if character matches set criteria, None otherwise
        """
        if cur >= len(s):
            return None
        if self.include:
            if s[cur] not in self.s:
                return None
        else:
            if s[cur] in self.s:
                return None
        return cur+1


# Type alias for special character class definitions
SPECIAL_QUOTES: Dict[str, Tuple[Set[str], bool]] = {
    'd': (set(string.digits), True),
    'D': (set(string.digits), False),
    's': (set(string.whitespace), True),
    'S': (set(string.whitespace), False),
    'w': (set('_'+string.ascii_letters+string.digits), True),
    'W': (set('_'+string.ascii_letters+string.digits), False),
}
