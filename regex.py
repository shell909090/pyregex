import logging

from matcher import Context, Str, any, Charset, SPECIAL_QUOTES, GroupMatch, Group


class Search(object):

    def __init__(self, m, repeat, greedy):
        self.m = m
        self.repeat = repeat
        self.greedy = greedy
        self.smallest = self.longest = 0
        if repeat.startswith('{'):
            repeat = repeat.strip('{}')
            if ',' not in self.repeat:
                self.smallest = self.longest = int(repeat)
            else:
                repeat = repeat.split(',', 2)
                self.smallest, self.longest = int(repeat[0]), int(repeat[1])

    def __repr__(self):
        return f'search({self.m}, {self.repeat}, {self.greedy})'

    def __eq__(self, o):
        return self.m == o.m and self.repeat == o.repeat and self.greedy == o.greedy

    def scan(self, ctx, cur, start, end):
        ''' all the pos that the NEXT matcher could possible be '''
        while end >= cur:
            r, next = self.m(ctx, cur)
            if cur >= start:
                yield cur
            if not r:
                return
            cur = next

    def search(self, ctx, cur):
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


def buffered(f):
    def _(self, exp):
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


def debugging(f):
    def _(self, ctx, ecur, scur, depth):
        logging.info(f'{"+"*depth}run: "{self.e[:ecur]}{self.e[ecur:]}", "{ctx.s[:scur]}[{ctx.s[scur:]}]"')
        r = f(self, ctx, ecur, scur, depth)
        if r:
            logging.info(f'{"+"*depth}successed match')
        return r
    return _


class Regex(object):

    def __init__(self, exp=None):
        self.e = []
        self.groups = []
        if exp is not None:
            self.compile(exp)

    def compile(self, exp):
        self.stack = []
        self.e = list(self._compile(exp))
        del self.stack

    @buffered
    def _compile(self, exp):
        cur = 0
        while len(exp) > cur:
            m, cur = self.eval(exp, cur)

            if len(exp) <= cur:
                yield m
                return

            if exp[cur] not in '*+?{':
                yield m
                continue

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

    def eval(self, exp, cur):
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
            m = Group(name, len(self.stack)+1)
            self.groups.append(m)
            self.stack.append(m)
            return m.left, cur

        if exp[cur] == ')':
            m = self.stack.pop(-1)
            return m.right, cur+1

        c = exp[cur]
        return c, cur+1

    @debugging
    def _match(self, ctx, ecur, scur, depth):
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

    def match(self, s):
        ctx = Context(s)
        ctx.groups.append(GroupMatch(0, '', 0))
        r = self._match(ctx, 0, 0, 0)
        if r[0]:
            ctx.groups[0].end = r[1]
            return ctx


def match(exp, s):
    # import re
    # m = re.match(exp, s)
    # return bool(m)
    r = Regex(exp)
    return r.match(s)
