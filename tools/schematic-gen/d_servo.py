"""Sheets 11-15: CH344Q quad UART and the dual-mode servo port (x4)."""
from common import *  # noqa: F401,F403
from common import vR, vC, hR, hC, decap, vdiode, tvs, testpoint, testpoint_pwr, vpart, hpart, end, note, heading, new_sheet, top_bottom, left_right, R0603, C0603, C0805, TVS_SMB
from d_usb import classed


HIER_UART = [('DS4_DP', 'bidirectional', 'USB2_HS'), ('DS4_DM', 'bidirectional', 'USB2_HS')]
for _n in range(4):
    HIER_UART += [(f'UART{_n}_TXD', 'output', None), (f'UART{_n}_RXD', 'input', None), (f'UART{_n}_TNOW', 'output', None)]


def sheet_uart(lib):
    s = new_sheet(lib, 'servo-uart', 'A3', 'Servo UART bridge: CH344Q quad UART on hub port DS4',
                  'WCH CH344DS1 (datasheets/ch344.pdf) · FUNCTIONAL.md §5.2 TNOW', ['servo-uart'])
    note(s, 12.7, 12.7,
         "SERVO UART — CH344Q on hub port DS4 (USB 2.0 HS, UD+/UD- straight from the ESD array, no series resistors per WCH), four UARTs → servo-port-0..3.\n"
         "UART index ↔ physical port index is fixed by copper (software contract). 8 MHz ±0.4‰ crystal with 33 pF (20 pF CL), 100 nF on every VCC pin, TEST = GND.\n"
         "TNOW: a 4.7 k pull-down on each DTRx/TNOWx pin at power-up selects the TNOW function (CH344Q) and keeps the line low = receive when idle (ROBOTIS TX_Enable idle).\n"
         "RXD pull-ups live on the servo-port sheet next to the receivers (one 10 k per port; RXD3 has no internal pull-up). RESET: 10 k up + 100 nF, test point.\n"
         "ACT (USB configured, active low) drives the green LED. Unused modem / GPIO pins left open (RTS0 and RTS3 must NOT be pulled down: they change pin functions).\n"
         "Open items: V1 (TNOW polarity — scope the dongle), V2 (TNOW release latency vs Return Delay Time). Test points on every TXD / RXD / TNOW.")
    y = 71.12
    for name, shape, nc in HIER_UART:
        s.hier(name, shape, 30.48, y, nc)
        y += 5.08
    u = s.place('CH344Q_C2988084', 'U', 190.5, 127, 0, value='CH344Q', refnum=1, fields={'max_mA': 30})
    import re
    for p in u.pins:
        n = p.name
        if n == 'VCC':
            s.power(p, '+3V3')
        elif n == 'GND':
            s.power(p, 'GND')
        elif re.match(r'^TXD(\d)$', n):
            s.label(p, f'UART{n[3]}_TXD')
        elif re.match(r'^RXD(\d)$', n):
            s.label(p, f'UART{n[3]}_RXD')
        elif n.startswith('TNOW'):
            s.label(p, f'UART{n[4]}_TNOW')
        elif n == 'UD+':
            s.label(p, 'UDP')
        elif n == 'UD-':
            s.label(p, 'UDM')
        elif n in ('XI', 'XO'):
            s.label(p, n)
        elif n == 'RESET':
            s.label(p, 'RESET')
        elif n == 'TEST':
            s.power(p, 'GND')
        elif n == 'ACT':
            s.label(p, 'ACT')
        elif p.type != 'no_connect':
            s.nc(p)
    heading(s, 85, 175, 'Crystal, reset, TNOW strap pull-downs, ACT LED')
    yc = hpart(s, 'Crystal_8MHz_5032', 'Y', 99.06, 193.04, 'net:XI', 'net:XO', refnum=1)
    vC(s, 86.36, 210.82, '33pF', 'net:XI', 'pwr:GND')
    vC(s, 111.76, 210.82, '33pF', 'net:XO', 'pwr:GND')
    vR(s, 127, 193.04, '10k', 'pwr:+3V3', 'net:RESET')
    vC(s, 139.7, 193.04, '100nF', 'net:RESET', 'pwr:GND')
    testpoint(s, 149.86, 185.42, 'RESET')
    x = 162.56
    for n in range(4):
        vR(s, x, 193.04, '4.7k', f'net:UART{n}_TNOW', 'pwr:GND')
        x += 12.7
    r = vR(s, 220.98, 185.42, '1k', 'pwr:+3V3', None)
    d = s.place('LED_0805_Green', 'D', 220.98, 203.2, 0, value='LED ACT', refnum=1)
    s.connect(top_bottom(r)[1], d.pin('2'))
    s.label(d.pin('1'), 'ACT')
    heading(s, 250, 55, 'USB 2.0 ESD (hub DS4 ↔ CH344 UD+/UD-)')
    d1 = s.place('USBLC6-2SC6_C2687116', 'D', 266.7, 76.2, 0, value='USBLC6-2SC6', refnum=2)
    s.label(d1.pin('6'), 'DS4_DP')
    s.label(d1.pin('1'), 'UDP')
    s.label(d1.pin('4'), 'DS4_DM')
    s.label(d1.pin('3'), 'UDM')
    s.power(d1.pin('5'), '+3V3')
    s.power(d1.pin('2'), 'GND')
    classed(s, 'UDP', 'USB2_HS', 254.0, 96.52)
    classed(s, 'UDM', 'USB2_HS', 254.0, 101.6)
    heading(s, 250, 115, 'Decoupling (one 100 nF per VCC pin + 10 µF)')
    x = 254.0
    for i in range(4):
        decap(s, x, 134.62, '+3V3')
        x += 7.62
    decap(s, x, 134.62, '+3V3', '10uF', size='0805')
    heading(s, 250, 160, 'Test points (bring-up)')
    x = 254.0
    for n in range(4):
        y = 177.8
        for sig in ('TXD', 'RXD', 'TNOW'):
            testpoint(s, x, y, f'UART{n}_{sig}')
            y += 15.24
        x += 25.4
    return s


def sheet_port(lib):
    s = new_sheet(lib, 'servo-port', 'A3', 'Dual-mode servo port: RS-485 or TTL front-end + port power',
                  'ROBOTIS recommended circuits (datasheets/reference/robotis) · TPS1663 / TPS25961 datasheets',
                  ['servo-port-0', 'servo-port-1', 'servo-port-2', 'servo-port-3'])
    note(s, 12.7, 12.7,
         "SERVO PORT — one sheet, instantiated 4× as servo-port-0..3 (UART0..3). Everything replicated per port lives here.\n"
         "Front-end = ROBOTIS's RS-485 and 3.3 V TTL circuits with TNOW as TX_Enable: SP3485EN (DI = TXD, DE = TNOW, RE# = TNOW only when RS-485 is selected) and\n"
         "SN74LVC2G241 (2A = TXD → 2Y = DATA, 2OE = TNOW, 1A = DATA → 1Y = RXD, 1OE# = TNOW only when TTL is selected). Both receivers are off while TNOW is high → no echo in either mode.\n"
         "Mode select JP1 (D2): centre = TNOW, 1-2 bridged (default) = RS-485 receiver enabled, 2-3 = TTL receiver enabled; the unselected enable is pulled high (100 k, weak against the 4.7 k TNOW pull-down).\n"
         "RXD: 10 k pull-up (both receiver outputs wire-OR onto RXD; only one is ever enabled). DATA: 10 k pull-up to +3V3, 22 Ω series, SMF5.0A. A/B: PSM712 array, 120 Ω termination as DNP option.\n"
         "Port power: +12V_SERVO → TPS16630 (ILIM 4.02 k = 4.5 A, dVdT 100 nF, UVLO 8.9 V / OVP 16.8 V, MODE jumper bridged = auto-retry, open = latch; SHDN pulled up, test point for a GPIO e-stop, D3)\n"
         "→ 470 µF/25 V polymer + 100 nF + SMBJ13A → J1 (B4B-EH-A: 1 GND, 2 VDD, 3 D+ = A, 4 D- = B).  +5V_SERVO → TPS25961 (ILIM 27 k ≈ 2 A, OVLO = GND fixed) → 470 µF/10 V + 100 nF + SMBJ6.0A → J2 (B3B-EH-A: 1 GND, 2 VDD, 3 DATA).\n"
         "Net names the project patterns key on: A, B (RS485), DATA (TTL_DATA), VDD_485 / VDD_TTL (PWR_SERVO). Per-instance differences are impossible (values and DNP are shared). Open items: D1, D2, D3, V1.")
    y = 71.12
    for name, shape in [('TXD', 'input'), ('RXD', 'output'), ('TNOW', 'input')]:
        s.hier(name, shape, 30.48, y)
        y += 5.08
    # ---------------- front-end
    heading(s, 60, 55, 'Front-end: RS-485 transceiver and TTL half-duplex buffer, mode select')
    u1 = s.place('SP3485EN', 'U', 114.3, 88.9, 0, refnum=1, fields={'max_mA': 35})
    s.label(u1.pin('RO'), 'RXD')
    s.label(u1.pin('RE#'), 'RE_485')
    s.label(u1.pin('DE'), 'TNOW')
    s.label(u1.pin('DI'), 'TXD')
    s.power(u1.pin('VCC'), '+3V3')
    s.label(u1.pin('B'), 'B')
    s.label(u1.pin('A'), 'A')
    s.power(u1.pin('GND'), 'GND')
    u2 = s.place('SN74LVC2G241DCU', 'U', 114.3, 127, 0, refnum=2, fields={'max_mA': 5})
    s.label(u2.pin('~{1OE}'), 'OE_TTL')
    s.label(u2.pin('1A'), 'DATA_BUF')
    s.label(u2.pin('2Y'), 'DATA_BUF')
    s.power(u2.pin('GND'), 'GND')
    s.power(u2.pin('VCC'), '+3V3')
    s.label(u2.pin('2OE'), 'TNOW')
    s.label(u2.pin('1Y'), 'RXD')
    s.label(u2.pin('2A'), 'TXD')
    jp = s.place('SolderJumper_3_Bridged12', 'JP', 63.5, 111.76, 0, value='MODE: 1-2 RS-485 (default), 2-3 TTL', nobom=True, lcsc='n/a', refnum=1)
    s.label(jp.pin('A'), 'RE_485')
    s.label(jp.pin('C'), 'TNOW')
    s.label(jp.pin('B'), 'OE_TTL')
    vR(s, 48.26, 139.7, '100k', 'pwr:+3V3', 'net:RE_485')
    vR(s, 78.74, 139.7, '100k', 'pwr:+3V3', 'net:OE_TTL')
    vR(s, 63.5, 139.7, '10k', 'pwr:+3V3', 'net:RXD')
    decap(s, 149.86, 88.9, '+3V3')
    decap(s, 149.86, 127, '+3V3')
    # RS-485 line side
    heading(s, 170, 55, 'RS-485 side (J1) and TTL side (J2)')
    dd = s.place('PSM712', 'D', 193.04, 83.82, 0, refnum=1)
    s.label(dd.pin('1'), 'A')
    s.label(dd.pin('2'), 'B')
    s.power(dd.pin('3'), 'GND')
    hR(s, 198.12, 101.6, '120', 'net:A', 'net:B', dnp=True)
    j1 = s.place('B4B-EH-A', 'J', 254.0, 88.9, 0, value='RS-485 JST EH 4p', refnum=1)
    s.power(j1.pin('1'), 'GND')
    s.label(j1.pin('2'), 'VDD_485')
    s.label(j1.pin('3'), 'A')
    s.label(j1.pin('4'), 'B')
    # TTL line side
    hR(s, 180.34, 127, '22', 'net:DATA_BUF', 'net:DATA')
    vR(s, 198.12, 142.24, '10k', 'pwr:+3V3', 'net:DATA')
    vdiode(s, 'SMF5.0A', 213.36, 142.24, 'net:DATA', 'pwr:GND', refnum=2)
    j2 = s.place('B3B-EH-A', 'J', 254.0, 127, 0, value='TTL JST EH 3p', refnum=2)
    s.power(j2.pin('1'), 'GND')
    s.label(j2.pin('2'), 'VDD_TTL')
    s.label(j2.pin('3'), 'DATA')
    # ---------------- 12 V port power
    heading(s, 60, 165, 'Port power, RS-485 side: +12V_SERVO → TPS16630 e-fuse → VDD_485')
    u3 = s.place('TPS16630PWPR', 'U', 114.3, 203.2, 0, refnum=3)
    s.chain_pwr(u3.pins_named('IN'), '+12V_SERVO')
    s.power(u3.pin('P_IN'), '+12V_SERVO')
    s.label(u3.pin('UVLO'), 'UVLO_485')
    s.label(u3.pin('OVP'), 'OVP_485')
    s.power(u3.pin('GND'), 'GND')
    s.label(u3.pin('dVdT'), 'DVDT_485')
    s.label(u3.pin('ILIM'), 'ILIM_485')
    s.label(u3.pin('MODE'), 'MODE_485')
    s.label(u3.pin('~{SHDN}'), 'SHDN_485')
    s.nc(u3.pin('IMON'), u3.pin('~{FLT}'), u3.pin('PGOOD'))
    s.chain(*u3.pins_named('OUT'), net='VDD_485')
    s.power(u3.pin('EP'), 'GND')
    vR(s, 33.02, 193.04, '249k', 'pwr:+12V_SERVO', 'net:OVP_485')
    vR(s, 33.02, 213.36, '18.2k', 'net:OVP_485', 'net:UVLO_485')
    vR(s, 33.02, 233.68, '20.5k', 'net:UVLO_485', 'pwr:GND')
    vC(s, 48.26, 233.68, '100nF', 'net:DVDT_485', 'pwr:GND')
    vR(s, 63.5, 233.68, '4.02k', 'net:ILIM_485', 'pwr:GND')
    jp2 = s.place('SolderJumper_2_Bridged', 'JP', 83.82, 243.84, 0, value='MODE: bridged = auto-retry, open = latch-off', nobom=True, lcsc='n/a', refnum=2)
    s.label(jp2.pin('A'), 'MODE_485')
    s.power(jp2.pin('B'), 'GND')
    vR(s, 162.56, 193.04, '100k', 'pwr:+12V_SERVO', 'net:SHDN_485')
    testpoint(s, 172.72, 185.42, 'SHDN_485')
    decap(s, 63.5, 193.04, '+12V_SERVO')
    vpart(s, 'MA25V470M8X10', 'C', 187.96, 233.68, 'net:VDD_485', 'pwr:GND', value='470uF 25V')
    vC(s, 203.2, 233.68, '100nF', 'net:VDD_485', 'pwr:GND')
    vdiode(s, 'TVS_SMB', 218.44, 233.68, 'net:VDD_485', 'pwr:GND', value='SMBJ13A', lcsc=TVS_SMB['SMBJ13A'], refnum=3)
    # ---------------- 5 V port power
    heading(s, 280, 165, 'Port power, TTL side: +5V_SERVO → TPS25961 e-fuse → VDD_TTL')
    u4 = s.place('TPS25961DRVR', 'U', 317.5, 203.2, 0, refnum=4)
    s.label(u4.pin('OUT'), 'VDD_TTL')
    s.power(u4.pin('OVLO'), 'GND')
    s.label(u4.pin('ILIM'), 'ILIM_TTL')
    s.power(u4.pin('IN'), '+5V_SERVO')
    s.label(u4.pin('EN/UVLO'), 'EN_TTL')
    for p in u4.pins_named('GND'):
        s.power(p, 'GND')
    vR(s, 287.02, 233.68, '27k', 'net:ILIM_TTL', 'pwr:GND')
    vR(s, 350.52, 193.04, '100k', 'pwr:+5V_SERVO', 'net:EN_TTL')
    decap(s, 365.76, 193.04, '+5V_SERVO')
    vpart(s, 'MA10V470M6X8', 'C', 322.58, 243.84, 'net:VDD_TTL', 'pwr:GND', value='470uF 10V')
    vC(s, 337.82, 243.84, '100nF', 'net:VDD_TTL', 'pwr:GND')
    vdiode(s, 'TVS_SMB', 353.06, 243.84, 'net:VDD_TTL', 'pwr:GND', value='SMBJ6.0A', lcsc=TVS_SMB['SMBJ6.0A'], refnum=4)
    # ---------------- test points
    heading(s, 280, 55, 'Test points (bring-up)')
    x = 294.64
    for sig in ('TXD', 'RXD', 'TNOW', 'A', 'B', 'DATA'):
        testpoint(s, x, 76.2, sig)
        x += 17.78
    return s
