import string
import logging


class Str(str):

    def slip(self, s, cur):
        if len(s)-cur < len(self):
            return False, cur
        if not s[cur:].startswith(self):
            return False, cur
        return True, cur+len(self)


class Any(object):

    def __repr__(self):
        return '.'

    def slip(self, s, cur):
        if len(s) <= cur:
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

    def slip(self, s, cur):
        if len(s) <= cur:
            return False, cur
        if self.include != (s[cur] in self.charset):
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


def eval(exp, cur):
    if len(exp) <= cur:
        raise Exception()

    if exp[cur] == '.':
        return any, cur+1

    # TODO: \A \b \B \Z
    if exp[cur] == '\\':
        cur += 1
        if len(exp) <= cur:
            raise Exception()  # FIXME: compile exception
        c = exp[cur]
        cur += 1
        if c in SPECIAL_QUOTES:
            return SPECIAL_QUOTES[c], cur
        return c, cur

    if exp[cur] == '[':
        return Charset.eval(exp, cur+1)

    c = exp[cur]
    return c, cur+1
