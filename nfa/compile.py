"""
Compile regex string to NFA using Thompson's Construction.
"""
import logging
from typing import List, Tuple, Set, Generator
from .edges import Empty, Any, Char, Charset, SPECIAL_QUOTES
from .nodes import Node


def compile(regex: str) -> Node:
    """Compile regex string to NFA using Thompson's Construction."""
    toks = list(tokenizer(regex))
    logging.debug(toks)
    head = Node('end')
    graph = compile_subgraph(head, toks)
    graph.name = 'begin'
    logging.debug(graph.graph2dot())
    return graph


def compile_subgraph(head: Node, toks: List[str]) -> Node:
    """Recursively compile token list into NFA subgraph, returns new head."""
    tail = head
    quantifiers = '1'

    while toks:
        tok = toks.pop(-1)
        match tok[0]:
            case ')':
                idx = scan_brackets(toks)
                if idx == -1:
                    raise Exception('Unmatched parenthesis')
                newhead = compile_subgraph(head, toks[idx+1:])
                toks = toks[:idx]
            case '(':
                raise Exception('Unmatched parenthesis')
            case '.':
                newhead = Node()
                newhead.outs.append((Any(), head))
            case '\\' if len(tok) > 1 and tok[1] in SPECIAL_QUOTES:
                newhead = Node()
                newhead.outs.append((Charset(*SPECIAL_QUOTES[tok[1]]), head))
            case '\\':
                newhead = Node()
                newhead.outs.append((Char(tok[1]), head))
            case '[':
                newhead = Node()
                newhead.outs.append((Charset(*tok_to_set(tok)), head))
            case '|':
                newhead = compile_subgraph(tail, toks)
                newhead.outs.append((Empty(), head))
            case '*' | '+' | '?':
                quantifiers = tok
                continue
            case _ if tok.startswith('{'):
                quantifiers = tok
                continue
            case _:
                newhead = Node()
                newhead.outs.append((Char(tok), head))

        newhead, head = proc_quantifiers(quantifiers, newhead, head)
        quantifiers = '1'

        head = newhead

    return head


def scan_brackets(toks: List[str]) -> int:
    """Find matching '(' for already-popped ')', handling nested brackets."""
    cur = len(toks) - 1
    level = 1
    while cur >= 0:
        match toks[cur]:
            case ')':
                level += 1
            case '(':
                level -= 1
        if level == 0:
            return cur
        cur -= 1
    return -1


def tok_to_set(tok: str) -> Tuple[Set[str], bool]:
    """Parse charset token like '[a-z]' into (char_set, include_flag)."""
    tok = tok[1:-1]
    include = tok[0] != '^'
    if tok[0] == '^':
        tok = tok[1:]
    cset: Set[str] = set()
    cur = 0
    while cur < len(tok):
        if cur < len(tok) - 2 and tok[cur+1] == '-':
            for c in range(ord(tok[cur]), ord(tok[cur+2])+1):
                cset.add(chr(c))
            cur += 3
        else:
            cset.add(tok[cur])
            cur += 1
    return cset, include


def proc_quantifiers(quantifiers: str, newhead: Node, head: Node) -> Tuple[Node, Node]:
    """Apply quantifier (*, +, ?, {n,m}) to nodes by adding epsilon transitions."""
    match quantifiers:
        case '?':
            newhead.outs.append((Empty(), head))
        case '??':
            newhead.outs.insert(0, (Empty(), head))
        case '+':
            head.outs.append((Empty(), newhead))
        case '+?':
            head.outs.insert(0, (Empty(), newhead))
        case '*':
            newhead.outs.append((Empty(), head))
            head.outs.append((Empty(), newhead))
        case '*?':
            newhead.outs.insert(0, (Empty(), head))
            head.outs.insert(0, (Empty(), newhead))
        case _ if quantifiers.startswith('{'):
            newhead, head = repeat_n(quantifiers[1:-1], newhead, head)
    return newhead, head


def repeat_n(quantifiers: str, newhead: Node, head: Node) -> Tuple[Node, Node]:
    """Implement {n,m} quantifier by cloning nodes n-1 times, adding optional paths."""
    m = None
    if ',' in quantifiers:
        n, m = quantifiers.split(',', 1)
        n = int(n)
        m = int(m) if m else -1
    else:
        n = int(quantifiers)
    if n < 0:
        raise Exception('')
    if m is not None and m != -1 and m < n:
        raise Exception('')
    logging.debug(f'{quantifiers}: {n}, {m}')

    for _ in range(n-1):
        nn = newhead.clone({head: newhead})
        head, newhead = newhead, nn

    match m:
        case None:
            pass
        case -1:
            nn = newhead.clone({head: newhead})
            head, newhead = newhead, nn
            newhead.outs.append((Empty(), head))
            head.outs.append((Empty(), newhead))
        case _ if m == n:
            pass
        case _:
            nn = newhead.clone({head: newhead})
            head, newhead = newhead, nn
            newhead.outs.append((Empty(), head))
            if m-n > 1:
                for _ in range(m-n-1):
                    nn = newhead.clone({head: newhead})
                    head, newhead = newhead, nn

    return newhead, head


def tokenizer(regex: str) -> Generator[str, None, None]:
    """Split regex into tokens, handling quantifiers, brackets, escapes."""
    cur = 0
    while cur < len(regex):
        if regex[cur] in '*+?':
            if cur + 1 < len(regex) and regex[cur+1] == '?':
                yield regex[cur:cur+2]
                cur += 2
            else:
                yield regex[cur]
                cur += 1
        elif regex[cur] == '[':
            idx = regex[cur:].find(']')
            if idx == -1:
                raise Exception('Unmatched bracket')
            idx += 1
            yield regex[cur:cur+idx]
            cur += idx
        elif regex[cur] == '{':
            idx = regex[cur:].find('}')
            if idx == -1:
                raise Exception('Unmatched brace')
            idx += 1
            yield regex[cur:cur+idx]
            cur += idx
        elif regex[cur] == '\\':
            if cur + 1 < len(regex):
                yield regex[cur:cur+2]
                cur += 2
            else:
                raise Exception('Incomplete escape sequence')
        else:
            yield regex[cur]
            cur += 1
