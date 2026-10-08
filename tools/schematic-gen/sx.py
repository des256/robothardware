"""Minimal KiCad s-expression reader/writer.

Quoted strings parse to QStr so the writer can re-quote them; bare tokens stay str.
"""
import re
import copy as _copy


class QStr(str):
    """A string that must be written with double quotes."""
    pass


_tok = re.compile(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()"]+')


def _unescape(s):
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == '\\' and i + 1 < len(s):
            n = s[i + 1]
            if n == 'n':
                out.append('\n')
            elif n == 't':
                out.append('\t')
            else:
                out.append(n)
            i += 2
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def parse(text):
    stack = [[]]
    for m in _tok.finditer(text):
        t = m.group(0)
        if t == '(':
            stack.append([])
        elif t == ')':
            lst = stack.pop()
            stack[-1].append(lst)
        else:
            if t.startswith('"'):
                stack[-1].append(QStr(_unescape(t[1:-1])))
            else:
                stack[-1].append(t)
    if len(stack) != 1:
        raise ValueError("unbalanced s-expression")
    return stack[0][0]


def parse_all(text):
    """Parse a file that may contain several top-level forms."""
    stack = [[]]
    for m in _tok.finditer(text):
        t = m.group(0)
        if t == '(':
            stack.append([])
        elif t == ')':
            lst = stack.pop()
            stack[-1].append(lst)
        else:
            if t.startswith('"'):
                stack[-1].append(QStr(_unescape(t[1:-1])))
            else:
                stack[-1].append(t)
    return stack[0]


def find(lst, key):
    return [x for x in lst if isinstance(x, list) and x and x[0] == key]


def first(lst, key, default=None):
    f = find(lst, key)
    return f[0] if f else default


def prop(sym, name):
    for p in find(sym, 'property'):
        if p[1] == name:
            return p[2]
    return None


def set_prop(sym, name, value, template=None, hide=None):
    """Set property value; create from template (another property list) if missing."""
    for p in find(sym, 'property'):
        if p[1] == name:
            p[2] = QStr(value)
            if hide is not None:
                _set_hide(p, hide)
            return p
    if template is None:
        template = find(sym, 'property')[-1]
    p = _copy.deepcopy(template)
    p[1] = QStr(name)
    p[2] = QStr(value)
    if hide is not None:
        _set_hide(p, hide)
    # insert after the last property
    idx = max(i for i, x in enumerate(sym) if isinstance(x, list) and x and x[0] == 'property')
    sym.insert(idx + 1, p)
    return p


def _set_hide(p, hide):
    # KiCad 9 style: (hide yes) as a direct child of property; older: (effects ... hide)
    for h in find(p, 'hide'):
        p.remove(h)
    eff = first(p, 'effects')
    if eff is not None and 'hide' in eff:
        eff.remove('hide')
    if hide:
        # place after (at ...) to mirror KiCad output
        pos = 2
        for i, x in enumerate(p):
            if isinstance(x, list) and x and x[0] == 'at':
                pos = i + 1
        p.insert(pos, ['hide', 'yes'])


def num(v):
    if isinstance(v, (int,)) and not isinstance(v, bool):
        return str(v)
    s = ('%.4f' % float(v)).rstrip('0').rstrip('.')
    if s in ('-0', ''):
        s = '0'
    return s


def _esc(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def fmt(x):
    if isinstance(x, QStr):
        return _esc(x)
    if isinstance(x, bool):
        return 'yes' if x else 'no'
    if isinstance(x, float):
        return num(x)
    if isinstance(x, int):
        return str(x)
    return str(x)


def dump(node, indent=0):
    if not isinstance(node, list):
        return fmt(node)
    if all(not isinstance(c, list) for c in node):
        return '(' + ' '.join(fmt(c) for c in node) + ')'
    i = 0
    atoms = []
    while i < len(node) and not isinstance(node[i], list):
        atoms.append(fmt(node[i]))
        i += 1
    out = '(' + ' '.join(atoms)
    for c in node[i:]:
        out += '\n' + '\t' * (indent + 1) + dump(c, indent + 1)
    out += '\n' + '\t' * indent + ')'
    return out


def Q(s):
    return QStr(s)
