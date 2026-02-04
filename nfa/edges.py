"""
Edge types for NFA regex engine.

All edge types inherit from the Edge base class and implement
the match() method for their specific matching logic.
"""
import string
from typing import Set, Optional, Dict, Tuple
from abc import ABC, abstractmethod


class Edge(ABC):
    """Abstract base for NFA edges - decoupled from nodes, only check transition conditions."""

    @abstractmethod
    def match(self, s: str, cur: int) -> Optional[int]:
        """Try to match at position, return new position or None."""
        pass


class Empty(Edge):
    """Epsilon edge - transitions without consuming input."""

    def __repr__(self) -> str:
        return 'ε'

    def match(self, s: str, cur: int) -> int:
        """Always succeeds, returns current position unchanged."""
        return cur


class Any(Edge):
    """Matches any single character if available."""

    def __repr__(self) -> str:
        return '.'

    def match(self, s: str, cur: int) -> Optional[int]:
        """Advance by one if char available."""
        if cur >= len(s):
            return None
        return cur+1


class Char(Edge):
    """Matches a specific character."""

    def __init__(self, c: str) -> None:
        self.c: str = c

    def __repr__(self) -> str:
        return self.c

    def match(self, s: str, cur: int) -> Optional[int]:
        """Match if current char equals expected char."""
        if cur >= len(s):
            return None
        if s[cur] != self.c:
            return None
        return cur+1


class Charset(Edge):
    """Matches chars in/not-in a set, for [a-z] or [^0-9] patterns."""

    def __init__(self, s: Set[str], include: bool) -> None:
        self.s: Set[str] = set(s)
        self.include: bool = include

    def __repr__(self) -> str:
        return f'[{"^" if not self.include else ""}{"".join(sorted(self.s))}]'

    def match(self, s: str, cur: int) -> Optional[int]:
        """Check if char is in/not-in set based on include flag."""
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
