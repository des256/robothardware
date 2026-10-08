# Datasheets and golden references

Everything the schematic gets drawn from, so nobody designs from memory.

- `manifest.tsv` lists every part datasheet (file, LCSC number, MPN, block, URL).
  URLs come from the JLCPCB catalog (`jlcpcb_parts.db`); TI links were rewritten
  to the English editions (`/lit/` instead of `/cn/lit/`).
- `fetch.sh` (re)downloads everything in the manifest and verifies each file is a
  PDF. Safe to re-run; cached files are skipped. LCSC-hosted sheets need the
  `wmsc.lcsc.com/wmsc/upload/file/pdf/…` form of the link (the `www.lcsc.com/datasheet/…`
  form returns an HTML viewer), so the manifest uses those.
- `reference/` holds vendor reference designs, app notes and the ROBOTIS
  circuits — the "golden references" HARDWARE.md §8 asks for per block.

Identical files were collapsed: one JST EH catalog sheet covers B3B/B4B/S3B/S4B,
one Hongjiacheng sheet covers all SMBJ values, one WCH sheet covers CH344Q/L.

## Part datasheets (by block)

| Block | Part (LCSC) | File | Notes |
|-------|-------------|------|-------|
| USB 3.0 hub | TUSB8041IRGCR (C544686) | `tusb8041.pdf` | 49 p. Rails: VDD 1.1 V + VDD33 3.3 V; 24 MHz crystal; `USB_VBUS` via 90.9 kΩ divider; per-port `PWRCTLx` / `OVERCURxz` |
| USB 3.0 hub (alt) | RTS5411S-GR (C5356838) | `rts5411s.pdf` | Consumer-hub chip, thinner docs |
| USB 3.0 hub (alt) | CYUSB3304-68LTXC (C462531) | `cyusb3304.pdf` | |
| USB-UART ×4 | CH344Q (C2988084), CH344L (C2887250) | `ch344.pdf` | **Chinese edition** (CH344DS1, 8 p.). TNOW facts extracted in `FUNCTIONAL.md` §5. English copy: manual grab from wch-ic.com (JS-only site) |
| RS-485 transceiver ×4 | SP3485EN-L/TR (C8963) | `sp3485en.pdf` | 3.3 V, 10 Mbps, −7…+12 V common mode; DE / R̄E̅ pins |
| TTL half-duplex buffer ×4 | SN74LVC2G241DCUR (C10430) | `sn74lvc2g241.pdf` | 1OE active-low, 2OE active-high; ±24 mA @ 3.3 V |
| TTL buffer (2-chip alt) | SN74LVC1G126 (C7834), SN74LVC1G125 (C23654) | `sn74lvc1g126.pdf`, `sn74lvc1g125.pdf` | |
| Buck controller, servo rails | LM5145RGYR (C485912) | `lm5145.pdf` | 6–75 V in, external FETs |
| Buck controller, dual (alt) | LM5143RHAR (C5219297) | `lm5143.pdf` | One chip for both servo rails |
| Buck 5 V USB | TPS54560DDAR (C31966) | `tps54560.pdf` | 60 V in, 5 A |
| Buck 3.3 V | TLV62569DBVR (C141836) | `tlv62569.pdf` | 2 A, Vin ≤ 5.5 V |
| eFuse, 12 V buses | TPS16630PWPR (C1849461) | `tps1663.pdf` | 60 V, ~6 A class |
| eFuse, light 5 V buses | TPS25961DRVR (C5571272) | `tps25961.pdf` | ≤ 2 A class |
| VBUS switch ×3 | SY6280AAC (C55136) | `sy6280.pdf` | `Ilim(A) = 6800 / Rset(Ω)`; EN must not float |
| VBUS switch (alt) | TPS2553DBVR (C55266) | `tps2553.pdf` | |
| USB-C CC + SS mux | HD3SS3220RNHR (C165155) | `hd3ss3220.pdf` | UFP: `PORT`=L, `ADDR`=NC (GPIO mode), `ENn_CC`=L, `VBUS_DET` via 900 kΩ |
| Ideal-diode controller | LM74700QDBVRQ1 (C2941042) | `lm74700-q1.pdf` | Drives external N-FET |
| TVS, rails | SMBJ24A / 13A / 6.0A (C19077578 / 67 / 60) | `smbj-series.pdf` | Chinese vendor sheet, all values |
| ESD, USB3 SS pairs | TPD4E05U06DQAR (C138714) | `tpd4e05u06.pdf` | 0.5 pF |
| ESD, USB2 + TTL DATA | USBLC6-2SC6 (C2687116) | `usblc6-2sc6.pdf` | UMW clone |
| ESD, RS-485 | SM712 (C7420375) | `sm712.pdf` | −7 / +12 V asymmetric |
| Servo connectors | JST B4B-EH-A (C160258), B3B-EH-A (C160259), S4B-EH (C265068), S3B-EH (C263754) | `jst-eh-series.pdf` | EH catalog page (drawings, ratings) |
| 19 V input | XT30PW-M (C431092) | `xt30pw-m.pdf` | Chinese drawing |
| 19 V out (alt) | DC-005-A200 (C720557) | `dc-005-a200.pdf` | |
| USB-A 3.0 receptacle ×3 | HC-ST-003-01-J (C2845330) | `usba3-hc-st-003-01-j.pdf` | Chinese drawing |
| USB-C receptacle | TYPE-C 24P QT (C2681555), QCHT (C456013) | `usbc-24p-qt.pdf`, `usbc-24p-qcht.pdf` | Chinese drawings |
| Buck / ideal-diode FET ×5 | CSD18532Q5B (C882766) | `csd18532q5b.pdf` | 60 V, 2.5 mΩ, SON 5×6; RILIM 240 Ω / 150 Ω sized for it |
| Buck inductors | TMPA1265SP-4R7MN-D (C2880057), TMPC1265HP-3R3MG-D (C357272), SMNR4020-2.2UH (C135262) | `tmpa1265sp-4r7.pdf`, `tmpc1265hp-3r3.pdf`, `smnr4020-2r2.pdf` | 12 V, 5 V servo, 3V3/1V1 bucks |
| Buck inductor, +5V_USB | 7447798720 (C105681) | `we-7447798720.pdf` | Würth 7.2 µH 6 A (TPS54560EVM part) |
| Catch diode, +5V_USB | B560C-13-F (C85100) | `b560c.pdf` | |
| 100 V input ceramics | C3225X7S2A475KT000N (C342614), C3225X7R2A225KT5L0U (C76686) | `tdk-c3225x7s2a475k.pdf`, `tdk-c3225x7r2a225k.pdf` | 1210 |
| Buck output ceramics | GRM32ER61C476KE15L (C77101), CS3225X7R226K250NRL (C2918511) | `murata-grm32er61c476k.pdf`, `samwha-cs3225x7r226k.pdf` | 1210 |
| Bulk capacitors | RVE470UF35V167RV084 (C5155332) | `rve470uf35v.pdf` | 19 V input bank. The polymer MA25V470M8X10 (C46550466) / MA10V470M6X8 (C46550459) have no datasheet file in the JLCPCB catalog — spec is the catalog line (25 mΩ / 20 mΩ, 4.1 A / 3.1 A ripple) |
| Fuses | 0453015.MR (C178997), 1206TD-4A (C2838918) | `littelfuse-0453015.pdf`, `prosemi-1206td-4a.pdf` | 15 A time-lag input, 4 A time-lag Jetson |

## Reference designs and app notes (`reference/`)

| Block | File | What it is |
|-------|------|------------|
| USB hub | `ti-sllu198-tusb8041-evm-users-guide.pdf` | TUSB8041 EVM — the reference schematic to copy |
| USB hub / SS layout | `ti-slla414a-usb-hub-highspeed-layout-guidelines.pdf` | TI SuperSpeed layout rules |
| USB ESD | `ti-slvaf82b-esd-surge-protection-usb.pdf` | Where the TVS arrays go |
| USB-C upstream | `ti-sllu241-hd3ss3220-ufp-dongle-evm.pdf` | HD3SS3220 in **UFP** mode — our exact use |
| USB-C upstream | `ti-slla481-hd3ss3220-schematic-checklist.pdf` | 3-page checklist; run it before ERC |
| 12 V / 5 V servo bucks | `ti-snvu545-lm5145evm-hd-20a.pdf` | LM5145 20 A EVM — schematic, BOM, layout |
| 5 V USB buck | `ti-slvu863-tps54560-evm.pdf` | TPS54560 EVM |
| Input protection | `ti-slvae57b-basics-of-ideal-diodes.pdf` | Background for the LM74700 stage |
| Servo TTL front-end | `robotis/dynamixel-x-ttl-circuit-3v3-74lvc2g241.png` | **ROBOTIS's recommended 3.3 V TTL circuit** (XL330 / XC330-M) — 74LVC2G241, TX_Enable → 1OE̅ + 2OE |
| Servo TTL front-end | `robotis/dynamixel-x-ttl-circuit-5v.png` | Same circuit at 5 V (XL430 / XM430-T class) |
| Servo RS-485 front-end | `robotis/dynamixel-x-rs485-circuit.jpg` | ROBOTIS's recommended RS-485 circuit — MAX485, TX_Enable → DE + R̄E̅ tied |
| Servo connectors | `robotis/dynamixel-x-ttl-connector-pinout.png`, `robotis/dynamixel-x-rs485-connector-pinout.png`, `robotis/emanual-jst-connectors.md` | Pinouts: TTL `1 GND, 2 VDD, 3 DATA`; RS-485 `1 GND, 2 VDD, 3 D+, 4 D−` |
| Servo specs | `robotis/dxl_x_info.yml` | ROBOTIS's own spec data for every X-series servo (voltage, stall current, baud) — feeds the fleet table |
| U2D2 | `robotis/u2d2-emanual.md`, `robotis/u2d2-pinouts.png` | ROBOTIS doesn't publish the U2D2 schematic; the emanual page + the circuits above are what exists |

Source pages: TI product pages (`ti.com/product/<part>`), ROBOTIS e-Manual
(`github.com/ROBOTIS-GIT/emanual`, `_includes/en/dxl/*_connection_x.md`).

## Still to collect (manual)

| Item | Why manual | Blocked on |
|------|-----------|------------|
| WEBENCH designs: LM5145 → 12 V, LM5145 → 5 V, TPS54560 → 5 V | Interactive TI tool, needs login. Export PDF + BOM into `reference/webench/` | Servo fleet decision (currents) |
| English CH344DS1 | wch-ic.com is JavaScript-only; curl gets nothing | — |
| Jetson Orin NX carrier: datasheet / design guide (input range, polarity, USB-C port capabilities) | Depends on which carrier | Carrier decision |
| Dynamixel e-Manual pages for the chosen servos | Fleet not decided; `dxl_x_info.yml` already has the numbers | Fleet decision |
| JLCPCB impedance stackup (JLC04161H-7628) + DRC template | Layout stage | — |
