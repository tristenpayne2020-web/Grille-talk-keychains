# Handoff: Grille Talk car-front keychains

Project root: `C:\Users\trist\AppData\Local\Temp\claude\C--Users-trist\eb31f25f-c0e7-4c47-a2a2-d10d3da19ae7\scratchpad\kc`.
All paths below are relative to it unless absolute.

Delivery folder: `C:\Users\trist\Downloads\CarKeychains`. `finalize.py` wipes it and regenerates it.

Older running notes are in `RESUME_NOTES.md`. This file supersedes them where they disagree.

**Status: PAUSED by the user.** Do not start any work until the user says "continue". The user is close to their usage limit and wants work run in small batches.

---

## 1. The goal

The user runs a small business called **Grille Talk** that sells 3D-printed car-front keychains, through Etsy and at car meets.

They gave me their own BMW M3 G80 keychain (`C:\Users\trist\Downloads\G80Keychain.step`). I make more cars in the same design language, optimised for bulk printing on a **Creality K2 + CFS** with the **0.4 nozzle only**, using as little time and purge waste as possible, and sliced in **Creality Print**.

### Design language

- Straight-on front view, cropped at the windshield base, mirror-symmetric.
- Body 80.5 mm wide and 3.0 mm thick.
- White body, black details, white DRL light signatures.
- Relief grille, using slats or mesh.
- Engraved grooves 0.5–0.6 mm.
- Keyring tab on the viewer's left: 4.5 mm hole with a 2.0 mm wall.
- Minimum feature and gap size 0.5 mm.

### Builds produced for every car

- **Production "1-swap":**
  - black base 0–1.6 mm, white cap 1.6–3.0 mm;
  - one filament change per plate.
- **Classic:**
  - flush full-depth inlays like the G80;
  - about 15 changes per plate.
- **Custom body colour, 3 filaments:**
  - 1 = black, 2 = body colour, 3 = white for lights;
  - comes in production3 and classic3 versions;
  - about 8 and about 21 changes per plate respectively.

Each build is delivered as STL, STEP, a single 3MF and a full-plate 3MF (260×260 bed, prime tower in the back-right corner at 216/229). There are also renders, a sampler plate set, a pricing model (xlsx) and a pricing guide.

### User rules (all standing)

- **BMWs:** exactly ONE tow-hook cover, on the viewer's left, `mirror=False`. Never a mirrored pair.
- **Revision:** 2 rounds maximum.
- **Batches:** small pools of 2–3 cars, and pause when asked.
- **Approved designs are frozen:**
  - snapshot the specs when showing drafts (`spec_SHOWN_<stamp>.py`);
  - on approval, restore from that snapshot and lock it as `spec_APPROVED_by_user.py`;
  - running revise agents have overwritten approved designs before, so stop the workflow first.
- **Slicer settings:** ONE master preset, never per-car settings (see section 2).
- **NO LOGOS on any car.** The user decided this on 2026-09-30, for trademark reasons. DONE 2026-10-01: see section 5, step 1.

---

## 2. Current state

### Finished and packaged: 28 cars

All of these are in `cars_pkg.json` and in Downloads, and all point at the master preset:

- g80_m3, g87_m2, f82_m4, gt3rs_992, c8_corvette, gt500_mustang, r8_audi
- svj_aventador, amg_gt, r35_gtr, g20_m340i_lci, camaro_zl1, mclaren_720s
- ct5v_blackwing, charger_srt, mk5_supra, challenger_hellcat, f92_m8, e30_m3
- f87_m2, amg_gt63_4door, c7_z06, g42_m240i_lci, lexus_is350, civic_11th
- camry_xv80, bugatti_chiron, lambo_urus

The user-approved specs are locked as `cars/<id>/spec_APPROVED_by_user.py`.

The G80 is built from `cars/g80_m3/spec_from_step.pkl` (made from the user's STEP by `cars/g80_m3/make_spec_from_step.py`, with the right tow ring dropped).

### Slicer: Creality Print 7.3.0.6149

The app auto-updated. It still installs to `C:\Program Files\Creality\Creality Print 7.1`.

- **CLI command:** `CrealityPrint.exe --cli --slice 1 --outputdir DIR --need-gcode-file in.3mf`, which writes `DIR/plate_1.gcode`.
- 7.3 slices real multi-colour 3MFs directly.

### Master preset (the single source of slicer settings)

- **Name:** `Grille Talk Keychain 0.20mm @Creality K2 0.4 nozzle`.
- **Parent:** `0.20mm Standard @Creality K2 0.4 nozzle` (setting_id GP004).
- **Installed at:** `%APPDATA%\Creality\Creality Print\7.3\user\3477890751\process\` (.json + .info).
- **Copies:** in `Downloads\CarKeychains\_MASTER_SLICER_PRESET\`, together with `HOW_TO_USE.txt`.
- **Contents:** the user's tuned Copy(2) process plus `k2config.KEYCHAIN`. The latest user changes are:
  - top_shell_layers 6
  - wall_transition_angle 50
  - ironing_flow 25%
  - ironing_spacing 0.12
- **Source of truth:** the installed preset file wins (`master_preset.settings()`), so edits the user saves in the GUI are picked up.
- **Changing a setting:** edit the preset, then run `python lib/apply_master.py "C:\Users\trist\Downloads\CarKeychains" cars/*/out`. That re-syncs every 3MF in seconds, with NO geometry rebuild. `finalize.py` also does this at its end.
- **Not verified in the GUI:** that the preset shows in the list, and that Ctrl+I imports a 3MF as geometry while keeping the per-part filaments. The user denied computer-use access to Creality Print.

### Verified numbers

From real 7.3 slices of the G80, 13-piece plate:

| Build | Time | Changes |
|---|---|---|
| 1-swap | 5h 12m | 1 |
| Classic | 8h 20m | 15 |
| Custom colour, 1-swap | 5h 34m | 8 |
| Custom colour, classic | 8h 15m | 21 |

Average cost is about $1.10 per keychain. Etsy at $16.99 with free shipping makes about $6.04 profit each; selling at a car meet for $10 makes about $8.65.

### Design workflow

The script is `C:\Users\trist\.claude\projects\C--Users-trist-AppData-Local-Temp-claude-C--Users-trist-eb31f25f-c0e7-4c47-a2a2-d10d3da19ae7-scratchpad\eb31f25f-c0e7-4c47-a2a2-d10d3da19ae7\workflows\scripts\car-keychains-next.js`. It runs these stages:

1. trace
2. two critics per round (likeness, and style + printability)
3. revise, repeated up to `max_rounds`
4. an art-director consistency pass over the new cars only

**Args:**
- `sp`, `pool`, `max_rounds`, `cars` (each `[{id, name, brief, prev}]`), `prev_done`;
- `others` = fixed reference spec paths, listing all finished cars except the G80.

The latest args file is `batchC_args.json`. The latest run, `wf_79ea1558-861` (GR86 + BRZ), was STOPPED by the user's pause while still tracing. Nothing in it completed, but partial files may exist in `cars/gr86` and `cars/brz_zd8`.

### Queues (not started)

- **`queue_batch6.json`:**
  - gr86, brz_zd8
  - g90_m5, f90_m5, ferrari_sf90, tesla_model3, tesla_models_plaid
  - jesko, ferrari_f40, huracan_evo, c6_corvette, c5_corvette
  - zonda_cinque was REMOVED by the user.
- **`queue_batch7.json`:**
  - g20_330i, lexus_lc500, g30_m550i, kia_stinger, s550_mustang
  - s650_mustang (reuses the old `cars/s650_mustang`)
  - audi_rs5, audi_rs7, nd_miata, camaro_1ss, ram_trx
  - trackhawk was REMOVED by the user (Jeep trade dress).
- **`queue_batch8.json`:**
  - dodge_viper, civic_type_r_fl5, f150, mini_cooper_s, elantra_n, silverado
  - escalade, x5m, x4m, macan, cayenne
  - jeep_wrangler: ASK the user before designing it, because the seven-slot grille is a trademark.
  - nissan_350z

  The queue_batch8 briefs already say there are no logos.

---

## 3. Files actively being edited or used

### lib/

- `k2config.py`:
  - builds the project config;
  - `KEYCHAIN` holds the overrides;
  - `build()` / `build_n()` apply the master preset and set `print_settings_id` to the master name and `inherits_group[0]` to the parent.
- `master_preset.py`: generates, installs and reads the master preset.
- `apply_master.py`: re-syncs project 3MFs to the master, without a rebuild.
- `verify_plate2.py`: real 7.3 slices of the delivered single and plate 3MFs, which produce `verify_report.json` (also read by the pricing script).
- `slicecheck.py`:
  - `slice_3mf()` uses the 7.3 syntax with a fallback;
  - `parse_gcode` interpolates G2/G3 arcs.
- `export.py`, `export3.py`, `build3d.py`, `geom.py`, `plate.py`, `render.py`, `package.py`, `write3mf*.py`, `cli_multi.py`, `lineup.py`, `trace_tools.py`.

### Top-level scripts

- `finalize.py`: packages Downloads. Steps:
  1. `package`
  2. lineup and gallery
  3. sampler
  4. pricing model and guide
  5. master preset install and HOW_TO
  6. `apply_master`
- `rebuild_all.py`: rebuilds and verifies every packaged car, then runs finalize. `finish_cars.py --only=id,id` does the same for selected cars.
  - Both log to `rebuild_log.txt` and `rebuild_status.json`.
- `add_cars_pkg.py <ids>`: adds finished cars to `cars_pkg.json`. Names come from `NAMES` or from the queue files.
- `make_sampler.py`, `make_readme.py`, `make_gallery.py`, `pricing_inputs.py`, `make_pricing.py`, `make_pricing_guide.py`.

### Specs and docs

- `cars/<id>/spec.py`: the car specs.
- `cars/README_SPEC.md`: the spec format guide.

### Per car, the finish sequence is

```
python lib/export.py cars/<id>/spec.py cars/<id>/out
python lib/export3.py cars/<id>/spec.py cars/<id>/out
python lib/verify_plate2.py cars/<id>/out
python add_cars_pkg.py <id>
python finalize.py
```

`finish_cars.py --only=<id>,...` runs this whole sequence.

---

## 4. Things that failed and what replaced them

- **Creality Print 7.1/7.2 CLI:**
  - It crashed without an embedded thumbnail. Always embed thumbnails.
  - It crashed on multi-colour 3MFs (prime-tower pre-check). The workaround was an STL route plus single-colour analytic estimates. This is now obsolete, because the 7.3 CLI slices multi-colour files directly.
- **Old CLI syntax:** `--slice 1 --export-3mf` stopped working in 7.3. Use the new syntax above.
- **Shapes in project_settings:** lists that don't match the GUI's 2-filament config crash the slicer. `k2config.conform()` fixes them against `lib/gui_2filament_config.json`.
- **`verify_plate2.py`:** it had a circular reference (`two_colour = cp` pointed at itself). Fixed by copying the dict.
- **STEP export:** a fuse with one shape returned null on the C8. Guarded with `if len(shapes)==1`.
- **G2/G3 arcs:** the checker drew them as chords, which falsely reported lost features on the GT3 RS. Fixed by interpolating the arcs.
- **Audi R8 badge:** the middle rings were classified as lights. Fixed by loosening the `split_white` thresholds (circ > 0.90, aspect < 1.2).
- **Workflow script:** a CRLF line ending caused a "control characters" error. Write the script with LF only.
- **`__SEE_FILE__` placeholder args:** these failed. Point the prompts at the state files instead.
- **Workflow stalls and session limits:** use small pools (2–3) and retry the trace once.
- **Approved specs overwritten by running revise agents:** stop the workflow FIRST, then restore from `spec_SHOWN_*` and check that it rebuilds pixel-identical. Discarded revisions go to `work/spec_revision_discarded*.py`.
- **Wipe tower in the master preset:** `wipe_tower_x` and `wipe_tower_y` aren't system process preset keys, so they were left out. The plate 3MFs keep their own tower position.
- **Windows paths in bash heredocs:** escaping problems. Use the Write tool or Python `os.path.join`.
- **The Civic "not a one-swap" report:** this was the user's own mistake. The Civic is fine, at 1 change.

---

## 5. Next steps, in order, once the user says "continue"

1. **No-logo versions of everything: DONE 2026-10-01 (cloud session).**
   - Switch: `geom.py` sets `KC_BADGE=0` by default; `build_maps` skips `spec['badge']` unless `KC_BADGE=1`. Specs with
     `SHOW_BADGE` / `BADGE_ON` read the same variable (env checks added to mclaren_720s, c7_z06, lambo_urus, amg_gt,
     svj_aventador, c8_corvette; the AMG GT hood emblem now sits behind `BADGE_ON` too).
   - All 28 cars rebuilt with `--no-slice` in the cloud (all build types, 0 design errors), checked by eye.
     Previews: `previews/no_logo/`. Still to run on the PC: `python kc/rebuild_all.py` (slice checks + finalize).
   - Queue briefs (6, 7, 8), `README_SPEC.md` and the workflow prompts all carry the no-logo rule.
   - Cloud renders need a display: start `Xvfb :99` and set `DISPLAY=:99`.
   Original plan for reference:
   - Add one global switch (e.g. in `geom.badge_geoms` / `build_maps`, or an env/flag read by `export.py`) that drops every badge: the built-in types (roundel, star, rings, shield, flags, pony, bar) and the custom `SHOW_BADGE` badges.
   - Make it the default.
   - Run `python rebuild_all.py` (all 28 cars, about 2.5 min each), check that every car rebuilt and the logos are gone, then confirm finalize ran.
   - Tell the agents in all future design runs to make cars badge-free; the queue_batch8 briefs already say so.
2. **Snake-eye headlight variants** of the G80 M3 and G87 M2, as EXTRA versions next to the originals:
   - Get the exact headlight style or a reference photo from the user, or research it, before designing.
   - Use new ids, e.g. `g80_m3_snakeeye` and `g87_m2_snakeeye`, so the approved originals stay untouched.
3. **Resume the design runs:**
   - GR86 + BRZ: resume `wf_79ea1558-861` with `batchC_args.json`, or start fresh.
   - Then the rest of queue_batch6 in groups of 5: (g90_m5, f90_m5, ferrari_sf90, tesla_model3, tesla_models_plaid), then (jesko, ferrari_f40, huracan_evo, c6_corvette, c5_corvette).
   - Then queue_batch7, then queue_batch8. Ask about the Wrangler first.
   - Use pool 2–3 and 2 rounds. Add newly approved cars to `others`.
   - Show drafts as a contact sheet (reference | flat face | 3D render), as in `work/current_designs_*.png`, and snapshot the specs at show time.
   - When the user approves cars: stop the run, restore and lock the specs, then run `finish_cars.py --only=...`.
4. **Report back** to the user after each batch, with short updates.

---

## 6. Working from this repo (cloud session)

- The repo root plays the role of the old scratchpad: run every command from the repo root (`python kc/lib/...`), and pass
  the repo root as the workflow arg `sp` (`kc/batchC_args.json` has `<REPO_ROOT>` placeholders to replace).
- Install: `pip install -r requirements.txt` (Python 3.12+, cadquery 2.7 / OCP 7.8, vtk 9.3).
- No Creality Print in the cloud: use `--design-only` or `--no-slice`; `slicecheck`, `verify_plate2.py`, `rebuild_all.py`,
  `finish_cars.py`, `finalize.py` must run on the user's Windows PC (they slice with Creality Print 7.3 and write to Downloads).
  So in the cloud: design / trace / critique / build geometry; then on the PC: `git pull` + `python kc/finish_cars.py --only=...`.
- Presets: `kc/lib/k2config.py` and `master_preset.py` fall back to `kc/slicer_presets/` when the Creality AppData folders
  are missing. The installed preset on the PC stays the source of truth there; keep `kc/slicer_presets/<master>.json` in sync.
- Not in the repo (too big / regenerable): `kc/cars/*/out/` build outputs, agent scratch (`work/`, `cand/`), unused reference
  crops. Rebuild outputs with export.py. The G80 comes from `kc/cars/g80_m3/spec_from_step.pkl` (user STEP included as
  `G80Keychain_user_original.step`).
- The design workflow script is in `workflows/` (paths use `/`). In a Claude Code session the Workflow tool runs it via
  `scriptPath`; ultracode / explicit user opt-in is needed to launch workflows.


---

## 7. Cloud session 2026-10-01: design runs done, ALL APPROVED by the user

38 new car drafts, all logo-free, traced from real photos, 1 critique + 1 revision round each (cost cut agreed with
the user; `final_critique=false`, `consistency=false` in the args). Specs snapshotted as `spec_SHOWN_20261001_draft<X>.py`.
Contact sheets: `previews/drafts_batchD|E|F|G/contact_sheet.png`.

- Batch D: gr86, brz_zd8 (photos from the earlier PC run).
- Batch E: g90_m5, f90_m5, ferrari_sf90 (remade from photos after network access was opened), jesko, ferrari_f40,
  huracan_evo, c6_corvette, c5_corvette.
- Batch F (queue 7): g20_330i, lexus_lc500, g30_m550i, kia_stinger, s550_mustang, s650_mustang, audi_rs5, audi_rs7,
  nd_miata, camaro_1ss, ram_trx.
- Batch G (queue 8): dodge_viper, civic_type_r_fl5, f150, mini_cooper_s, elantra_n, silverado, escalade, x5m, x4m,
  macan, cayenne, nissan_350z. jeep_wrangler NOT designed: ask the user first (seven-slot grille trademark).

Next: the user reviews the sheets. On approval: copy the shown snapshot to `spec_APPROVED_by_user.py`, then on the PC
`python kc/finish_cars.py --only=<ids>` (real slice check + packaging). Still open from section 5: snake-eye G80/G87
variants (needs a reference from the user).
Spend in this session: about 14.4M subagent tokens (D 1.2M, E 3.3M, F 4.7M, G 5.2M), about $160 at the user's $11/M.

UPDATE (same day): the user approved all 33 new cars. Each `spec_APPROVED_by_user.py` is a copy of its last
`spec_SHOWN_20261001_draft*.py`, and all 33 are in `cars_pkg.json` (paths relative).
Snake-eye variants (user photos: two near-vertical DRL bars per lamp, CSL style) added as new ids
`g80_m3_snakeeye` and `g87_m2_snakeeye`, built by `kc/cars/_snakeeye.py` on top of the approved G80/G87, which stay
untouched. Also locked and packaged. The line is now 63 cars.
On the PC: `git pull`, then `python kc/rebuild_all.py` (all 63: slice check + Downloads packaging, 0 tokens).
