"""Parser e scrittore minimo di s-expression KiCad."""
import re

_tok = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))')


class Q(str):
    """Stringa da scrivere tra virgolette."""


def parse(text):
    stack, cur, pos = [], [], 0
    n = len(text)
    while pos < n:
        m = _tok.match(text, pos)
        if not m:
            break
        pos = m.end()
        if m.group(1):
            stack.append(cur)
            cur = []
        elif m.group(2):
            done = cur
            cur = stack.pop()
            cur.append(done)
        elif m.group(3) is not None:
            cur.append(Q(m.group(3).replace('\\"', '"').replace('\\\\', '\\')))
        elif m.group(4) is not None:
            cur.append(m.group(4))
    return cur[0]


def dump(e, ind=0):
    if isinstance(e, list):
        if not e:
            return "()"
        simple = all(not isinstance(x, list) for x in e)
        if simple and len(e) <= 6:
            return "(" + " ".join(dump(x) for x in e) + ")"
        pad = "\t" * (ind + 1)
        head = dump(e[0])
        rest = "".join("\n" + pad + dump(x, ind + 1) for x in e[1:])
        return "(" + head + rest + "\n" + "\t" * ind + ")"
    if isinstance(e, Q):
        return '"' + e.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(e, float):
        s = ("%.4f" % e).rstrip("0").rstrip(".")
        return "0" if s in ("-0", "") else s
    return str(e)


def find(e, key):
    return [x for x in e if isinstance(x, list) and x and x[0] == key]


def first(e, key):
    r = find(e, key)
    return r[0] if r else None
