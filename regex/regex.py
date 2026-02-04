import logging
from typing import Union, Callable, Iterator, List, Tuple, Generator, Optional

from .matcher import Context, Str, any, Charset, SPECIAL_QUOTES, GroupMatch, Group


# Type alias for matchers
Matcher = Union[Str, Charset, 'any.__class__', Callable[[Context, int], Tuple[bool, int]]]
Element = Union[str, Str, 'Search', Matcher, Callable[[Context, int], Tuple[bool, int]]]


class Search(object):

    def __init__(self, m: Matcher, repeat: str, greedy: bool) -> None:
        self.m: Matcher = m
        self.repeat: str = repeat
        self.greedy: bool = greedy
        self.smallest: int = 0
        self.longest: int = 0
        if repeat.startswith('{'):
            repeat_str = repeat.strip('{}')
            if ',' not in self.repeat:
                self.smallest = self.longest = int(repeat_str)
            else:
                repeat_parts = repeat_str.split(',', 2)
                self.smallest, self.longest = int(repeat_parts[0]), int(repeat_parts[1])

    def __repr__(self) -> str:
        return f'search({self.m}, {self.repeat}, {self.greedy})'

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Search):
            return False
        return self.m == o.m and self.repeat == o.repeat and self.greedy == o.greedy

    def scan(self, ctx: Context, cur: int, start: int, end: int) -> Generator[int, None, None]:
        ''' all the pos that the NEXT matcher could possible be '''
        while end >= cur:
            r, next = self.m(ctx, cur)
            if cur >= start:
                yield cur
            if not r:
                return
            cur = next

    def search(self, ctx: Context, cur: int) -> Iterator[int]:
        """
        Search for matches of this element with quantifier.

        Args:
            ctx: Matching context
            cur: Current position in string

        Returns:
            Iterator of possible match end positions
        """
        if self.repeat == '*':
            r = self.scan(ctx, cur, cur, len(ctx.s))
        elif self.repeat == '+':
            r = self.scan(ctx, cur, cur+1, len(ctx.s))
        elif self.repeat == '?':
            r = self.scan(ctx, cur, cur, min(len(ctx.s), cur+1))
        elif self.repeat.startswith('{'):
            r = self.scan(ctx, cur, cur+self.smallest, min(len(ctx.s), cur+self.longest))
        else:
            raise Exception()  # just in case
        if self.greedy:
            r = reversed(list(r))
        return r


def buffered(f: Callable[['Regex', str], Generator[Element, None, None]]) -> Callable[['Regex', str], Generator[Union[Str, Element], None, None]]:
    """
    Decorator to buffer consecutive string matches into Str elements.

    Args:
        f: Generator function that yields Element objects

    Returns:
        Wrapped generator that yields Str or Element objects with buffered strings
    """
    def _(self: 'Regex', exp: str) -> Generator[Union[Str, Element], None, None]:
        buf = ''
        for m in f(self, exp):
            if isinstance(m, str):
                buf += m
            else:
                if buf:
                    yield Str(buf)
                buf = ''
                yield m
        if buf:
            yield Str(buf)
    return _


def debugging(f: Callable[['Regex', Context, int, int, int], Tuple[bool, int]]) -> Callable[['Regex', Context, int, int, int], Tuple[bool, int]]:
    """
    Decorator to add debug logging to matching functions.

    Args:
        f: Matching function to wrap with debug logging

    Returns:
        Wrapped function with logging output
    """
    def _(self: 'Regex', ctx: Context, ecur: int, scur: int, depth: int) -> Tuple[bool, int]:
        logging.info(f'{"+"*depth}run: "{self.e[:ecur]}{self.e[ecur:]}", "{ctx.s[:scur]}[{ctx.s[scur:]}]"')
        r = f(self, ctx, ecur, scur, depth)
        if r:
            logging.info(f'{"+"*depth}successed match')
        return r
    return _


class Regex(object):

    def __init__(self, exp: Optional[str] = None) -> None:
        self.e: List[Element] = []
        self.groups: List[Group] = []
        self.stack: List[Group] = []
        if exp is not None:
            self.compile(exp)

    def compile(self, exp: str) -> None:
        """
        Compile regular expression string into internal representation.

        Args:
            exp: Regular expression string to compile

        Raises:
            Exception: If there are unmatched parentheses
        """
        self.stack = []
        self.group_id = 1
        self.e = list(self._compile(exp))
        if self.stack:
            raise Exception('')
        del self.stack
        del self.group_id

    @buffered
    def _compile(self, exp: str) -> Generator[Element, None, None]:
        cur = 0
        while len(exp) > cur:
            m, cur = self.eval(exp, cur)

            if len(exp) <= cur:
                yield m
                return

            if exp[cur] not in '*+?{':
                yield m
                continue

            if (
                callable(m)
                and getattr(m, "__name__", "") == "right"
                and isinstance(getattr(m, "__self__", None), Group)
            ):
                raise Exception('quantifier on group is not supported')

            # turn to search
            if exp[cur] == '{':
                pos = exp.find('}', cur+1)
                if pos == -1:
                    raise Exception()
                repeat = exp[cur:pos+1]
                cur = pos+1
            else:
                repeat = exp[cur]
                cur += 1

            greedy = True
            if len(exp) > cur and exp[cur] == '?':
                greedy = False
                cur += 1

            if isinstance(m, str):
                m = Str(m)

            yield Search(m, repeat, greedy)

    def eval(self, exp: str, cur: int) -> Tuple[Union[Element, Callable[[Context, int], Tuple[bool, int]]], int]:
        """
        Parse and evaluate a single regex element from the expression.

        Args:
            exp: Regular expression string
            cur: Current position in the expression

        Returns:
            Tuple of (parsed element, new position)

        Raises:
            Exception: If expression is invalid at current position
        """
        if len(exp) <= cur:
            raise Exception()

        if exp[cur] == '.':
            return any, cur+1

        # TODO: \A \b \B \Z
        if exp[cur] == '\\':
            cur += 1
            if len(exp) <= cur:
                raise Exception()  # TODO: compile exception
            c = exp[cur]
            cur += 1
            if c in SPECIAL_QUOTES:
                return SPECIAL_QUOTES[c], cur
            return c, cur

        if exp[cur] == '[':
            return Charset.eval(exp, cur+1)

        if exp[cur] == '(':
            cur += 1
            name = ''
            if len(exp) > cur+3 and exp[cur:cur+3] == '?P<':
                pos = exp.find('>', cur+3)
                if pos == -1:
                    raise Exception()
                name = exp[cur+3:pos]
                cur = pos+1
            m = Group(name, self.group_id)
            self.group_id += 1
            self.groups.append(m)
            self.stack.append(m)
            return m.left, cur

        if exp[cur] == ')':
            m = self.stack.pop(-1)
            return m.right, cur+1

        c = exp[cur]
        return c, cur+1

    @debugging
    def _match(self, ctx: Context, ecur: int, scur: int, depth: int) -> Tuple[bool, int]:
        sinit = scur
        while len(self.e) > ecur:
            # logging.info(f'loop {self.e[ecur:]}, "{s[scur:]}"')
            m = self.e[ecur]
            if len(ctx.matches) <= ecur:
                ctx.matches.append(scur)
            else:
                ctx.matches[ecur] = scur
            # print(depth, ecur, ctx.matches)

            if hasattr(m, 'search'):
                logging.info(f'{"+"*depth}search {m} in "{ctx.s[scur:]}"')
                for snext in m.search(ctx, scur):
                    r, send = self._match(ctx, ecur+1, snext, depth+1)
                    if r:
                        return True, send
                return False, sinit

            r, snext = m(ctx, scur)
            if not r:
                return False, sinit
            ecur += 1
            scur = snext

        return True, scur

    def match(self, s: str) -> Optional[Context]:
        """
        Match the regex pattern against a string from the beginning.

        Args:
            s: String to match against

        Returns:
            Context object with match information if successful, None otherwise
        """
        ctx = Context(s)
        ctx.groups.append(GroupMatch(0, '', 0))
        r = self._match(ctx, 0, 0, 0)
        if r[0]:
            ctx.groups[0].end = r[1]
            return ctx
        return None


def match(exp: str, s: str) -> Optional[Context]:
    """
    Compile and match a regex pattern against a string.

    Args:
        exp: Regular expression pattern
        s: String to match against

    Returns:
        Context object with match information if successful, None otherwise
    """
    r = Regex(exp)
    return r.match(s)
