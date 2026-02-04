"""
Edge types for NFA regex engine.
"""
import copy
import string
from typing import Set, Optional


class Empty(object):

    def __init__(self, next) -> None:
        self.next = next

    def __repr__(self) -> str:
        return 'ε'

    def match(self, st):
        st = copy.copy(st)
        st.n = self.next
        return st


class Any(object):

    def __init__(self, next) -> None:
        self.next = next

    def __repr__(self) -> str:
        return '.'

    def match(self, st):
        if st.cur >= len(st.s):
            return
        st = copy.copy(st)
        st.cur += 1
        st.n = self.next
        return st


class Char(object):

    def __init__(self, next, c) -> None:
        self.next = next
        self.c = c

    def __repr__(self) -> str:
        return self.c

    def match(self, st):
        if st.cur >= len(st.s):
            return
        if st.s[st.cur] != self.c:
            return
        st = copy.copy(st)
        st.cur += 1
        st.n = self.next
        return st


class Charset(object):

    def __init__(self, next, s, include) -> None:
        self.next = next
        self.s = set(s)
        self.include = include

    def __repr__(self) -> str:
        return f'[{"^" if not self.include else ""}{"".join(sorted(self.s))}]'

    def match(self, st):
        if st.cur >= len(st.s):
            return
        if self.include:
            if st.s[st.cur] not in self.s:
                return
        else:
            if st.s[st.cur] in self.s:
                return
        st = copy.copy(st)
        st.cur += 1
        st.n = self.next
        return st


SPECIAL_QUOTES: Dict[str, Charset] = {
    'd': (set(string.digits), True),
    'D': (set(string.digits), False),
    's': (set(string.whitespace), True),
    'S': (set(string.whitespace), False),
    'w': (set('_'+string.ascii_letters+string.digits), True),
    'W': (set('_'+string.ascii_letters+string.digits), False),
}
