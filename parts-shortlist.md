# Parts shortlist (JLCPCB catalog query results)

Auto-generated from `jlcpcb_parts.db` (jlcparts snapshot: 2026-08-29T14:48:52Z) by
querying per-block candidates from HARDWARE.md section 3. Raw query output --
curated picks are marked separately. Price is the qty-1 tier in USD; Lib
Basic = no extended-part fee at JLCPCB assembly. Stock changes daily; re-check
before ordering.

## Curated picks

Selection criteria: real datasheet + reference design available, stock depth,
price, Basic where possible. All main ICs are Extended parts (per-line feeding
fee at assembly -- normal for a board like this). **Every pick still needs its
datasheet read before the schematic is drawn.**

| Block | Pick | LCSC | USD@1 | Why / caveats |
|-------|------|------|-------|---------------|
| USB 3.0 hub | TUSB8041IRGCR | C544686 | 4.62 | Industrial temp, best docs + TI reference schematic. Cheap alt: RTS5411S (C5356838, $2.09), ubiquitous in consumer hubs; Cypress CYUSB3304 (C462531) also credible. Cross-check chosen chip against librealsense issue reports before committing. |
| USB-UART (4x UART) | CH344Q | C2988084 | 3.42 | Description lists RS-485 mode. **Verify per-UART TNOW pins in the WCH datasheet** -- that's the load-bearing feature. CH344L (C2887250) alt; CH343P (C2846043) single-bus fallback. |
| RS-485 transceiver (x4) | SP3485EN-L/TR | C8963 | 0.31 | **Basic part**, 3.3 V, 10 Mbps (> 4.5 Mbps Dynamixel max), DE/RE pins for TNOW. 395k stock. |
| TTL half-duplex buffer (x4) | SN74LVC2G241DCUR | C10430 | 0.51 | The one-chip front-end (complementary OEs). Alt: SN74LVC1G126 (TX, OE active-high) + SN74LVC1G125 (RX, OE active-low) -- same TNOW drives both, no inverter. |
| Buck controller 12 V | LM5145RGYR | C485912 | 2.45 | 6-75 V in, external FETs, WEBENCH support. Consolidation option: LM5143 (C5219297) is a *dual* controller -- one chip could run both servo rails. |
| Buck 5 V USB | TPS54560DDAR | C31966 | 1.02 | 60 V in, 5 A, SOIC-8-EP, 47k stock. Bound port limits so the sum fits (HARDWARE.md section 3). |
| Buck 3.3 V | TLV62569DBVR | C141836 | 0.07 | 2 A, Vin <= 5.5 V -- fed from the quiet 5 V USB rail. |
| eFuse, servo buses | TPS16630PWPR / TPS25961DRVR | C1849461 / C5571272 | 2.50 / 0.39 | Current class must match the bus: TPS1663x (60 V, ~6 A class) for 12 V buses; TPS25961 (19 V, <= 2 A) only for light 5 V TTL buses. Recompute per fleet; polyfuse + TVS is the budget fallback. |
| VBUS switch (x3) | TPS2553DBVR | C55266 | 0.54 | **Changed 2026-10-08 while drawing usb-port:** SY6280AAC (C55136, still imported as the alternate) has no fault output, so the hub's OVERCURxz could never see an over-current. TPS2553: FAULT open-drain → hub, EN active high from PWRCTLx, RILIM 16.9 kΩ → 1.51 A. |
| USB-C CC + SS mux | HD3SS3220RNHR | C165155 | 1.89 | The standard UFP orientation part; 5.5k stock. |
| Ideal diode ctrl | LM74700QDBVRQ1 | C2941042 | 1.06 | 65 V, drives external NFET (pick FET by input current). |
| TVS, rails | SMBJ24A / SMBJ13A / SMBJ6.0A | C19077578 / C19077567 / C19077560 | ~0.05 | All **Basic** (hongjiacheng). 19 V in / 12 V servo / 5 V servo respectively. |
| ESD, USB3 SS pairs | TPD4E05U06DQAR | C138714 | 0.08 | TI genuine, 0.5 pF, 94k stock. |
| ESD, USB2 + TTL DATA | USBLC6-2SC6 | C2687116 | 0.05 | UMW clone; TI/ST original if preferred. |
| ESD, RS-485 | SM712 | C7420375 | 0.07 | **Basic**, asymmetric -7/+12 V, made for RS-485. |
| Servo conn, RS-485 (x4) | B4B-EH-A(LF)(SN) | C160258 | 0.08 | JST EH 4-pin top-entry. Side-entry alt: S4B-EH (C265068). |
| Servo conn, TTL (x4) | B3B-EH-A(LF)(SN) | C160259 | 0.06 | JST EH 3-pin top-entry. Side-entry alt: S3B-EH (C263754). EHR-3/EHR-4 housings (C161660 etc.) are the *cable-side* parts for building servo leads. |
| 19 V input | XT30PW-M | C431092 | 0.38 | PCB right-angle, 15 A. **Do not use a barrel jack here** -- DC-005 class is ~3 A, a 150-240 W input needs 8-13 A. Adapter mates via a pigtail. |
| 19 V out (Jetson) | XT30PW-M or DC-005-A200 | C431092 / C720557 | 0.38 / 0.14 | ~2.1 A at 40 W, so the 3 A barrel is acceptable here if you want a barrel-to-barrel cable; XT30 is more robust. |
| USB-A 3.0 recept (x3) | HC-ST-003-01-J | C2845330 | 0.13 | 9-pin THT right-angle, shell stakes. |
| USB-C recept (upstream) | TYPE-C 24P QT | C2681555 | 0.54 | **Must be 24P full-featured female** for SuperSpeed -- the plentiful 16P parts are USB2-only, and one 24P hit (C3151751) is male. Alt: C456013. |

### Parts added during schematic capture (resolved against JLCPCB's live catalog, 2026-10-08)

`jlcpcb_parts.db` was unusable that day (see README.md), so these were looked up
one by one with JLCPCB's component search; stock is the figure returned then.
Values for the bucks are the TI reference designs (LM5145 datasheet application
circuits 1 and 2, TPS54560 datasheet figure 33, TLV62569 §8.2); E96 resistors
are the UNI-ROYAL 0603WAF series.

| Role | Part | LCSC | Stock | Note |
|------|------|------|-------|------|
| Buck + ideal-diode N-FET (×5) | CSD18532Q5B, 60 V, 2.5 mΩ, SON 5×6 | C882766 | 2426 | TI, same package as the datasheet's CSD18563Q5A; RILIM recomputed for 2.5 mΩ (240 Ω / 150 Ω) |
| 12 V buck inductor | TMPA1265SP-4R7MN-D 4.7 µH 20 A / 25 A sat | C2880057 | 1243 | TAI-TECH, 13.5 × 12.6 mm like the Cyntec part TI lists |
| 5 V servo buck inductor | TMPC1265HP-3R3MG-D 3.3 µH 18 A / 30 A sat | C357272 | 753 | |
| 5 V USB buck inductor | 7447798720 7.2 µH 6 A | C105681 | 406 | Würth, the TPS54560EVM part |
| 3V3 / 1V1 buck inductor (×2) | SMNR4020-2.2UH 2.2 µH 3.4 A | C135262 | 103006 | |
| Catch diode, TPS54560 | B560C-13-F 60 V 5 A SMC | C85100 | 150633 | Diodes Inc, the EVM part |
| 100 V input ceramics | C3225X7S2A475KT000N 4.7 µF 100 V 1210 (×5) / C3225X7R2A225KT5L0U 2.2 µF 100 V 1210 (×9) | C342614 / C76686 | 4656 / 1572 | TDK |
| Buck output ceramics | GRM32ER61C476KE15L 47 µF 16 V 1210 (×7) / CS3225X7R226K250NRL 22 µF 25 V 1210 (×2) | C77101 / C2918511 | 225941 / 85727 | Murata / Samwha |
| 12 V bulk + per-port (×6) | MA25V470M8X10 470 µF 25 V polymer, 25 mΩ | C46550466 | 128243 | jieerrui |
| 5 V bulk + per-port (×5) | MA10V470M6X8 470 µF 10 V polymer, 20 mΩ | C46550459 | 81105 | |
| 19 V input bulk (×2) | RVE470UF35V167RV084 470 µF 35 V, 230 mΩ | C5155332 | 8698 | KNSCHA |
| Input fuse | 0453015.MR 15 A time-lag 2410 | C178997 | 530 | Littelfuse |
| Jetson fuse | 1206TD-4A 4 A time-lag 1206, 72 V | C2838918 | 374 | prosemi |
| Hub crystal | X322524MRB4SI 24 MHz 18 pF 3225 | C70571 | 44317 | YXC; 30 pF load caps |
| CH344 crystal | X50328MSB2GI 8 MHz 20 pF 5032 | C115962 | Basic | CDFER library; 33 pF load caps |
| Ferrites | BLM18PG221SN1D 0603 1.4 A (hub core) / BLM21PG221SN1D 0805 2 A (USB-A VBUS ×3) | C80165 / C85840 | 317212 / 262582 | Murata |
| RS-485 TVS (×4) | PSM712-LF-T7 | C32677 | Basic | ProTek SM712 equivalent, CDFER library |
| TTL DATA TVS (×4) | SMF5.0A SOD-123FL | C19077497 | Basic | hongjiacheng, CDFER library |
| VCC bias diode (12 V buck) | SS14 | C2480 | Basic | |
| Rail LEDs (×6) | 0805 green | C2297 | Basic | |
| E96 resistors 0603 1 % | 2.37k C25964 · 24.9k C25962 · 80.6k C23249 · 33.2k C23003 · 23.2k C23346 · 4.42k C23043 · 422 C23052 · 402 C23049 · 90.9k C23129 · 53.6k C23074 · 10.2k C22772 · 16.9k C25954 · 243k C23351 · 442k C23175 · 9.53k C23127 · 4.02k C23040 · 18.2k C22892 · 20.5k C22910 · 249k C22918 · 453k C25818 · 910k C23263 | — | ≥ 250 each | UNI-ROYAL 0603WAF |
| E24 resistors / ceramics | JLC Basic parts from the CDFER library (`tools/schematic-gen/common.py` has the full value → LCSC table) | — | Basic | |

Raw query noise to ignore below: HD3SS6126 and PTN36241G in the hub tables are
*redrivers*, not hubs; the "TPS16-N1F1" rows in the eFuse table are USB-C
connectors; the IDC headers in the DC-jack table matched a loose subcategory
filter; C598201 in the USB-A table is a Micro-B.

### USB 3.0 hub controller (known candidates)

|   LCSC    |      MPN      |      Maker      |       Pkg        | USD@1 | Stock | Lib |                                Description                                |                                         DS                                         |
|-----------|---------------|-----------------|------------------|-------|-------|-----|---------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C390630   | GL3523-OTY30  | Genesys Logic   | QFN-76-EP(9x9)   | 2.46  | 15315 | Ext | 4 4.75V~5.5V Transceiver USB 3.1 QFN-76-EP(9x9) USB Converters ROHS       | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588893245463515136) |
| C7501408  | GL3510-OSY52  | Genesys Logic   | QFN-64           | 1.45  |  4007 | Ext | 0℃~+70℃ 2 4.75V~5.25V 5Gbps USB 3.1 QFN-64 USB Converters ROHS            | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590908898847379456) |
| C19725282 | GL3523-OTY3C  |                 | QFN-76(9x9)      | 2.13  |  2619 | Ext | 0℃~+70℃ 4 4.75V~5.25V Transceiver USB 3.1 QFN-76(9x9) USB Converters R    | [ds]()                                                                             |
| C5159024  | RTS5411T-GR   | Realtek Semicon | QFN-76(9x9)      | 1.74  |  2259 | Ext | 0℃~+70℃ 1.1V、3.3V Hub USB 3.2 QFN-76(9x9) USB HUB Controllers ROHS       | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8589834533467295744) |
| C544686   | TUSB8041IRGCR |                 | QFN-64-EP(9x9)   | 4.62  |  1865 | Ext | -40℃~+85℃ 0.99V~1.26V、3V~3.6V 33mA 4 778mA Hub I2C、SMBus USB 2.0、USB 3 | [ds](https://www.ti.com/cn/lit/gpn/tusb8041)                                       |
| C5356838  | RTS5411S-GR   |                 | QFN-76           | 2.09  |  1100 | Ext | 0℃~+70℃ 4 4.45V~5.25V USB 3.1 USB Hub QFN-76 USB Converters ROHS          | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8589838617779597312) |
| C633621   | USB5744-I/2G  | Microchip Tech  | HVQFN-56-EP(7x7) | 4.90  |   276 | Ext | 0℃~+70℃ 1.2V、3.3V 5Gbps Hub USB 2.0、USB 3.2 HVQFN-56-EP(7x7) USB HUB C  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8576734294138167296) |
| C626715   | USB5744T-I/2G | Microchip Tech  | VQFN-56-EP(7x7)  | 5.22  |   203 | Ext | -40℃~+85℃ 1.2V、3.3V 5Gbps Hub USB 2.0、USB 3.2 VQFN-56-EP(7x7) USB HUB   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8589805030820769792) |

### USB 3.0 hub controller (generic search)

|   LCSC   |       MPN        |          Maker           |        Pkg         | USD@1 | Stock | Lib |                                Description                                |                                         DS                                         |
|----------|------------------|--------------------------|--------------------|-------|-------|-----|---------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C5159024 | RTS5411T-GR      | Realtek Semicon          | QFN-76(9x9)        | 1.74  |  2259 | Ext | 0℃~+70℃ 1.1V、3.3V Hub USB 3.2 QFN-76(9x9) USB HUB Controllers ROHS       | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8589834533467295744) |
| C544686  | TUSB8041IRGCR    |                          | QFN-64-EP(9x9)     | 4.62  |  1865 | Ext | -40℃~+85℃ 0.99V~1.26V、3V~3.6V 33mA 4 778mA Hub I2C、SMBus USB 2.0、USB 3 | [ds](https://www.ti.com/cn/lit/gpn/tusb8041)                                       |
| C5356838 | RTS5411S-GR      |                          | QFN-76             | 2.09  |  1100 | Ext | 0℃~+70℃ 4 4.45V~5.25V USB 3.1 USB Hub QFN-76 USB Converters ROHS          | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8589838617779597312) |
| C462531  | CYUSB3304-68LTXC | Infineon Cypress Semicon | QFN-68             | 3.43  |   626 | Ext | -40℃~+85℃ 1.2V、3.3V、5V 4 5Gbps Hub I2C USB 3.0 QFN-68 USB HUB Controll  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8589838206326763520) |
| C701818  | HD3SS6126RUAR    |                          | WFQFN-42-EP(3.5x9) | 1.57  |   566 | Ext | 0℃~+70℃ 10Gbps 3.3V 3mA Hub USB 2.0、USB 3.0 WFQFN-42-EP(3.5x9) USB HUB   | [ds](https://www.ti.com/cn/lit/gpn/hd3ss6126)                                      |
| C633621  | USB5744-I/2G     | Microchip Tech           | HVQFN-56-EP(7x7)   | 4.90  |   276 | Ext | 0℃~+70℃ 1.2V、3.3V 5Gbps Hub USB 2.0、USB 3.2 HVQFN-56-EP(7x7) USB HUB C  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8576734294138167296) |
| C2678039 | TUSB8020BIPHPRQ1 | Texas Instruments        | HTQFP-48(7x7)      | 6.27  |   253 | Ext | -40℃~+85℃ 0.99V~1.26V、3V~3.6V 2 5Gbps Hub I2C、SMBus USB 3.0 HTQFP-48(7  | [ds](https://www.ti.com/cn/lit/gpn/tusb8020b-q1)                                   |
| C2675243 | PTN36241GHXZ     | NXP Semicon              | XQFN-12(1.7x2)     | 1.98  |   207 | Ext | -40℃~+85℃ 1.8V 5Gbps Hub USB 3.0 XQFN-12(1.7x2) USB HUB Controllers RO    | [ds](https://www.nxp.com/docs/en/data-sheet/PTN36241G.pdf)                         |

### USB-UART bridge: CH344 (quad) + CH343 (single, fallback)

|   LCSC   |  MPN   |        Maker         |         Pkg         | USD@1 | Stock | Lib |                                Description                                |                                         DS                                         |
|----------|--------|----------------------|---------------------|-------|-------|-----|---------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C2846043 | CH343P | WCH Jiangsu Qin Heng | TQFN-16-EP(3x3)     | 1.11  |  4152 | Ext | -40℃~+85℃ 3.3V、5V 3mA 6Mbps 90uA USB 2.0 USB to UART TQFN-16-EP(3x3) U   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8618866816802574336) |
| C5832295 | CH343K |                      | ESSOP-10-150mil-1mm | 1.08  |  3918 | Ext | 1.8V~5V、3.3V、5V 15mA 50uA 6Mbps USB 2.0 USB to UART ESSOP-10-150mil-1m  | [ds]()                                                                             |
| C2844153 | CH343G | WCH Jiangsu Qin Heng | SOP-16              | 1.22  |  3239 | Ext | -40℃~+85℃ 15mA 160uA 3.3V、5V 6Mbps USB 2.0 USB to UART SOP-16 USB Conv   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8618866813874679808) |
| C2887250 | CH344L | WCH Jiangsu Qin Heng | LQFP-48(7x7)        | 2.82  |  1425 | Ext | -40℃~+85℃ 3.3V、5V 4 USB 2.0 USB to UART LQFP-48(7x7) USB Converters RO   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8618866860662546432) |
| C2988084 | CH344Q | WCH Jiangsu Qin Heng | LQFP-48(7x7)        | 3.42  |   477 | Ext | -40℃~+85℃ 3.3V 4 6Mbps USB to UART、USB to RS232、USB to RS422、USB to RS | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8618866915339493376) |

### RS-485 transceivers (known candidates)

|   LCSC    |       MPN       |                Maker                |  Pkg   | USD@1 | Stock  |  Lib  |                               Description                               |                                         DS                                         |
|-----------|-----------------|-------------------------------------|--------|-------|--------|-------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C8963     | SP3485EN-L/TR   | MaxLinear                           | SOIC-8 | 0.31  | 395153 | Basic | -40℃~+85℃ 1 1 10Mbps 2mA 3.3V 32 Half-Duplex Transceiver SOIC-8 RS-485  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8579709476519542784) |
| C94206    | TP8485E-SR      | 3PEAK                               | SOIC-8 | 0.14  | 117396 | Ext   | -40℃~+125℃ 1 1 1.4mA 250Kbps 256 3V~5.5V Transceiver ±18kV SOIC-8 RS-4  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588879899309821952) |
| C668205   | SP3485EEN(UMW)  |                                     | SOP-8  | 0.27  | 113295 | Ext   | -40℃~+85℃ 1 1 12Mbps 2.97V~3.63V 256 520uA Half-Duplex Transceiver SOP  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8757270730231173120) |
| C313015   | SIT3485ESA      | SIT                                 | SOP-8  | 0.35  | 102472 | Ext   | -40℃~+85℃ 1 1 12Mbps 256 3V~3.6V 800uA Half-Duplex Transceiver SOP-8 R  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588881758171639808) |
| C3235232  | THVD1400DR      |                                     | SOIC-8 | 0.42  |  93954 | Ext   | -40℃~+125℃ 1 1 1.5mA 256 3V~5.5V 500Kbps Enable shutdown、Tx/Rx enable  | [ds](https://www.ti.com/cn/lit/ds/symlink/thvd1400.pdf)                            |
| C41365340 | SP3485EN-L/TR   | ElecSuper                           | SOP-8  | 0.21  |  58642 | Ext   |                                                                         | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8604439314516627456) |
| C668204   | MAX3485ESA(UMW) |                                     | SOP-8  | 0.38  |  51823 | Ext   | -40℃~+85℃ 1 1 12Mbps 2.97V~3.63V 256 Half-Duplex Transceiver SOP-8 RS-  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8757271611299119104) |
| C3235215  | THVD1420DR      |                                     | SOIC-8 | 0.76  |  31181 | Ext   | -40℃~+125℃ 1 1 1.5mA 12Mbps 256 3V~5.5V Half-Duplex Transceiver ±12kV   | [ds](https://www.ti.com/cn/lit/gpn/thvd1420)                                       |
| C9943     | MAX3485EESA+T   | Analog Devices Inc Maxim Integrated | SOIC-8 | 1.99  |  27908 | Ext   | -40℃~+85℃ 1 1 12Mbps 2.2mA 3V~3.6V Half-Duplex Transceiver ±15kV SOIC-  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8586171749355933696) |
| C382671   | SIT3485EUA      | SIT                                 | MSOP-8 | 0.37  |  25763 | Ext   | -40℃~+85℃ 1 1 12Mbps 256 3V~3.6V 800uA Half-Duplex Transceiver MSOP-8   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588883641350545408) |

### RS-485 transceivers (generic, high stock)

|   LCSC   |      MPN       |               Maker               |  Pkg   | USD@1 | Stock  |  Lib  |                               Description                               |                                         DS                                         |
|----------|----------------|-----------------------------------|--------|-------|--------|-------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C8963    | SP3485EN-L/TR  | MaxLinear                         | SOIC-8 | 0.31  | 395153 | Basic | -40℃~+85℃ 1 1 10Mbps 2mA 3.3V 32 Half-Duplex Transceiver SOIC-8 RS-485  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8579709476519542784) |
| C6855    | SP485EEN-L/TR  | MaxLinear                         | SOIC-8 | 0.24  | 268465 | Basic | -40℃~+85℃ 1 1 10Mbps 4.75V~5.25V 900uA Half-Duplex Transceiver ±15kV S  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8579709487195668480) |
| C7063    | SN75176BDR     | Texas Instruments                 | SOIC-8 | 0.20  | 157024 | Basic | 0℃~+70℃ 1 1 4.75V~5.25V Transceiver SOIC-8 RS-485 / RS-422 ICs ROHS     | [ds](https://www.ti.com/cn/lit/gpn/sn75176b)                                       |
| C269864  | GM3085E        | GATEMODE                          | SOP-8  | 0.12  | 295847 | Ext   | -40℃~+85℃ 1 1 1Mbps 256 3V~5.5V 600uA Half-Duplex Transceiver ±15kV SO  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588881092011307009) |
| C269866  | YD3082EESA     | GATEMODE                          | SOP-8  | 0.22  | 178995 | Ext   | -40℃~+85℃ 1 1 1Mbps 256 3V~5.5V 600uA Half-Duplex Transceiver ±15kV SO  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8586198293885542400) |
| C277895  | SSP485         | Shanghai Siproin Microelectronics | SOP-8  | 0.20  | 166337 | Ext   | -40℃~+85℃ 1 1 256 2Mbps 450uA 5V Half-Duplex Transceiver ±15kV SOP-8 R  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588881756942032896) |
| C94206   | TP8485E-SR     | 3PEAK                             | SOIC-8 | 0.14  | 117396 | Ext   | -40℃~+125℃ 1 1 1.4mA 250Kbps 256 3V~5.5V Transceiver ±18kV SOIC-8 RS-4  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588879899309821952) |
| C2960453 | BL3085(I47)    | BL Shanghai Belling               | SOP-8  | 0.17  | 116471 | Ext   | -40℃~+85℃ 1 1 256 3.3V、5V 500Kbps 600uA Half-Duplex Transceiver ±15kV  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8589834892167962624) |
| C668205  | SP3485EEN(UMW) |                                   | SOP-8  | 0.27  | 113295 | Ext   | -40℃~+85℃ 1 1 12Mbps 2.97V~3.63V 256 520uA Half-Duplex Transceiver SOP  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8757270730231173120) |
| C313015  | SIT3485ESA     | SIT                               | SOP-8  | 0.35  | 102472 | Ext   | -40℃~+85℃ 1 1 12Mbps 256 3V~3.6V 800uA Half-Duplex Transceiver SOP-8 R  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588881758171639808) |

### TTL half-duplex buffer: 74LVC2G241 (and 1G125/1G126 two-chip alt)

|   LCSC   |          MPN          |              Maker              |   Pkg    | USD@1 | Stock | Lib |                              Description                               |                                         DS                                         |
|----------|-----------------------|---------------------------------|----------|-------|-------|-----|------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C7394032 | SN74LVC1G126DCKR(UMW) | UMW Youtai Semiconductor Co Ltd | SC-70-5  | 0.04  | 84425 | Ext | -40℃~+85℃ 1 1 1.65V~5.5V 10uA 24mA 24mA 4.8ns@5V,50pF 74LVC Tri-State  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590905756558708736) |
| C7834    | SN74LVC1G126DBVR      | Texas Instruments               | SOT-23-5 | 0.08  | 75466 | Ext | -40℃~+125℃ 1 1 1.65V~5.5V 10uA 3.7ns@3.3V,15pF 32mA 32mA 74LVC Tri-Sta | [ds](https://www.ti.com/cn/lit/gpn/sn74lvc1g126)                                   |
| C23654   | SN74LVC1G125DBVR      | Texas Instruments               | SOT-23-5 | 0.21  | 51120 | Ext | -40℃~+125℃ 1 1 1.65V~5.5V 10uA 3.7ns@3.3V,15pF 32mA 32mA 74LVC Tri-Sta | [ds](https://www.ti.com/cn/lit/gpn/sn74lvc1g125)                                   |
| C7833    | SN74LVC1G125DCKR      | Texas Instruments               | SC-70-5  | 0.10  | 46893 | Ext | -40℃~+125℃ 0.6ns@3.3V,15pF 1 1 1.65V~5.5V 10uA 32mA 32mA 74LVC Tri-Sta | [ds](https://www.ti.com/cn/lit/gpn/sn74lvc1g125)                                   |
| C88039   | SN74LVC1G126DCKR      | Texas Instruments               | SC-70-5  | 0.06  | 39956 | Ext | -40℃~+125℃ 1 1 1.65V~5.5V 10uA 3.7ns@3.3V,15pF 32mA 32mA 74LVC Tri-Sta | [ds](https://www.ti.com/cn/lit/gpn/sn74lvc1g126)                                   |
| C12519   | 74LVC1G125GW,125      | Nexperia                        | SOT-353  | 0.11  | 37943 | Ext | -40℃~+125℃ 1 1 1.65V~5.5V 2.1ns@3.3V,50pF 32mA 32mA 4uA 74LVC Schmitt  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8586172448777908224) |
| C7394017 | SN74LVC1G125DBVR(UMW) | UMW Youtai Semiconductor Co Ltd | SOT-23-5 | 0.05  | 35189 | Ext | -40℃~+85℃ 1 1 1.65V~5.5V 10uA 24mA 24mA 74LVC Tri-State Unidirectional | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590904162777444352) |
| C3040595 | 74LVC1G125GV-TP       | TECH PUBLIC                     | SOT-23-5 | 0.09  | 25524 | Ext | -40℃~+125℃ 1.65V~5.5V 2.6ns@5.0V,50pF 24mA 24mA 2uA 74LVC Tri-State SO | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8589837347358470144) |

### Buck controllers for 12V/5V servo rails (external FETs, 10-20A)

|   LCSC   |       MPN       |       Maker       |         Pkg         | USD@1 | Stock | Lib |                              Description                               |                                         DS                                         |
|----------|-----------------|-------------------|---------------------|-------|-------|-----|------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C485912  | LM5145RGYR      | Texas Instruments | VQFN-20-EP(3.5x4.5) | 2.45  |  4116 | Ext | -40℃~+125℃@(TJ) 1 1.8mA 1MHz 6V~75V 800mV~60V Adjustable Buck Buck Ext | [ds](https://www.ti.com/cn/lit/gpn/lm5145)                                         |
| C56175   | TPS40170RGYR    | Texas Instruments | TQFN-20-EP(3.5x4.5) | 1.80  |  2979 | Ext | -40℃~+125℃@(TJ) 1 4.5V~60V 600kHz 6A Adjustable Buck Buck External Yes | [ds](https://www.ti.com/cn/lit/gpn/tps40170)                                       |
| C148172  | TPS53355DQPR    | Texas Instruments | LSON-22-EP(5x6)     | 6.13  |  1045 | Ext | -40℃~+125℃ 1 1.5V~15V 1MHz 30A 420uA 600mV~5.5V Adjustable Buck Buck B | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588893308009517056) |
| C181238  | TPS40170QRGYRQ1 | Texas Instruments | VQFN-20-EP(3.7x4.7) | 2.20  |   479 | Ext | -40℃~+125℃@(TA) 1 100kHz~600kHz 4.5V~60V Adjustable Buck Buck External | [ds](https://www.ti.com/cn/lit/gpn/tps40170-q1)                                    |
| C5219258 | LM5143QRHARQ1   | Texas Instruments | VQFN-40(6x6)        | 3.95  |   376 | Ext | -40℃~+150℃ 15uA 2 2.2MHz 3.5V~65V 600mV~55V Buck Buck Built-in Yes VQF | [ds](https://www.ti.com/cn/lit/gpn/lm5143a-q1)                                     |
| C2876740 | LM25145RGYR     | Texas Instruments | VQFN-20-EP(3.5x4.5) | 3.65  |   350 | Ext | -40℃~+125℃@(TJ) 1 100kHz~1MHz 6V~42V 800mV~40V Adjustable Buck Buck Ex | [ds](https://www.ti.com/cn/lit/gpn/lm25145)                                        |
| C1849541 | LM5143QRWGRQ1   | Texas Instruments | VQFN-40-EP(6x6)     | 5.83  |   294 | Ext | -40℃~+150℃@(TJ) 15uA 2 2.2MHz 3.5V~65V 600mV~55V Adjustable Buck Buck  | [ds](https://www.ti.com/cn/lit/gpn/lm5143-q1)                                      |
| C5219297 | LM5143RHAR      |                   | VQFN-40-EP(6x6)     | 4.83  |   252 | Ext | -40℃~+150℃@(TJ) 15uA 2 2.2MHz 3.5V~65V 600mV~55V Adjustable Buck Buck  | [ds](https://www.ti.com/cn/lit/gpn/lm5143)                                         |

### Monolithic bucks, 60V-class in (5V USB rail candidates)

|   LCSC   |      MPN      |        Maker        |     Pkg      | USD@1 | Stock | Lib |                              Description                               |                                         DS                                         |
|----------|---------------|---------------------|--------------|-------|-------|-----|------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C31966   | TPS54560DDAR  | Texas Instruments   | SOIC-8-EP    | 1.02  | 47941 | Ext | -40℃~+150℃@(TJ) 1 146uA 2.5MHz 4.5V~60V 5A 800mV~58.8V Adjustable Buck | [ds](https://www.ti.com/cn/lit/gpn/tps54560)                                       |
| C95286   | TPS54540DDAR  | Texas Instruments   | SOIC-8-EP    | 1.42  | 14850 | Ext | -40℃~+150℃@(TJ) 1 146uA 2.5MHz 4.5V~42V 5A 800mV~41.1V Adjustable Buck | [ds](https://www.ti.com/cn/lit/gpn/tps54540)                                       |
| C1850354 | TPS54560BDDAR | Texas Instruments   | SO-8         | 1.19  | 11483 | Ext | -40℃~+150℃@(TJ) 1 146uA 4.5V~60V 500kHz 5A 800mV~58.8V Adjustable Buck | [ds](https://www.ti.com/cn/lit/gpn/tps54560b)                                      |
| C841384  | LMR33630ADDAR | Texas Instruments   | ESOP-8       | 0.69  |  9908 | Ext | -40℃~+125℃@(TJ) 1 1V~24V 24uA 3.8V~36V 3A 400kHz Adjustable Buck Buck  | [ds](https://www.ti.com/cn/lit/gpn/lmr33630)                                       |
| C477928  | LM5164DDAR    | Texas Instruments   | SO-8-EP      | 1.36  |  6260 | Ext | -40℃~+150℃@(TJ) 1 10.5uA 1A 1MHz 6V~100V Adjustable Buck Buck Built-in | [ds](https://www.ti.com/cn/lit/gpn/lm5164)                                         |
| C1850368 | TPS54540BDDAR | Texas Instruments   | SO-8         | 2.23  |  5032 | Ext | -40℃~+150℃@(TJ) 1 146uA 4.5V~42V 500kHz 5A 800mV~41.1V Adjustable Buck | [ds](https://www.ti.com/cn/lit/gpn/tps54540b)                                      |
| C544370  | LMR33630BDDAR | Texas Instruments   | SOIC-8-EP    | 0.74  |  4197 | Ext | -40℃~+125℃@(TJ) 1 1.4MHz 1V~24V 24uA 3.8V~36V 3A Adjustable Buck Buck  | [ds](https://www.ti.com/cn/lit/gpn/lmr33630)                                       |
| C3194572 | AP63357QZV-7  | Diodes Incorporated | VDFN-13(2x3) | 1.09  |  3246 | Ext | -40℃~+125℃@(TA) 1 22uA 3.5A 3.8V~32V 450kHz 800mV~32V Adjustable Buck  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590903542410657792) |

### Small 3.3V buck (from 5V USB rail)

|   LCSC   |      MPN      |        Maker        |      Pkg      | USD@1 | Stock  | Lib |                              Description                               |                                         DS                                         |
|----------|---------------|---------------------|---------------|-------|--------|-----|------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C468250  | TPS563208DDCR | Texas Instruments   | TSOT-23-6     | 0.16  | 140671 | Ext | -40℃~+125℃@(TJ) 1 3A 4.5V~17V 580kHz 768mV~7V Adjustable Buck Buck Bui | [ds](https://www.ti.com/cn/lit/gpn/tps563208)                                      |
| C116592  | TPS563201DDCR | Texas Instruments   | SOT-23-THIN-6 | 0.07  | 113251 | Ext | -40℃~+125℃@(TJ) 1 3A 4.5V~17V 580kHz 768mV~7V Adjustable Buck Buck Bui | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588884106902323200) |
| C141836  | TLV62569DBVR  | Texas Instruments   | SOT-23-5      | 0.07  | 108275 | Ext | -40℃~+125℃@(TJ) 1 1.5MHz 2.5V~5.5V 2A 600mV~5.5V Adjustable Buck Buck  | [ds](https://www.ti.com/cn/lit/gpn/tlv62569)                                       |
| C2895288 | AP62200TWU-7  | Diodes Incorporated | TSOT-26       | 0.21  |  38030 | Ext | -40℃~+125℃ 1 135uA 2A 4.2V~18V 750kHz 800mV~7V Adjustable Buck Buck Bu | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8560089911954341888) |
| C2071106 | TPS56339DDCR  | Texas Instruments   | TSOT-23-6     | 0.36  |  15757 | Ext | -40℃~+125℃@(TJ) 1 3A 4.5V~24V 500kHz 800mV~16V 98uA Adjustable Buck Bu | [ds](https://www.ti.com/cn/lit/gpn/tps56339)                                       |
| C97253   | TPS563200DDCR | Texas Instruments   | TSOT-23-6     | 1.41  |  14409 | Ext | -40℃~+85℃@(TA) 1 3A 4.5V~17V 650kHz 760mV~7V Adjustable Buck Buck Buil | [ds](https://www.ti.com/cn/lit/gpn/tps563200)                                      |
| C1323282 | AP62200WU-7   | Diodes Incorporated | TSOT-26       | 0.17  |  14253 | Ext | -40℃~+125℃ 1 135uA 2A 4.2V~18V 750kHz 800mV~7V Adjustable Buck Buck Bu | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8560078892020097024) |
| C1513007 | TPS563202DRLR | Texas Instruments   | SOT-563       | 0.15  |  13346 | Ext | -40℃~+125℃@(TJ) 1 3A 4.3V~17V 580kHz 806mV~7V Adjustable Buck Buck Bui | [ds](https://www.ti.com/cn/lit/gpn/tps563202)                                      |

### eFuses / per-bus protection

|   LCSC    |        MPN        |       Maker       |       Pkg       | USD@1 | Stock | Lib |                               Description                               |                                                                                                                         DS                                                                                                                          |
|-----------|-------------------|-------------------|-----------------|-------|-------|-----|-------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| C5571272  | TPS25961DRVR      | Texas Instruments | WSON-6(2x2)     | 0.39  | 27695 | Ext | -40℃~+125℃ 0.75mm 1 100mA~2A 106mΩ 2.7V~19V 2mm 2mm Integrated FET Sur  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590902654426439680)                                                                                                                                                                  |
| C2155806  | TPS25940AQRVCRQ1  | Texas Instruments | QFN-20-EP(3x4)  | 1.81  |  6766 | Ext | -40℃~+125℃ 0.8mm 1 10mA 2.7V~18V 3mm 42mΩ 4mm 66mV Integrated FET Surf  | [ds](https://www.ti.com/cn/lit/gpn/tps25940-q1)                                                                                                                                                                                                     |
| C7471768  | TPS16412DRCR      | Texas Instruments | VSON-10(3x3)    | 1.49  |  6178 | Ext | -40℃~+125℃ 1.8A 153mΩ 2.7V~40V Short-Circuit  Protection(SCP)、Over Vol | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8586208148742393856)                                                                                                                                                                  |
| C2155776  | TPS259630DDAR     | Texas Instruments | ESOP-8          | 0.70  |  4199 | Ext | -40℃~+125℃ 1 1.7mm 2.7V~19V 3.9mm 4.91mm 89mΩ Integrated FET Surface M  | [ds](https://www.ti.com/cn/lit/gpn/tps2596)                                                                                                                                                                                                         |
| C2155778  | TPS259631DDAR     | Texas Instruments | SOPowerPAD-8    | 0.79  |  3456 | Ext | -40℃~+125℃ 1 1.7mm 131mΩ 2.7V~19V 3.9mm 4.91mm Integrated FET Surface   | [ds](https://www.ti.com/cn/lit/gpn/tps2596)                                                                                                                                                                                                         |
| C1849461  | TPS16630PWPR      | Texas Instruments | HTSSOP-20       | 2.50  |  2066 | Ext | -40℃~+125℃@(Tj) 1 1.2mm 30.44mΩ 4.4mm 4.5V~60V 6.5mm Integrated FET Su  | [ds](https://www.ti.com/cn/lit/gpn/tps1663)                                                                                                                                                                                                         |
| C22357897 | TPS16-N1F1-2016-A | XFCN              | SMD             | 0.14  |  1321 | Ext | -25℃~+85℃ 1 10000 times 16P 5A 5V 6.5mm Laminated board Type-C SMD USB  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590921495675944960)                                                                                                                                                                  |
| C52750323 | TPS16-N1F1-2016-A |                   | SMD             | 0.09  |  1162 | Ext | -25℃~+85℃ 16P 3.16mm 5,000 cycles 5A 5V 6.5mm Black Female Type-C USB   | [ds]()                                                                                                                                                                                                                                              |
| C2653873  | TPS25940ARVCR     | Texas Instruments | WQFN-20-EP(3x4) | 2.00  |  1086 | Ext | -40℃~+125℃ 1 2.7V~18V 42mΩ 5.2A Active High Overvoltage protection、Sof | [ds](https://www.ti.com/cn/lit/ds/symlink/tps25940.pdf)                                                                                                                                                                                             |
| C22433503 | TPS16416DRCR      |                   | VSON-10-EP(3x3) | 1.66  |  1045 | Ext | -40℃~+125℃ 0.9mm 1 2.7V~40V 260mΩ 3mm 3mm Integrated FET Surface Mount  | [ds](https://www.ti.com.cn/cn/lit/ds/symlink/tps1641.pdf?ts=1739433643844&ref_url=https%253A%252F%252Fwww.ti.com.cn%252Fsitesearch%252Fzh-cn%252Fdocs%252Funiversalsearch.tsp%253FlangPref%253Dzh-CN%2526nr%253D10%2526searchTerm%253DTPS16416DRCR) |

### USB VBUS power switches (per-port current limit)

|   LCSC    |      MPN      |       Maker       |       Pkg       | USD@1 | Stock  | Lib |                                    Description                                     |                                         DS                                         |
|-----------|---------------|-------------------|-----------------|-------|--------|-----|------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C55136    | SY6280AAC     | Silergy Corp      | SOT-23-5        | 0.10  | 233263 | Ext | -40℃~+125℃ 1 2.4V~5.5V 80mΩ Active High High Side Switch Overcurrent P             | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8586176486478368768) |
| C42441843 | MT9700-N      |                   | SOT-23-5        | 0.04  | 226501 | Ext | -40℃~+85℃ 1 2.4V~5.5V 2A 80mΩ Active High Current Limiting Switch SOT-             | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8604442566352400384) |
| C55266    | TPS2553DBVR   | Texas Instruments | SOT-23-6        | 0.30  |  44248 | Ext | -40℃~+150℃ 1 1.5A 2.5V~6.5V 85mΩ Active High High Side Switch 过压保护、软启动     | [ds](https://www.ti.com/cn/lit/gpn/tps2553)                                        |
| C207620   | SY6280AAAC    | Silergy Corp      | SOT-23-5        | 0.10  |  32439 | Ext | -40℃~+125℃ 1 2.4V~5.5V 2A 63mΩ Active High High Side Switch Overcurren             | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588884728518336512) |
| C521201   | TPS2553DDBVR  | Texas Instruments | SOT-23-6        | 0.21  |  22579 | Ext | -40℃~+150℃ 1 1.5A 2.7V~6.5V 85mΩ Active High High Side Switch 软启动、欠压锁定     | [ds](https://www.ti.com/cn/lit/gpn/tps2553d)                                       |
| C111738   | TPS2553DBVR-1 | Texas Instruments | SOT-23-6        | 0.29  |  14979 | Ext | -40℃~+150℃ 1 1.5A 2.5V~6.5V 85mΩ Active High High Side Switch 过压保护、软启动     | [ds](https://www.ti.com/cn/lit/gpn/tps2553-1)                                      |
| C411878   | TPS2553DRVR-1 | Texas Instruments | WSON-6-EP(2x2)  | 0.38  |   4017 | Ext | -40℃~+105℃ 1 1.5A 115mΩ 2.5V~6.5V Active High Load Switch 软启动、欠压锁定、反向电 | [ds](https://www.ti.com/cn/lit/gpn/tps2553-1)                                      |
| C140303   | TPS2561DRCR   | Texas Instruments | VSON-10-EP(3x3) | 0.88  |   1213 | Ext | -40℃~+125℃ 2 2.5V~6.5V 2.8A 44mΩ Active High High Side Switch Overcurr             | [ds](https://www.ti.com/cn/lit/gpn/tps2561)                                        |

### USB-C CC controller + SS mux (upstream)

|   LCSC    |        MPN         |        Maker        |         Pkg         | USD@1 | Stock | Lib |                               Description                               |                                         DS                                         |
|-----------|--------------------|---------------------|---------------------|-------|-------|-----|-------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C165155   | HD3SS3220RNHR      | Texas Instruments   | WQFN-30-EP(2.5x4.5) | 1.89  |  5548 | Ext | -40℃~+85℃ 4.5V~5.5V 5uA I2C Not supported Not supported WQFN-30-EP(2.5  | [ds](https://www.ti.com/cn/lit/gpn/hd3ss3220)                                      |
| C701817   | HD3SS3220IRNHR     | Texas Instruments   | WQFN-30-EP(2.5x4.5) | 1.86  |  1392 | Ext | -40℃~+85℃ 10Gbps 2 4.5V、5.5V 5uA 900uA USB 3.1 WQFN-30-EP(2.5x4.5) USB | [ds](https://www.ti.com/cn/lit/gpn/hd3ss3220)                                      |
| C2155924  | HD3SS3220RNHT      | Texas Instruments   | WQFN-30-EP(2.5x4.5) | 1.99  |    67 | Ext | -40℃~+85℃ 2 8Ω Active High、Active Low WQFN-30-EP(2.5x4.5) Power Distri | [ds](https://www.ti.com/cn/lit/gpn/hd3ss3220)                                      |
| C2876685  | HD3SS3220IRNHT     | Texas Instruments   | WQFN-30-EP(2.5x4.5) | 3.37  |    37 | Ext | -40℃~+85℃ 4.5V~5.5V 700uA I2C WQFN-30-EP(2.5x4.5) Battery Management R  | [ds](https://www.ti.com/cn/lit/gpn/hd3ss3220)                                      |
| C2655457  | PI3USB31532ZLCEX   | Diodes Incorporated | TQFN-40(3x6)        | 3.53  |    25 | Ext | 6 TQFN-40(3x6) Analog Switches, Multiplexers ROHS                       | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8589837472323428352) |
| C3656542  | PI3USB30532ZLCEX   | Diodes Incorporated | TQFN-40(3x6)        | 3.45  |    16 | Ext | -40℃~+85℃ 3V~3.6V 6 6:4 6GHz USB TQFN-40(3x6) Analog Switches - Specia  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590293789173575680) |
| C23942354 | PI3USB31532Q2ZLCEX |                     | TQFN-40             | 3.14  |    10 | Ext |                                                                         | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8603206404455223296) |

### Ideal diode controller (19V reverse polarity)

|   LCSC   |       MPN        |                Maker                |      Pkg       | USD@1 | Stock | Lib |                              Description                               |                                         DS                                         |
|----------|------------------|-------------------------------------|----------------|-------|-------|-----|------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C129323  | LM5050MK-1/NOPB  | Texas Instruments                   | TSOT-23-6      | 1.01  |  8189 | Ext | -40℃~+125℃ 12V 22mV 2A 5V~75V External FET TSOT-23-6 ORing Controllers | [ds](https://www.ti.com/cn/lit/gpn/lm5050-1-q1)                                    |
| C473393  | LM5050MKX-1/NOPB | Texas Instruments                   | TSOT-23-6      | 1.00  |  7834 | Ext | -40℃~+125℃ 5V~75V 75uA TSOT-23-6 ORing Controllers ROHS                | [ds](https://www.ti.com/cn/lit/gpn/lm5050-1)                                       |
| C2941042 | LM74700QDBVRQ1   | Texas Instruments                   | SOT-23-6       | 1.06  |  5113 | Ext | -40℃~+150℃ 11mA 15V 2.37A 20mV 3.2V~65V 65V 80uA External FET Reverse  | [ds](https://www.ti.com/cn/lit/gpn/lm74700-q1)                                     |
| C2760463 | LM5050MK-2/NOPB  | Texas Instruments                   | SOT-23-6-THIN  | 1.75  |  4025 | Ext | -40℃~+125℃ 1.9A 11.5V 32uA 350uA 6V~75V External FET SOT-23-6-THIN ORi | [ds](https://www.ti.com/cn/lit/gpn/lm5050-2)                                       |
| C2877562 | LM5050MKX-2/NOPB | Texas Instruments                   | SOT-23-Thin-6  | 1.12  |  3946 | Ext | -40℃~+125℃ 1 6V~75V Active Low High Side Switch SOT-23-Thin-6 ORing Co | [ds](https://www.ti.com/cn/lit/gpn/lm5050-2)                                       |
| C2649431 | LM74610QDGKRQ1   | Texas Instruments                   | VSSOP-8-0.65mm | 1.63  |  3535 | Ext | -40℃~+125℃ 0uA 160mA 3.4uA 45V 480mV 6.3V External FET VSSOP-8-0.65mm  | [ds](https://www.ti.com/cn/lit/gpn/lm74610-q1)                                     |
| C2649430 | MAX40200AUK+T    | Analog Devices Inc Maxim Integrated | SOT-23-5       | 0.90  |  3155 | Ext | -40℃~+125℃ 1 1.5V~5.5V 1A Active High Ideal Diode SOT-23-5 ORing Contr | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588894020453994496) |
| C3215600 | LM74800QDRRRQ1   |                                     | SON-12(3x3)    | 2.23  |  2974 | Ext | -40℃~+125℃ 2.6A 3V~65V Ideal Diode Over Voltage Protection SON-12(3x3) | [ds](https://www.ti.com/cn/lit/gpn/lm7480-q1)                                      |

### TVS: power rails (19V in, 12V + 5V servo)

|   LCSC    |      MPN      |            Maker             |      Pkg      | USD@1 | Stock  |  Lib  |                              Description                               |                                         DS                                         |
|-----------|---------------|------------------------------|---------------|-------|--------|-------|------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C19077560 | SMBJ6.0A      | hongjiacheng                 | DO-214AA(SMB) | 0.06  | 249084 | Basic | -55℃~+150℃ 10.3V 58.25A@10/1000us 600W@10/1000us 6V 7.37V 800uA IEC 61 | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8564879118736121856) |
| C19077578 | SMBJ24A       | hongjiacheng                 | DO-214AA(SMB) | 0.05  |  40505 | Basic | -55℃~+150℃ 15.42A@10/1000us 24V 29.5V 38.9V 5uA 600W@10/1000us IEC 610 | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8564879132338790400) |
| C19077567 | SMBJ13A       | hongjiacheng                 | DO-214AA(SMB) | 0.05  |  14338 | Basic | -55℃~+150℃ 13V 15.9V 21.5V 27.91A@10/1000us 5uA 600W@10/1000us IEC 610 | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8564879123408982016) |
| C113976   | SMBJ6.0A      | MDD Microdiode Semiconductor | DO-214AA(SMB) | 0.05  |  50429 | Ext   | -65℃~+150℃ 10.3V 58.3A@10/1000us 600W@10/1000us 6V 7.37V 800uA TVS Uni | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8609171461395259392) |
| C908801   | SMBJ24A       | GOODWORK                     | DO-214AA(SMB) | 0.04  |  35016 | Ext   | -55℃~+150℃ 15.4A 24V 26.7V 38.9V 5uA 600W TVS Unidirectional DO-214AA( | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8757774745591271424) |
| C123819   | SMBJ24A       | MDD Microdiode Semiconductor | DO-214AA(SMB) | 0.06  |  27176 | Ext   | -65℃~+150℃ 15.5A@10/1000us 1uA 24V 29.5V 38.9V 600W@10/1000us TVS Unid | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8609171585337618432) |
| C87268    | SMBJ24A       | Brightking                   | SMB(DO-214AA) | 0.06  |  19924 | Ext   | 15.5A 1uA 24V 26.7V 38.9V 600W@10/1000us TVS Unidirectional SMB(DO-214 | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8756589758497996800) |
| C2759863  | SMBJ6.0A      | Leiditech                    | DO-214AA(SMB) | 0.08  |  19542 | Ext   | 10.3V 100uA 58.3A 6.67V 600W@10/1000us 6V TVS Unidirectional DO-214AA( | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588942791195414528) |
| C511906   | SMBJ6.0A      | BORN                         | DO-214AA(SMB) | 0.07  |  19498 | Ext   | -55℃~+150℃ 10.3V 58.3A 58.3uA 6.67V 6V TVS Unidirectional DO-214AA(SMB | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8757247862621253632) |
| C309975   | SMBJ6.0A/TR13 | Brightking                   | SMB(DO-214AA) | 0.06  |  16553 | Ext   | 1 10.3V 58.3A 6.67V 600W 6V 800uA TVS Unidirectional SMB(DO-214AA) ESD | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8586196212957786112) |

### ESD arrays: USB SS/HS + RS-485

|   LCSC    |     MPN      |              Maker              |    Pkg    | USD@1 | Stock  |  Lib  |                                Description                                 |                                         DS                                         |
|-----------|--------------|---------------------------------|-----------|-------|--------|-------|----------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C7420376  | SRV05-4      | hongjiacheng                    | SOT-23-6L | 0.08  | 622147 | Basic | -55℃~+150℃ 15V 1pF 4A 5V 5uA 6V 80W ESD Four channels IEC 61000-4-2、IE    | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590905124175241216) |
| C7420375  | SM712        | hongjiacheng                    | SOT-23    | 0.07  | 143295 | Basic | -55℃~+125℃ 12A 16V、26V 1uA、2uA 2 300W 7.5V、13.5V 75pF 7V、12V Bidirecti | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590905169016410112) |
| C20615829 | SRV05-4A     | hongjiacheng                    | SOT-23-6L | 0.03  |  27164 | Basic | -55℃~+155℃ 0.5pF、1pF 15V 4A@8/20us 5V 5uA 6V 80W@8/20us ESD IEC 61000-    | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590925050793451520) |
| C85364    | SRV05-4-P-T7 | ProTek Devices                  | SOT-23-6  | 0.19  |   1166 | Basic | 12V 1A@8/20us 3.5pF 500W@8/20us 5V 5uA 6V ESD Four channels IEC 61000-     | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8579709102848999424) |
| C558418   | SRV05-4      | TECH PUBLIC                     | SOT-23-6  | 0.03  | 461674 | Ext   | -55℃~+125℃ 0.3pF、0.8pF 20V 3A 500nA 5V 60W 6V ESD Four channels IEC 61    | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588894159876313088) |
| C2836319  | SRV05-4      | MSKSEMI                         | SOT-23-6  | 0.03  | 397622 | Ext   | -40℃~+125℃ 0.6pF 12V 1uA 4.5A@8/20us 5V 60W@8/20us 9V ESD Four channel     | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8589834761352220672) |
| C293966   | SM712        | DOWO                            | SOT-23    | 0.04  | 210740 | Ext   | -55℃~+125℃ 10V、26V 12A 1uA 2 400W 7.5V、13.3V 75pF 7V、12V Bidirectional  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588904366200008704) |
| C502564   | SM712        | MDD Microdiode Semiconductor    | SOT-23    | 0.07  | 186135 | Ext   | -55℃~+150℃ 12V 13.3V 17A 1uA 2 26V 400W 45pF、75pF ESD IEC 61000-4-2、IE   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588884856079568896) |
| C521963   | SM712        | TECH PUBLIC                     | SOT-23    | 0.04  | 151310 | Ext   | -55℃~+125℃ 10nA 15V、25V 2 50W@8/20us 7.5V、13.3V 75pF 7A@8/20us 7V、12V   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588886715817320448) |
| C2687116  | USBLC6-2SC6  | UMW Youtai Semiconductor Co Ltd | SOT-23-6  | 0.05  | 150192 | Ext   | 0.35pF、0.8pF 100nA 150W@8/20us 15V 2 5V 6A@8/20us 6V ESD SOT-23-6 ESD     | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8755886574108323840) |

### Servo connectors: JST EH shrouded headers (B3B/B4B)

|  LCSC   |       MPN        |           Maker           |     Pkg      | USD@1 | Stock | Lib |                              Description                               |                                         DS                                         |
|---------|------------------|---------------------------|--------------|-------|-------|-----|------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C225414 | A2502WV-6P       | CJT Changjiang Connectors | 插件,P=2.5mm | 0.09  | 31141 | Ext | -40℃~+105℃ 1 1x6P 2.5mm 250V 3A 6 6P Brass EH PA66 Through Hole Tin UL | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588889988351578112) |
| C160262 | B2B-EH-A(LF)(SN) | JST                       | 插件,P=2.5mm | 0.04  | 25902 | Ext | -25℃~+85℃ 1 1x2P 2 2.5mm 250V 2P 3.8mm 3A 6mm 7.5mm Brass EH PA66 Thro | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588890094543912961) |
| C161660 | EHR-3            | JST                       | P=2.5mm      | 0.03  | 25878 | Ext | -25℃~+85℃ 1 1x3P 2.5mm 3 EH Non-Latching PA66 UL94V-0 White Without Fi | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590165622547525632) |
| C160258 | B4B-EH-A(LF)(SN) | JST                       | 插件,P=2.5mm | 0.08  | 21283 | Ext | -25℃~+85℃ 1 12.5mm 1x4P 2.5mm 250V 3.8mm 3A 4 4P 6mm Brass EH K Pin PA | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588891962850627584) |
| C161662 | EHR-5            | JST                       | P=2.5mm      | 0.04  | 19848 | Ext | -25℃~+85℃ 1 1x5P 2.5mm 5 EH Non-Latching PA66 UL94V-0 White Without Fi | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590164157103845376) |
| C263754 | S3B-EH(LF)(SN)   | JST                       | 弯插,P=2.5mm | 0.05  | 19235 | Ext | -25℃~+85℃ 1 10mm 1x3P 2.5mm 250V 3 3A 3P 4.2mm 8.2mm Brass EH K Pin PA | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588890020664631297) |
| C160255 | B6B-EH-A(LF)(SN) | JST                       | 插件,P=2.5mm | 0.10  | 17786 | Ext | -25℃~+85℃ 1 17.5mm 1x6P 2.5mm 250V 3.8mm 3A 6 6P 6mm Brass EH K Pin PA | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588890094401171456) |
| C265084 | B5B-EH(LF)(SN)   | JST                       | 插件,P=2.5mm | 0.08  | 17461 | Ext | -25℃~+85℃ 1 15mm 1x5P 2.5mm 250V 3.8mm 3A 5 5P 6mm Brass EH K Pin PA66 | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588890634539581440) |
| C265068 | S4B-EH(LF)(SN)   | JST                       | 弯插,P=2.5mm | 0.08  | 14051 | Ext | -25℃~+85℃ 1 12.5mm 1x4P 2.5mm 250V 3A 4 4.2mm 4P 8.2mm Brass EH K Pin  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8561889239836762112) |
| C493147 | B6B-EH(LF)(SN)   | JST                       | 插件,P=2.5mm | 0.08  | 14036 | Ext | -25℃~+85℃ 1 17.5mm 1x6P 2.5mm 250V 3.8mm 3A 6 6P 6mm Brass EH K Pin PA | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590164464289935360) |

### USB-A 3.0 receptacles

|   LCSC   |       MPN        |        Maker         | Pkg  | USD@1 | Stock | Lib |                               Description                                |                                                                   DS                                                                    |
|----------|------------------|----------------------|------|-------|-------|-----|--------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| C2689987 | U-A-39SS-W-1     | Korean Hroparts Elec | SMD  | 0.34  | 17803 | Ext | -40℃~+85℃ 1 1,200 times 1.5A 14.45mm 9P Female Surface Mount, Right An   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588902990447054849)                                                      |
| C2845330 | HC-ST-003-01-J   | HCTL                 | 弯插 | 0.13  | 11840 | Ext | -25℃~+70℃ 1 1.5A 1500 Cycles 30V 9P Female Right Angle Type-A USB 3.0    | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588944600710569984)                                                      |
| C7501847 | HC-USB3.0-L257-P | Hong Cheng           | 插件 | 0.32  |  7477 | Ext | -55℃~+85℃ 1 1.8A 25.7mm 9P Blue Female Type-A USB 3.0 Vertical, Flag 插  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8564881558952693760)                                                      |
| C2762983 | GT-USB-7061      | G Switch             | SMD  | 1.15  |  7261 | Ext | -40℃~+85℃ 1 10,000 Cycles 24P 24V 5A 6.5mm Black Female Surface Mount,   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588904167348056065)                                                      |
| C587839  | 484080003        | MOLEX                | 插件 | 1.39  |  7153 | Ext | -20℃~+85℃ 1 1.8A 30V 4P 5,000 cycles Blue Female Through Hole Type-A U   | [ds](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/484/48408/484080003_sd.pdf?inline\) |
| C2845335 | HC-ST-003-03-Z   | HCTL                 | 插件 | 0.50  |  6944 | Ext | -25℃~+70℃ 1 1,500 Cycles 1.5A 30V 9P Blue Female Type-A USB 3.0 Vertic   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588945520001208320)                                                      |
| C2895028 | USB-303WSD-BRY   | XUNPU                | 弯插 | 0.54  |  6908 | Ext | -30℃~+85℃ 1.8A 2 30V 9Px2 Blue Female Right Angle Type-A USB 3.0 弯插 US | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588919343220731904)                                                      |
| C598201  | ZX360D-B-10P(30) | HRS Hirose           | SMD  | 0.88  |  5814 | Ext | -30℃~+85℃ 1 10P 1A 30V Black Female Micro-B Surface Mount, Right Angle   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588918811743424512)                                                      |
| C7501852 | HC-USB3.0-C34-P  | Hong Cheng           | SMD  | 0.15  |  5321 | Ext | -25℃~+70℃ 1 1,500 Cycles 1.5A 14.2mm 30V 9P Blue Female Laminated boar   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8564880205945585664)                                                      |
| C2845339 | HC-ST-003-07-J   | HCTL                 | 插件 | 0.20  |  5121 | Ext | -25℃~+70℃ 1 1.5A 1500 Cycles 30V 9P Blue Female Through Hole Type-A US   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588944931548745728)                                                      |

### USB-C receptacles (full-featured, 24P, for SS upstream)

|   LCSC   |         MPN          |         Maker          | Pkg  | USD@1 | Stock  | Lib |                              Description                               |                                         DS                                         |
|----------|----------------------|------------------------|------|-------|--------|-----|------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C709357  | KH-TYPE-C-16P        | Shenzhen Kinghelm Elec | SMD  | 0.08  | 306224 | Ext | -40℃~+85℃ 1 10,000 cycles 16P 30V 3A 7.81mm Female Surface Mount, Righ | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588905154556923904) |
| C2906290 | TYPE-C 16P CB1.6 073 | SHOU HAN               | SMD  | 0.10  |  67009 | Ext | -25℃~+85℃ 1 16P 3A 5,000 cycles 5V Black Female Laminated board Type-C | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8756352867156267008) |
| C2894897 | HC-TYPE-C-16P-01A    | HCTL                   | SMD  | 0.10  |  58642 | Ext | -55℃~+85℃ 1 16P 20V 5A 7.35mm Black Female Surface Mount, Right Angle  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588941055828381696) |
| C2681555 | TYPE-C 24P QT        | SHOU HAN               | SMD  | 0.54  |  49139 | Ext | -30℃~+80℃ 1 10,000 Cycles 24P 3A Black Female Surface Mount, Right Ang | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8756352863621144576) |
| C6332304 | MC-118LD-H65         | Hanbo Electronic       | 插件 | 0.24  |  47034 | Ext | -55℃~+85℃ 1 10,000 cycles 16P 5A 6.5mm Black Female Through Hole Type- | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8590905213601456128) |
| C456013  | TYPE-C 24P QCHT      | SHOU HAN               | SMD  | 0.53  |  40629 | Ext | -40℃~+85℃ 1 10,000 Cycles 24P 30V 3A Black Female Surface Mount, Right | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8756352776610172928) |
| C3151749 | TYPE-C 16PLT-H10.0   | SHOU HAN               | SMD  | 0.31  |  37711 | Ext | -40℃~+85℃ 1 10,000 Cycles 16P 20V 5A Black Female Surface Mount,Vertic | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8756353202214318080) |
| C3151747 | TYPE-C 16PLC-H10.0   | SHOU HAN               | 插件 | 0.25  |  37474 | Ext | -40℃~+85℃ 1 10,000 Cycles 16P 20V 5A Black Female Through Hole Type-C  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8756353178290008064) |
| C3151751 | TYPE-C 24P-GTJB 040  | SHOU HAN               | SMD  | 0.14  |  36287 | Ext | 1 20V 24P 3A Black Clamping plate Male Type-C USB 3.1 SMD USB Connecto | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8756353218450739200) |
| C2927038 | USB-TYPE-C-018       | DEALON                 | SMD  | 0.04  |  30734 | Ext | -25℃~+85℃ 1 10000 times 16P 3A 5V 7.35mm Female Surface Mount, Right A | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8589041631273738240) |

### DC barrel jacks (19V in / 19V out, 5.5mm)

|  LCSC   |       MPN       |            Maker            |      Pkg      | USD@1 | Stock  | Lib |                               Description                                |                                         DS                                         |
|---------|-----------------|-----------------------------|---------------|-------|--------|-----|--------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C5665   | 2.54-2*5P简牛   | BOOMELE Boom Precision Elec | 插件,P=2.54mm | 0.10  | 173787 | Ext | -55℃~+105℃ 1A 2 2.54mm 2.54mm 2x5P 5 Black Brass Gold IDC Header Throu   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588887095892430848) |
| C3405   | 2.54-2*10P简牛  | BOOMELE Boom Precision Elec | 插件,P=2.54mm | 0.14  |  93443 | Ext | -55℃~+105℃ 10 2 2.54mm 2.54mm 2x10P 3A Black Brass Gold IDC Header Thr   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588887091699073024) |
| C3406   | 2.54-2*8P简牛   | BOOMELE Boom Precision Elec | 插件,P=2.54mm | 0.14  |  84059 | Ext | -55℃~+105℃ 1A 2 2.54mm 2.54mm 2x8P 8 Black Brass Gold IDC Header Throu   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588887091857645568) |
| C16214  | DC-005 2.0      | BOOMELE Boom Precision Elec | 插件          | 0.06  |  80482 | Ext | -25℃~+85℃ 12V 1A 2mm 6.4mm DC Power Jack Right Angle 插件 DC Power Conne | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588893543708430336) |
| C720557 | DC-005-A200     | XUNPU                       | 插件          | 0.14  |  76247 | Ext | -20℃~+70℃ 2mm 30V 3A 6.4mm DC Power Jack Right Angle 插件 DC Power Conne | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588896245406842880) |
| C11215  | 2.54-2*7P简牛   | BOOMELE Boom Precision Elec | 插件,P=2.54mm | 0.12  |  72094 | Ext | 2 2.54mm 2.54mm 2x7P 7 Brass Gold IDC Header Through Hole 插件,P=2.54mm  | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588887105196478464) |
| C319099 | DC-005-2.5A-2.0 | XKB Connection              | 插件          | 0.15  |  68583 | Ext | -20℃~+70℃ 2mm 6.2mm DC Power Jack Panel Mount 插件 DC Power Connectors R | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588896376420257792) |
| C5661   | 2.0-2*5P直简牛  | BOOMELE Boom Precision Elec | 插件,P=2mm    | 0.14  |  66118 | Ext | -40℃~+105℃ 1.5A 2 2mm 2mm 2x5P 5 Brass IDC Header Through Hole 插件,P=2m | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588887094123245568) |
| C431533 | DC005           | SHOU HAN                    | 插件          | 0.05  |  64903 | Ext | -30℃~+70℃ 12V 2mm 500mA 6.3mm DC Power Jack Right Angle 插件 DC Power Co | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8756921126923067392) |
| C9136   | 2.54-2*6P简牛   | BOOMELE Boom Precision Elec | 插件,P=2.54mm | 0.12  |  55509 | Ext | -55℃~+105℃ 1A 2 2.54mm 2.54mm 2x6P 6 Black Brass Gold IDC Header Throu   | [ds](https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8588887100536471552) |

### Follow-up: parts crowded out of the top-N above

|  LCSC   |       MPN        |        Maker         |      Pkg       | USD@1 | Stock | Lib |                               Description                                |
|---------|------------------|----------------------|----------------|-------|-------|-----|--------------------------------------------------------------------------|
| C398546 | B3B-EH(LF)(SN)   | JST                  | 插件,P=2.5mm   | 0.04  |  2502 | Ext | -25℃~+85℃ 1 10mm 1x3P 2.5mm 250V 3 3.8mm 3A 3P 6mm Brass EH K Pin PA66   |
| C160259 | B3B-EH-A(LF)(SN) | JST                  | 插件,P=2.5mm   | 0.06  |  8317 | Ext | -25℃~+85℃ 1 10mm 1x3P 2.5mm 250V 3 3.8mm 3A 3P 6mm Brass EH K Pin PA66   |
| C720557 | DC-005-A200      | XUNPU                | 插件           | 0.14  | 76247 | Ext | -20℃~+70℃ 2mm 30V 3A 6.4mm DC Power Jack Right Angle 插件 DC Power Conne |
| C10430  | SN74LVC2G241DCUR | Texas Instruments    | VSSOP-8        | 0.51  |  2681 | Ext | -40℃~+85℃ 1 1.65V~5.5V 10uA 2 32mA 32mA 4.1ns@3.3V,50pF 74LVC Power-of   |
| C99257  | SN74LVC2G241DCUT | Texas Instruments    | VSSOP-8        | 0.40  |   303 | Ext | -40℃~+125℃ 1 1.4ns@3.3V,50pF 1.65V~5.5V 10uA 2 32mA 32mA 74LVC Tri-Sta   |
| C138714 | TPD4E05U06DQAR   | Texas Instruments    | USON-10(1x2.5) | 0.08  | 94387 | Ext | -40℃~+125℃ 0.5pF 10nA 14V 2.5A@8/20us 40W@8/20us 5.5V 6.5V ESD Four ch   |
| C431092 | XT30PW-M30.G.Y   | Changzhou Amass Elec | -              | 0.38  | 40696 | Ext | -、Aviation model plug 1.2mΩ 15A 16/18/20AWG 2pin DC 500V Male - Power   |
| C428721 | XT30UPB-M        | Changzhou Amass Elec | -              | 0.26  | 72201 | Ext | -、Aviation model plug 0.65mΩ 15A DC 500V Gold Plated Male PA Yellow -   |
