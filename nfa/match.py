"""
Match strings using NFA.
"""
from .edges import Empty


class State(object):

    def __init__(self, s, cur, n) -> None:
        self.s = s
        self.cur = cur
        self.n = n

    def __repr__(self) -> str:
        return f'{self.cur} {id(self.n)}'


def match(r: str, s: str):
    sts = [State(s, 0, r), ]
    history = set()
    while sts:
        print(sts)
        st = sts.pop(0)
        if not st.n.outs and st.cur == len(st.s):
            return True
        for e in st.n.outs:
            if isinstance(e, Empty):
                history.add((st.cur, id(st.n)))
            newst = e.match(st)
            if not newst:
                continue
            if (newst.cur, id(newst.n)) in history:
                continue
            sts.append(newst)
    return False
