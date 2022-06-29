import logging


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

    def get_end(self, s, scur):
        while len(s) > scur:
            r, snext = self.m.slip(s, scur)
            if not r:
                return scur
            scur = snext
        return len(s)

    def range(self, s, scur):
        send = self.get_end(s, scur)
        if self.repeat == '*':
            return scur, send
        if self.repeat == '+':
            return scur+1, send
        if self.repeat == '?':
            return scur, min(send, scur+1)
        if self.repeat.startswith('{'):
            return scur+self.smallest, min(send, scur+self.longest)
        raise Exception()  # just in case

    def search(self, s, scur, depth):
        start, end = self.range(s, scur)
        logging.info(f'{"+"*depth}search {self} in "{s}", range: {start}-{end}')
        if self.greedy:
            return range(end, start-1, -1)
        else:
            return range(start, end+1)
