"""
Compile regex string to NFA using Thompson's Construction.
"""
from .edges import Empty, Any, Char, Charset, SPECIAL_QUOTES
from .nodes import Node, to_list


def compile(regex: str):
    toks = list(tokenizer(regex))
    # print(toks)
    head = Node()
    graph = compile_subgraph(head, toks)
    return graph


def compile_subgraph(head: Node, toks: List[str]):
    tail = head
    quantifiers = '1'

    while toks:
        tok = toks.pop(-1)
        if tok == ')':
            idx = toks.index('(')
            if idx == -1:
                raise Exception('')
            newhead = compile_subgraph(head, toks[idx+1:])
            toks = toks[:idx]
        elif tok == '.':
            newhead = Node()
            newhead.outs.append(Any(head))
        elif tok[0] == '\\':
            if tok[1] in SPECIAL_QUOTES:
                newhead = Node()
                newhead.outs.append(Charset(head, *SPECIAL_QUOTES[tok[1]]))
            else:
                newhead = Node()
                newhead.outs.append(Char(head, tok[1]))
        elif tok[0] == '[':
            newhead = Node()
            newhead.outs.append(Charset(head, *tok_to_set(tok)))
        elif tok == '|':
            newhead = compile_subgraph(tail, toks)
            newhead.outs.append(Empty(head))
        elif tok[0] in '*+?':
            quantifiers = tok
            continue
        else:
            newhead = Node()
            newhead.outs.append(Char(head, tok))

        match quantifiers:
            case '?':
                newhead.outs.append(Empty(head))
            case '??':
                newhead.outs.insert(0, Empty(head))
            case '+':
                head.outs.append(Empty(newhead))
            case '+?':
                head.outs.insert(0, Empty(newhead))
            case '*':
                newhead.outs.append(Empty(head))
                head.outs.append(Empty(newhead))
            case '*?':
                newhead.outs.insert(0, Empty(head))
                head.outs.insert(0, Empty(newhead))
        quantifiers = '1'

        head = newhead

    return head


def tok_to_set(tok: str) -> Tuple[str, bool]:
    tok = tok[1:-1]
    include = tok[0] != '^'
    if tok[0] == '^':
        tok = tok[1:]
    cset = set()
    while tok:
        s, tok = tok[0], tok[1:]
        if tok and tok[0] == '-':
            for c in range(ord(s), ord(tok[1])+1):
                cset.add(chr(c))
            tok = tok[2:]
        else:
            cset.add(s)
    return cset, include
    


def tokenizer(regex: str) -> List[str]:
    cur = 0
    while cur < len(regex):
        if regex[cur] in '.':
            yield regex[cur]
            cur += 1
        elif regex[cur] in '*+?':
            if regex[cur+1] == '?':
                yield regex[cur:cur+1]
                cur += 2
            else:
                yield regex[cur]
                cur += 1
        elif regex[cur] == '[':
            idx = regex[cur:].find(']')
            if idx == -1:
                raise Exception('')
            idx += 1
            yield regex[cur:cur+idx]
            cur += idx
        elif regex[cur] == '{':
            idx = regex[cur:].find('}')
            if idx == -1:
                raise Exception('')
            idx += 1
            yield regex[cur:cur+idx]
            cur += idx
        elif regex[cur] in '^$':
            yield regex[cur]
            cur += 1
        elif regex[cur] == '\\':
            yield regex[cur:cur+2]
            cur += 2
        else:
            yield regex[cur]
            cur += 1
