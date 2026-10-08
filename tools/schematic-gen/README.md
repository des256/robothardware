# schematic-gen — generator for the backbone sheets and the placed board

Every sheet under `backbone/` and `backbone/backbone.kicad_pcb` were produced by
these scripts on 2026-10-08. They are the source of truth for *regenerating*;
once the sheets are edited by hand in KiCad, stop running the generator (it
rewrites whole files) and keep the scripts as documentation of how the circuit
was derived from the datasheets.

Files

| File | Role |
|---|---|
| `sx.py` | minimal KiCad s-expression reader/writer |
| `sch.py` | schematic writer (KiCad 9 file format, read by KiCad 10): places symbols at coordinates, computes pin positions, draws stubs, labels, power symbols, no-connects, hierarchical labels; `Sheet.check()` is a small connectivity self-check that reports shorted nets and pins lying on foreign wires before writing |
| `common.py` | LCSC catalog (value → part number, verified against JLCPCB on 2026-10-08) and layout helpers (`vR`, `vC`, `decap`, `vdiode`, `rail_led`, `testpoint`, …) |
| `libbuild.py` | one-off: builds `backbone/0_backbone.kicad_sym` — sets pin electrical types on the EasyEDA imports, copies the generic passives and small parts from the CDFER JLCPCB library (needs the unzipped PCM package, `CDFER_PKG=…`), copies KiCad's power / jumper / test point / mounting hole symbols and footprints. Already applied; rerun only after new `kkh-import-easyeda-parts` imports |
| `d_power.py` | sheets 2–5: input, LM5145 bucks (TI application circuits 1 and 2 parametrised in `P12` / `P5`), TPS54560 + TLV62569 |
| `d_usb.py` | sheets 6–10: HD3SS3220 upstream, TUSB8041 hub, USB-A port (×3) |
| `d_servo.py` | sheets 11–15: CH344Q, dual-mode servo port (×4) |
| `d_root.py` | root sheet: re-emits the skeleton block diagram (`skeleton/backbone.kicad_sch`) in KiCad 9 format and adds the mounting holes |
| `build.py` | writes the sheets into `backbone/` and runs ERC through the Flatpak KiCad 10 |
| `pcb.py` | builds the board from the exported netlist: footprints with nets and paths, placement rule areas, outline, texts; the floorplan is the `REGIONS` table (see `docs/placement.md`). Runs inside the Flatpak's Python |
| `skeleton/` | the original KiCad 10 root sheet and board stub the generator starts from (sheet-symbol UUIDs and page numbers come from here) |

Regenerate everything (run from the repository root; the Flatpak only sees `$PWD`):

```sh
python3 tools/schematic-gen/build.py                      # all sheets + ERC summary
python3 tools/schematic-gen/build.py usb-hub servo-port   # a subset
kicad-cli sch export netlist --format kicadsexpr -o backbone/outputs/scratch/backbone.net backbone/backbone.kicad_sch
flatpak run --filesystem=$PWD:rw --command=/usr/bin/python3 org.kicad.KiCad tools/schematic-gen/pcb.py
kicad-cli pcb export svg --layers F.Cu,F.SilkS,Edge.Cuts,Cmts.User --page-size-mode 2 --exclude-drawing-sheet -o docs/placement.svg backbone/backbone.kicad_pcb
```

`kicad-cli` resolves through `vendor/kevins-kicad-helpers/bin` (on PATH via
`mise.toml`), which falls back to the Flatpak when no native KiCad is installed.

Conventions baked into the generator

- Symbol UUIDs are `uuid5` of sheet name + reference + position, so reruns
  produce the same identities and the board keeps its schematic links.
- References are sheet number × 100 + n; multi-instance sheets get one
  reference per instance path (usb-port 8xx/9xx/10xx, servo-port 12xx–15xx).
- Non-assembled parts (test points, solder jumpers, mounting holes) are
  excluded from the BOM and carry `LCSC = n/a`; DNP parts (RS-485 termination,
  SW snubbers) are marked DNP.
- Power symbols come from the project library; the sheet that produces a rail
  owns its `PWR_FLAG` (`Sheet.flag_rail`).
