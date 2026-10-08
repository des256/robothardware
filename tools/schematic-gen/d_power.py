"""Sheets 2-5: input protection, the two LM5145 servo bucks, the TPS54560 + TLV62569 USB/3V3 bucks."""
from common import *  # noqa: F401,F403
from common import R, C, vR, vC, hR, hC, decap, vdiode, tvs, rail_led, testpoint, testpoint_pwr, vpart, hpart, end, note, heading, new_sheet, top_bottom, left_right, R0603, C0603, C0805, C1206, TVS_SMB


def sheet_input(lib):
    s = new_sheet(lib, 'input', 'A4', '19 V input protection and Jetson pass-through',
                  'HARDWARE.md §3 input protection · FUNCTIONAL.md §4 +19V_IN / +19V_JETSON', ['input'])
    note(s, 12.7, 12.7,
         "INPUT — 19 V adapter in (J201 XT30PW-M), 15 A time-lag fuse, reverse-polarity ideal diode (LM74700-Q1 + CSD18532Q5B),\n"
         "SMBJ24A surge clamp, 2 × 470 µF/35 V low-ESR bulk, 19 V pass-through to the Jetson carrier (J202) through a 4 A fuse.\n"
         "Golden reference: datasheets/lm74700-q1.pdf (C_VCAP 0.1 µF across VCAP-ANODE, EN tied to ANODE = always on),\n"
         "datasheets/reference/ti-slvae57b-basics-of-ideal-diodes.pdf. TVS clamps near 39 V, hence 60 V FETs and 100 V input caps on every buck.\n"
         "Open item D6: Jetson carrier input range / connector (XT30 kept; DC-005-A200 barrel is the imported alternate).")
    heading(s, 20, 45, 'Adapter input, fuse, ideal diode')
    # J201 adapter input (rot 90 -> + and - exit to the left)
    j1 = s.place('XT30PW-M', 'J', 40.64, 76.2, 90, refnum=1)
    s.label(j1.pin('+'), 'VIN_RAW')
    s.power(j1.pin('-'), 'GND')
    s.power(j1.pin('3'), 'GND')
    s.power(j1.pin('4'), 'GND')
    # F201 15 A time-lag, VIN_RAW -> VIN_F
    hpart(s, '0453015.MR', 'F', 63.5, 63.5, 'net:VIN_RAW', 'net:VIN_F', value='15A T 2410', refnum=1)
    # PWR_FLAG on the fused input (the adapter is the source)
    s.flag((76.2, 50.8))
    s.wire((76.2, 50.8), (76.2, 53.34))
    s.label_xy('VIN_F', 76.2, 53.34, 270)
    # D201 SMBJ24A clamp
    vdiode(s, 'TVS_SMB', 76.2, 96.52, 'net:VIN_F', 'pwr:GND', value='SMBJ24A', lcsc=TVS_SMB['SMBJ24A'], refnum=1)
    # U201 LM74700-Q1
    u = s.place('LM74700QDBVRQ1', 'U', 114.3, 76.2, 0, refnum=1)
    s.label(u.pin('VCAP'), 'VCAP')
    s.power(u.pin('GND'), 'GND')
    s.label(u.pin('EN'), 'VIN_F')
    s.label(u.pin('ANODE'), 'VIN_F')
    s.label(u.pin('GATE'), 'GATE')
    s.power(u.pin('CATHODE'), '+19V_IN')
    vC(s, 91.44, 96.52, '100nF', 'net:VCAP', 'net:VIN_F', refnum=1)
    # Q201 ideal-diode FET: source = VIN_F (anode side), drain = +19V_IN (cathode side)
    q = s.place('CSD18532Q5B', 'Q', 152.4, 76.2, 0, refnum=1)
    s.chain(*q.pins_named('S'), net='VIN_F')
    s.label(q.pin('G'), 'GATE')
    s.chain_pwr(q.pins_named('D') + [q.pin('EP')], '+19V_IN')
    # +19V_IN bulk + flag + bring-up
    heading(s, 175, 45, '+19V_IN bulk, flag, bring-up')
    s.flag_rail(177.8, 55.88, '+19V_IN')
    vpart(s, 'RVE470UF35V167RV084', 'C', 182.88, 101.6, 'pwr:+19V_IN', 'pwr:GND', value='470uF 35V')
    vpart(s, 'RVE470UF35V167RV084', 'C', 195.58, 101.6, 'pwr:+19V_IN', 'pwr:GND', value='470uF 35V')
    decap(s, 208.28, 101.6, '+19V_IN', '10uF 50V', size='1206')
    decap(s, 220.98, 101.6, '+19V_IN', '100nF 100V', size='0805')
    rail_led(s, 236.22, 96.52, '+19V_IN', '10k')
    testpoint_pwr(s, 251.46, 101.6, '+19V_IN')
    # Jetson pass-through
    heading(s, 20, 135, 'Jetson 19 V pass-through (J202, 4 A fuse)')
    hpart(s, '1206TD-4A', 'F', 63.5, 152.4, 'pwr:+19V_IN', 'pwr:+19V_JETSON', value='4A T 1206', refnum=2)
    s.flag_rail(88.9, 139.7, '+19V_JETSON')
    decap(s, 101.6, 165.1, '+19V_JETSON', '10uF 50V', size='1206')
    j2 = s.place('XT30PW-M', 'J', 127, 152.4, 270, refnum=2)
    s.power(j2.pin('+'), '+19V_JETSON')
    s.power(j2.pin('-'), 'GND')
    s.power(j2.pin('3'), 'GND')
    s.power(j2.pin('4'), 'GND')
    testpoint_pwr(s, 152.4, 165.1, '+19V_JETSON')
    # GND flag
    s.power_at('GND', (177.8, 165.1))
    s.wire((177.8, 165.1), (182.88, 165.1))
    s.flag((182.88, 165.1))
    return s


def lm5145_sheet(lib, name, title, rail, p):
    """Generic LM5145 synchronous buck sheet (TI LM5145 datasheet application circuits 1 and 2)."""
    s = new_sheet(lib, name, 'A3', title, 'TI LM5145 datasheet §9.2 + LM5145EVM-HD-20A (snvu545)', [name])
    note(s, 12.7, 12.7, p['note'])
    # ---------------- controller
    heading(s, 100, 55, 'LM5145 controller')
    u = s.place('LM5145RGYR', 'U', 127, 101.6, 0, refnum=1)
    s.label(u.pin('EN/UVLO'), 'UVLO')
    s.label(u.pin('RT'), 'RT')
    s.label(u.pin('SS/TRK'), 'SS')
    s.label(u.pin('COMP'), 'COMP')
    s.label(u.pin('FB'), 'FB')
    s.power(u.pin('AGND'), 'GND')
    s.nc(u.pin('SYNCOUT'))
    s.label(u.pin('SYNCIN'), 'SYNCIN')
    s.label(u.pin('PGOOD'), 'PGOOD')
    s.label(u.pin('ILIM'), 'ILIM')
    s.power(u.pin('PGND'), 'GND')
    s.label(u.pin('LO'), 'LO')
    s.label(u.pin('VCC'), 'VCC')
    for ep in u.pins_named('EP'):
        s.power(ep, 'GND')
    s.label(u.pin('BST'), 'BOOT')
    s.label(u.pin('HO'), 'HO')
    s.label(u.pin('SW'), 'SW')
    s.power(u.pin('VIN'), '+19V_IN')
    # ---------------- controller passives
    heading(s, 20, 140, 'UVLO, frequency, soft-start, compensation (type III)')
    vR(s, 30.48, 154.94, p['RUV1'], 'pwr:+19V_IN', 'net:UVLO')
    vR(s, 30.48, 175.26, p['RUV2'], 'net:UVLO', 'pwr:GND')
    vR(s, 45.72, 154.94, p['RRT'], 'net:RT', 'pwr:GND')
    vC(s, 60.96, 154.94, p['CSS'], 'net:SS', 'pwr:GND')
    rc1 = hR(s, 83.82, 154.94, p['RC1'], 'net:COMP', None)
    cc1 = hC(s, 99.06, 154.94, p['CC1'], None, 'net:FB')
    s.connect(left_right(rc1)[1], left_right(cc1)[0])
    hC(s, 91.44, 167.64, p['CC2'], 'net:COMP', 'net:FB')
    vR(s, 121.92, 154.94, p['RFB1'], 'pwr:' + rail, 'net:FB')
    vR(s, 121.92, 175.26, p['RFB2'], 'net:FB', 'pwr:GND')
    rc2 = vR(s, 134.62, 154.94, p['RC2'], 'pwr:' + rail, None)
    cc3 = vC(s, 134.62, 175.26, p['CC3'], None, 'net:FB')
    s.connect(top_bottom(rc2)[1], top_bottom(cc3)[0])
    heading(s, 150, 140, 'VCC, bootstrap, current limit, PGOOD, SYNCIN mode')
    vC(s, 162.56, 154.94, p['CVCC'], 'net:VCC', 'pwr:GND')
    if p.get('vcc_diode'):
        vdiode(s, 'SS14', 175.26, 154.94, 'net:VCC', 'pwr:' + rail)
    rb = hR(s, 167.64, 177.8, '2.2', 'net:BOOT', None)
    cb = hC(s, 182.88, 177.8, '100nF', None, 'net:SW')
    s.connect(left_right(rb)[1], left_right(cb)[0])
    vC(s, 193.04, 154.94, '100nF 100V', 'pwr:+19V_IN', 'pwr:GND', size='0805')
    hR(s, 175.26, 193.04, p['RILIM'], 'net:ILIM', 'net:SW')
    vC(s, 162.56, 193.04, p['CILIM'], 'net:ILIM', 'pwr:GND')
    vR(s, 208.28, 154.94, '20k', 'net:VCC', 'net:PGOOD')
    testpoint(s, 220.98, 160.02, 'PGOOD')
    jp = s.place('SolderJumper_3_Bridged12', 'JP', 220.98, 190.5, 0, value='SYNCIN: 1-2 GND=DEM, 2-3 VCC=FPWM', nobom=True, lcsc='n/a', refnum=1)
    s.power(jp.pin('A'), 'GND')
    s.label(jp.pin('C'), 'SYNCIN')
    s.label(jp.pin('B'), 'VCC')
    # ---------------- power stage
    heading(s, 250, 55, 'Power stage: Q1 high side, Q2 low side, inductor, output bank')
    q1 = s.place('CSD18532Q5B', 'Q', 266.7, 76.2, 0, refnum=1)
    s.label(q1.pin('G'), 'HO')
    s.chain(*q1.pins_named('S'), net='SW')
    s.chain_pwr(q1.pins_named('D') + [q1.pin('EP')], '+19V_IN')
    q2 = s.place('CSD18532Q5B', 'Q', 266.7, 116.84, 0, refnum=2)
    s.label(q2.pin('G'), 'LO')
    s.chain_pwr(q2.pins_named('S'), 'GND')
    s.chain(*q2.pins_named('D'), q2.pin('EP'), net='SW')
    L = s.place(p['L'], 'L', 320.04, 76.2, 0, value=p['Lvalue'], refnum=1)
    s.label(L.pin('1'), 'SW')
    s.power(L.pin('2'), rail)
    # input ceramics (100 V) along the top
    heading(s, 250, 25, 'CIN: 100 V ceramics (plus the bulk bank on the input sheet)')
    x = 254.0
    for i in range(p['CIN_n']):
        vpart(s, p['CIN'], 'C', x, 40.64, 'pwr:+19V_IN', 'pwr:GND', value=p['CINvalue'])
        x += 12.7
    # output capacitors
    heading(s, 250, 142, 'COUT: ceramics + polymer bulk bank (shared by all four ports)')
    x = 254.0
    for sym, val in p['COUT']:
        vpart(s, sym, 'C', x, 160.02, 'pwr:' + rail, 'pwr:GND', value=val)
        x += 12.7
    s.flag_rail(320.04, 101.6, rail)
    rail_led(s, 345.44, 101.6, rail, p['LEDr'])
    testpoint_pwr(s, 365.76, 106.68, rail)
    # optional snubber (DNP)
    heading(s, 250, 185, 'Optional SW-node RC snubber (DNP until the SW ringing is measured)')
    rs = vR(s, 266.7, 198.12, '2.2', 'net:SW', None, dnp=True)
    cs = vC(s, 266.7, 218.44, '100pF', None, 'pwr:GND', dnp=True)
    s.connect(top_bottom(rs)[1], top_bottom(cs)[0])
    return s


P12 = dict(
    note=("BUCK A — +12V_SERVO, 15 A continuous, 400 kHz. Copy of TI LM5145 datasheet Application Circuit 2 (12 V/10 A, 14.4-48 V in) with the\n"
          "power stage uprated: Q1/Q2 CSD18532Q5B (60 V, 2.5 mΩ), 4.7 µH 25 A inductor, 5 × 4.7 µF/100 V in, 4 × 47 µF + 2 × 22 µF + 2 × 470 µF polymer out.\n"
          "RILIM 240 Ω with 2.5 mΩ RDS(on) sets the valley current limit near 19 A (ILIM sources 200 µA in RDS(on) mode); CILIM to PGND, τ ≈ 6 ns.\n"
          "UVLO 82 k / 7.5 k: on at 14.3 V, off at 13.5 V. SYNCIN jumper: 1-2 = GND = diode emulation (default, cannot sink regen), 2-3 = VCC = FPWM.\n"
          "Net names SW and BOOT carry the SW_NODE net class by project pattern /buck-*/SW* and /buck-*/BOOT*.\n"
          "Open items: D1 (fleet → current), V3 (regen overvoltage behaviour: with DEM the SMBJ13A per port and the polymer bank absorb it)."),
    RUV1='82k', RUV2='7.5k', RRT='24.9k', CSS='33nF', RC1='15k', CC1='3.3nF', CC2='47pF', RFB1='33.2k', RFB2='2.37k',
    RC2='100', CC3='680pF', CVCC='2.2uF', RILIM='240', CILIM='10pF', vcc_diode=True,
    L='TMPA1265SP-4R7MN-D', Lvalue='4.7uH 20A', CIN='C3225X7S2A475KT000N', CINvalue='4.7uF 100V', CIN_n=5,
    COUT=[('GRM32ER61C476KE15L', '47uF 16V')] * 4 + [('CS3225X7R226K250NRL', '22uF 25V')] * 2 + [('MA25V470M8X10', '470uF 25V')] * 2,
    LEDr='4.7k',
)
P5 = dict(
    note=("BUCK B — +5V_SERVO, 10 A continuous, 200 kHz. Copy of TI LM5145 datasheet Application Circuit 1 (5 V/20 A) and the LM5145EVM-HD-20A:\n"
          "same controller passives, Q1/Q2 CSD18532Q5B, 3.3 µH 30 A inductor, 5 × 2.2 µF/100 V in, 6 × 47 µF/10 V + 470 µF/10 V polymer out.\n"
          "RILIM 150 Ω with 2.5 mΩ RDS(on) → valley current limit near 12 A. Separate sheet on purpose: values differ and D1 option (b) deletes this rail.\n"
          "NEVER merged with +5V_USB (HARDWARE.md §5). SYNCIN jumper as on Buck A. Net names SW / BOOT → SW_NODE class.\n"
          "Open items: D1, V3."),
    RUV1='82k', RUV2='7.5k', RRT='49.9k', CSS='47nF', RC1='11k', CC1='4.7nF', CC2='150pF', RFB1='23.2k', RFB2='4.42k',
    RC2='1k', CC3='1.8nF', CVCC='2.2uF', RILIM='150', CILIM='15pF', vcc_diode=False,
    L='TMPC1265HP-3R3MG-D', Lvalue='3.3uH 18A', CIN='C3225X7R2A225KT5L0U', CINvalue='2.2uF 100V', CIN_n=5,
    COUT=[('C_1206', '47uF 10V')] * 6 + [('MA10V470M6X8', '470uF 10V')],
    LEDr='1k',
)


def sheet_buck12(lib):
    return lm5145_sheet(lib, 'buck-12v-servo', 'Buck A: +12V_SERVO (LM5145 + external FETs)', '+12V_SERVO', P12)


def sheet_buck5(lib):
    # C_1206 generic symbol needs the LCSC per instance
    p = dict(P5)
    s = lm5145_sheet(lib, 'buck-5v-servo', 'Buck B: +5V_SERVO (LM5145, 5 V feedback divider)', '+5V_SERVO', p)
    for inst in s.insts:
        if inst.symname == 'C_1206' and inst.value == '47uF 10V':
            inst.lcsc = C1206['47uF 10V']
    return s


def sheet_buck_usb(lib):
    s = new_sheet(lib, 'buck-5v-usb', 'A3', 'Buck C: +5V_USB (TPS54560) and +3V3 (TLV62569)',
                  'TI TPS54560 datasheet Figure 33 (5 V design example) · TLV62569 datasheet §8.2', ['buck-5v-usb'])
    note(s, 12.7, 12.7,
         "BUCK C — +5V_USB (TPS54560, 5 A, 400 kHz) exactly as the TPS54560 datasheet 5 V design example / TPS54560EVM-515:\n"
         "EN divider 442 k / 90.9 k (UVLO ≈ 7 V on), RT 243 k, comp 16.9 k + 4.7 nF, 47 pF, FB 53.6 k / 10.2 k, 7.2 µH 6 A, B560C catch diode, 3 × 47 µF/16 V out.\n"
         "+3V3 — TLV62569 from the quiet +5V_USB rail (never the servo rails): 2.2 µH, 4.7 µF in, 22 µF out, FB 453 k / 100 k + 6.8 pF → 3.32 V.\n"
         "Feeds: 3 × 1.5 A USB-A ports + HD3SS3220 VDD5 + the +3V3 and +1V1_HUB regulators. Net names SW / SW_3V3 / BOOT → SW_NODE class.\n"
         "Bring-up: test points + LEDs on both rails.")
    heading(s, 20, 50, 'TPS54560: +19V_IN → +5V_USB')
    u = s.place('TPS54560DDAR', 'U', 76.2, 88.9, 0, refnum=1)
    s.label(u.pin('BOOT'), 'BOOT')
    s.power(u.pin('VIN'), '+19V_IN')
    s.label(u.pin('EN'), 'EN')
    s.label(u.pin('RT/CLK'), 'RT')
    s.label(u.pin('SW'), 'SW')
    s.power(u.pin('GND'), 'GND')
    s.label(u.pin('COMP'), 'COMP')
    s.label(u.pin('FB'), 'FB')
    s.power(u.pin('EP'), 'GND')
    vR(s, 30.48, 129.54, '442k', 'pwr:+19V_IN', 'net:EN')
    vR(s, 30.48, 149.86, '90.9k', 'net:EN', 'pwr:GND')
    vR(s, 45.72, 129.54, '243k', 'net:RT', 'pwr:GND')
    r4 = vR(s, 60.96, 129.54, '16.9k', 'net:COMP', None)
    c5 = vC(s, 60.96, 149.86, '4.7nF', None, 'pwr:GND')
    s.connect(top_bottom(r4)[1], top_bottom(c5)[0])
    vC(s, 76.2, 129.54, '47pF', 'net:COMP', 'pwr:GND')
    vR(s, 91.44, 129.54, '53.6k', 'pwr:+5V_USB', 'net:FB')
    vR(s, 91.44, 149.86, '10.2k', 'net:FB', 'pwr:GND')
    hC(s, 114.3, 71.12, '100nF', 'net:BOOT', 'net:SW')
    x = 20.32
    for i in range(4):
        vpart(s, 'C3225X7R2A225KT5L0U', 'C', x, 175.26, 'pwr:+19V_IN', 'pwr:GND', value='2.2uF 100V')
        x += 12.7
    L = s.place('7447798720', 'L', 134.62, 88.9, 0, value='7.2uH 6A', refnum=1)
    s.label(L.pin('1'), 'SW')
    s.power(L.pin('2'), '+5V_USB')
    vpart(s, 'B560C-13-F', 'D', 114.3, 106.68, 'net:SW', 'pwr:GND', value='B560C', refnum=1)
    x = 154.94
    for i in range(3):
        vpart(s, 'GRM32ER61C476KE15L', 'C', x, 106.68, 'pwr:+5V_USB', 'pwr:GND', value='47uF 16V')
        x += 12.7
    s.flag_rail(154.94, 71.12, '+5V_USB')
    rail_led(s, 200.66, 101.6, '+5V_USB', '1k')
    testpoint_pwr(s, 215.9, 106.68, '+5V_USB')
    # ---- 3V3
    heading(s, 250, 50, 'TLV62569: +5V_USB → +3V3')
    u2 = s.place('TLV62569DBVR', 'U', 292.1, 88.9, 0, refnum=2)
    s.power(u2.pin('EN'), '+5V_USB')
    s.power(u2.pin('GND'), 'GND')
    s.label(u2.pin('SW'), 'SW_3V3')
    s.power(u2.pin('VIN'), '+5V_USB')
    s.label(u2.pin('FB'), 'FB_3V3')
    L2 = s.place('SMNR4020-2.2UH', 'L', 330.2, 101.6, 0, value='2.2uH 3.4A', refnum=2)
    s.label(L2.pin('1'), 'SW_3V3')
    s.power(L2.pin('2'), '+3V3')
    vR(s, 355.6, 129.54, '453k', 'pwr:+3V3', 'net:FB_3V3')
    vC(s, 368.3, 129.54, '6.8pF', 'pwr:+3V3', 'net:FB_3V3')
    vR(s, 355.6, 149.86, '100k', 'net:FB_3V3', 'pwr:GND')
    decap(s, 259.08, 129.54, '+5V_USB', '4.7uF', size='0805')
    decap(s, 274.32, 129.54, '+3V3', '22uF', size='0805')
    s.flag_rail(330.2, 71.12, '+3V3')
    rail_led(s, 358.14, 71.12, '+3V3', '1k')
    testpoint_pwr(s, 375.92, 76.2, '+3V3')
    return s
