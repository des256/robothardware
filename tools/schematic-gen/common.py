"""Shared catalog + layout helpers for the backbone schematic generator."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sch import Sheet, Lib, g  # noqa: E402,F401
from sx import parse, find, first, prop  # noqa: E402,F401

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
PROJ = os.path.join(REPO, 'backbone')
ROOT_UUID = 'a5b47dc5-6b70-4377-9b8b-b0e1e9cf73c9'

# ------------------------------------------------------------------ LCSC catalog (verified against JLCPCB on 2026-10-08)
R0603 = {
    '0': 'C21189', '2.2': 'C22939', '22': 'C23345', '100': 'C22775', '120': 'C22787', '150': 'C22808',
    '240': 'C23350', '402': 'C23049', '422': 'C23052', '1k': 'C21190', '2.37k': 'C25964', '4.02k': 'C23040',
    '4.42k': 'C23043', '4.7k': 'C23162', '7.5k': 'C23234', '9.53k': 'C23127', '10k': 'C25804', '10.2k': 'C22772',
    '11k': 'C25950', '15k': 'C22809', '16.9k': 'C25954', '18.2k': 'C22892', '20k': 'C4184', '20.5k': 'C22910',
    '23.2k': 'C23346', '24.9k': 'C25962', '27k': 'C22967', '33.2k': 'C23003', '49.9k': 'C23184', '53.6k': 'C23074',
    '80.6k': 'C23249', '82k': 'C23254', '90.9k': 'C23129', '100k': 'C25803', '200k': 'C25811', '243k': 'C23351',
    '249k': 'C22918', '442k': 'C23175', '453k': 'C25818', '910k': 'C23263', '1M': 'C22935',
}
C0603 = {
    '6.8pF': 'C1679', '10pF': 'C1634', '15pF': 'C1644', '30pF': 'C1658', '33pF': 'C1663', '47pF': 'C1671',
    '100pF': 'C14858', '150pF': 'C1594', '680pF': 'C1630', '1.8nF': 'C107042', '3.3nF': 'C1613', '4.7nF': 'C53987',
    '33nF': 'C21117', '47nF': 'C1622', '100nF': 'C14663', '1uF': 'C15849', '2.2uF': 'C23630',
}
C0402 = {'100nF': 'C307331'}
C0805 = {'100nF 100V': 'C28233', '4.7uF': 'C1779', '10uF': 'C15850', '10uF 50V': 'C440198', '22uF': 'C45783'}
C1206 = {'10uF 50V': 'C13585', '47uF 10V': 'C96123', '22uF 25V': 'C12891', '1nF 2kV': 'C9196'}
TVS_SMB = {'SMBJ24A': 'C19077578', 'SMBJ13A': 'C19077567', 'SMBJ6.0A': 'C19077560'}
FB0603 = ('BLM18PG221SN1D', 'C80165')   # 220 R @ 100 MHz, 1.4 A
FB0805 = ('BLM21PG221SN1D', 'C85840')   # 220 R @ 100 MHz, 2 A


def R(s, x, y, value, rot=0, **kw):
    return s.R(x, y, value, R0603[value], rot=rot, **kw)


def C(s, x, y, value, size='0603', rot=0, **kw):
    cat = {'0603': C0603, '0402': C0402, '0805': C0805, '1206': C1206}[size]
    return s.C(x, y, value, cat[value], size=size, rot=rot, **kw)


def end(s, pin, spec):
    """Terminate a pin: 'net:NAME' | 'pwr:NET' | 'nc' | None (leave for manual wiring)."""
    if spec is None:
        return None
    if spec == 'nc':
        s.nc(pin)
        return None
    kind, _, arg = spec.partition(':')
    if kind == 'pwr':
        return s.power(pin, arg)
    if kind == 'net':
        return s.label(pin, arg)
    raise ValueError(spec)


def top_bottom(inst):
    """(top pin, bottom pin) of a vertical 2-pin part."""
    a, b = inst.pins[0], inst.pins[1]
    return (a, b) if a.y < b.y else (b, a)


def left_right(inst):
    a, b = inst.pins[0], inst.pins[1]
    return (a, b) if a.x < b.x else (b, a)


def native_horizontal(s, sym):
    p = s.lib.pins(sym)
    return len(p) == 2 and abs(p[0]['x'] - p[1]['x']) > abs(p[0]['y'] - p[1]['y'])


def vpart(s, sym, prefix, x, y, top, bottom, value=None, lcsc=None, rot=None, **kw):
    if rot is None:
        rot = 270 if native_horizontal(s, sym) else 0   # pin 1 ends up on top either way
    inst = s.place(sym, prefix, x, y, rot, value=value, lcsc=lcsc, **kw)
    t, b = top_bottom(inst)
    end(s, t, top)
    end(s, b, bottom)
    return inst


def vR(s, x, y, value, top, bottom, **kw):
    return vpart(s, 'R_0603', 'R', x, y, top, bottom, value=value, lcsc=R0603[value], **kw)


def vC(s, x, y, value, top, bottom, size='0603', **kw):
    cat = {'0603': C0603, '0402': C0402, '0805': C0805, '1206': C1206}[size]
    return vpart(s, 'C_' + size, 'C', x, y, top, bottom, value=value, lcsc=cat[value], **kw)


def decap(s, x, y, rail, value='100nF', size='0603'):
    return vC(s, x, y, value, 'pwr:' + rail, 'pwr:GND', size=size)


def vdiode(s, sym, x, y, cathode, anode, value=None, lcsc=None, **kw):
    """Vertical diode drawn with cathode at top (rot 180): cathode spec, anode spec."""
    inst = s.place(sym, 'D', x, y, 180, value=value, lcsc=lcsc, **kw)
    k = inst.pin('1')
    a = inst.pin('2')
    end(s, k, cathode)
    end(s, a, anode)
    return inst


def tvs(s, x, y, part, rail, lcsc=None):
    return vdiode(s, 'TVS_SMB', x, y, 'pwr:' + rail, 'pwr:GND', value=part, lcsc=lcsc or TVS_SMB[part])


def rail_led(s, x, y, rail, rvalue):
    """Power-good LED: rail -> R -> LED -> GND"""
    r = s.place('R_0603', 'R', x, y, 0, value=rvalue, lcsc=R0603[rvalue])
    d = s.place('LED_0805_Green', 'D', x, y + 12.7, 0)
    rt, rb = top_bottom(r)
    s.power(rt, rail)
    s.connect(rb, d.pin('2'))
    s.power(d.pin('1'), 'GND')
    return r, d


def testpoint(s, x, y, net, name=None):
    tp = s.place('TestPoint', 'TP', x, y, 0, value=name or net, nobom=True, lcsc='n/a', dnp=False)
    s.label(tp.pins[0], net)
    return tp


def testpoint_pwr(s, x, y, rail):
    tp = s.place('TestPoint', 'TP', x, y, 0, value=rail, nobom=True, lcsc='n/a')
    s.power(tp.pins[0], rail)
    return tp


def hpart(s, sym, prefix, x, y, left, right, value=None, lcsc=None, rot=None, **kw):
    """Horizontal 2-pin part (pin 1 on the left)."""
    if rot is None:
        rot = 0 if native_horizontal(s, sym) else 90
    inst = s.place(sym, prefix, x, y, rot, value=value, lcsc=lcsc, **kw)
    l, r = left_right(inst)
    end(s, l, left)
    end(s, r, right)
    return inst


def hR(s, x, y, value, left, right, **kw):
    return hpart(s, 'R_0603', 'R', x, y, left, right, value=value, lcsc=R0603[value], **kw)


def hC(s, x, y, value, left, right, size='0603', **kw):
    cat = {'0603': C0603, '0402': C0402, '0805': C0805, '1206': C1206}[size]
    return hpart(s, 'C_' + size, 'C', x, y, left, right, value=value, lcsc=cat[value], **kw)


def note(s, x, y, text):
    s.text(x, y, text)


def heading(s, x, y, text):
    s.text(x, y, text, size=2.0, bold=True)


def sheet_uuids():
    """Map sheet name -> (sheet symbol uuid, page) from the existing root file."""
    d = parse(open(os.path.join(PROJ, 'backbone.kicad_sch'), encoding='utf-8').read())
    out = {}
    for sh in find(d, 'sheet'):
        name = prop(sh, 'Sheetname')
        u = first(sh, 'uuid')[1]
        page = None
        inst = first(sh, 'instances')
        if inst:
            for pr in find(inst, 'project'):
                for pa in find(pr, 'path'):
                    page = int(first(pa, 'page')[1])
        out[name] = (u, page)
    return out


def file_uuid(name):
    d = parse(open(os.path.join(PROJ, name + '.kicad_sch'), encoding='utf-8').read())
    return first(d, 'uuid')[1]


def new_sheet(lib, name, paper, title, comment, instance_names):
    su = sheet_uuids()
    inst = [su[n] for n in instance_names]
    return Sheet(lib, name, file_uuid(name), paper, title, comment, ROOT_UUID, inst)
