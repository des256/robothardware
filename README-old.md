# robothardware — Robot Backbone PCB

KiCad workspace for the backbone board described in [`HARDWARE.md`](HARDWARE.md)
(how and with what) and [`FUNCTIONAL.md`](FUNCTIONAL.md) (what it does, seen from
its connectors and from software).
Tooling follows [kevins-kicad-helpers](https://github.com/lynaghk/kevins-kicad-helpers)
(vendored at `vendor/kevins-kicad-helpers`, on PATH via `mise.toml`).

## Toolchain status

1. **mise** — `~/.local/bin/mise` (2026.10.3), activation line in `~/.bashrc`.
   `mise trust && mise install` done in this directory (babashka, cljfmt, uv).
2. **sqlite3** — static binary at `~/.local/bin/sqlite3` (3.53.4).
3. **KiCad 10** — 10.0.6 as a *user Flatpak* (`org.kicad.KiCad`, installed
   2026-10-08 because the apt PPA install did not land on this machine; the
   apt `kicad` package is absent). The kkh `bin/kicad-cli` shim falls back to
   the Flatpak automatically, so `kkh check`, `kkh build` and
   `kkh-analyze-schematic` work unchanged — run them from inside the repository,
   the Flatpak sandbox only sees `$PWD`. Direct use:
   `flatpak run --filesystem=$PWD:rw --command=/app/bin/kicad-cli org.kicad.KiCad …`.
4. **KiCad plugins** — *not* installed in the Flatpak yet: bennymeg/Fabrication-Toolkit
   (needed by `kkh build`; install from the Plugin and Content Manager inside
   the Flatpak KiCad) and CDFER/JLCPCB-Kicad-Library (not needed any more — the
   symbols, footprints and STEP models the project uses were copied into the
   project-local `0_backbone` library, see Library status).
5. **Analyzer toolchain** (`kkh check` / `kkh-analyze-schematic`) — Java
   temurin-25, clj-kondo and cljfmt via `mise -C vendor/kevins-kicad-helpers/analyzer install`.
   Clojure still needs the asdf-plugin workaround (`mise plugins install clojure
   https://github.com/asdf-community/asdf-clojure.git`, then
   `~/.local/bin/{clojure,clj}` → `~/.local/share/mise/installs/clojure/1.12.5.1654/bin/`).
   Verified: `kkh-analyze-schematic backbone/backbone.kicad_sch` runs.
6. **`KICAD_PYTHON`** — the apt `pcbnew` module is gone with the apt package;
   the board generator (`tools/schematic-gen/pcb.py`) therefore runs inside the
   Flatpak's own Python (`flatpak run --command=/usr/bin/python3 org.kicad.KiCad`).
   `mise.toml` still points `KICAD_PYTHON` at `/usr/bin/python3` for kkh's
   step-export helper; that path has no `pcbnew` until a KiCad apt package is
   installed again.

## Project layout

- `backbone/` — the KiCad project (`backbone.kicad_pro`, root sheet plus one file
  per block, see below); kkh tools discover it by scanning for `*.kicad_pro`.
  `0_backbone.kicad_sym` / `0_backbone.pretty/` / `0_backbone.3dshapes/` are the
  project-local libraries written by `kkh-import-easyeda-parts` (registered in
  the project `sym-lib-table` / `fp-lib-table`; reopen the project in KiCad
  after an import so it picks them up). Library status is tracked in the
  Schematic plan section.
- `jlcpcb_parts.db` — local JLCPCB catalog mirror (gitignored). **Currently not
  usable:** upstream jlcparts switched to a `source-db-v2` layout whose daily dump
  only carries LCSC numbers above ~C6,300,000, so the mirror built on 2026-10-08
  holds 72,611 parts and none of the classic Basic parts or the curated ICs
  (the vendored `kkh-download-jlcpcb-parts-database` also chokes on the split
  zip). The parts added during schematic capture were resolved against
  JLCPCB's live catalog search instead — see `parts-shortlist.md`.
- `docs/placement.md` — the board floorplan (placement diagram) with the
  rendered `docs/placement.png` / `.svg`.
- `tools/schematic-gen/` — the generator that produced every sheet and the
  placed board (see its README); rerun it instead of hand-editing wholesale.
- `parts-shortlist.md` — distilled candidate parts per block, queried from the DB.
- `datasheets/` — part datasheets for every curated pick plus vendor reference
  designs and the ROBOTIS servo circuits (`datasheets/README.md` is the index;
  `datasheets/fetch.sh` re-downloads from `manifest.tsv`).

## Schematic plan (mirrors HARDWARE.md sections 1 and 8)

**Status 2026-10-08: all 15 pages are drawn.** `kicad-cli sch erc` (KiCad 10.0.6)
reports zero errors and zero warnings for the whole hierarchy,
`kkh-analyze-schematic` passes (228 mA of `max_mA` on +3V3, nothing on VBUS),
and the kkh LCSC check passes. `backbone.kicad_pcb` holds every footprint with
its net and schematic link, placed block by block (`docs/placement.md`); it is
not routed, so `kkh check` stops at DRC with 499 unconnected pads.

The hierarchy lives in `backbone/`. The root sheet `backbone.kicad_sch` is the
block diagram of FUNCTIONAL.md §3 and holds only sheet symbols; every block is
its own file, and the two repeated blocks are one file instantiated several
times:

| Page | Sheet file | Instances | Contents | Golden reference |
|------|------------|-----------|----------|------------------|
| 2 | `input` | 1 | J1, fuse, LM74700 + FET, SMBJ24A, bulk; J2 19 V out with its fuse | LM74700 datasheet |
| 3 | `buck-12v-servo` | 1 | LM5145 → `+12V_SERVO`, shared bulk bank | LM5145 EVM / WEBENCH |
| 4 | `buck-5v-servo` | 1 | LM5145 → `+5V_SERVO` (own file: values differ, and D1 may delete it) | same |
| 5 | `buck-5v-usb` | 1 | TPS54560 → `+5V_USB`, TLV62569 → `+3V3` | TPS54560 EVM |
| 6 | `usbc-upstream` | 1 | J3, HD3SS3220 (UFP, GPIO mode), VBUS_DET, ESD | HD3SS3220 checklist + EVM |
| 7 | `usb-hub` | 1 | TUSB8041, 24 MHz crystal, +1V1_HUB buck (TLV62569 + ferrite), straps, GRSTz RC, USB_VBUS divider | TUSB8041 EVM |
| 8–10 | `usb-port` | 3: `usb-port-1..3` = hub DS1..DS3 | TPS2553 + RILIM (1.51 A, FAULT → hub), ferrite, TPD4E05U06, USBLC6-2, USB-A 3.0 receptacle | hub EVM downstream port |
| 11 | `servo-uart` | 1 | CH344Q on hub DS4, TNOW pull-downs, RXD pull-ups | CH344 datasheet |
| 12–15 | `servo-port` | 4: `servo-port-0..3` = CH344 UART0..3 | SP3485EN + LVC2G241 front-end, mode solder jumper, ESD, both connectors, TPS16630 / TPS25961 e-fuses, 470 µF polymer + TVS per connector | ROBOTIS circuits |

Every sheet starts with a note (golden references, LCSC parts, rails, open
FUNCTIONAL.md decisions) and its hierarchical pins on wire stubs. Anything that
must differ between instances cannot live in a multi-instance sheet: KiCad
stores only reference and unit per instance; values, footprints and DNP are
shared.

Conventions (see HARDWARE.md section 8):

- Rails are global power symbols — `+19V_IN`, `+19V_JETSON`, `+12V_SERVO`,
  `+5V_SERVO`, `+5V_USB`, `+3V3`, `+1V1_HUB`, `VBUS`, `GND` — with the
  `PWR_FLAG` on the sheet that produces the rail. In KiCad 10 a power symbol's
  Value is its net name, so a `power:+5V` symbol with Value `+5V_SERVO` *is*
  the `+5V_SERVO` rail. `VBUS` is reserved for the upstream USB-C VBUS (the
  < 10 µF check); the switched port outputs are `VBUS_OUT`.
- Signals cross sheets through hierarchical pins; the labels on the root name
  the top-level nets (`US_*` upstream ↔ hub, `DSn_*` hub ↔ ports, `UARTn_*`
  uart ↔ servo ports). Inside a multi-instance sheet nets get paths such as
  `/servo-port-0/DATA` — the net-class patterns and DRC rules key on them.
- Designators are sheet number × 100 + n (`R301` is on sheet 3, `#PWR0201` on
  sheet 2); multi-instance sheets count per instance (usb-port 8xx/9xx/10xx,
  servo-port 12xx–15xx). FUNCTIONAL.md §2 carries the resulting connector
  numbers (J201/J202, J601, J801/J901/J1001, J12x1/J12x2 …).
- Non-assembled items (test points, solder jumpers, mounting holes) are
  excluded from the BOM and carry `LCSC = n/a`, which is what the kkh LCSC
  check needs to pass without pretending they are purchasable parts.
- Net-class patterns in `backbone.kicad_pro` were extended while drawing:
  `/usb-port-*/VBUS_*` (the switched output has a ferrite, so two nets),
  `/usb-hub/SW_1V1` (the core-rail buck), plus the original ones.
- `max_mA`: `kkh-analyze-schematic` sums every `max_mA` in the design
  regardless of rail and asserts ≤ 300 mA (hardcoded in
  `vendor/kevins-kicad-helpers/analyzer/src/kicad_analyzer/core.clj`), so it is
  set only on the +3V3 ICs with typical-active numbers: hub VDD33 33, CH344Q 30,
  HD3SS3220 5, 4 × SP3485EN 35, 4 × LVC2G241 5 = 228 mA. The rail budgets
  stay in FUNCTIONAL.md §4.
- `kkh check` fails any placed part (non-DNP, with a footprint) whose `LCSC`
  field is empty — CDFER-library and `kkh-import-easyeda-parts` symbols carry
  it, symbols taken from KiCad's own libraries (`Device:R`, …) need it filled
  in by hand.

### Library status (`0_backbone` is self-contained)

Every symbol the sheets use lives in `backbone/0_backbone.kicad_sym` (KiCad 9
library format, read by KiCad 10) with its footprint in `0_backbone.pretty` and
STEP model in `0_backbone.3dshapes`; nothing depends on the global symbol or
footprint tables. Three sources:

- **`kkh-import-easyeda-parts`** (EasyEDA symbol + footprint + 3D, LCSC field
  filled): TUSB8041IRGCR, CH344Q, SN74LVC2G241DCU, LM5145RGYR, TPS54560DDAR,
  TLV62569DBVR, TPS16630PWPR, TPS25961DRVR, SY6280AAC (unused, kept as the
  imported alternate), HD3SS3220RNHR, LM74700QDBVRQ1, TPD4E05U06DQAR,
  USBLC6-2SC6, B4B-EH-A, B3B-EH-A, XT30PW-M, HC-ST-003-01-J (USB-A 3.0),
  TYPE-C 24P QT, TPS2553DBVR, and the parts added on 2026-10-08: CSD18532Q5B
  (buck + ideal-diode FET), the four inductors (TMPA1265SP-4R7MN-D,
  TMPC1265HP-3R3MG-D, 7447798720, SMNR4020-2.2UH), the 100 V / 16 V / 25 V
  1210 ceramics, the polymer and electrolytic bulk capacitors, both fuses and
  the B560C catch diode. Pin electrical types were set by hand (the import
  leaves them "unspecified", which ERC flags) — see `PIN_TYPES` in
  `tools/schematic-gen/libbuild.py`.
- **Copied from CDFER/JLCPCB-Kicad-Library 2025.07.18** (symbol, footprint,
  STEP; vendor stock/price fields dropped): generic `R_0603`, `C_0402`,
  `C_0603`, `C_0805`, `C_1206`, `FB_0603`, `FB_0805`, `TVS_SMB` — Value and
  LCSC are set per instance from the catalog in `tools/schematic-gen/common.py`
  — plus `LED_0805_Green`, `SMF5.0A`, `SS14`, `PSM712`, `SP3485EN`,
  `Crystal_8MHz_5032`, `Crystal_24MHz_3225`.
- **Copied from KiCad's own libraries**: the power symbols (`+VDC`, `+12V`,
  `+5V`, `+3V3`, `+1V1`, `VBUS`, `GND`, `PWR_FLAG`), `TestPoint`,
  `SolderJumper_3_Bridged12`, `SolderJumper_2_Bridged`, `SolderJumper_2_Open`,
  `MountingHole` with their footprints.

Footprint fixes applied to the imports (so DRC and schematic parity are
clean): the unnumbered thermal-via pads inside the HTSSOP-20 (TPS16630) and
SOIC-8-EP (TPS54560) exposed pads now carry the exposed pad's number, and the
two alignment pegs of both USB-C footprints are NPTH instead of copper-less
PTH. **V4 is still open**: every imported footprint must be checked against
its datasheet drawing before ordering; the USB-C QT shell legs in particular
are modelled as two overlapping oval PTH pads per side.

Alternates that stay importable as a symbol swap: RTS5411S-GR, CYUSB3304-68LTXC,
CH344L, SN74LVC1G126DBVR, SN74LVC1G125DBVR, LM5143RHAR, S4B-EH, S3B-EH,
DC-005-A200, TYPE-C 24P QCHT, SY6280AAC.

EasyEDA's API rate-limits bulk pulls (HTTP 403 after ~15 parts within a
minute); wait a few minutes and rerun the same command for the parts that
failed. Reruns skip parts the library already has.

### Schematic ↔ PCB correspondence

KiCad has no sheet-to-layer mapping; sheets are functional, layers are copper.
The links that do exist, and where each one is set up:

| Link | Where | State |
|------|-------|-------|
| Stackup | `backbone.kicad_pcb`: 4 copper layers, In1.Cu named `GND` (plane), In2.Cu named `PWR` | set; enter the JLC04161H-7628 thicknesses in Board Setup → Physical Stackup |
| Net classes | `backbone.kicad_pro`: `USB3_SS`, `USB2_HS`, `RS485`, `TTL_DATA`, `PWR_19V`, `PWR_SERVO`, `PWR_USB`, `SW_NODE`; Default clearance 0.127 mm (JLCPCB minimum, needed by the 0.4 mm-pitch HD3SS3220 and the USB-C pads) | defined; USB3_SS / USB2_HS width and gap **still to fill from the JLCPCB impedance calculator** (they inherit Default until then); power-class widths are starting values. The class clearances (SW_NODE 0.5 mm, PWR_SERVO 0.3 mm) and the 3 mm `sw_node_away_from_signals` rule also bite at IC pads (37 DRC clearance errors on the placed board) — scope them to tracks/zones with `A.Type` conditions in the `.kicad_dru` during layout |
| Class of a signal net | directive label on its stub inside the sheet (a multi-instance sheet applies it to every instance) | placed on every USB pair |
| Class of a rail / per-port net | `netclass_patterns` in `backbone.kicad_pro`: `+12V_SERVO`, `/servo-port-*/A`, `/servo-port-*/B`, `/servo-port-*/DATA`, `/servo-port-*/VDD_*`, `/usb-port-*/VBUS_*`, `/buck-*/SW*`, `/buck-*/BOOT*`, `/usb-hub/SW_1V1` | set and used by the drawn sheets |
| Layer geometry and keep-outs | `backbone.kicad_dru`: USB3_SS on F.Cu only and without vias, 1 mm zone clearance to the USB pairs, SW_NODE on outer layers and 3 mm from signal classes, PWR_SERVO copper barred from a rule area named `usb_section` (draw and name it in the PCB editor) | written; check it with Board Setup → Custom Rules → "Check rule syntax" — `kicad-cli pcb drc` silently ignores rule-file errors |
| Sheet → board region | `backbone.kicad_pcb`: one placement rule area per sheet instance (named like the sheet, source = sheet name) plus the `usb_section` area, generated by `tools/schematic-gen/pcb.py`; footprints are packed into them (`docs/placement.md`) | done; routing, exact placement and the connector orientations are the layout stage's job |
| Sheet → component class | `sheet_component_classes` enabled in `backbone.kicad_pro`; rules can use `A.hasComponentClass(...)` | enabled |

Workflow. ERC is clean and the footprints are placed, so `kkh check` now
stops at DRC (unconnected pads) until the board is routed; `kkh build` needs
the Fabrication Toolkit plugin as well. To regenerate sheets or the board after
editing the generator, see `tools/schematic-gen/README.md`. Direct commands:

```sh
kicad-cli sch erc --exit-code-violations -o /dev/stdout backbone/backbone.kicad_sch   # via the kkh shim → Flatpak
kicad-cli pcb drc --schematic-parity -o /dev/stdout backbone/backbone.kicad_pcb
kkh-analyze-schematic backbone/backbone.kicad_sch     # max_mA total, VBUS < 10 uF
kkh-import-easyeda-parts C544686 C2988084 ...          # symbols/footprints per LCSC number
```

From layout onward: `kkh check`, then `kkh build` for the JLCPCB order
package. Put `${KKH_VERSION_DATE}` on the silkscreen (the first `kkh check`
adds the placeholder text variable to `backbone.kicad_pro`; commit it).
