# robothardware — Robot Backbone PCB

KiCad workspace for the backbone board described in [`HARDWARE.md`](HARDWARE.md)
(how and with what) and [`FUNCTIONAL.md`](FUNCTIONAL.md) (what it does, seen from
its connectors and from software).
Tooling follows [kevins-kicad-helpers](https://github.com/lynaghk/kevins-kicad-helpers)
(vendored at `vendor/kevins-kicad-helpers`, on PATH via `mise.toml`).

## Toolchain status

1. **mise** — installed at `~/.local/bin/mise`; activate in your shell
   (`eval "$(mise activate bash)"` in `~/.bashrc`, the installer appended it).
   Run `mise trust && mise install` once in this directory.
2. **sqlite3** — static binary at `~/.local/bin/sqlite3` (needed by the
   parts-database script; not in mise).
3. **KiCad 10** — installed (10.0.6; verify with `kicad-cli --version`).
4. **KiCad plugins** — installed: bennymeg/Fabrication-Toolkit (JLCPCB outputs;
   `kkh build` drives it) and CDFER/JLCPCB-Kicad-Library (symbols/footprints
   for JLC Basic parts).
5. **Analyzer toolchain** (`kkh check` / `kkh-analyze-schematic` run a JVM
   Clojure tool) — Java temurin-25 and clj-kondo via
   `mise -C vendor/kevins-kicad-helpers/analyzer install`. Clojure needs a
   workaround: mise 2026.8.14 cannot resolve the registry name `clojure`, so
   the CLI was installed through the asdf plugin the analyzer's `mise.lock`
   names (`mise plugins install clojure https://github.com/asdf-community/asdf-clojure.git`)
   and symlinked onto the PATH: `~/.local/bin/{clojure,clj}` →
   `~/.local/share/mise/installs/clojure/1.12.5.1654/bin/`. `mise exec` then
   finds it from the ambient PATH. Verified: `kkh-analyze-schematic` runs.
6. **`KICAD_PYTHON`** — set in `mise.toml` to `/usr/bin/python3` (the PATH
   `python3` is PlatformIO's venv and cannot import `pcbnew`).

## Project layout

- `backbone/` — the KiCad project (`backbone.kicad_pro`, root sheet plus one file
  per block, see below); kkh tools discover it by scanning for `*.kicad_pro`.
  `0_backbone.kicad_sym` / `0_backbone.pretty/` / `0_backbone.3dshapes/` are the
  project-local libraries written by `kkh-import-easyeda-parts` (registered in
  the project `sym-lib-table` / `fp-lib-table`; reopen the project in KiCad
  after an import so it picks them up). Library status is tracked in the
  Schematic plan section.
- `jlcpcb_parts.db` — local JLCPCB catalog mirror (gitignored; rebuild anytime
  with `kkh-download-jlcpcb-parts-database jlcpcb_parts.db`). Check freshness:
  `sqlite3 jlcpcb_parts.db "SELECT value FROM meta WHERE key='generated_at'"`.
- `parts-shortlist.md` — distilled candidate parts per block, queried from the DB.
- `datasheets/` — part datasheets for every curated pick plus vendor reference
  designs and the ROBOTIS servo circuits (`datasheets/README.md` is the index;
  `datasheets/fetch.sh` re-downloads from `manifest.tsv`).

## Schematic plan (mirrors HARDWARE.md sections 1 and 8)

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
| 7 | `usb-hub` | 1 | TUSB8041, crystal, 1V1 LDO, straps, USB_VBUS divider | TUSB8041 EVM |
| 8–10 | `usb-port` | 3: `usb-port-1..3` = hub DS1..DS3 | SY6280 + Rset, TPD4E05U06, USBLC6-2, USB-A 3.0 receptacle | hub EVM downstream port |
| 11 | `servo-uart` | 1 | CH344Q on hub DS4, TNOW pull-downs, RXD pull-ups | CH344 datasheet |
| 12–15 | `servo-port` | 4: `servo-port-0..3` = CH344 UART0..3 | SP3485EN + LVC2G241 front-end, mode jumper, ESD, both connectors, both e-fuses / bulk / TVS | ROBOTIS circuits |

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
- Annotate with "First free after sheet number × 100" so a designator names
  its sheet; the pre-placed power symbols already follow it (`#PWR0201` is on
  sheet 2). This will renumber FUNCTIONAL.md's J1–J14 — update that table once
  the connectors are placed.
- `max_mA`: `kkh-analyze-schematic` sums every `max_mA` in the design
  regardless of rail and asserts ≤ 300 mA (hardcoded in
  `vendor/kevins-kicad-helpers/analyzer/src/kicad_analyzer/core.clj`), so put
  it only on the +3V3 ICs. The rail budgets stay in FUNCTIONAL.md §4.
- `kkh check` fails any placed part (non-DNP, with a footprint) whose `LCSC`
  field is empty — CDFER-library and `kkh-import-easyeda-parts` symbols carry
  it, symbols taken from KiCad's own libraries (`Device:R`, …) need it filled
  in by hand.

### Library status (what `kkh-import-easyeda-parts` has pulled so far)

Imported into `0_backbone` from LCSC, with the EasyEDA footprint and 3D model
(non-interactive run, so no KiCad standard footprint was substituted — review
each footprint against the datasheet drawing, V4):
TUSB8041IRGCR, CH344Q, SN74LVC2G241DCU, LM5145RGYR, TPS54560DDAR,
TLV62569DBVR, TPS16630PWPR, TPS25961DRVR, SY6280AAC, HD3SS3220RNHR,
LM74700QDBVRQ1, TPD4E05U06DQAR, USBLC6-2SC6, B4B-EH-A, B3B-EH-A, XT30PW-M,
HC-ST-003-01-J (USB-A 3.0), TYPE-C 24P QT.

Served by the installed CDFER JLCPCB library instead (symbols already carry
the LCSC field; place them from `PCM_JLCPCB-…`): SP3485EN-L/TR, SMBJ24A,
SMBJ13A, SMBJ6.0A, SM712.

KiCad's own libraries also ship symbols for TUSB8041, CH344Q, TLV62569DBV,
LM74700, TPD4E05U06DQA and USBLC6-2SC6 — either is fine, but a symbol taken
from KiCad's library needs its `LCSC` field filled by hand.

Alternates, imported as well so a swap is a symbol change: RTS5411S-GR,
CYUSB3304-68LTXC, CH344L, SN74LVC1G126DBVR, SN74LVC1G125DBVR, LM5143RHAR,
TPS2553DBVR, S4B-EH, S3B-EH, DC-005-A200, TYPE-C 24P QCHT.

EasyEDA's API rate-limits bulk pulls (HTTP 403 after ~20 parts within a
minute); wait a few minutes and rerun the same command for the parts that
failed. Reruns skip parts the library already has.

### Schematic ↔ PCB correspondence

KiCad has no sheet-to-layer mapping; sheets are functional, layers are copper.
The links that do exist, and where each one is set up:

| Link | Where | State |
|------|-------|-------|
| Stackup | `backbone.kicad_pcb`: 4 copper layers, In1.Cu named `GND` (plane), In2.Cu named `PWR` | set; enter the JLC04161H-7628 thicknesses in Board Setup → Physical Stackup |
| Net classes | `backbone.kicad_pro`: `USB3_SS`, `USB2_HS`, `RS485`, `TTL_DATA`, `PWR_19V`, `PWR_SERVO`, `PWR_USB`, `SW_NODE` | defined; USB3_SS / USB2_HS width and gap **still to fill from the JLCPCB impedance calculator** (they inherit Default until then); power-class widths are starting values |
| Class of a signal net | directive label on its stub inside the sheet (a multi-instance sheet applies it to every instance) | placed on every USB pair |
| Class of a rail / per-port net | `netclass_patterns` in `backbone.kicad_pro`: `+12V_SERVO`, `/servo-port-*/A`, `/servo-port-*/B`, `/servo-port-*/DATA`, `/servo-port-*/VDD_*`, `/usb-port-*/VBUS_OUT`, `/buck-*/SW*`, `/buck-*/BOOT*` | set — use these net names when drawing |
| Layer geometry and keep-outs | `backbone.kicad_dru`: USB3_SS on F.Cu only and without vias, 1 mm zone clearance to the USB pairs, SW_NODE on outer layers and 3 mm from signal classes, PWR_SERVO copper barred from a rule area named `usb_section` (draw and name it in the PCB editor) | written; check it with Board Setup → Custom Rules → "Check rule syntax" — `kicad-cli pcb drc` silently ignores rule-file errors |
| Sheet → board region | PCB editor: "Generate Placement Rule Areas…" (one area per hierarchical sheet), then "Pack and Move Footprints" | use after the first Update PCB from Schematic |
| Sheet → component class | `sheet_component_classes` enabled in `backbone.kicad_pro`; rules can use `A.hasComponentClass(...)` | enabled |

Workflow while drawing sheets. ERC on the skeleton reports only "Label not
connected", "Unconnected wire endpoint" and "Pin not connected" — one per
interface pin or rail that has no part on it yet; they disappear as the sheets
fill up. `kkh check` therefore stops at ERC until then, and afterwards at the
DRC schematic-parity step until footprints are placed:

```sh
kicad-cli sch erc --exit-code-violations -o /dev/stdout backbone/backbone.kicad_sch
kkh-analyze-schematic backbone/backbone.kicad_sch     # max_mA total, VBUS < 10 uF
kkh-import-easyeda-parts C544686 C2988084 ...          # symbols/footprints per LCSC number
```

From layout onward: `kkh check`, then `kkh build` for the JLCPCB order
package. Put `${KKH_VERSION_DATE}` on the silkscreen (the first `kkh check`
adds the placeholder text variable to `backbone.kicad_pro`; commit it).
