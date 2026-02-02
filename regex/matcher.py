import string
from typing import List, Tuple, Set, Dict, Optional


class Context(object):

    def __init__(self, s: str) -> None:
        self.s: str = s
        self.len: int = len(self.s)
        self.matches: List[int] = []
        self.groups: List['GroupMatch'] = []

    def __repr__(self) -> str:
        return '<regex context>'


class Str(str):

    def __call__(self, ctx: Context, cur: int) -> Tuple[bool, int]:
        if ctx.len-cur < len(self):
            return False, cur
        if ctx.s[cur:cur+len(self)] != self:
            return False, cur
        return True, cur+len(self)


class Any(object):

    def __repr__(self) -> str:
        return '.'

    def __call__(self, ctx: Context, cur: int) -> Tuple[bool, int]:
        if ctx.len <= cur:
            return False, cur
        return True, cur+1

any: Any = Any()


class Charset(object):

    def __init__(self, charset: Optional[Set[str]] = None, include: bool = True) -> None:
        if charset is None:
            charset = set()
        self.charset: Set[str] = charset
        self.include: bool = include

    def __repr__(self) -> str:
        return f'charset({self.include}, "{"".join(sorted(self.charset))}")'

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Charset):
            return False
        return self.charset == o.charset and self.include == o.include

    @classmethod
    def eval(cls, exp: str, cur: int) -> Tuple['Charset', int]:
        self = cls()

        if exp[cur] == '^':
            self.include = False
            cur += 1

        while cur < len(exp):
            if cur+2 < len(exp) and exp[cur+1] == '-':
                for c in range(ord(exp[cur]), ord(exp[cur+2])+1):
                    self.charset.add(chr(c))
                cur += 3

            elif cur+1 < len(exp) and exp[cur] == '\\':
                if exp[cur+1] in SPECIAL_QUOTES:
                    sq = SPECIAL_QUOTES[exp[cur+1]]
                    if sq.include != self.include:
                        raise Exception(f'invalid charset in {exp}')
                    self.charset |= sq.charset
                else:
                    self.charset.add(exp[cur+1])
                cur += 2

            elif exp[cur] == ']':
                cur += 1
                break

            else:
                self.charset.add(exp[cur])
                cur += 1

        return self, cur

    def __call__(self, ctx: Context, cur: int) -> Tuple[bool, int]:
        if ctx.len <= cur:
            return False, cur
        if self.include != (ctx.s[cur] in self.charset):
            return False, cur
        return True, cur+1


SPECIAL_QUOTES: Dict[str, Charset] = {
    'd': Charset(charset=set(string.digits), include=True),
    'D': Charset(charset=set(string.digits), include=False),
    's': Charset(charset=set(string.whitespace), include=True),
    'S': Charset(charset=set(string.whitespace), include=False),
    'w': Charset(charset=set('_'+string.ascii_letters+string.digits), include=True),
    'W': Charset(charset=set('_'+string.ascii_letters+string.digits), include=False),
}


class GroupMatch(object):

    def __init__(self, n: int, name: str, start: int) -> None:
        self.n: int = n
        self.name: str = name
        self.start: int = start
        self.end: Optional[int] = None

    def __repr__(self) -> str:
        return f'<group "{self.name}" {self.n}>: {self.start}-{self.end or ""}'


class Group(object):

    def __init__(self, name: str, n: int) -> None:
        self.name: str = name
        self.n: int = n

    def __repr__(self) -> str:
        return f'<group "{self.name}" {self.n+1}>'

    def left(self, ctx: Context, cur: int) -> Tuple[bool, int]:
        if len(ctx.groups) <= self.n:
            ctx.groups.append(GroupMatch(self.n, self.name, cur))
        else:
            ctx.groups[self.n].start = cur
        return True, cur

    def right(self, ctx: Context, cur: int) -> Tuple[bool, int]:
        ctx.groups[self.n].end = cur
        return True, cur
