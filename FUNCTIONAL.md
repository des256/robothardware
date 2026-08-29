# FUNCTIONAL — Robot Backbone PCB

What the board *does*, seen from its connectors and from the Jetson's software.
[`HARDWARE.md`](HARDWARE.md) is the how-and-with-what; this document is the
what, so everyone — hardware, firmware, robot software — shares one picture
before the first schematic sheet is drawn. Facts below come from the datasheets
in [`datasheets/`](datasheets/README.md); anything not yet nailed down is an
explicit **Decision** (D‑n) or **Verify** (V‑n) item, collected in §10.

> **Status: draft for review.** D1 (which servos, on which rail) changes the
> power sheets and the connector story; settle it first.

## 1. The board in one paragraph

A self-powered USB 3.0 hub plus a servo-bus controller plus a power
distribution board, in one PCB. It takes 19 V from a laptop adapter, passes it
through to the Jetson Orin NX, and makes three more rails: 12 V and 5 V for
servo buses and 5 V for USB. The Jetson talks to the board over one USB-C
cable; behind that the board presents three generic USB 3.0 ports (RealSense,
ReSpeaker, whatever comes next) and four independent Dynamixel servo buses,
each usable in RS-485 or TTL mode. Every external connector is fused/limited,
ESD-protected and hot-plug tolerant. Nothing on the board runs firmware — it is
all hardware behaviour plus standard Linux USB drivers.

## 2. External interfaces

| # | Connector | Qty | Direction | Carries | Rail / limit |
|---|-----------|-----|-----------|---------|--------------|
| J1 | 19 V IN — XT30PW-M | 1 | in | Adapter power | 19 V, adapter-rated (§4 budget); TVS + ideal diode + fuse behind it |
| J2 | 19 V OUT — XT30PW-M (or barrel, D6) | 1 | out | Jetson carrier power | 19 V passthrough, fused ~3 A class |
| J3 | USB-C upstream — 24-pin receptacle | 1 | in (host) | USB 3.0 SS + USB 2.0 from Jetson | VBUS *not* used for power (§6) |
| J4–J6 | USB-A 3.0 downstream | 3 | out (device side) | USB 3.0 SS + 2.0, generic | +5V_USB, 1.5 A each, switched |
| J7–J10 | Servo RS-485 — JST B4B-EH-A | 4 | bus | `1 GND · 2 VDD · 3 D+ · 4 D−` | +12V_SERVO, per-port e-fuse |
| J11–J14 | Servo TTL — JST B3B-EH-A | 4 | bus | `1 GND · 2 VDD · 3 DATA` | +5V_SERVO (**D1**), per-port e-fuse |
| — | Test points, rail LEDs, mode jumpers | — | — | Bring-up (§9) | — |

Pinouts are ROBOTIS's (`datasheets/reference/robotis/`). RS-485 and TTL
connectors of the same servo port share one UART; one is populated with a
cable at a time (§5.3).

## 3. Block diagram

```
                J1 19V IN
                   │
     [fuse]─[ideal diode LM74700]─[TVS SMBJ24A]─[bulk]──── +19V_IN
                   │
     ┌─────────────┼──────────────────────┬──────────────────────┐
     │             │                      │                      │
 [fuse/switch]  [Buck A  LM5145]      [Buck B  LM5145]      [Buck C  TPS54560]
     │          +12V_SERVO 10–20 A     +5V_SERVO 5–10 A      +5V_USB 5 A
  J2 19V OUT       │                      │                      │
  (Jetson)   ┌─────┼─────┐          ┌─────┼─────┐         ┌──────┼──────┐
             4× [eFuse+cap+TVS]     4× [eFuse+cap+TVS]    3× [SY6280 1.5A] [TLV62569]
             J7–J10 VDD             J11–J14 VDD           J4–J6 VBUS      +3V3 ─┐
                                                                                │
 ──────────────────────────── data ─────────────────────────────────────────────┤
                                                                                │
  J3 USB-C ──[HD3SS3220 CC + SS mux]──┐                                         │
   (Jetson host)                      ▼                          hub core LDO ◄─┤
                             [TUSB8041 4-port hub]  ◄── 3V3, 1V1               │
                    ┌────────┬────────┼──────────────┐                          │
                   DS1      DS2      DS3            DS4 (USB 2.0 only)          │
                    │        │        │              │                          │
                 J4 USB-A  J5 USB-A  J6 USB-A     [CH344Q quad UART] ◄── 3V3 ───┘
                 (SS+HS)   (SS+HS)   (SS+HS)         │  │  │  │
                                            4× ─────┘  │  │  └───── UARTx: TXDx RXDx TNOWx
                                                       ▼
                                          ┌── per servo port ──────────────────────┐
                                          │  TNOWx ─┬─► SP3485EN  DE, R̄E̅ ─► A/B ─► J7+n (RS-485)
                                          │         └─► LVC2G241  2OE, 1OE̅ ─► DATA ─► J11+n (TTL)
                                          │  TXDx ──► both drivers      RXDx ◄── one receiver (mode jumper)
                                          └─────────────────────────────────────────┘
```

Net names that the automation checks (HARDWARE.md §8): `VBUS` is reserved for
the upstream USB-C VBUS; the servo rails are `+12V_SERVO` / `+5V_SERVO`; the
USB rail is `+5V_USB`; every load symbol carries `max_mA`.

## 4. Power domains

| Rail | Source | Feeds | Budget (worst case) | Protection at the load | Enable / sequencing |
|------|--------|-------|---------------------|------------------------|---------------------|
| +19V_IN | Adapter via fuse, LM74700 ideal diode, SMBJ24A, bulk caps | Everything | Adapter rating (**D1** sets it; HARDWARE.md §2 example lands ~240 W) | Reverse polarity blocked; surge clamped ~39 V, hence 60 V-rated bucks | Present whenever the adapter is |
| +19V_JETSON (J2) | +19V_IN via fuse / load switch | Jetson carrier | ~40 W → ~2.1 A | Fuse | Same as input (Jetson boots as soon as power arrives) |
| +12V_SERVO | Buck A (LM5145 + FETs) | 4× RS-485 servo ports | Sum of stall of the RS-485 fleet, bounded by per-port e-fuses | Per port: e-fuse (TPS1663x class), ≥ 470 µF low-ESR, SMBJ13A | Up at power-on; per-port e-fuse soft-start staggers inrush (**D3**: always-on vs software-controlled) |
| +5V_SERVO | Buck B (same LM5145 design, 5 V divider) | 4× TTL servo ports | Sum of stall of the TTL fleet, bounded by per-port e-fuses | Per port: e-fuse (TPS25961 class if ≤ 2 A, else TPS1663x), ≥ 470 µF, SMBJ6.0A | As above. **Never merged with +5V_USB** |
| +5V_USB | Buck C (TPS54560) | 3× VBUS switches + 3V3 buck | 3 × 1.5 A + 3V3 load ≈ 5 A | Per port: SY6280 current limit 1.5 A, fault → hub | Port VBUS switched on by the hub (`PWRCTLx`) after enumeration |
| +3V3 | TLV62569 from +5V_USB | Hub I/O, HD3SS3220, CH344Q, transceivers, buffers | < 0.5 A | — | Up with +5V_USB |
| +1V1_HUB | LDO per TUSB8041 datasheet (0.99–1.26 V) | Hub core | per DS | — | Sequenced per hub DS |
| VBUS (upstream) | Jetson, through J3 | HD3SS3220 `VBUS_DET` (900 kΩ) and TUSB8041 `USB_VBUS` (90.9 kΩ divider) — **detection only** | ~0 | < 10 µF total on this net (USB inrush rule; `kkh` checks it) | — |

### 4.1 Fleet worksheet (input to D1)

ROBOTIS's own figures (`datasheets/reference/robotis/dxl_x_info.yml`): stall
current at rated voltage, and — the important part — which rail each family
actually wants.

| Family | Bus | Input voltage (recommended) | Stall current | Notes |
|--------|-----|-----------------------------|---------------|-------|
| XL330-M077 / M288 | TTL, **3.3 V logic** (5 V compatible) | 3.7–6.0 V (**5 V**) | 1.11 A @ 3.7 V | The only family that is genuinely a 5 V servo |
| XC330-M181 / M288 | TTL, 3.3 V logic | 3.7–6.0 V (**5 V**) | 1.34 A @ 3.7 V | |
| XC330-T181 / T288 | TTL, 5 V logic | 6.5–12.0 V (**11.1 V**) | 0.61 A @ 9 V | Same 3-pin EH connector as the 5 V units |
| XL430-W250 (and 2XL430) | TTL, 5 V logic | 6.5–12.0 V (**11.1 V**) | 1.0 A @ 9 V | |
| XC430-W150 / W240 (and 2XC430) | TTL, 5 V logic | 6.5–14.8 V (**12 V**) | 1.1 A @ 9 V | |
| XM430-W210 / W350 | RS-485 (-R) **or** TTL (-T) | 10–14.8 V (**12 V**) | 2.1 A @ 11.1 V | |
| XH430-W210 / W350 | RS-485 or TTL | 10–14.8 V (**12 V**) | 1.2 A @ 11.1 V | |
| XH430-V210 / V350 | RS-485 | **24 V** | 0.7 A @ 24 V | Not supported by this board (no 24 V rail) |
| XM540-W150 / W270 | RS-485 or TTL | 10–14.8 V (**12 V**) | 4.2 A @ 11.1 V | |
| XH540-W150 / W270 | RS-485 or TTL | 10–14.8 V (**12 V**) | 4.5 A @ 11.1 V | |
| XW430 / XW540-T | RS-485 | 10–14.8 V (**12 V**) | 1.2 / 4.5 A | IP-rated |

Baud: 9.6 kbps – 4 Mbps (X330) or 4.5 Mbps (others). Protocol 2.0 throughout.

**What this means (D1):** HARDWARE.md pairs "TTL ↔ 5 V" and "RS-485 ↔ 12 V",
but only the X330-M family is a 5 V servo. Every other TTL X-series servo
(XL430, XC430, XM430-T, XH430-W-T, XC330-T) is a **12 V servo on the same
3-pin EH connector** — the connector keying does *not* separate 5 V from 12 V
TTL servos. The board therefore has to choose what VDD its 3-pin ports carry:

- **(a) 5 V** — as drafted. Supports X330-M only on the TTL ports; every 12 V
  servo must be an RS-485 variant on the 4-pin ports.
- **(b) 12 V on both connector types** — one servo rail, one buck; TTL ports
  serve XL430/XC430/XM430-T; X330-M units are then *excluded* (plugging one in
  destroys it — no keying protects against it).
- **(c) Per-port VDD select (jumper)** — flexible, but the failure mode of (b)
  becomes a jumper mistake. Only worth it with an idiot-proof mechanism.

Pick the fleet, then the option; the power sheets follow from that.

## 5. Servo subsystem — behaviour

### 5.1 Topology

One CH344Q on hub port DS4 (USB 2.0 High-Speed, 480 Mbps) exposes **four
independent UARTs**. UARTx drives servo port *x* (x = 0..3). The mapping UART
index → physical port is fixed by copper, so software may rely on it (contrast
with the USB-A ports, §6.3). Each port has both a 4-pin RS-485 and a 3-pin TTL
connector; both physical layers hang off the same UART.

### 5.2 Direction control — TNOW

- CH344Q provides **per-UART `TNOWx`** on the `DTRx/TNOWx/GPIOx` pins (Q
  package pins 39, 18, 19, 34). Each pin becomes TNOW instead of DTR when the
  chip sees a **pull-down resistor on that pin at power-on** (4.7 kΩ to GND
  is the value the datasheet uses for the same mechanism on the L variant).
  Per-pin, independent, no software involvement — the WCH `ch343` driver
  contains no TNOW/RS-485 handling at all, which is what we want.
- Semantics (datasheet, translated): "RS-485 transmit/receive control pin of
  the corresponding UART" — asserted while the UART is shifting out data.
- **V1 — polarity.** The Chinese CH344DS1 does not state the level explicitly.
  WCH's family convention is active-high (matches DE on a transceiver
  directly); confirm on the existing CH344Q dongle with a scope before the
  front-end sheet is finalised — if it is active-low, one inverter per port or
  the two-chip '126/'125 alternative fixes it.
- **V2 — release timing.** How long after the last stop bit TNOW de-asserts is
  not specified. Dynamixel **Return Delay Time** defaults to 250 × 2 µs =
  500 µs but can be set to 0 (2 µs) — at 1 Mbps that is two bit times. Until
  the release latency is measured, the servo software keeps Return Delay Time
  at a value comfortably above it (default is fine). This is the one place the
  board's behaviour and the servo configuration have to agree.

### 5.3 Front-end per port

Mirrors ROBOTIS's recommended circuits exactly (`datasheets/reference/robotis/`),
with TNOW playing the role of ROBOTIS's `TX_Enable`:

| Signal | RS-485 path (SP3485EN, 3.3 V) | TTL path (SN74LVC2G241, 3.3 V) |
|--------|-------------------------------|--------------------------------|
| TXDx | `DI` | `2A` → `2Y` = DATA |
| Transmit gate | `DE` = TNOWx (active-high) | `2OE` = TNOWx (active-high) |
| Receive gate | `R̄E̅` = TNOWx **when this mode is selected**, else tied high (receiver off) | `1OE̅` = TNOWx **when this mode is selected**, else tied high (receiver off) |
| RXDx | `RO` | `1Y` |
| Bus | A = D+ (pin 3), B = D− (pin 4) | DATA (pin 3), 10 kΩ pull-up to 3.3 V |
| Pull-ups | RXDx 10 kΩ to 3.3 V (CH344Q has internal pull-ups on RXD0–2 but **RXD3 needs an external one** — fit all four for uniformity) | same RXDx pull-up; TNOW line 10 kΩ pull-down (idle = receive, as ROBOTIS) |
| Protection | SM712 on A/B, 120 Ω termination as 0 Ω-option | 5 V-working TVS on DATA, ~10–22 Ω series |

Behavioural consequences:

- **Transmit:** TNOW high → both drivers active. The RS-485 driver copies the
  packet onto A/B, the '241 copies it onto DATA. The unused connector carries a
  harmless copy.
- **No echo, either mode:** TNOW high also disables *both* receivers, so the
  UART never hears its own packet. Echo behaviour is identical on all four
  ports and both modes; the servo software needs no per-port special-casing.
- **Receive:** TNOW low → drivers Hi-Z, the *selected* receiver drives RXDx.
  The other receiver is held disabled (Hi-Z) — its output is wire-ORed on the
  same RXDx net, which is safe precisely because at most one is ever enabled.
- **Mode select (D2):** a per-port 3-pin jumper / solder bridge routes TNOWx
  to exactly one receiver-enable and leaves the other pulled inactive. Default
  bridge position is per fleet (D1). Software control via CH344Q GPIO is
  possible later (the CTS/RTS pins double as GPIO0–7) but ROBOTIS's own U2D2
  keeps *both* receivers enabled and relies on unique IDs — we deliberately
  don't, because two enabled receivers wire-ORed on RXD corrupt each other's
  packets and the U2D2 documents that failure mode.
- **Levels:** everything runs at 3.3 V (CH344Q native). ROBOTIS specifies the
  3.3 V '241 circuit for X330 and the 5 V one for the rest; LVC inputs are
  5 V-tolerant and a 3.3 V high clears the 5 V-logic servos' TTL threshold, so
  the 3.3 V build serves both — the pull-up on DATA stays at 3.3 V.
- **Speed:** CH344Q ≤ 6 Mbps, SP3485EN 10 Mbps, LVC2G241 far above — the
  4.5 Mbps Dynamixel ceiling is covered on every port.

### 5.4 Servo power ports

Per port, on the rail the port's mode uses: e-fuse → local bulk capacitor
(≥ 470 µF low-ESR, at the connector) → TVS → connector VDD.

- **Overcurrent / short on one bus:** its e-fuse limits, then trips; the other
  three buses and the rest of the board are unaffected (**D3**: latch-off with
  manual reset vs auto-retry; and whether the enable is software-controlled for
  a per-bus e-stop and staggered power-up).
- **Regenerative back-EMF:** the buck cannot sink; the local + shared bulk
  absorbs, the TVS clamps the rest (SMBJ13A on 12 V, SMBJ6.0A on 5 V).
- **Star distribution:** each port gets its own pour from the buck's bulk bank
  so one bus's stall sag does not appear on another.

## 6. USB subsystem — behaviour

### 6.1 Upstream (J3, USB-C, Jetson is host)

HD3SS3220 in **UFP, GPIO mode** — no I2C, no software: `PORT` tied low (UFP),
`ADDR` left open (GPIO mode), `ENn_CC` low (enabled), `VBUS_DET` from the
connector's VBUS through 900 kΩ. The CC logic detects attach and orientation;
the integrated 2:1 mux routes the live SuperSpeed pair to the hub. Result:
USB 3.0 works in **both plug orientations**. `CURRENT_MODE` is don't-care in UFP.

**VBUS is never a power source.** It only reaches the two detection inputs
(HD3SS3220 `VBUS_DET`, TUSB8041 `USB_VBUS` divider). The board is self-powered:
the Jetson cannot back-power it, it cannot back-power the Jetson, and the
< 10 µF rule on the `VBUS` net keeps the Jetson's port happy at attach.

### 6.2 Hub (TUSB8041)

- Self-powered 4-port hub; VID/PID and port configuration by **pin strapping**
  (no EEPROM, no I2C) unless a reason appears (**D5**).
- DS1–DS3 → J4–J6, full SuperSpeed + High-Speed. DS4 → CH344Q, USB 2.0 only;
  its SS pins are unused (**V5**: the datasheet has no explicit unused-SS-port
  note — take the termination from the EVM guide or TI E2E before ERC).
- Per port: `PWRCTLx` → VBUS switch `EN`; `OVERCURxz` ← switch fault. The hub
  turns port power on after the upstream connection is established and reports
  over-current to the host as a standard hub status change, so Linux logs the
  event and the OS/driver can react — no custom software.
- Rails: 3.3 V I/O + 1.1 V core (LDO per DS), 24 MHz crystal, `GRSTz` reset.
- Suspend: the hub follows USB suspend from the host; downstream port power
  behaviour in suspend is a strap option (**D5**).

### 6.3 Generic downstream ports (J4–J6)

- Identical wiring, identical 1.5 A limit (SY6280 `Rset` per `Ilim = 6800/Rset`),
  identical ESD (TPD4E05U06 on SS, USBLC6-2 on D+/D−). Any device fits any port.
- **Software contract:** devices are identified by **VID/PID** (as the existing
  ReSpeaker udev rule already does). Nothing may key on `/dev/serial/by-path`
  or USB topology for J4–J6, because a device can move ports. The servo UARTs
  are the exception: CH344Q interface *n* ↔ servo port *n* is fixed.

### 6.4 What Linux sees

```
Jetson USB-C (host)
└── TUSB8041 hub (USB 3.0 + companion USB 2.0 hub, as all SS hubs)
    ├── port 1: whatever is on J4 (e.g. RealSense D435 — SS)
    ├── port 2: whatever is on J5 (e.g. ReSpeaker — HS)
    ├── port 3: whatever is on J6
    └── port 4: CH344Q → 4 serial interfaces (ttys via WCH ch343 driver — already verified on this kernel)
```

## 7. Power-up, hot-plug and fault behaviour

| Event | Board behaviour |
|-------|-----------------|
| Adapter connected | Ideal diode conducts, bucks start (all rails up, within their soft-start), Jetson receives 19 V and boots. Servo rails are live before any USB activity; servo ports power up staggered by e-fuse soft-start (D3). |
| Reverse-polarity adapter | LM74700 keeps the FET off — nothing conducts. |
| Input surge / adapter overshoot | SMBJ24A clamps; downstream bucks are 60 V-rated so they survive the clamp voltage. |
| USB-C plugged (either orientation) | HD3SS3220 detects, selects SS lane; hub enumerates as self-powered; hub enables J4–J6 VBUS. |
| Device plugged into J4–J6 | Enumerates. Over 1.5 A → switch limits, asserts fault → hub reports over-current → host disables the port. |
| Servo plugged in hot | Local bulk cap charges through the e-fuse's current limit (no spark-inrush on the shared rail). |
| Servo stall on bus *n* | Rail sags locally; star pour + local bulk keep buses ≠ *n* clean; per-port e-fuse bounds the current. |
| Servo back-driven / decelerating | Rail rises; caps absorb, TVS clamps; the buck stops switching (**V3**: confirm LM5145 output-overvoltage behaviour). |
| Crushed servo cable (short) on bus *n* | e-fuse on bus *n* trips; other buses and the robot keep running. |
| Jetson powered off / USB-C unplugged | Servo rails stay up (they don't depend on USB); hub drops port power per its strap; nothing back-feeds. |

## 8. What software needs to know (contract)

1. Three generic USB 3.0 ports; identify devices by VID/PID only.
2. Four servo buses = four CH344Q UART interfaces, fixed index ↔ port.
3. Both bus modes look identical to software: same framing, no echo, same
   direction timing. Only the physical layer (jumper) differs.
4. Keep Dynamixel Return Delay Time at default until V2 is measured.
5. Over-current on a USB port arrives as a normal hub over-current event.
6. Servo bus power is not software-visible unless D3 chooses GPIO-controlled
   e-fuses (then: per-bus enable/e-stop, staggered start).

## 9. Bring-up and test features

Test point on every rail and on TXD/RXD/TNOW/A/B/DATA of every servo port;
power-good LED per rail; 0 Ω options for RS-485 termination, mode-select
defaults and the VBUS-detect dividers; `${KKH_VERSION_DATE}` on the silkscreen;
mounting holes. Bring-up order per HARDWARE.md §7: rails alone → scope → hub →
servos → RealSense last.

## 10. Open decisions and verifications

| ID | Item | Affects | Owner |
|----|------|---------|-------|
| **D1** | Servo fleet: models × count per bus → rail per connector type (§4.1 options a/b/c), buck currents, e-fuse classes, adapter wattage | Power sheets, connectors, budget | Robot design |
| **D2** | Mode-select mechanism: solder bridge / jumper (recommended) vs CH344Q GPIO | Servo-port sheet | HW |
| **D3** | Servo e-fuse behaviour: latch vs auto-retry; enable always-on vs GPIO (per-bus e-stop, staggered start) | Servo power sheet, software contract §8.6 | HW + SW |
| **D4** | Hub chip: TUSB8041 vs alternatives, after checking librealsense issue history | Hub sheet | HW |
| **D5** | Hub configuration: pure pin-strap vs EEPROM (custom VID/PID, suspend port-power behaviour) | Hub sheet | HW |
| **D6** | Jetson carrier model → accepted input range/polarity, J2 connector type | Input sheet | Robot design |
| **V1** | TNOW polarity on CH344Q (scope the existing dongle) | Front-end gating; may add inverter | HW |
| **V2** | TNOW release latency after stop bit vs Dynamixel Return Delay Time | Software contract §8.4 | HW + SW |
| **V3** | LM5145 behaviour on output overvoltage from regen (stops switching?) | Servo rail protection | HW |
| **V4** | Every imported footprint against its datasheet drawing (HARDWARE.md §7) | Everything | HW |
| **V5** | Termination of the unused SS pins on hub port DS4 | Hub sheet | HW |
