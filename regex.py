import logging

import matcher
import searcher


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

        yield searcher.Search(m, repeat, greedy)


def debugging(f):
    def _(self, ecur, scur, depth):
        logging.info(f'{"+"*depth}run: "{self.e[:ecur]}{self.e[ecur:]}", "{self.s[:scur]}[{self.s[scur:]}]"')
        r = f(self, ecur, scur, depth)
        if r:
            logging.info(f'{"+"*depth}successed match')
        return r
    return _


# TODO: group
class Match(object):

    def __init__(self, e, s):
        self.e = e
        self.s = s

    @debugging
    def run(self, ecur, scur, depth):
        while len(self.e) > ecur:
            # logging.info(f'loop {self.e[ecur:]}, "{self.s[scur:]}"')
            m = self.e[ecur]
            ecur += 1

            if hasattr(m, 'search'):
                for snext in m.search(self.s, scur, depth):
                    if self.run(ecur, snext, depth+1):
                        return True
                return False

            if not hasattr(m, 'slip'):
                raise Exception()  # TODO: runtime exception

            r, snext = m.slip(self.s, scur)
            if not r:
                return False
            scur = snext

        return True


def match(exp, s):
    # import re
    # m = re.match(e, s)
    # return bool(m)
    e = list(compile(exp))
    m = Match(e, s)
    return m.run(0, 0, 0)
