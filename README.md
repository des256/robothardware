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

## Project layout

- `backbone/` — the KiCad project (`backbone.kicad_pro`). Create it in KiCad 10
  (File > New Project) as `backbone` inside this directory; kkh tools discover it
  by scanning for `*.kicad_pro`.
- `jlcpcb_parts.db` — local JLCPCB catalog mirror (gitignored; rebuild anytime
  with `kkh-download-jlcpcb-parts-database jlcpcb_parts.db`). Check freshness:
  `sqlite3 jlcpcb_parts.db "SELECT value FROM meta WHERE key='generated_at'"`.
- `parts-shortlist.md` — distilled candidate parts per block, queried from the DB.
- `datasheets/` — part datasheets for every curated pick plus vendor reference
  designs and the ROBOTIS servo circuits (`datasheets/README.md` is the index;
  `datasheets/fetch.sh` re-downloads from `manifest.tsv`).

## Schematic plan (mirrors HARDWARE.md sections 1 and 8)

Hierarchical sheets under `backbone.kicad_sch`:

| Sheet | Instances | Golden reference |
|-------|-----------|------------------|
| `input-protection` | 1 | ideal-diode controller datasheet |
| `buck-12v-servo` | 1 | vendor design tool (WEBENCH) |
| `buck-5v-servo` | 1 | same controller design, different divider |
| `buck-5v-usb + 3v3` | 1 | vendor design tool |
| `usbc-upstream` | 1 | HD3SS3220 datasheet |
| `usb-hub` | 1 | hub datasheet reference schematic |
| `usb-port` | 3 (multi-instance) | hub datasheet downstream-port example |
| `servo-port` (dual-mode RS-485/TTL front-end) | 4 (multi-instance) | ROBOTIS U2D2 schematic |

Conventions (see HARDWARE.md section 8): `max_mA` property on every load;
net name `VBUS` reserved for the upstream USB-C VBUS only; servo rails are
`+12V_SERVO` / `+5V_SERVO`.

Workflow: `kkh check` from the first sheet onward; `kkh build` for the
JLCPCB order package. Put `${KKH_VERSION_DATE}` on the silkscreen.
