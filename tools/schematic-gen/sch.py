"""Programmatic KiCad schematic writer (KiCad 9 file format, readable by KiCad 10).

Design: every symbol is placed at explicit coordinates; each used pin gets a short wire stub
ending in a local label, a power symbol, a hierarchical label connection, or a direct wire to
another pin.  Unused pins get no-connect markers automatically at write time.
"""
import math
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sx import parse, dump, find, first, prop, QStr as Q  # noqa: E402

NS = uuid.UUID('5f2f2c2e-9d0e-4b7e-9f0e-ba9b0e3e0000')
LIBNAME = '0_backbone'
PROJECT = 'backbone'
GRID = 1.27


def uid(*parts):
    return str(uuid.uuid5(NS, '|'.join(str(p) for p in parts)))


def g(v):
    """snap to the 50 mil grid"""
    return round(round(v / GRID) * GRID, 2)


class Lib:
    def __init__(self, path):
        self.tree = parse(open(path, encoding='utf-8').read())
        self.syms = {s[1]: s for s in find(self.tree, 'symbol')}

    def pins(self, name):
        s = self.syms[name]
        out = []
        for u in find(s, 'symbol'):
            for p in find(u, 'pin'):
                a = first(p, 'at')
                out.append({
                    'number': first(p, 'number')[1], 'name': first(p, 'name')[1], 'type': p[1],
                    'x': float(a[1]), 'y': float(a[2]), 'rot': float(a[3]) if len(a) > 3 else 0.0,
                    'len': float(first(p, 'length')[1]),
                })
        return out

    def embedded(self, name):
        """Deep copy of the library symbol renamed for embedding in lib_symbols."""
        import copy
        s = copy.deepcopy(self.syms[name])
        s[1] = Q(LIBNAME + ':' + name)
        return s

    def is_power(self, name):
        return bool(find(self.syms[name], 'power'))


class Pin:
    def __init__(self, inst, p):
        self.inst = inst
        self.p = p
        self.number = p['number']
        self.name = p['name']
        self.type = p['type']
        # symbol coords (y up) -> rotate CCW -> schematic (y down)
        r = math.radians(inst.rot)
        x, y = p['x'], p['y']
        xr = x * math.cos(r) - y * math.sin(r)
        yr = x * math.sin(r) + y * math.cos(r)
        if inst.mirror == 'y':
            xr = -xr
        if inst.mirror == 'x':
            yr = -yr
        self.x = round(inst.x + xr, 2)
        self.y = round(inst.y - yr, 2)
        # outward direction (away from body): pin rot points toward body
        orot = math.radians(p['rot'] + 180 + inst.rot)
        ox, oy = math.cos(orot), math.sin(orot)
        if inst.mirror == 'y':
            ox = -ox
        if inst.mirror == 'x':
            oy = -oy
        self.dx = int(round(ox))
        self.dy = -int(round(oy))
        self.used = False

    @property
    def pos(self):
        return (self.x, self.y)


class Inst:
    def __init__(self, sheet, symname, refbase, x, y, rot=0, mirror=None, value=None, lcsc=None,
                 fp=None, dnp=False, nobom=False, fields=None, hide_value=False):
        self.sheet = sheet
        self.symname = symname
        self.refbase = refbase          # ('R', 5) -> R305 on page 3
        self.x, self.y, self.rot, self.mirror = g(x), g(y), rot, mirror
        self.value = value
        self.lcsc = lcsc
        self.fp = fp
        self.dnp = dnp
        self.nobom = nobom
        self.fields = fields or {}
        self.hide_value = hide_value
        self.pins = [Pin(self, p) for p in sheet.lib.pins(symname)]
        self.uuid = uid(sheet.name, 'sym', refbase[0], refbase[1], symname, x, y)

    def pin(self, key):
        key = str(key)
        for p in self.pins:
            if p.number == key:
                return p
        for p in self.pins:
            if p.name == key:
                return p
        raise KeyError(f'{self.symname}: no pin {key!r}; have {[(p.number, p.name) for p in self.pins]}')

    def pins_named(self, name):
        return [p for p in self.pins if p.name == name]

    def pins_matching(self, rx):
        import re
        return [p for p in self.pins if re.search(rx, p.name)]

    def ref(self, page):
        if self.refbase[0] in ('#PWR', '#FLG'):
            return '%s%04d' % (self.refbase[0], page * 100 + self.refbase[1])
        return '%s%d' % (self.refbase[0], page * 100 + self.refbase[1])


class Sheet:
    def __init__(self, lib, name, file_uuid, paper, title, comment, root_uuid, instances):
        """instances: list of (sheet_symbol_uuid, page) -- one per instantiation of this file."""
        self.lib = lib
        self.name = name
        self.file_uuid = file_uuid
        self.paper = paper
        self.title = title
        self.comment = comment
        self.root_uuid = root_uuid
        self.instances = instances
        self.insts = []
        self.wires = []
        self.labels = []
        self.hlabels = []
        self.flags = []
        self.ncs = []
        self.junctions = []
        self.texts = []
        self.raw = []
        self.counters = {}
        self.power_refs = {}
        self.used_syms = set()

    # ------------------------------------------------------------ placement
    def next_ref(self, prefix):
        n = self.counters.get(prefix, 0) + 1
        self.counters[prefix] = n
        return (prefix, n)

    def place(self, symname, prefix, x, y, rot=0, mirror=None, value=None, lcsc=None, fp=None,
              dnp=False, nobom=False, fields=None, refnum=None, hide_value=False):
        refbase = (prefix, refnum) if refnum else self.next_ref(prefix)
        if refnum:
            self.counters[prefix] = max(self.counters.get(prefix, 0), refnum)
        inst = Inst(self, symname, refbase, x, y, rot, mirror, value, lcsc, fp, dnp, nobom, fields, hide_value)
        self.insts.append(inst)
        self.used_syms.add(symname)
        return inst

    # ------------------------------------------------------------ passives helpers
    def R(self, x, y, value, lcsc, rot=0, **kw):
        return self.place('R_0603', 'R', x, y, rot, value=value, lcsc=lcsc, **kw)

    def C(self, x, y, value, lcsc, size='0603', rot=0, **kw):
        return self.place('C_' + size, 'C', x, y, rot, value=value, lcsc=lcsc, **kw)

    # ------------------------------------------------------------ connectivity
    def wire(self, a, b):
        a = (g(a[0]), g(a[1]))
        b = (g(b[0]), g(b[1]))
        if a == b:
            return
        self.wires.append((a, b))

    def stub(self, pin, length=2.54):
        pin.used = True
        e = (pin.x + pin.dx * length, pin.y + pin.dy * length)
        self.wire(pin.pos, e)
        return e

    def label(self, pin, name, length=2.54):
        e = self.stub(pin, length)
        self._label_at(name, e, pin.dx, pin.dy)
        return e

    def _label_at(self, name, e, dx, dy):
        if dx > 0:
            rot, just = 0, 'left bottom'
        elif dx < 0:
            rot, just = 180, 'right bottom'
        elif dy < 0:
            rot, just = 90, 'left bottom'
        else:
            rot, just = 270, 'right bottom'
        self.labels.append((name, g(e[0]), g(e[1]), rot, just))

    def label_xy(self, name, x, y, rot=0):
        just = {0: 'left bottom', 180: 'right bottom', 90: 'left bottom', 270: 'right bottom'}[rot]
        self.labels.append((name, g(x), g(y), rot, just))

    def power(self, pin, net, length=None, symbol=None):
        """Attach a global power symbol: vertical pins get the symbol in line, horizontal pins get it
        rotated so the graphic points away from the body (no perpendicular legs -> no collisions)."""
        is_gnd = net == 'GND'
        if pin.dx != 0:
            e = self.stub(pin, length or 5.08)
            if pin.dx > 0:
                rot = 90 if is_gnd else 270
            else:
                rot = 270 if is_gnd else 90
        else:
            e = self.stub(pin, length or 2.54)
            rot = 180 if ((is_gnd and pin.dy < 0) or (not is_gnd and pin.dy > 0)) else 0
        self.power_at(net, e, symbol, rot)
        return e

    def chain_pwr(self, pins, net):
        """Join pins with a bus line and hang a power symbol off its end."""
        pins = sorted(pins, key=lambda p: p.y)
        pts = self.chain(*pins)
        e = pts[0] if net != 'GND' else pts[-1]
        dx = pins[0].dx
        e2 = (e[0] + dx * 2.54, e[1])
        self.wire(e, e2)
        e3 = (e2[0], e2[1] + (2.54 if net == 'GND' else -2.54))
        self.wire(e2, e3)
        self.power_at(net, e3)
        return pts

    def flag_rail(self, x, y, net):
        """power symbol + PWR_FLAG pair marking the sheet that produces a rail"""
        x, y = g(x), g(y)
        self.power_at(net, (x, y))
        self.wire((x, y), (x + 5.08, y))
        self.flag((x + 5.08, y))

    def power_at(self, net, e, symbol=None, rot=None):
        if symbol is None:
            symbol = 'GND' if net == 'GND' else {'+12V_SERVO': '+12V', '+5V_SERVO': '+5V', '+5V_USB': '+5V',
                                                   '+3V3': '+3V3', '+1V1_HUB': '+1V1', 'VBUS': 'VBUS',
                                                   '+19V_IN': '+VDC', '+19V_JETSON': '+VDC'}.get(net, '+VDC')
        if rot is None:
            rot = 0
        inst = self.place(symbol, '#PWR', e[0], e[1], rot, value=net)
        inst.pins[0].used = True
        return inst

    def flag(self, e, rot=0):
        """PWR_FLAG at a point"""
        inst = self.place('PWR_FLAG', '#FLG', e[0], e[1], rot, value='PWR_FLAG')
        inst.pins[0].used = True
        return inst

    def nc(self, *pins):
        for pin in pins:
            pin.used = True
            self.ncs.append((pin.x, pin.y))

    def nc_all_unused(self, inst):
        for p in inst.pins:
            if not p.used and p.type != 'no_connect':
                self.nc(p)

    def connect(self, a, b):
        """Wire two pins with an L-shaped route: stubs outward then meet."""
        ea = self.stub(a, 2.54)
        eb = self.stub(b, 2.54)
        if ea[0] == eb[0] or ea[1] == eb[1]:
            self.wire(ea, eb)
        else:
            mid = (eb[0], ea[1]) if a.dx != 0 else (ea[0], eb[1])
            self.wire(ea, mid)
            self.wire(mid, eb)
            self.junctions.append(mid) if False else None

    def chain(self, *pins, net=None):
        """Join several pins to one horizontal/vertical bus line through a shared point."""
        pins = sorted(pins, key=lambda p: (p.y, p.x))
        pts = [self.stub(p, 2.54) for p in pins]
        for i in range(1, len(pts)):
            self.wire(pts[i - 1], pts[i])
        for p in pts[1:-1]:
            self.junctions.append(p)
        if net:
            self._label_at(net, pts[0], -1 if pins[0].dx < 0 else 1, 0)
        return pts

    def hier(self, name, shape, x, y, netclass=None, length=25.4):
        """Hierarchical label with a wire stub and optional netclass directive (skeleton style)."""
        self.hlabels.append((name, shape, g(x), g(y)))
        e = (g(x + length), g(y))
        self.wire((g(x), g(y)), e)
        if netclass:
            self.flags.append((netclass, e[0], e[1]))
        else:
            self.label_xy(name, e[0], e[1], 0)
        return e

    def text(self, x, y, s, size=1.27, bold=False):
        self.texts.append((s, g(x), g(y), size, bold))

    def junction(self, x, y):
        self.junctions.append((g(x), g(y)))

    # ------------------------------------------------------------ writing
    def _effects(self, size=1.27, justify=None, hide=False):
        e = ['effects', ['font', ['size', size, size]]]
        if justify:
            e.append(['justify'] + justify.split())
        if hide:
            e.append(['hide', 'yes'])
        return e

    def _symbol_node(self, inst):
        node = ['symbol', ['lib_id', Q(LIBNAME + ':' + inst.symname)],
                ['at', inst.x, inst.y, inst.rot]]
        if inst.mirror:
            node.append(['mirror', inst.mirror])
        node += [['unit', 1], ['exclude_from_sim', 'yes' if inst.nobom else 'no'],
                 ['in_bom', 'no' if inst.nobom else 'yes'], ['on_board', 'yes'],
                 ['dnp', 'yes' if inst.dnp else 'no'], ['fields_autoplaced', 'yes'],
                 ['uuid', Q(inst.uuid)]]
        ref0 = inst.ref(self.instances[0][1])
        is_pwr = inst.symname in ('GND', 'PWR_FLAG') or inst.refbase[0] == '#PWR' or inst.refbase[0] == '#FLG'
        rx, ry = inst.x + 2.54, inst.y - 2.54
        node.append(['property', Q('Reference'), Q(ref0), ['at', rx, ry, 0],
                     self._effects(justify='left', hide=is_pwr)])
        node.append(['property', Q('Value'), Q(inst.value if inst.value is not None else prop(self.lib.syms[inst.symname], 'Value') or ''),
                     ['at', rx, ry + 2.54 if not is_pwr else ry + 5.08, 0],
                     self._effects(justify='left', hide=inst.hide_value)])
        fp = inst.fp if inst.fp is not None else (prop(self.lib.syms[inst.symname], 'Footprint') or '')
        node.append(['property', Q('Footprint'), Q(fp), ['at', inst.x, inst.y, 0], self._effects(hide=True)])
        node.append(['property', Q('Datasheet'), Q(prop(self.lib.syms[inst.symname], 'Datasheet') or ''),
                     ['at', inst.x, inst.y, 0], self._effects(hide=True)])
        node.append(['property', Q('Description'), Q(prop(self.lib.syms[inst.symname], 'Description') or ''),
                     ['at', inst.x, inst.y, 0], self._effects(hide=True)])
        if not is_pwr:
            lcsc = inst.lcsc if inst.lcsc is not None else (prop(self.lib.syms[inst.symname], 'LCSC') or '')
            node.append(['property', Q('LCSC'), Q(lcsc), ['at', inst.x, inst.y, 0], self._effects(hide=True)])
            for k, v in inst.fields.items():
                node.append(['property', Q(k), Q(str(v)), ['at', inst.x, inst.y, 0], self._effects(hide=True)])
        for p in inst.pins:
            node.append(['pin', Q(p.number), ['uuid', Q(uid(inst.uuid, 'pin', p.number, p.name))]])
        proj = ['project', Q(PROJECT)]
        for sheet_uuid, page in self.instances:
            path = '/' + self.root_uuid + ('/' + sheet_uuid if sheet_uuid else '')
            proj.append(['path', Q(path), ['reference', Q(inst.ref(page))], ['unit', 1]])
        node.append(['instances', proj])
        return node

    def tree(self):
        root = ['kicad_sch', ['version', 20250114], ['generator', Q('eeschema')], ['generator_version', Q('9.0')],
                ['uuid', Q(self.file_uuid)], ['paper', Q(self.paper)],
                ['title_block', ['title', Q(self.title)], ['rev', Q('A')], ['comment', 1, Q(self.comment)]]]
        libs = ['lib_symbols']
        for name in sorted(self.used_syms):
            libs.append(self.lib.embedded(name))
        root.append(libs)
        for (s, x, y, size, bold) in self.texts:
            eff = ['effects', ['font', ['size', size, size]] + ([['bold', 'yes']] if bold else []), ['justify', 'left', 'top']]
            root.append(['text', Q(s), ['exclude_from_sim', 'no'], ['at', x, y, 0], eff, ['uuid', Q(uid(self.name, 'text', x, y))]])
        for (x, y) in self.junctions:
            root.append(['junction', ['at', x, y], ['diameter', 0], ['color', 0, 0, 0, 0], ['uuid', Q(uid(self.name, 'j', x, y))]])
        for (x, y) in self.ncs:
            root.append(['no_connect', ['at', x, y], ['uuid', Q(uid(self.name, 'nc', x, y))]])
        for (a, b) in self.wires:
            root.append(['wire', ['pts', ['xy', a[0], a[1]], ['xy', b[0], b[1]]],
                         ['stroke', ['width', 0], ['type', 'default']], ['uuid', Q(uid(self.name, 'w', a, b))]])
        for (name, x, y, rot, just) in self.labels:
            root.append(['label', Q(name), ['at', x, y, rot], ['fields_autoplaced', 'yes'],
                         self._effects(justify=just), ['uuid', Q(uid(self.name, 'l', name, x, y))]])
        for (name, shape, x, y) in self.hlabels:
            root.append(['hierarchical_label', Q(name), ['shape', shape], ['at', x, y, 180],
                         ['fields_autoplaced', 'yes'], self._effects(justify='right'),
                         ['uuid', Q(uid(self.name, 'hl', name, x, y))]])
        for (netclass, x, y) in self.flags:
            root.append(['netclass_flag', Q(''), ['length', 2.54], ['shape', 'round'], ['at', x, y, 0],
                         ['fields_autoplaced', 'yes'], self._effects(justify='left bottom'),
                         ['uuid', Q(uid(self.name, 'nf', netclass, x, y))],
                         ['property', Q('Netclass'), Q(netclass), ['at', x + 1.016, y - 2.54, 0],
                          ['show_name', 'no'], self._effects(justify='left')]])
        for inst in self.insts:
            root.append(self._symbol_node(inst))
        for r in self.raw:
            root.append(r)
        if self.instances == [('', 1)]:
            root.append(['sheet_instances', ['path', Q('/'), ['page', Q('1')]]])
        return root

    # ------------------------------------------------------------ self check
    def check(self):
        """Mini connectivity solver: report points of different nets that touch, and pins lying on
        foreign wires (KiCad would silently connect them)."""
        parent = {}

        def key(p):
            return (round(p[0], 2), round(p[1], 2))

        def findp(a):
            parent.setdefault(a, a)
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        def union(a, b):
            ra, rb = findp(a), findp(b)
            if ra != rb:
                parent[ra] = rb

        pinpts = []
        for inst in self.insts:
            for p in inst.pins:
                pinpts.append((key(p.pos), inst, p))
        names = {}
        for (name, x, y, rot, just) in self.labels:
            names.setdefault(key((x, y)), set()).add(name)
        for (name, shape, x, y) in self.hlabels:
            names.setdefault(key((x, y)), set()).add(name)
        for inst in self.insts:
            if inst.refbase[0] == '#PWR':
                names.setdefault(key(inst.pins[0].pos), set()).add(inst.value)
        problems = []
        for (a, b) in self.wires:
            union(key(a), key(b))
            # pins or named points lying strictly inside this segment
            for (pt, inst, p) in pinpts:
                if pt in (key(a), key(b)):
                    continue
                if _on_segment(pt, key(a), key(b)):
                    problems.append(f'pin {inst.ref(self.instances[0][1])}.{p.number} at {pt} lies on wire {key(a)}-{key(b)}')
                    union(pt, key(a))
            for pt in list(names):
                if pt in (key(a), key(b)):
                    continue
                if _on_segment(pt, key(a), key(b)):
                    problems.append(f'label {names[pt]} at {pt} lies on wire {key(a)}-{key(b)}')
                    union(pt, key(a))
        # pins touching other pins at the same point are legitimately connected
        for pt, inst, p in pinpts:
            union(pt, pt)
        # a point with two different names
        for pt, ns in names.items():
            if len(ns) > 1:
                problems.append(f'two nets at {pt}: {ns}')
        # components with two different names
        comp = {}
        for pt, ns in names.items():
            comp.setdefault(findp(pt), set()).update(ns)
        for root, ns in comp.items():
            if len(ns) > 1:
                problems.append(f'wired together: {sorted(ns)}')
        # pins sharing a point with a differently named net is fine; pins of two instances at one
        # point with no wire is a hidden connection
        seen = {}
        for pt, inst, p in pinpts:
            if pt in seen and seen[pt][0] is not inst and pt not in names:
                problems.append(f'pins touch without wire at {pt}: {seen[pt][0].symname}.{seen[pt][1].number} / {inst.symname}.{p.number}')
            seen[pt] = (inst, p)
        return problems

    def write(self, path):
        for inst in self.insts:
            self.nc_all_unused(inst)
        for pr in self.check():
            print('  CHECK', self.name + ':', pr)
        open(path, 'w', encoding='utf-8').write(dump(self.tree()) + '\n')
        return path


def _on_segment(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    if ax == bx:
        return px == ax and min(ay, by) < py < max(ay, by)
    if ay == by:
        return py == ay and min(ax, bx) < px < max(ax, bx)
    return False
