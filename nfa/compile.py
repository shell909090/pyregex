"""
Compile regex string to NFA using Thompson's Construction.
"""
import logging
from typing import List, Tuple, Set, Generator
from .edges import Empty, Any, Char, Charset, SPECIAL_QUOTES
from .nodes import Node


def compile(regex: str) -> Node:
    """
    Compile regex string to NFA.

    Args:
        regex: Regular expression string

    Returns:
        Start node of the compiled NFA
    """
    toks = list(tokenizer(regex))
    logging.debug(toks)
    head = Node('end')
    graph = compile_subgraph(head, toks)
    graph.name = 'begin'
    logging.debug(graph.graph2dot())
    return graph


def compile_subgraph(head: Node, toks: List[str]) -> Node:
    """
    Compile a subgraph from token list.

    Args:
        head: Head node to connect to
        toks: List of tokens

    Returns:
        New head node of the compiled subgraph
    """
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
    """
    Scan for matching opening parenthesis for an already-popped closing parenthesis.

    This function assumes a ')' has already been popped from the end of the token list.
    It scans backwards through the remaining tokens to find the matching '(' for that
    popped ')'. It correctly handles nested parentheses by tracking the nesting level.

    Args:
        toks: List of tokens after the closing ')' has been popped.
              The function finds the '(' that matches that popped ')'.

    Returns:
        Index of the matching '(' token, or -1 if not found

    Example:
        >>> # Pattern: (a) - after popping ')', toks = ['(', 'a']
        >>> scan_brackets(['(', 'a'])
        0
        >>> # Pattern: ((a)) - after popping outer ')', toks = ['(', '(', 'a', ')']
        >>> scan_brackets(['(', '(', 'a', ')'])
        0
        >>> # Pattern: (a)(b) - after popping ')', toks = ['(', 'a', ')', '(', 'b']
        >>> scan_brackets(['(', 'a', ')', '(', 'b'])
        3
    """
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
    """
    Parse character set token to set and include flag.

    Args:
        tok: Token string like '[a-z]' or '[^0-9]'

    Returns:
        Tuple of (character set, include flag)
    """
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
    """
    Process quantifiers and modify NFA nodes accordingly.

    Args:
        quantifiers: Quantifier string (?, +, *, ??, +?, *?, {n,m})
        newhead: The newly created node
        head: The head node to connect to

    Returns:
        Tuple of (new head node, head node) after applying quantifier logic
    """
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
    """
    Implement limited quantifiers {n,m} by cloning nodes.

    This function supports three formats:
    - {n}: Exactly n repetitions
    - {n,}: At least n repetitions (n or more)
    - {n,m}: Between n and m repetitions (inclusive)

    The implementation uses node cloning to create the required repetition structure:
    1. First creates (n-1) mandatory clones for the minimum repetitions
    2. For {n,m}: Creates (m-n) optional clones with epsilon transitions
    3. For {n,}: Creates one more clone with loop-back for unlimited repetitions

    Args:
        quantifiers: The content inside {} (e.g., "3", "2,5", "3,")
        newhead: The node to repeat
        head: The target node after repetitions

    Returns:
        Tuple of (new head node, head node) after creating repetition structure

    Raises:
        Exception: If n <= 1 or if m is specified and m <= n
    """
    m = None
    if ',' in quantifiers:
        n, m = quantifiers.split(',', 1)
        n = int(n)
        m = int(m) if m else -1
    else:
        n = int(quantifiers)
    if n <= 1:
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
    """
    Tokenize regex string into tokens.

    Args:
        regex: Regular expression string

    Yields:
        Token strings
    """
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
