"""Assemble the project symbol library 0_backbone.kicad_sym.

- fixes pin electrical types on the EasyEDA-imported symbols (they come in as "unspecified")
- copies the generic passives / small parts we need from the CDFER JLCPCB library
  (symbol + footprint + STEP model) into the project-local library
- copies the KiCad standard power / jumper / test point / mounting hole symbols so the
  project is self-contained (no dependency on global symbol libraries)
"""
import copy
import glob
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sx import parse, dump, find, first, prop, set_prop, QStr as Q  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
PROJ = os.path.join(REPO, 'backbone')
CDFER = os.environ.get('CDFER_PKG', '/tmp/kk/cdfer_pkg')  # unzipped JLCPCB-KiCad-Library PCM package
KSYM = '/usr/share/kicad/symbols'
LIBNAME = '0_backbone'

# ---------------------------------------------------------------- pin types
# name regex -> type, first match wins; '*' is the default for the symbol
PIN_TYPES = {
    'TUSB8041IRGCR': [
        (r'^VDD(33)?$', 'power_in'), (r'^VSS$', 'power_in'),
        (r'^USB_D[PM]_', 'bidirectional'), (r'^USB_SSTX', 'output'), (r'^USB_SSRX', 'input'),
        (r'^PWRCTL\d', 'output'), (r'^PWRCTL_POL', 'bidirectional'), (r'^OVERCUR', 'input'),
        (r'^(SDA|SCL)/', 'bidirectional'),
        (r'^(SMBUSz|FULLPWRMGMTz|GANGED|AUTOENz)', 'bidirectional'),
        (r'^(TEST|GRSTz|XI|USB_VBUS)$', 'input'), (r'^XO$', 'output'), (r'^USB_R1$', 'passive'),
        (r'^NC$', 'no_connect'),
    ],
    'CH344Q_C2988084': [
        (r'^VCC$', 'power_in'), (r'^GND$', 'power_in'), (r'^TXD', 'output'), (r'^RXD', 'input'),
        (r'^TNOW', 'output'), (r'^(CTS|DSR|RI|DCD)', 'input'), (r'^RTS', 'output'),
        (r'^(ACT|TX_S|RX_S)', 'output'), (r'^UD[+-]$', 'bidirectional'), (r'^XI$', 'input'),
        (r'^XO$', 'output'), (r'^(RESET|TEST)$', 'input'), (r'^NC$', 'no_connect'),
    ],
    'SN74LVC2G241DCU': [
        (r'OE', 'input'), (r'^[12]A$', 'input'), (r'^[12]Y$', 'tri_state'),
        (r'^(VCC|GND)$', 'power_in'),
    ],
    'LM5145RGYR': [
        (r'^(EN/UVLO|RT|SS/TRK|FB|SYNCIN|ILIM)$', 'input'), (r'^(COMP|SYNCOUT|LO|HO)$', 'output'),
        (r'^(AGND|PGND|EP|VIN)$', 'power_in'), (r'^PGOOD$', 'open_collector'),
        (r'^VCC$', 'power_out'), (r'^(BST|SW)$', 'passive'), (r'^NC$', 'no_connect'),
    ],
    'TPS54560DDAR': [
        (r'^(BOOT|SW)$', 'passive'), (r'^(VIN|GND|EP)$', 'power_in'),
        (r'^(EN|RT/CLK|FB)$', 'input'), (r'^COMP$', 'output'),
    ],
    'TLV62569DBVR': [
        (r'^(EN|FB)$', 'input'), (r'^(GND|VIN)$', 'power_in'), (r'^SW$', 'passive'),
    ],
    'TPS16630PWPR': [
        (r'^(IN|P_IN|GND|EP)$', 'power_in'), (r'^N\.C$', 'no_connect'),
        (r'^(UVLO|OVP|MODE|~\{SHDN\})$', 'input'), (r'^(dVdT|ILIM|OUT)$', 'passive'),
        (r'^IMON$', 'output'), (r'^~\{FLT\}$', 'open_collector'), (r'^PGOOD$', 'output'),
    ],
    'TPS25961DRVR': [
        (r'^(OUT|ILIM)$', 'passive'), (r'^(OVLO|EN/UVLO)$', 'input'), (r'^(GND|IN)$', 'power_in'),
    ],
    'HD3SS3220RNHR': [
        (r'^CC[12]$', 'bidirectional'),
        (r'^(CURRENT_MODE|PORT|VBUS_DET|ENn_MUX|ADDR|ENn_CC)$', 'input'),
        (r'^(TX|RX)', 'bidirectional'), (r'^(VCC33|VDD5|GND|EP)$', 'power_in'),
        (r'^(DIR|INT_N/OUT3|VCONN_FAULT_N|SDA/OUT1|SCL/OUT2|ID)$', 'open_collector'),
    ],
    'LM74700QDBVRQ1': [
        (r'^(VCAP|CATHODE)$', 'passive'), (r'^(GND|ANODE)$', 'power_in'),
        (r'^EN$', 'input'), (r'^GATE$', 'output'),
    ],
    'TPD4E05U06DQAR_C138714': [(r'^D', 'passive'), (r'^GND$', 'power_in'), (r'^NC$', 'no_connect')],
    'USBLC6-2SC6_C2687116': [(r'^GND$', 'power_in'), (r'.*', 'passive')],
    'TPS2553DBVR': [
        (r'^(IN|GND)$', 'power_in'), (r'^EN$', 'input'), (r'^/FAULT$', 'open_collector'),
        (r'^(ILIM|OUT)$', 'passive'),
    ],
    'CSD18532Q5B': [(r'^G$', 'input'), (r'.*', 'passive')],
    'SP3485EN': [
        (r'^RO$', 'tri_state'), (r'^(RE#|DE|DI)$', 'input'), (r'^(GND|VCC)$', 'power_in'),
        (r'^[AB]$', 'bidirectional'),
    ],
}
ALL_PASSIVE = [
    'B4B-EH-A', 'B3B-EH-A', 'XT30PW-M', 'HC-ST-003-01-J', 'TYPE-C24PQT',
    'TMPA1265SP-4R7MN-D', 'TMPC1265HP-3R3MG-D', '7447798720', 'SMNR4020-2.2UH',
    'C3225X7S2A475KT000N', 'C3225X7R2A225KT5L0U', 'GRM32ER61C476KE15L', 'CS3225X7R226K250NRL',
    'MA25V470M8X10', 'MA10V470M6X8', 'RVE470UF35V167RV084', '0453015.MR', '1206TD-4A', 'B560C-13-F',
    'PSM712', 'Crystal_8MHz_5032', 'Crystal_24MHz_3225',
    'R_0603', 'C_0402', 'C_0603', 'C_0805', 'C_1206', 'FB_0603', 'FB_0805', 'LED_0805_Green',
    'TVS_SMB', 'SMF5.0A', 'SS14',
]

# ---------------------------------------------------------------- CDFER copies
# new name, cdfer lib, cdfer symbol, footprint (CDFER name), value, lcsc, description
CDFER_COPIES = [
    ('R_0603', 'JLCPCB-Resistors', '0603,10kΩ', 'R_0603', '', '', 'Resistor 0603 (value + LCSC per instance)'),
    ('C_0402', 'JLCPCB-Capacitors', '0402,100nF,(2)', 'C_0402', '', '', 'Capacitor 0402 (value + LCSC per instance)'),
    ('C_0603', 'JLCPCB-Capacitors', '0603,100nF', 'C_0603', '', '', 'Capacitor 0603 (value + LCSC per instance)'),
    ('C_0805', 'JLCPCB-Capacitors', '0805,100nF', 'C_0805', '', '', 'Capacitor 0805 (value + LCSC per instance)'),
    ('C_1206', 'JLCPCB-Capacitors', '1206,10uF', 'C_1206', '', '', 'Capacitor 1206 (value + LCSC per instance)'),
    ('FB_0603', 'JLCPCB-Inductors', 'Ferrite,0603,(2)', 'FB_0603', '', '', 'Ferrite bead 0603 (value + LCSC per instance)'),
    ('FB_0805', 'JLCPCB-Inductors', 'Ferrite,0805', 'FB_0805', '', '', 'Ferrite bead 0805 (value + LCSC per instance)'),
    ('LED_0805_Green', 'JLCPCB-Diodes', 'LED,0805,Green', 'D_0805', 'LED Green', 'C2297', 'Green LED 0805 (JLC Basic)'),
    ('TVS_SMB', 'JLCPCB-Diodes', 'TVS-Uni,SMBJ28A', 'D_SMB', '', '', 'Unidirectional TVS, SMB (value + LCSC per instance)'),
    ('SMF5.0A', 'JLCPCB-Diodes', 'TVS-Uni,SMF5.0A', 'D_SOD-123FL', 'SMF5.0A', 'C19077497', 'TVS 5 V working, SOD-123FL (JLC Basic)'),
    ('SS14', 'JLCPCB-Diodes', 'Schottky,SS14', 'D_SMA', 'SS14', 'C2480', 'Schottky 40 V 1 A, SMA (JLC Basic)'),
    ('PSM712', 'JLCPCB-Diode-Packages', 'TVS-Bi, PSM712-LF-T7', 'SOT-23-3_L3.0-W1.7-P0.95-LS2.9-BR', 'PSM712-LF-T7', 'C32677', 'RS-485 TVS array -7/+12 V, SOT-23 (JLC Basic)'),
    ('SP3485EN', 'JLCPCB-Interface', 'Transceiver, RS485/422, 10Mbps, SP3485EN-L/TR', 'SOIC-8_L5.0-W4.0-P1.27-LS6.0-BL', 'SP3485EN-L/TR', 'C8963', 'RS-485 transceiver 3.3 V 10 Mbps (JLC Basic)'),
    ('Crystal_8MHz_5032', 'JLCPCB-Crystals', 'Crystal, 8MHz, 20pF, ±10ppm', 'CRYSTAL-SMD_L5.0-W3.2', '8MHz 20pF', 'C115962', 'Crystal 8 MHz 20 pF SMD5032 (JLC Basic)'),
    ('Crystal_24MHz_3225', 'JLCPCB-Crystals', 'Crystal, 25MHz, 11pF', 'OSC-SMD_4P-L3.2-W2.5-BL', '24MHz 18pF', 'C70571', 'Crystal 24 MHz 18 pF SMD3225 (YXC X322524MRB4SI)'),
]
DROP_PROPS = {'Stock', 'Price', 'Minimum Qty', 'Process', 'Attrition Qty', 'Part', 'LCSC Part', 'Manufacturer Part'}

# ---------------------------------------------------------------- KiCad std copies
KICAD_COPIES = [
    ('power', '+VDC', None), ('power', '+12V', None), ('power', '+5V', None), ('power', '+3V3', None),
    ('power', '+1V1', None), ('power', 'VBUS', None), ('power', 'GND', None), ('power', 'PWR_FLAG', None),
    ('Connector', 'TestPoint', 'TestPoint:TestPoint_Pad_D1.5mm'),
    ('Jumper', 'SolderJumper_3_Bridged12', 'Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm'),
    ('Jumper', 'SolderJumper_2_Bridged', 'Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm'),
    ('Jumper', 'SolderJumper_2_Open', 'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm'),
    ('Mechanical', 'MountingHole', 'MountingHole:MountingHole_3.2mm_M3_Pad_Via'),
]


def load_lib(path):
    return parse(open(path, encoding='utf-8').read())


def symbols(tree):
    return {s[1]: s for s in find(tree, 'symbol')}


def rename_symbol(sym, new):
    old = sym[1]
    sym[1] = Q(new)
    for u in find(sym, 'symbol'):
        if u[1].startswith(old + '_'):
            u[1] = Q(new + u[1][len(old):])
    return sym


def set_pin_types(sym, rules):
    for u in find(sym, 'symbol'):
        for p in find(u, 'pin'):
            name = first(p, 'name')[1]
            for rx, typ in rules:
                if re.search(rx, name):
                    p[1] = typ
                    break


def pin_type_fix(libsyms):
    for name, rules in PIN_TYPES.items():
        if name in libsyms:
            set_pin_types(libsyms[name], rules)
    for name in ALL_PASSIVE:
        if name in libsyms:
            set_pin_types(libsyms[name], [(r'.*', 'passive')])


def copy_footprint(fp, src_dir, dst_pretty, dst_3d):
    src = os.path.join(src_dir, fp + '.kicad_mod')
    dst = os.path.join(dst_pretty, fp + '.kicad_mod')
    text = open(src, encoding='utf-8').read()
    m = re.search(r'\(model "([^"]+)"', text)
    if m:
        model = m.group(1)
        step = os.path.basename(model)
        step_src = os.path.join(CDFER, '3dmodels', 'JLCPCB.3dshapes', step)
        if os.path.exists(step_src):
            shutil.copyfile(step_src, os.path.join(dst_3d, step))
            text = text.replace(model, '${KIPRJMOD}/' + LIBNAME + '.3dshapes/' + step)
        else:
            text = re.sub(r'\(model "[^"]+"', '(model ""', text)
    open(dst, 'w', encoding='utf-8').write(text)


def main():
    proj_lib_path = os.path.join(PROJ, LIBNAME + '.kicad_sym')
    tree = load_lib(proj_lib_path)
    libsyms = symbols(tree)

    cdfer_libs = {}
    for fn in glob.glob(os.path.join(CDFER, 'symbols', '*.kicad_sym')):
        cdfer_libs[os.path.basename(fn)[:-10]] = symbols(load_lib(fn))

    new_syms = []
    for new, lib, srcname, fp, value, lcsc, desc in CDFER_COPIES:
        if new in libsyms:
            continue
        src = cdfer_libs[lib][srcname]
        sym = copy.deepcopy(src)
        rename_symbol(sym, new)
        # drop volatile vendor fields, rename Part -> MPN
        mpn = prop(sym, 'Part')
        for p in list(find(sym, 'property')):
            if p[1] in DROP_PROPS:
                sym.remove(p)
        set_prop(sym, 'Footprint', LIBNAME + ':' + fp, hide=True)
        set_prop(sym, 'Value', value)
        set_prop(sym, 'LCSC', lcsc, hide=True)
        set_prop(sym, 'Description', desc, hide=True)
        if mpn and value:
            set_prop(sym, 'MPN', mpn, hide=True)
        copy_footprint(fp, os.path.join(CDFER, 'footprints', 'JLCPCB.pretty'),
                       os.path.join(PROJ, LIBNAME + '.pretty'), os.path.join(PROJ, LIBNAME + '.3dshapes'))
        new_syms.append(sym)
        libsyms[new] = sym

    for lib, name, fp in KICAD_COPIES:
        if name in libsyms:
            continue
        src = symbols(load_lib(os.path.join(KSYM, lib + '.kicad_sym')))[name]
        sym = copy.deepcopy(src)
        if fp:
            set_prop(sym, 'Footprint', fp, hide=True)
        new_syms.append(sym)
        libsyms[name] = sym

    pin_type_fix(libsyms)

    # KiCad standard footprints for the test points / jumpers / mounting holes: copy into the
    # project library so nothing depends on the global fp-lib-table
    KFP = '/usr/share/kicad/footprints'
    for sym, lib, fp in [('TestPoint', 'TestPoint', 'TestPoint_Pad_D1.5mm'),
                         ('SolderJumper_3_Bridged12', 'Jumper', 'SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm'),
                         ('SolderJumper_2_Bridged', 'Jumper', 'SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm'),
                         ('SolderJumper_2_Open', 'Jumper', 'SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm'),
                         ('MountingHole', 'MountingHole', 'MountingHole_3.2mm_M3_Pad_Via')]:
        src_fp = os.path.join(KFP, lib + '.pretty', fp + '.kicad_mod')
        dst_fp = os.path.join(PROJ, LIBNAME + '.pretty', fp + '.kicad_mod')
        if not os.path.exists(dst_fp):
            shutil.copyfile(src_fp, dst_fp)
        if sym in libsyms:
            set_prop(libsyms[sym], 'Footprint', LIBNAME + ':' + fp, hide=True)

    # rebuild the library tree with a KiCad 9 header
    out = ['kicad_symbol_lib', ['version', '20241209'], ['generator', Q('kicad_symbol_editor')],
           ['generator_version', Q('9.0')]]
    for s in find(tree, 'symbol'):
        out.append(s)
    for s in new_syms:
        out.append(s)
    open(proj_lib_path, 'w', encoding='utf-8').write(dump(out) + '\n')
    print('library written:', proj_lib_path, 'symbols:', len(find(out, 'symbol')))


if __name__ == '__main__':
    main()
