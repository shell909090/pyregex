import string
import logging


def debugging(f):
    def _(self, ecur, scur, depth):
        logging.info(f'{"+"*depth}run: "{self.e[:ecur]}[{self.e[ecur:]}]", "{self.s[:scur]}[{self.s[scur:]}]"')
        r = f(self, ecur, scur, depth)
        if r:
            logging.info(f'{"+"*depth}successed match')
        return r
    return _


SPECIAL_QUOTES = {
    'd': (True, set(string.digits)),
    'D': (False, set(string.digits)),
    's': (True, set(string.whitespace)),
    'S': (False, set(string.whitespace)),
    'w': (True, set('_'+string.ascii_letters+string.digits)),
    'W': (False, set('_'+string.ascii_letters+string.digits)),
}


def special_quote(c):
    if c == 'A':
        return 


def gen_charset(s):
    charset = set()
    include = True
    i = 0
    if s[0] == '^':
        include = False
        i = 1

    while i < len(s):
        if i+2 < len(s) and s[i+1] == '-':
            for c in range(ord(s[i]), ord(s[i+2])+1):
                charset.add(chr(c))
            i += 3

        elif i+1 < len(s) and s[i] == '\\':
            if s[i+1] in SPECIAL_QUOTES:
                sq = SPECIAL_QUOTES[s[i+1]]
                if sq[0] != include:
                    raise Exception(f'invaild charset {s}')
                charset |= sq[1]
            else:
                charset.add(s[i+1])
            i += 2

        elif s[i] == ']':
            i += 1
            break

        else:
            charset.add(s[i])
            i += 1

    return (include, charset), i


def match_chunk(chunk, c):
    # logging.info(f'match: {chunk}, {c}')
    if isinstance(chunk, str):
        return c == chunk
    if chunk is None:
        return True
    if isinstance(chunk, tuple):
        return chunk[0] == (c in chunk[1])
    raise Exception()


def search_chunk(chunk, s):
    for i, c in enumerate(s):
        if not match_chunk(chunk, c):
            return i
    else:
        return len(s)


def determine_range(repeat, longest):
    if repeat == '*':
        return 0, longest
    if repeat == '+':
        return 1, longest
    if repeat == '?':
        return 0, min(longest, 1)
    if repeat.startswith('{'):
        repeat = repeat.strip('{}')
        if ',' not in repeat:
            smallest = longest = int(repeat)
        else:
            repeat = repeat.split(',', 2)
            smallest, longest = int(repeat[0]), int(repeat[1])
        return smallest, longest
    raise Exception()  # just in case


# TODO: group
class Match(object):

    def __init__(self, e, s):
        self.e = e
        self.s = s

    def getchunk(self, ecur):
        if len(self.e) <= ecur:
            raise Exception()

        if self.e[ecur] == '.':
            return None, ecur+1

        # TODO: \A \b \B \Z
        if self.e[ecur] == '\\':
            ecur += 1
            if len(self.e) <= ecur:
                raise Exception()
            chunk = self.e[ecur]
            if chunk in SPECIAL_QUOTES:
                chunk = SPECIAL_QUOTES[chunk]
            return chunk, ecur+1

        if self.e[ecur] == '[':
            chunk, pos = gen_charset(self.e[ecur+1:])
            return chunk, ecur+pos+1

        chunk = self.e[ecur]
        return chunk, ecur+1

    def match(self, ecur, scur):
        while len(self.e) > ecur:
            chunk, enext = self.getchunk(ecur)

            # turn to search
            if len(self.e) > enext and self.e[enext] in '*+?{':
                return True, ecur, scur

            # empty string
            if len(self.s) <= scur:
                return False, ecur, scur

            # not match
            if not match_chunk(chunk, self.s[scur]):
                return False, ecur, scur

            ecur = enext
            scur += 1
        
        # all match
        return True, ecur, scur

    @debugging
    def run(self, ecur, scur, depth):
        r, enext, snext = self.match(ecur, scur)
        logging.info(f'{"+"*depth}match {r} "{self.e[:ecur]}[{self.e[ecur:enext]}]{self.e[enext:]}" "{self.s[:scur]}[{self.s[scur:snext]}]{self.s[snext:]}"')
        ecur, scur = enext, snext
        if not r:
            return False
        if len(self.e) <= ecur:
            return True

        ec_begin = ecur
        chunk, ecur = self.getchunk(ecur)  # do it again
        ec_end = ecur
        if self.e[ecur] == '{':
            pos = self.e.find('}', ecur+1)
            if pos == -1:
                raise Exception()
            repeat = self.e[ecur:pos+1]
            ecur = pos+1
        else:
            repeat = self.e[ecur]
            ecur += 1

        greedy = True
        if len(self.e) > ecur and self.e[ecur] == '?':
            greedy = False
            ecur += 1

        longest = search_chunk(chunk, self.s[scur:])
        smallest, longest = determine_range(repeat, longest)
        logging.info(f'{"+"*depth}search "{self.e[ec_begin:ec_end]}", "{repeat}" in "{self.s[scur:]}", range: {smallest}-{longest}')

        if greedy:
            n, stop, step = longest, smallest-1, -1
        else:
            n, stop, step = smallest, longest+1, 1

        while n != stop:
            if self.run(ecur, scur+n, depth+1):
                return True
            n += step

        return False


def match(e, s):
    # import re
    # m = re.match(e, s)
    # return bool(m)
    m = Match(e, s)
    return m.run(0, 0, 0)
