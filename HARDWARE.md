# HARDWARE — Robot Backbone PCB

Design notes for the power-and-interconnect motherboard: USB 3.0 hub with three
generic downstream ports (RealSense D435, ReSpeaker 4-mic array, future
hardware), four dual-mode servo buses (RS-485 @ 12 V or TTL @ 5 V) via a CH344,
and step-down converters feeding the Jetson Orin NX and peripherals.

> **Status: design guidance, not a finished design.** Every part number below is a
> *candidate* to be verified against its datasheet and current stock — nothing here
> substitutes for the reference design in each datasheet.

## 1. System architecture

```
19V laptop adapter ──► [fuse + reverse-polarity ideal diode + TVS + bulk caps]
                            │
        ├──► 19V passthrough ──► [fuse/load switch] ──► 19V out (Jetson Orin NX)
        ├──► Buck #1: 12V ──► star ──► 4× [e-fuse + bulk caps + TVS] ──► 4-pin RS-485 connectors
        ├──► Buck #2: 5V servo ──► star ──► 4× [e-fuse + bulk caps + TVS] ──► 3-pin TTL connectors
        └──► Buck #3: 5V USB @ ~5A ──► 3× VBUS switches ──► USB-A 3.0 sockets
                       │
                       └──► 3.3V (small buck or LDO) ──► hub, CH344, bus front-ends

USB-C (from Jetson, upstream) ──► [CC controller + SS mux] ──► USB 3.0 hub (4-port)
        ├── ports 1–3 (SS): generic USB-A 3.0 ──► RealSense, ReSpeaker, future hardware
        └── port 4 (USB2 only): CH344 ──► 4× dual-mode front-ends ──► RS-485 or TTL connector
```

Key insight: the Jetson is both a *load* (19V out) and the *USB host* (USB-C in).
The board is a **self-powered hub** — that has consequences (see §3, USB rules).

## 2. Power budget first — everything else follows from it

Build this table before picking any converter. Worst case, not typical:

| Rail | Loads | Estimate |
|------|-------|----------|
| 19V passthrough | Orin NX at MAXN (clocks pinned per README) + carrier | ~40 W (the Jetson's own USB loads live on *this* board, so it stays moderate — check the carrier's spec) |
| 12V servo (RS-485 buses) | RS-485 servo fleet. Sum-of-stall (~2 A @ 12 V per Dynamixel-X-class servo) is the conservative ceiling; size for the worst *simultaneous* mechanical load you can justify and let per-bus e-fuses bound the rest (§5) | 10–20 A depending on fleet |
| 5V servo (TTL buses) | TTL servo fleet — same sizing philosophy. XL330-class servos stall around 1–1.5 A each (verify per model). **Never shared with the USB 5 V rail** | 5–10 A depending on fleet |
| 5V USB | 3 generic ports × per-port current limit (~1.5 A each) + the 3.3 V rail derived from this (quiet) rail. **Generic ports mean sizing for the sum of the limits, not for a known device list** | ~5 A |
| 3.3V | Hub + CH344 + bus front-ends | < 0.5 A |

Sum at ~85% converter efficiency: a build with a 10 A 12 V budget and a 5 A TTL
budget lands around **~240 W peak** (≈141 W + ≈29 W for the servo rails + ≈29 W
USB + ~40 W Jetson). Big laptop bricks top out around 230–330 W — **spec the
adapter from this table, not from habit**, and recompute when the servo fleet
changes. A 90 W adapter will brown out during a servo stall while the Jetson is
at MAXN — the classic "robot reboots when the arm hits something" bug.

## 3. Component selection, block by block

### Input protection (19V)

Blade fuse or high-current polyfuse → reverse-polarity protection with an
ideal-diode controller + N-FET (e.g., LM74700-Q1) rather than a lossy series diode
(at 6 A a Schottky wastes ~3 W) → TVS with standoff above the adapter's max
(19 V + 10% → something like an SMBJ24A, which clamps near 39 V — so every
downstream converter needs Vin(max) well above that; hence 60 V-rated bucks) →
bulk electrolytics.

### Step-down converters

- 12 V at four-bus current (10–20 A) is beyond single-chip bucks — use a
  controller + external FETs (LM5145 class) or a validated power module. The same
  controller design can be reused for the 5 V servo rail with a different
  feedback divider — good BOM consolidation.
- 5 V servo rail: sized to the TTL fleet (§2); a single-chip 5 A part suffices
  only for a small fleet.
- 5 V USB at ~5 A sits right at the edge of a single-chip part like the TPS54560
  (4.5–60 V, 5 A): either bound the per-port limits so the sum fits (e.g.,
  3 × 1.3 A), or reuse the controller-based design here too.
- Use TI WEBENCH / the vendor's design tool for inductor and compensation values,
  then **copy the datasheet layout example exactly** — buck layout is not a place
  for creativity.
- 3.3 V via a small buck (TPS62-class) or LDO (if confirmed < ~300 mA), fed from
  the **quiet USB 5 V rail — never the servo rails**.
- USB 3.0 hub chips also need a core rail (1.1/1.2 V) — follow the hub datasheet's
  reference design, usually a dedicated LDO.

### USB 3.0 hub

4-port SuperSpeed hub controller — candidates: Microchip USB5744, TI TUSB8041,
VIA VL817. Selection criteria: in stock at LCSC/Digi-Key, a public reference
schematic, and (this matters) evidence people run RealSense cameras through it —
the D435 is notoriously picky about marginal USB3 links, and the librealsense
GitHub issues are full of hub horror stories. Search for hubs the RealSense
community has validated.

### Generic downstream ports

All three non-CH344 downstream ports are wired identically as USB-A 3.0: full
SuperSpeed pairs, same ESD array, same per-port power switch. Consequences:

- Any device fits any port. The RealSense needs SuperSpeed; the ReSpeaker is
  USB 2.0 and works fine in a USB 3.0 socket (the USB2 pins are a superset).
- Cost vs. dedicated ports: two extra SS pair routes + ESD arrays — cheap for the
  flexibility.
- **Per-port current limits must be identical (~1.5 A)** since you no longer know
  which device lands where, and the 5 V USB rail must be sized for the *sum* of
  the limits plus the 3.3 V derivation (§2) — not for the known device list.
- Software should identify devices by VID/PID (as the existing ReSpeaker udev
  rule already does), never by physical port position — anything keyed to
  `/dev/serial/by-path` or USB topology breaks when a device moves ports.

### USB-C upstream — a real gotcha

For SuperSpeed to work in *both* plug orientations, a device needs a CC controller
+ 2:1 SS mux (e.g., TI HD3SS3220 — the standard part for exactly this). Without
it, wire Rd (5.1 kΩ) pull-downs on CC1/CC2 and SS only links in one orientation,
silently falling back to USB 2.0 in the other — which for the D435 means depth
streams fail mysteriously. Budget the mux.

### Self-powered hub rules

- Do **not** connect upstream VBUS to the 5 V rail — the Jetson must not
  back-power the board or vice versa. Upstream VBUS goes only to the hub's
  VBUS-detect pin (through the divider the datasheet specifies).
- Downstream, give each USB-A socket a current-limiting power switch (TPS2553
  single / TPS2561A dual), fault flag wired to the hub's overcurrent-sense pins.
- Set all three port limits identically (~1.5 A) — generic ports, unknown
  placement (see above).

### Servo buses — CH344, four dual-mode ports (RS-485 or TTL)

- The **CH344 is a quad-UART bridge** — one USB 2.0 hub port in, four independent
  UARTs out. Each UART feeds a **dual-mode front-end**: a 4-pin RS-485 connector
  (12 V power) *and* a 3-pin TTL connector (5 V power), with one mode in use per
  port.
- **Both modes speak the same UART framing and protocol** — the difference is
  physical layer only. RS-485: differential A/B pair. TTL: single-ended,
  single-wire half-duplex — TX and RX share one DATA line that idles high via a
  pull-up.
- **RS-485 side:** one transceiver per port. With TNOW available (below), a plain
  DE/R̄E̅ transceiver (THVD1450-class) is preferred over auto-direction parts —
  one direction scheme serves both modes.
- **TTL side:** one tri-state buffer per port (SN74LVC2G241-class). Its two
  complementary output enables make a single chip a complete half-duplex
  front-end — one gate drives TXD onto DATA when enabled, the other feeds DATA
  back to RXD. This mirrors ROBOTIS's own U2D2 reference circuit — pull up that
  schematic as the golden reference.
- **Direction:** the CH344's per-UART TNOW pin (asserts during transmission)
  drives both the RS-485 DE and the '241 enables. Verify TNOW polarity against
  the enable pins — a tiny inverter may be needed.
- **Mode select (the either/or):** TXD may fan out to both drivers permanently —
  the unused connector just carries a harmless copy. **RX is the only conflict:**
  exactly one receiver may drive the UART RXD pin. A per-port jumper /
  solder-bridge (or GPIO) enables one receiver — transceiver R̄E̅ vs. '241 RX
  gate — with both outputs wire-OR'd onto RXD through a pull-up.
- **Echo symmetry:** gate both receivers off during TNOW so neither mode echoes
  the transmitted packet — echo behavior stays identical across all ports and
  modes, and the servo software needs no per-port special-casing.
- **Levels:** run logic at 3.3 V (the CH344's native level). LVC buffers are
  5 V-tolerant, so a 5 V-pulled DATA line is fine, and 3.3 V drive meets TTL
  thresholds — but check the specific servo's DATA-pin spec (XL330-class 5 V
  servos have 3.3 V-compatible logic; verify per model).
- **TTL caution:** single-ended means far less noise immunity than RS-485 on a
  robot full of motors — keep TTL runs short, ground solid, ESD TVS on DATA
  (5 V working-voltage part), optional small series resistor (~10–22 Ω).
- Check the transceiver's, buffer's, and CH344's max data rates against the servo
  protocol (Dynamixel Protocol 2.0 commonly runs 57.6 kbps–1 Mbps+).
- **Driver check before committing:** confirm how the CH344 enumerates on the
  L4T/Jetson kernel — the four ttys typically come from WCH's out-of-tree `ch343`
  serial driver; verify it builds for aarch64. Cheapest test: a CH344 dongle
  before the board exists.
- Why four buses: RS-485/TTL are multi-drop, so one bus *could* daisy-chain every
  servo — the four buses exist for **control bandwidth** (each bus polls fewer
  servos per cycle → lower feedback latency), plus fault isolation and per-limb
  home-run cabling.

### Connectors

- RS-485 mode: Dynamixel-X RS-485 servos use a JST EH 4-pin (GND, V+, D+, D−) —
  match the servo's actual pinout *from its manual*.
- TTL mode: bigger X-series TTL servos use a JST EH 3-pin (GND, V+, DATA);
  XL330-class servos use a smaller housing — check the manual.
- **The different 3-pin/4-pin housings double as keying**: a 5 V TTL servo
  physically can't be plugged into a 12 V RS-485 connector. Preserve that
  property when picking connectors.
- Mind per-contact current ratings (EH-class contacts are good for ~2–3 A — a
  daisy-chain of stalling servos can exceed that even on a single bus).
- Barrel jacks are often rated only ~5 A; adequate for ~40 W at 19 V but check the
  specific part. Verify the Jetson carrier's accepted input range and polarity
  before committing (official carriers take roughly 9–20 V center-positive —
  confirm).
- USB-A receptacles with through-hole shell stakes for mechanical strength.

### ESD on every external connector

Low-capacitance TVS arrays — TPD4E05U06-class on SuperSpeed pairs, USBLC6-2 on
USB 2.0 pairs, SM712 on RS-485, a 5 V-working-voltage single-line TVS on TTL
DATA, plain SMBJ on the power connectors.

## 4. Servo surge protection

Two distinct phenomena, applying to **both** servo rails (12 V and 5 V):

1. **Stall/inrush transients** — the servo rail sags. Fix: bulk low-ESR
   capacitance (≥ 470–1000 µF electrolytic/polymer) physically at each servo
   connector, plus a buck with headroom. Cap voltage rating: ≥ 25 V on the 12 V
   rail, ≥ 10 V on the 5 V rail.
2. **Regenerative back-EMF** — when servos decelerate or are back-driven, they
   *pump current into* the rail, and **buck converters cannot sink current**, so
   the rail voltage rises. Fix: the same bulk capacitance absorbs the energy, and
   a TVS catches what the caps don't — SMBJ13A-class (13 V standoff) on the 12 V
   rail, SMBJ6.0A-class (6 V standoff) on the 5 V servo rail. Confirm the buck
   tolerates output overvoltage gracefully (most modern ones stop switching). For
   large servos with heavy loads the proper fix is an active brake/shunt clamp
   (comparator + FET + power resistor); for Dynamixel-class servos, caps + TVS is
   standard practice.

A series diode between buck and servo rail (to protect the buck) is usually *not*
used — it ruins regulation, and the regen energy has nowhere to go but up. Caps +
TVS is the right shape.

## 5. Four dual-mode servo ports on shared rails

**One buck per voltage class, not per bus.** The standard shape is one 12 V rail
and one 5 V servo rail, each with per-connector protection — separate bucks per
bus are 4× the parts and board area for little gain, and each would still need
sizing for its own bus's stall anyway. Split a rail into two bucks only for very
asymmetric loads (one heavy arm bus + three light buses) or when hard fault
domains are required.

Applies identically to the 12 V (RS-485) and 5 V (TTL) rails:

- **Buck sizing:** each rail carries its whole fleet — see §2. Sum-of-stall is
  the conservative ceiling; size for the worst simultaneous mechanical load you
  can justify, and let per-bus current limits bound the rest.
- **Caps, shared + distributed:** a large bulk bank at the buck output, plus a
  local ~470 µF low-ESR cap *at each connector*. Regen from one bus pumps the
  shared rail, where the shared bulk — and the load of the other buses — absorbs
  it; that's a mild benefit of sharing one rail.
- **One TVS per connector.** Cheap; keep them all (voltage class per §4).
- **Per-connector e-fuse or polyfuse:** fault isolation, so a crushed servo cable
  on one limb doesn't drop the whole robot. GPIO-controlled e-fuses (TPS259x
  class) additionally give soft-start, a per-bus e-stop, and staggered power-up
  to tame the combined inrush of multiple buses enabling at once.
- **Star distribution:** route each rail from its buck's bulk bank to the
  connectors as separate polygon pours, so one bus's stall sag doesn't couple
  through shared trace impedance into the others.
- **The 5 V servo rail is never the USB 5 V rail** — servo stall transients on a
  shared rail would brown out the cameras. Two separate bucks, two separate
  distribution trees, joined only at ground.

## 6. Layout and stackup — where USB 3.0 boards live or die

- **4-layer minimum**: Signal / GND / Power / Signal. Order the fab's
  impedance-controlled stackup (e.g., JLCPCB's JLC04161H-7628) and use *their*
  calculator for trace geometry — don't copy numbers from forums.
- SuperSpeed pairs: 90 Ω differential, intra-pair matched to ~0.1 mm, continuous
  ground reference underneath (no plane splits), no stubs, AC-coupling caps
  (0.1 µF) on TX pairs where the hub datasheet shows them, ESD arrays right at the
  connector. Keep pairs short — place the hub between the USB-C and the USB-A
  ports.
- Keep buck inductors and switch nodes **away** from USB, RS-485, and TTL DATA
  routing; keep each buck's input loop tiny; thermal vias under converter pads.
- High-current paths (19 V in, both servo rails, servo ground returns) get
  polygons, not traces; route servo returns so they don't flow under the USB
  section.
- 2.4 GHz radios on the robot: USB 3.0 famously radiates in that band (Intel has a
  whole whitepaper) — keep antennas away from this board and use shielded
  connectors/cables.

## 7. Workflow: KiCad → fab

1. **Prototype the architecture first with off-the-shelf modules** — a powered
   USB3 hub, a CH344-based USB-RS485 dongle (doubles as the L4T driver check),
   buck modules. Most of this stack already runs; the PCB is an *integration*
   step, so de-risk each block before committing copper. The dual-mode front-end
   is breadboardable: CH344 dongle + '241 buffer + one TTL servo.
2. Hierarchical schematic, one sheet per block above. Pull symbols/footprints via
   easyeda2kicad (LCSC parts) or SnapEDA — and **verify every footprint against
   the datasheet drawing**; wrong footprints are the #1 first-spin killer.
3. If using JLCPCB assembly, prefer parts in their library ("Basic" parts avoid
   setup fees) and check stock *before* finalizing the schematic.
4. Set up net classes and diff-pair rules from the fab's stackup numbers; use
   KiCad's diff-pair router and length tuner; import the fab's DRC template.
5. ERC → layout → DRC → 3D check (connector collisions!) → `kkh build` produces
   the full JLCPCB order package (Gerbers, BOM, CPL, STEP, PDFs),
   git-revision-stamped — put `${KKH_VERSION_DATE}` on the silkscreen so the
   fabbed board identifies its own revision.
6. Board bring-up features: test points on every rail plus all four bus
   front-ends (both modes), power-good LEDs per rail, mounting holes, and 0 Ω
   resistor options where unsure (e.g., RS-485 termination, mode-select defaults,
   VBUS detect divider).
7. Order ~5 boards, assemble 2. Bring up power rails with USB/servos
   *disconnected* first, check every rail with a scope, then add subsystems one at
   a time — RealSense last, since it's the fussiest.

## 8. Schematic start: KiCad 10 + kevins-kicad-helpers

Toolchain: KiCad 10 with
[kevins-kicad-helpers](https://github.com/lynaghk/kevins-kicad-helpers) vendored
as a git submodule. Per its README that means `mise` for env management plus two
KiCad plugins: bennymeg/Fabrication-Toolkit and the CDFER JLCPCB-Kicad-Library
(ready-made symbols/footprints for JLC Basic parts).

The workspace is this repository (see [`README.md`](README.md)); the distilled
candidate parts are in [`parts-shortlist.md`](parts-shortlist.md).

Order of operations:

1. **Parts before wires.** `kkh-download-jlcpcb-parts-database` mirrors the
   JLCPCB catalog into SQLite with parametric columns. Resolve every "candidate"
   part in §3 into an actual LCSC part number — with stock, price, and
   Basic/Extended status — *before* drawing anything. Datasheets drive the
   schematic, not vice versa, and it prevents late "out of stock" redesigns.
2. **Golden references per block:** hub datasheet reference schematic, ROBOTIS
   U2D2 schematic (servo front-end), HD3SS3220 datasheet (USB-C upstream),
   vendor design-tool output (bucks). Collected under `datasheets/` — see
   `datasheets/README.md`; ROBOTIS does not publish the U2D2 schematic, the
   golden reference is their recommended TTL / RS-485 circuits instead
   (`datasheets/reference/robotis/`). The functional behaviour these blocks
   must deliver is written up in `FUNCTIONAL.md`.
3. **Hierarchical sheets, multi-instance:** the root sheet mirrors §1. The
   dual-mode servo front-end is *one* sheet instantiated 4×; the generic USB
   port is *one* sheet instantiated 3× — fix a bug once, every instance follows.
4. **Draw the risky blocks first** (servo front-end, USB-C upstream). The power
   sheets are cookbook copies of vendor reference designs and come after.
5. **Conventions that feed the automation:** put `max_mA` properties on the
   3.3 V ICs so `kkh-analyze-schematic` totals their draw — it sums every
   `max_mA` regardless of rail and asserts ≤ 300 mA, so it is a 3.3 V-rail
   check, not the §2 budget (that lives in FUNCTIONAL.md §4).
   Reserve the net name `VBUS` for the true upstream VBUS so its < 10 µF check
   enforces the USB device-side inrush limit — servo rails are `+12V_SERVO` /
   `+5V_SERVO` so their deliberately huge bulk banks don't trip it.
6. **`kkh check` from the first sheet onward;** pull symbols/footprints with
   `kkh-import-easyeda-parts` as parts get placed.

## 9. Biggest caveats, ranked

1. **Adapter wattage** vs. MAXN-Jetson + two servo rails of stall — do the math
   (§2); dual-rail builds escape 150 W-adapter territory fast.
2. **USB-C orientation mux**, or SuperSpeed works only one way.
3. **Bucks can't sink servo regen** — bulk caps + TVS, per connector, both rails
   (§4, §5).
4. **CH344 is a UART bridge** — per-port RS-485 transceivers *and* TTL half-duplex
   buffers are still required, and the L4T driver must be verified early (§3).
5. **RX contention on dual-mode ports** — exactly one receiver per UART RXD;
   mode-select gating is mandatory, not optional (§3).
6. **Never merge the 5 V servo rail with the 5 V USB rail** — servo stalls would
   brown out the cameras.
7. **D435 link-quality sensitivity** — pick a community-validated hub chip and
   test with the real camera at first power-on, not last.
