"""Root sheet: keep the skeleton's block diagram (sheet symbols, labels, wires) and re-emit it in the
KiCad 9 file format (KiCad 10 reads it); add the mechanical items (mounting holes)."""
import copy
import os

from common import *  # noqa: F401,F403
from common import PROJ, ROOT_UUID, new_sheet, note
from sx import parse, find, first, prop, QStr as Q

SKELETON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skeleton', 'backbone.kicad_sch')
DROP = {'show_name', 'do_not_autoplace', 'in_pos_files', 'duplicate_pin_numbers_are_jumpers', 'body_style'}


def strip10(node):
    if not isinstance(node, list):
        return node
    out = []
    for c in node:
        if isinstance(c, list) and c and c[0] in DROP:
            continue
        out.append(strip10(c))
    return out


ROOT_NOTE = (
    "ROBOT BACKBONE — root sheet = block diagram (FUNCTIONAL.md §3). Sheet symbols plus the mechanical items (mounting holes) live here; everything electrical is in the sub-sheets.\n"
    "Sheets: 2 input · 3 buck-12v-servo · 4 buck-5v-servo · 5 buck-5v-usb · 6 usbc-upstream · 7 usb-hub · 8-10 usb-port-1..3 (one file) · 11 servo-uart · 12-15 servo-port-0..3 (one file)\n"
    "Rails are global power symbols from the project library 0_backbone: +19V_IN +19V_JETSON +12V_SERVO +5V_SERVO +5V_USB +3V3 +1V1_HUB VBUS GND. Each rail has its PWR_FLAG on the sheet that produces it.\n"
    "VBUS = upstream USB-C VBUS only (kkh checks < 10 µF on it). +5V_SERVO is never merged with +5V_USB.\n"
    "Signals cross sheets through hierarchical pins; the labels on this sheet name the top-level nets (US_* upstream↔hub, DSn_* hub↔ports, UARTn_* uart↔servo ports).\n"
    "Net classes (Board Setup → Net Classes, stored in backbone.kicad_pro): USB3_SS, USB2_HS, RS485, TTL_DATA, PWR_19V, PWR_SERVO, PWR_USB, SW_NODE.\n"
    "  – signal nets: directive labels inside the sub-sheets (a multi-instance sheet applies them to every instance)\n"
    "  – rails and per-port nets: project net-class patterns (+12V_SERVO, /servo-port-*/A, /buck-*/SW*, /usb-port-*/VBUS_*, /usb-hub/SW_1V1, …)\n"
    "Layer geometry per class lives in backbone.kicad_dru (impedance widths are TODO from the JLCPCB JLC04161H-7628 calculator). Layers: F.Cu / In1.Cu=GND / In2.Cu=PWR / B.Cu.\n"
    "Designators: sheet number × 100 + n (R301 = sheet 3; usb-port instances count 8xx/9xx/10xx, servo-port instances 12xx..15xx). Power symbols #PWR0201… follow the same scheme.\n"
    "kkh-analyze-schematic sums every max_mA and asserts <= 300 mA: max_mA is set only on the +3V3 ICs (hub VDD33 33, CH344Q 30, HD3SS3220 5, 4 × SP3485EN 35, 4 × LVC2G241 5 = 228 mA).\n"
    "Every assembled part carries its LCSC number (kkh check). Non-assembled items (test points, solder jumpers, mounting holes) are excluded from the BOM and carry LCSC = n/a.\n"
    "Put the ${KKH_VERSION_DATE} text on the PCB silkscreen (done in backbone.kicad_pcb)."
)


def sheet_root(lib):
    d = parse(open(SKELETON, encoding='utf-8').read())
    s = new_sheet(lib, 'backbone', 'A3', 'Robot backbone — root (block diagram)',
                  'HARDWARE.md · FUNCTIONAL.md · README.md', [])
    s.instances = [('', 1)]
    s.file_uuid = ROOT_UUID
    for kind in ('sheet', 'label', 'wire', 'junction'):
        for n in find(d, kind):
            s.raw.append(strip10(copy.deepcopy(n)))
    note(s, 12.7, 252.73, ROOT_NOTE)
    # mounting holes (M3, 4 corners) — mechanical only, excluded from the BOM
    for i, (x, y) in enumerate([(342.9, 226.06), (355.6, 226.06), (368.3, 226.06), (381.0, 226.06)]):
        s.place('MountingHole', 'H', x, y, 0, value='M3', nobom=True, lcsc='n/a', refnum=i + 1)
    s.text(342.9, 215.9, 'Mounting holes (M3, pad + vias)', size=2.0, bold=True)
    return s
