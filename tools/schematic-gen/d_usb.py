"""Sheets 6-10: USB-C upstream (HD3SS3220), TUSB8041 hub, generic USB-A 3.0 port (x3)."""
from common import *  # noqa: F401,F403
from common import vR, vC, hR, hC, decap, vdiode, rail_led, testpoint, testpoint_pwr, vpart, hpart, end, note, heading, new_sheet, top_bottom, left_right, R0603, C0603, C0805, C1206, FB0603, FB0805


def classed(s, name, netclass, x, y):
    """A local label carrying a net-class directive (for nets that only live inside this sheet)."""
    s.label_xy(name, x, y, 180)
    s.wire((x, y), (x + 5.08, y))
    s.flags.append((netclass, g(x + 5.08), g(y)))


HIER_USBC = [('US_SSTX_P', 'input', 'USB3_SS'), ('US_SSTX_N', 'input', 'USB3_SS'),
             ('US_SSRX_P', 'output', 'USB3_SS'), ('US_SSRX_N', 'output', 'USB3_SS'),
             ('US_DP', 'bidirectional', 'USB2_HS'), ('US_DM', 'bidirectional', 'USB2_HS')]


def sheet_usbc(lib):
    s = new_sheet(lib, 'usbc-upstream', 'A3', 'USB-C upstream: HD3SS3220 CC controller + SS mux (UFP)',
                  'TI HD3SS3220 datasheet · sllu241 UFP dongle EVM · slla481 schematic checklist', ['usbc-upstream'])
    note(s, 12.7, 12.7,
         "USB-C UPSTREAM — J601 24-pin receptacle, HD3SS3220 in UFP / GPIO mode: PORT = GND (UFP), ADDR open (GPIO mode), ENn_CC = GND, ENn_MUX = GND,\n"
         "CURRENT_MODE = GND (don't care as UFP), VBUS_DET from the connector VBUS through 910 k, DIR pulled up 200 k (open drain, required).\n"
         "VBUS is detection only — never a power source; the VBUS net stays below 10 µF (kkh-analyze-schematic enforces it) and only feeds VBUS_DET, USB_VBUS (hub) and the ESD clamps.\n"
         "SuperSpeed: hub TX (US_SSTX, hub transmits) → 100 nF AC caps → mux TXp/TXn → TX1/TX2 pins of the receptacle (the host side has its own caps on its TX = our RX path).\n"
         "Mux RXp/RXn → US_SSRX (hub receives). Both plug orientations work; the mux picks the live pair from CC1/CC2. USB 2.0 D+/D- are shorted at the connector (both rows).\n"
         "ESD: TPD4E05U06 on each connector-side SS pair, USBLC6-2 on D+/D-. Shield (EP pads) to GND through 1 MΩ || 1 nF 2 kV.\n"
         "Supplies: VDD5 from +5V_USB (must be up before VCC33, naturally true since +3V3 is derived from it), VCC33 from +3V3. Checklist slla481 run: item list in README.")
    y = 71.12
    for name, shape, nc in HIER_USBC:
        s.hier(name, shape, 30.48, y, nc)
        y += 5.08
    # AC coupling on the hub TX pair, placed on the mux side (one set only: internal connection to the hub)
    heading(s, 85, 55, 'AC coupling (hub SSTX) and straps')
    hC(s, 101.6, 71.12, '100nF', 'net:US_SSTX_P', 'net:SSTX_P_C', size='0402')
    hC(s, 101.6, 78.74, '100nF', 'net:US_SSTX_N', 'net:SSTX_N_C', size='0402')
    vR(s, 119.38, 101.6, '910k', 'pwr:VBUS', 'net:VBUS_DET')
    vR(s, 132.08, 101.6, '200k', 'pwr:+3V3', 'net:DIR')
    testpoint(s, 134.62, 116.84, 'DIR')
    # U601
    u = s.place('HD3SS3220RNHR', 'U', 190.5, 127, 0, refnum=1, fields={'max_mA': 5})
    s.label(u.pin('CC2'), 'CC2')
    s.label(u.pin('CC1'), 'CC1')
    s.power(u.pin('CURRENT_MODE'), 'GND')
    s.power(u.pin('PORT'), 'GND')
    s.label(u.pin('VBUS_DET'), 'VBUS_DET')
    s.label(u.pin('TXp'), 'SSTX_P_C')
    s.label(u.pin('TXn'), 'SSTX_N_C')
    s.power(u.pin('VCC33'), '+3V3')
    s.label(u.pin('RXp'), 'US_SSRX_P')
    s.label(u.pin('RXn'), 'US_SSRX_N')
    s.label(u.pin('DIR'), 'DIR')
    s.power(u.pin('ENn_MUX'), 'GND')
    for p in u.pins_named('GND'):
        s.power(p, 'GND')
    s.power(u.pin('EP'), 'GND')
    s.label(u.pin('RX1n'), 'C_RX1N')
    s.label(u.pin('RX1p'), 'C_RX1P')
    s.label(u.pin('TX1n'), 'C_TX1N')
    s.label(u.pin('TX1p'), 'C_TX1P')
    s.label(u.pin('RX2n'), 'C_RX2N')
    s.label(u.pin('RX2p'), 'C_RX2P')
    s.label(u.pin('TX2n'), 'C_TX2N')
    s.label(u.pin('TX2p'), 'C_TX2P')
    s.nc(u.pin('ADDR'), u.pin('INT_N/OUT3'), u.pin('VCONN_FAULT_N'), u.pin('SDA/OUT1'), u.pin('SCL/OUT2'), u.pin('ID'))
    s.power(u.pin('ENn_CC'), 'GND')
    s.power(u.pin('VDD5'), '+5V_USB')
    heading(s, 85, 170, 'Decoupling (VCC33 2 × 100 nF, VDD5 1 µF + 100 nF)')
    decap(s, 96.52, 190.5, '+3V3')
    decap(s, 109.22, 190.5, '+3V3')
    decap(s, 121.92, 190.5, '+5V_USB', '1uF')
    decap(s, 134.62, 190.5, '+5V_USB')
    # ESD arrays on the connector-side SS pairs
    heading(s, 240, 55, 'ESD and the receptacle')
    for i, (n, nets) in enumerate([(1, ('C_TX1P', 'C_TX1N', 'C_RX1P', 'C_RX1N')), (2, ('C_TX2P', 'C_TX2N', 'C_RX2P', 'C_RX2N'))]):
        d = s.place('TPD4E05U06DQAR_C138714', 'D', 254.0, 76.2 + i * 25.4, 0, value='TPD4E05U06', refnum=n)
        s.label(d.pin('D1+'), nets[0])
        s.label(d.pin('D1-'), nets[1])
        s.label(d.pin('D2+'), nets[2])
        s.label(d.pin('D2-'), nets[3])
        for p in d.pins_named('GND'):
            s.power(p, 'GND')
    d3 = s.place('USBLC6-2SC6_C2687116', 'D', 254.0, 127, 0, value='USBLC6-2SC6', refnum=3)
    s.label(d3.pin('1'), 'DP_C')
    s.label(d3.pin('6'), 'US_DP')
    s.label(d3.pin('3'), 'DM_C')
    s.label(d3.pin('4'), 'US_DM')
    s.power(d3.pin('5'), 'VBUS')
    s.power(d3.pin('2'), 'GND')
    # receptacle
    j = s.place('TYPE-C24PQT', 'J', 340.36, 127, 0, value='USB-C 24P receptacle', refnum=1)
    conn = {'A1': 'pwr:GND', 'A12': 'pwr:GND', 'B1': 'pwr:GND', 'B12': 'pwr:GND',
            'A4': 'pwr:VBUS', 'A9': 'pwr:VBUS', 'B4': 'pwr:VBUS', 'B9': 'pwr:VBUS',
            'A5': 'net:CC1', 'B5': 'net:CC2', 'A6': 'net:DP_C', 'B6': 'net:DP_C', 'A7': 'net:DM_C', 'B7': 'net:DM_C',
            'A8': 'nc', 'B8': 'nc', 'A2': 'net:C_TX1P', 'A3': 'net:C_TX1N', 'A10': 'net:C_RX2N', 'A11': 'net:C_RX2P',
            'B2': 'net:C_TX2P', 'B3': 'net:C_TX2N', 'B10': 'net:C_RX1N', 'B11': 'net:C_RX1P',
            '25': 'net:SHIELD_C', '3': 'net:SHIELD_C', '4': 'net:SHIELD_C'}
    for num, spec in conn.items():
        end(s, j.pin(num), spec)
    vR(s, 370.84, 180.34, '1M', 'net:SHIELD_C', 'pwr:GND')
    vC(s, 383.54, 180.34, '1nF 2kV', 'net:SHIELD_C', 'pwr:GND', size='1206')
    # VBUS flag (the Jetson's port is the source)
    s.flag_rail(154.94, 55.88, 'VBUS')
    # net classes for the connector-side pairs
    heading(s, 240, 170, 'Net-class directives for the sheet-local USB nets')
    y = 185.42
    for name, nc in [('C_TX1P', 'USB3_SS'), ('C_TX1N', 'USB3_SS'), ('C_RX1P', 'USB3_SS'), ('C_RX1N', 'USB3_SS'),
                     ('C_TX2P', 'USB3_SS'), ('C_TX2N', 'USB3_SS'), ('C_RX2P', 'USB3_SS'), ('C_RX2N', 'USB3_SS'),
                     ('SSTX_P_C', 'USB3_SS'), ('SSTX_N_C', 'USB3_SS'), ('DP_C', 'USB2_HS'), ('DM_C', 'USB2_HS')]:
        classed(s, name, nc, 254.0, y)
        y += 5.08
    return s


HIER_HUB_L = [('US_SSTX_P', 'output', 'USB3_SS'), ('US_SSTX_N', 'output', 'USB3_SS'),
              ('US_SSRX_P', 'input', 'USB3_SS'), ('US_SSRX_N', 'input', 'USB3_SS'),
              ('US_DP', 'bidirectional', 'USB2_HS'), ('US_DM', 'bidirectional', 'USB2_HS')]
for _n in (1, 2, 3):
    HIER_HUB_L += [(f'DS{_n}_SSTX_P', 'output', 'USB3_SS'), (f'DS{_n}_SSTX_N', 'output', 'USB3_SS'),
                   (f'DS{_n}_SSRX_P', 'input', 'USB3_SS'), (f'DS{_n}_SSRX_N', 'input', 'USB3_SS'),
                   (f'DS{_n}_DP', 'bidirectional', 'USB2_HS'), (f'DS{_n}_DM', 'bidirectional', 'USB2_HS'),
                   (f'DS{_n}_PWRCTL', 'output', None), (f'DS{_n}_OVERCUR_N', 'input', None)]
HIER_HUB_L += [('DS4_DP', 'bidirectional', 'USB2_HS'), ('DS4_DM', 'bidirectional', 'USB2_HS')]


def sheet_hub(lib):
    s = new_sheet(lib, 'usb-hub', 'A3', 'USB 3.0 hub: TUSB8041, self-powered, pin-strapped',
                  'TI TUSB8041 datasheet §9.2 · sllu198 TUSB8041 EVM', ['usb-hub'])
    note(s, 12.7, 12.7,
         "USB HUB — TUSB8041 (4-port SS hub), 24 MHz crystal (18 pF CL, 2 × 30 pF, 1 MΩ feedback), 9.53 k on USB_R1, USB_VBUS = VBUS × 10 k / (90.9 k + 10 k).\n"
         "Straps (sampled at GRSTz release, all left at their internal defaults): FULLPWRMGMTz PD → power switching + over-current supported, GANGED PD → individual,\n"
         "PWRCTL_POL PU → PWRCTLx active high (TPS2553 EN), SMBUSz PU → I2C mode but no EEPROM fitted (D5: defaults, pin-strap only), AUTOENz PU → no auto charge mode,\n"
         "BATENx not pulled up → no battery charging, TEST = GND. GRSTz: 10 k pull-up + 10 µF (≈100 ms), released well after +3V3 and +1V1_HUB are stable (datasheet td2 ≥ 3 ms).\n"
         "Core 1.1 V: TLV62569 from +5V_USB (82 k / 100 k → 1.09 V, inside the 0.99–1.26 V window), ferrite-isolated into VDD_HUB with 8 × 100 nF + 10 µF; the EVM's TPS74801 LDO (C129193)\n"
         "is the drop-in alternative if switching noise on the core rail is a problem. DS1–DS3 → usb-port-1..3 (SS + HS). DS4 → servo-uart (USB 2.0 only); DS4 SS pins left open (V5).\n"
         "OVERCURxz: 10 k pull-ups, driven low by the TPS2553 FAULT outputs. max_mA on the hub = VDD33 current only (33 mA per TI); the core current (≤ 778 mA) is on +1V1_HUB.")
    y = 71.12
    for i, (name, shape, nc) in enumerate(HIER_HUB_L):
        if i < 24:
            s.hier(name, shape, 30.48, y, nc)
            y += 5.08
        else:
            if i == 24:
                y = 71.12
            s.hier(name, shape, 119.38, y, nc)
            y += 5.08
    # hub
    u = s.place('TUSB8041IRGCR', 'U', 266.7, 142.24, 0, refnum=1, fields={'max_mA': 33})
    import re
    for p in u.pins:
        m = re.match(r'USB_(DP|DM|SSTXP|SSTXM|SSRXP|SSRXM)_(DN(\d)|UP)$', p.name)
        if m:
            kind, side, n = m.group(1), m.group(2), m.group(3)
            suffix = {'DP': 'DP', 'DM': 'DM', 'SSTXP': 'SSTX_P', 'SSTXM': 'SSTX_N', 'SSRXP': 'SSRX_P', 'SSRXM': 'SSRX_N'}[kind]
            if side == 'UP':
                s.label(p, 'US_' + suffix)
            elif n == '4' and kind.startswith('SS'):
                s.nc(p)
            else:
                s.label(p, f'DS{n}_{suffix}')
            continue
        m = re.match(r'PWRCTL(\d)/BATEN', p.name)
        if m:
            n = m.group(1)
            s.label(p, f'DS{n}_PWRCTL') if n != '4' else s.nc(p)
            continue
        m = re.match(r'OVERCUR(\d)z', p.name)
        if m:
            n = m.group(1)
            s.label(p, f'DS{n}_OVERCUR_N') if n != '4' else s.nc(p)
            continue
        if p.name in ('SDA/SMBDAT', 'SCL/SMBCLK', 'SMBUSz/SS_SUSPEND', 'FULLPWRMGMTz/SMBA1/SS_UP', 'PWRCTL_POL',
                      'GANGED/SMBA2/HS_UP', 'AUTOENz/HS_SUSPEND'):
            s.nc(p)
        elif p.name == 'TEST':
            s.power(p, 'GND')
        elif p.name == 'GRSTz':
            s.label(p, 'GRSTz')
        elif p.name == 'USB_R1':
            s.label(p, 'USB_R1')
        elif p.name == 'USB_VBUS':
            s.label(p, 'USB_VBUS')
        elif p.name in ('XI', 'XO'):
            s.label(p, p.name)
        elif p.name == 'VDD':
            s.label(p, 'VDD_HUB')
        elif p.name == 'VDD33':
            s.power(p, '+3V3')
        elif p.name == 'VSS':
            s.power(p, 'GND')
    # straps / clock / reset
    heading(s, 150, 215, 'Reset, reference, VBUS sense, over-current pull-ups')
    vR(s, 162.56, 236.22, '10k', 'pwr:+3V3', 'net:GRSTz')
    vC(s, 175.26, 236.22, '10uF', 'net:GRSTz', 'pwr:GND', size='0805')
    testpoint(s, 185.42, 226.06, 'GRSTz')
    vR(s, 198.12, 236.22, '9.53k', 'net:USB_R1', 'pwr:GND')
    vR(s, 213.36, 236.22, '90.9k', 'pwr:VBUS', 'net:USB_VBUS')
    vR(s, 213.36, 256.54, '10k', 'net:USB_VBUS', 'pwr:GND')
    x = 231.14
    for n in (1, 2, 3):
        vR(s, x, 236.22, '10k', 'pwr:+3V3', f'net:DS{n}_OVERCUR_N')
        x += 12.7
    heading(s, 275, 215, '24 MHz crystal')
    yc = s.place('Crystal_24MHz_3225', 'Y', 297.18, 241.3, 0, refnum=1)
    s.label(yc.pin('1'), 'XI')
    s.label(yc.pin('3'), 'XO')
    s.power(yc.pin('2'), 'GND')
    s.power(yc.pin('4'), 'GND')
    vC(s, 322.58, 241.3, '30pF', 'net:XI', 'pwr:GND')
    vC(s, 335.28, 241.3, '30pF', 'net:XO', 'pwr:GND')
    hR(s, 330.2, 226.06, '1M', 'net:XI', 'net:XO')
    # +1V1_HUB regulator
    heading(s, 330, 55, '+1V1_HUB core: TLV62569, ferrite to VDD_HUB')
    u2 = s.place('TLV62569DBVR', 'U', 342.9, 86.36, 0, refnum=2)
    s.power(u2.pin('EN'), '+5V_USB')
    s.power(u2.pin('GND'), 'GND')
    s.label(u2.pin('SW'), 'SW_1V1')
    s.power(u2.pin('VIN'), '+5V_USB')
    s.label(u2.pin('FB'), 'FB_1V1')
    L2 = s.place('SMNR4020-2.2UH', 'L', 375.92, 99.06, 0, value='2.2uH 3.4A', refnum=1)
    s.label(L2.pin('1'), 'SW_1V1')
    s.power(L2.pin('2'), '+1V1_HUB')
    vR(s, 332.74, 121.92, '82k', 'pwr:+1V1_HUB', 'net:FB_1V1')
    vC(s, 345.44, 121.92, '6.8pF', 'pwr:+1V1_HUB', 'net:FB_1V1')
    vR(s, 332.74, 142.24, '100k', 'net:FB_1V1', 'pwr:GND')
    decap(s, 360.68, 121.92, '+5V_USB', '4.7uF', size='0805')
    decap(s, 375.92, 121.92, '+1V1_HUB', '22uF', size='0805')
    s.flag_rail(337.82, 66.04, '+1V1_HUB')
    hpart(s, 'FB_0603', 'FB', 358.14, 160.02, 'pwr:+1V1_HUB', 'net:VDD_HUB', value=FB0603[0], lcsc=FB0603[1])
    s.flag((378.46, 160.02))
    s.wire((378.46, 160.02), (378.46, 162.56))
    s.label_xy('VDD_HUB', 378.46, 162.56, 270)
    testpoint(s, 396.24, 157.48, 'VDD_HUB')
    heading(s, 330, 180, 'VDD_HUB (1.1 V core) and VDD33 decoupling')
    x = 335.28
    for i in range(8):
        vC(s, x, 198.12, '100nF', 'net:VDD_HUB', 'pwr:GND')
        x += 7.62
    vC(s, x, 198.12, '10uF', 'net:VDD_HUB', 'pwr:GND', size='0805')
    x = 335.28
    for i in range(4):
        decap(s, x, 226.06, '+3V3')
        x += 7.62
    decap(s, x, 226.06, '+3V3', '10uF', size='0805')
    classed(s, 'SW_1V1', 'SW_NODE', 335.28, 256.54)
    return s


HIER_PORT = [('SSTX_P', 'input', 'USB3_SS'), ('SSTX_N', 'input', 'USB3_SS'), ('SSRX_P', 'output', 'USB3_SS'),
             ('SSRX_N', 'output', 'USB3_SS'), ('DP', 'bidirectional', 'USB2_HS'), ('DM', 'bidirectional', 'USB2_HS'),
             ('PWRCTL', 'input', None), ('OVERCUR_N', 'output', None)]


def sheet_port(lib):
    s = new_sheet(lib, 'usb-port', 'A3', 'Generic USB-A 3.0 downstream port (one sheet, three instances)',
                  'TUSB8041 EVM downstream port · TPS2553 datasheet · slvaf82b ESD placement', ['usb-port-1', 'usb-port-2', 'usb-port-3'])
    note(s, 12.7, 12.7,
         "USB PORT — one sheet, instantiated 3× as usb-port-1..3 (hub DS1..DS3). Any device fits any port; identical 1.5 A limit on every port.\n"
         "Switch: TPS2553DBVR (replaces the SY6280 of the first draft: SY6280 has no fault output, so the hub's OVERCURxz could never see an over-current;\n"
         "TPS2553 FAULT is open-drain → OVERCUR_N, EN active high from PWRCTL). ILIM 16.9 k → 1.51 A nominal (IOS = 23950 / RILIM^0.977 mA).\n"
         "VBUS_OUT: 47 µF low-ESR bulk at the switch, 220 Ω@100 MHz 2 A ferrite, 100 nF at the connector (TUSB8041 datasheet §10.2). Net class PWR_USB by pattern /usb-port-*/VBUS_*.\n"
         "Signals: hub SSTX (hub transmits) → 100 nF AC caps at the connector → StdA_SSTX pins; StdA_SSRX pins → SSRX (hub receives). TPD4E05U06 on both SS pairs, USBLC6-2 on D+/D-.\n"
         "Shell → SHIELD → 1 MΩ || 1 nF 2 kV to GND. Everything per instance is identical (values, DNP and footprints are shared between instances).\n"
         "Consumes: +5V_USB, +3V3, GND.")
    y = 71.12
    for name, shape, nc in HIER_PORT:
        s.hier(name, shape, 30.48, y, nc)
        y += 5.08
    heading(s, 85, 55, 'VBUS switch (TPS2553, 1.5 A, fault → hub)')
    u = s.place('TPS2553DBVR', 'U', 114.3, 101.6, 0, refnum=1)
    s.power(u.pin('IN'), '+5V_USB')
    s.power(u.pin('GND'), 'GND')
    s.label(u.pin('EN'), 'PWRCTL')
    s.label(u.pin('OUT'), 'VBUS_OUT')
    s.label(u.pin('ILIM'), 'ILIM')
    s.label(u.pin('/FAULT'), 'OVERCUR_N')
    vR(s, 139.7, 127, '16.9k', 'net:ILIM', 'pwr:GND')
    vR(s, 154.94, 127, '10k', 'pwr:+3V3', 'net:OVERCUR_N')
    decap(s, 86.36, 127, '+5V_USB')
    decap(s, 99.06, 127, '+5V_USB', '10uF', size='0805')
    vC(s, 170.18, 127, '47uF 10V', 'net:VBUS_OUT', 'pwr:GND', size='1206')
    hpart(s, 'FB_0805', 'FB', 190.5, 99.06, 'net:VBUS_OUT', 'net:VBUS_J', value=FB0805[0], lcsc=FB0805[1])
    vC(s, 198.12, 127, '100nF', 'net:VBUS_J', 'pwr:GND')
    heading(s, 85, 150, 'ESD, AC coupling, receptacle')
    hC(s, 101.6, 167.64, '100nF', 'net:SSTX_P', 'net:SSTX_P_J', size='0402')
    hC(s, 101.6, 175.26, '100nF', 'net:SSTX_N', 'net:SSTX_N_J', size='0402')
    d2 = s.place('TPD4E05U06DQAR_C138714', 'D', 147.32, 172.72, 0, value='TPD4E05U06', refnum=2)
    s.label(d2.pin('D1+'), 'SSTX_P_J')
    s.label(d2.pin('D1-'), 'SSTX_N_J')
    s.label(d2.pin('D2+'), 'SSRX_P')
    s.label(d2.pin('D2-'), 'SSRX_N')
    for p in d2.pins_named('GND'):
        s.power(p, 'GND')
    d1 = s.place('USBLC6-2SC6_C2687116', 'D', 147.32, 203.2, 0, value='USBLC6-2SC6', refnum=1)
    s.label(d1.pin('1'), 'DP_J')
    s.label(d1.pin('6'), 'DP')
    s.label(d1.pin('3'), 'DM_J')
    s.label(d1.pin('4'), 'DM')
    s.label(d1.pin('5'), 'VBUS_J')
    s.power(d1.pin('2'), 'GND')
    j = s.place('HC-ST-003-01-J', 'J', 254.0, 180.34, 0, value='USB-A 3.0 receptacle', refnum=1)
    s.label(j.pin('1'), 'VBUS_J')
    s.label(j.pin('2'), 'DM_J')
    s.label(j.pin('3'), 'DP_J')
    s.power(j.pin('4'), 'GND')
    s.label(j.pin('5'), 'SSRX_N')
    s.label(j.pin('6'), 'SSRX_P')
    s.power(j.pin('7'), 'GND')
    s.label(j.pin('8'), 'SSTX_N_J')
    s.label(j.pin('9'), 'SSTX_P_J')
    s.label(j.pin('10'), 'SHIELD')
    s.label(j.pin('11'), 'SHIELD')
    vR(s, 299.72, 180.34, '1M', 'net:SHIELD', 'pwr:GND')
    vC(s, 312.42, 180.34, '1nF 2kV', 'net:SHIELD', 'pwr:GND', size='1206')
    heading(s, 240, 55, 'Net-class directives for the sheet-local nets')
    y = 71.12
    for name, nc in [('SSTX_P_J', 'USB3_SS'), ('SSTX_N_J', 'USB3_SS'), ('DP_J', 'USB2_HS'), ('DM_J', 'USB2_HS')]:
        classed(s, name, nc, 254.0, y)
        y += 5.08
    return s
