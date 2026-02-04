"""
NFA-based regex engine.
"""
from .compile import compile
from .match import match
from .nodes import Node

__all__ = ['compile', 'match', 'Node']
