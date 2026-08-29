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
`+12V_SERVO` / `+5V_SERVO`. In addition `kkh check` fails any placed part
(non-DNP, with a footprint) whose `LCSC` field is empty — CDFER-library and
`kkh-import-easyeda-parts` symbols carry it, symbols taken from KiCad's own
libraries (`Device:R`, …) need it filled in by hand.

Workflow while drawing sheets (the PCB is still empty, so `kkh check` fails
at the DRC schematic-parity step until footprints are placed):

```sh
kicad-cli sch erc --exit-code-violations -o /dev/stdout backbone/backbone.kicad_sch
kkh-analyze-schematic backbone/backbone.kicad_sch     # max_mA totals, VBUS < 10 uF
kkh-import-easyeda-parts C544686 C2988084 ...          # symbols/footprints per LCSC number
```

From layout onward: `kkh check`, then `kkh build` for the JLCPCB order
package. Put `${KKH_VERSION_DATE}` on the silkscreen (the first `kkh check`
adds the placeholder text variable to `backbone.kicad_pro`; commit it).
