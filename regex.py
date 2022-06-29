import logging

import matcher


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

    def scan(self, s, cur, start, end):
        while end >= cur:
            r, next = self.m.slip(s, cur)
            if cur >= start:
                yield cur
            if not r:
                return
            cur = next

    def search(self, s, cur):
        if self.repeat == '*':
            r = self.scan(s, cur, cur, len(s))
        elif self.repeat == '+':
            r = self.scan(s, cur, cur+1, len(s))
        elif self.repeat == '?':
            r = self.scan(s, cur, cur, min(len(s), cur+1))
        elif self.repeat.startswith('{'):
            r = self.scan(s, cur, cur+self.smallest, min(len(s), cur+self.longest))
        else:
            raise Exception()  # just in case
        if self.greedy:
            r = reversed(list(r))
        return r


def buffered(f):
    def _(exp):
        buf = ''
        for m in f(exp):
            if isinstance(m, str):
                buf += m
            else:
                yield matcher.Str(buf)
                buf = ''
                yield m
        if buf:
            yield matcher.Str(buf)
    return _


@buffered
def compile(exp):
    cur = 0
    while len(exp) > cur:
        m, cur = matcher.eval(exp, cur)

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
            m = matcher.Str(m)

        yield Search(m, repeat, greedy)


def debugging(f):
    def _(self, ecur, scur, depth):
        logging.info(f'{"+"*depth}run: "{self.e[:ecur]}{self.e[ecur:]}", "{self.s[:scur]}[{self.s[scur:]}]"')
        r = f(self, ecur, scur, depth)
        if r:
            logging.info(f'{"+"*depth}successed match')
        return r
    return _


# TODO: group
# TODO: search all
class Match(object):

    def __init__(self, e, s):
        self.e = e
        self.s = s

    @debugging
    def run(self, ecur, scur, depth):
        sinit = scur
        while len(self.e) > ecur:
            # logging.info(f'loop {self.e[ecur:]}, "{self.s[scur:]}"')
            m = self.e[ecur]
            ecur += 1

            if hasattr(m, 'search'):
                logging.info(f'{"+"*depth}search {m} in "{self.s[scur:]}"')
                for snext in m.search(self.s, scur):
                    r, send = self.run(ecur, snext, depth+1)
                    if r:
                        return True, send
                return False, sinit

            if not hasattr(m, 'slip'):
                raise Exception()  # TODO: runtime exception

            r, snext = m.slip(self.s, scur)
            if not r:
                return False, sinit
            scur = snext

        return True, scur


def match(exp, s):
    # import re
    # m = re.match(exp, s)
    # return bool(m)
    e = list(compile(exp))
    m = Match(e, s)
    return m.run(0, 0, 0)[0]
