import string
import logging


class Context(object):

    def __init__(self, s):
        self.s = s
        self.len = len(self.s)
        self.matches = []
        self.groups = []

    def __repr__(self):
        return f'<regex context>'


class Str(str):

    def __call__(self, ctx, cur):
        if ctx.len-cur < len(self):
            return False, cur
        if ctx.s[cur:cur+len(self)] != self:
            return False, cur
        return True, cur+len(self)


class Any(object):

    def __repr__(self):
        return '.'

    def __call__(self, ctx, cur):
        if ctx.len <= cur:
            return False, cur
        return True, cur+1

any = Any()


class Charset(object):

    def __init__(self, charset=None, include=True):
        if charset is None:
            charset = set()
        self.charset = charset
        self.include = include

    def __repr__(self):
        return f'charset({self.include}, "{"".join(sorted(self.charset))}")'

    def __eq__(self, o):
        return self.charset == o.charset and self.include == o.include

    @classmethod
    def eval(cls, exp, cur):
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
                        raise Exception(f'invaild charset {s}')
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

    def __call__(self, ctx, cur):
        if ctx.len <= cur:
            return False, cur
        if self.include != (ctx.s[cur] in self.charset):
            return False, cur
        return True, cur+1


SPECIAL_QUOTES = {
    'd': Charset(charset=set(string.digits), include=True),
    'D': Charset(charset=set(string.digits), include=False),
    's': Charset(charset=set(string.whitespace), include=True),
    'S': Charset(charset=set(string.whitespace), include=False),
    'w': Charset(charset=set('_'+string.ascii_letters+string.digits), include=True),
    'W': Charset(charset=set('_'+string.ascii_letters+string.digits), include=False),
}


class GroupMatch(object):

    def __init__(self, n, name, start):
        self.n = n
        self.name = name
        self.start = start
        self.end = None

    def __repr__(self):
        return f'<group "{self.name}" {self.n}>: {self.start}-{self.end or ""}'


class Group(object):

    def __init__(self, name, n):
        self.name = name
        self.n = n

    def __repr__(self):
        return f'<group "{self.name}" {self.n+1}>'

    def left(self, ctx, cur):
        if len(ctx.groups) <= self.n:
            ctx.groups.append(GroupMatch(self.n, self.name, cur))
        else:
            ctx.groups[self.n].start = cur
        return True, cur

    def right(self, ctx, cur):
        ctx.groups[self.n].end = cur
        return True, cur
