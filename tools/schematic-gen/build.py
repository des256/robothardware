"""Build driver: write the generated sheets into the project and run ERC with the Flatpak KiCad 10."""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PROJ, REPO  # noqa: E402
from sch import Lib  # noqa: E402

KICAD = ['flatpak', 'run', '--filesystem=' + REPO + ':rw', '--command=/app/bin/kicad-cli', 'org.kicad.KiCad']


def build(which=None):
    import d_power
    lib = Lib(os.path.join(PROJ, '0_backbone.kicad_sym'))
    builders = {
        'input': d_power.sheet_input,
        'buck-12v-servo': d_power.sheet_buck12,
        'buck-5v-servo': d_power.sheet_buck5,
        'buck-5v-usb': d_power.sheet_buck_usb,
    }
    try:
        import d_usb
        builders.update({
            'usbc-upstream': d_usb.sheet_usbc,
            'usb-hub': d_usb.sheet_hub,
            'usb-port': d_usb.sheet_port,
        })
    except ImportError:
        pass
    try:
        import d_servo
        builders.update({
            'servo-uart': d_servo.sheet_uart,
            'servo-port': d_servo.sheet_port,
        })
    except ImportError:
        pass
    try:
        import d_root
        builders['backbone'] = d_root.sheet_root
    except ImportError:
        pass
    written = []
    for name, fn in builders.items():
        if which and name not in which:
            continue
        s = fn(lib)
        path = s.write(os.path.join(PROJ, name + '.kicad_sch'))
        written.append(path)
        print('wrote', path, 'symbols', len(s.insts), 'wires', len(s.wires), 'labels', len(s.labels))
    return written


def erc(show_sheets=None, limit=60):
    out = os.path.join(PROJ, 'outputs', 'scratch', 'erc.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    r = subprocess.run(KICAD + ['sch', 'erc', '--format', 'json', '-o', out, os.path.join(PROJ, 'backbone.kicad_sch')],
                       capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-400:])
    d = json.load(open(out))
    from collections import Counter
    total = Counter()
    n = 0
    for sh in d['sheets']:
        path = sh.get('path') or sh.get('uuid_path') or ''
        name = sh.get('path', '?')
        for v in sh['violations']:
            total[(v['type'], v['severity'])] += 1
            if show_sheets is None or any(ss in name for ss in show_sheets):
                if n < limit:
                    items = '; '.join((i.get('description') or '')[:70] for i in v['items'][:2])
                    print(f"  [{name}] {v['severity']} {v['type']}: {v['description'][:100]} | {items}")
                    n += 1
    print('TOTAL', dict(total))
    return d


if __name__ == '__main__':
    args = sys.argv[1:]
    which = [a for a in args if not a.startswith('--')] or None
    build(which)
    if '--no-erc' not in args:
        erc(which)
