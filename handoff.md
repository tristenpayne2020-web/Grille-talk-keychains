# Handoff: Grille Talk car-front keychains (2026-10-04)

The repo is https://github.com/tristenpayne2020-web/Grille-talk-keychains.
- **Working branch:** `claude/exciting-pascal-4qpm9o`. All recent work is here.
- **Branch `main`:** older (see plan step 1).
- **Local clone on the user's PC:** `C:\Users\trist\grille-talk-keychains`, checked out on the working branch.
- **Delivery folder (PC):** `C:\Users\trist\Downloads\CarKeychains`. `finalize.py` regenerates it.
- **Extras (PC):** `Downloads\GrilleTalk_Extras`.

Run every command from the repo root unless noted. The scripts in `kc\` (`finish_cars.py`, `finalize.py` and so on) also work as `python kc\<script>.py`, because they chdir into `kc` themselves.

---

## 1. Goal

The user runs a small business called **Grille Talk**. It sells 3D-printed car-front keychains on Etsy, at car meets, and later through a Shopify site.

The starting point is the user's own BMW M3 G80 keychain (`kc/cars/g80_m3/G80Keychain_user_original.step`). Every other car follows the same design language.

The printer is a **Creality K2 + CFS** with the **0.4 nozzle only**. The slicer is **Creality Print 7.3**. The aims are bulk plates, minimal print time, and minimal purge waste.

### Design language

- Straight-on front view, cropped at the windshield base, mirror-symmetric.
- Body 80.5 mm wide and 3.0 mm thick.
- White body, black details, white DRL light signatures.
- Relief grille, using slats or mesh.
- Engraved grooves 0.5–0.6 mm.
- Keyring tab on the viewer's left: 4.5 mm hole with a 2.0 mm wall.
- Minimum feature and gap size 0.5 mm.

### Every car ships in 4 builds

| Build | Location | Changes per plate |
|---|---|---|
| 1-swap: black base 0–1.6 mm, white cap 1.6–3.0 mm | `1-swap_production` | 1 |
| Classic flush inlay, like the G80 | `classic_inlay` | ~15 |
| Custom body colour, 1-swap style (1 = black, 2 = body colour, 3 = white lights) | `custom_body_colour\1-swap_style` | ~8 |
| Custom body colour, classic style | `custom_body_colour\classic_style` | ~21 |

Each build has a STEP file, a single 3MF, a full-plate 3MF (260×260 bed, prime tower in the back-right corner at 216/229), STL parts and renders.

The package also includes:
- sampler plates with one of each car;
- `Pricing_Model.xlsx` and `PRICING_GUIDE.txt`;
- a gallery (`index.html`) and a lineup image;
- `_MASTER_SLICER_PRESET`.

### Standing user rules

- **No logos or emblems on any car.** This is for trademark reasons.
  - It is the default: `KC_BADGE=0` in `kc/lib/geom.py`. Setting `KC_BADGE=1` brings badges back.
  - The Jeep Trackhawk was removed and the Jeep Wrangler is on hold. The seven-slot grille is a Jeep trademark, so ask before designing the Wrangler.
- **BMWs:** exactly ONE tow-hook cover, on the viewer's left, `mirror=False`. Never a mirrored pair.
- **One master slicer preset, never per-car settings.**
  - The preset is `Grille Talk Keychain 0.20mm @Creality K2 0.4 nozzle`.
  - It is installed in `%APPDATA%\Creality\Creality Print\7.3\user\3477890751\process\`, with a copy in `kc/slicer_presets/`.
  - User settings in it: top shell layers 6, wall transition angle 50, ironing flow 25%, ironing spacing 0.12 mm.
  - To change a setting: edit the preset, then run `python kc/lib/apply_master.py "%USERPROFILE%\Downloads\CarKeychains" kc/cars/*/out`. That re-syncs every 3MF in seconds, with no rebuild.
- **Approved designs are frozen.**
  - Snapshot each spec when showing drafts (`spec_SHOWN_<stamp>.py`).
  - On approval, copy the snapshot to `spec_APPROVED_by_user.py`.
  - Never let a running revise agent overwrite an approved spec: stop the run first.
- **Work style:**
  - at most 1–2 revision rounds;
  - small batches (pool 2–3);
  - stop immediately when the user says "pause";
  - the user watches their usage limit, so keep design runs lean (`final_critique=false`, `consistency=false`).
- **Brand:** the name is "Grille Talk". Logo files are in `brand/`.

---

## 2. What has been done

### The line: 63 cars, all approved, locked, logo-free, built and packaged

The original 28:
- g80_m3, g87_m2, f82_m4, gt3rs_992, c8_corvette, gt500_mustang, r8_audi
- svj_aventador, amg_gt, r35_gtr, g20_m340i_lci, camaro_zl1, mclaren_720s
- ct5v_blackwing, charger_srt, mk5_supra, challenger_hellcat, f92_m8, e30_m3
- f87_m2, amg_gt63_4door, c7_z06, g42_m240i_lci, lexus_is350, civic_11th
- camry_xv80, bugatti_chiron, lambo_urus

33 more, from the cloud design runs (batches D–G, 2026-10-01). The user approved all of them:
- gr86, brz_zd8, g90_m5, f90_m5, ferrari_sf90, jesko, ferrari_f40, huracan_evo
- c6_corvette, c5_corvette, g20_330i, lexus_lc500, g30_m550i, kia_stinger
- s550_mustang, s650_mustang, audi_rs5, audi_rs7, nd_miata, camaro_1ss, ram_trx
- dodge_viper, civic_type_r_fl5, f150, mini_cooper_s, elantra_n, silverado
- escalade, x5m, x4m, macan, cayenne, nissan_350z

2 snake-eye variants:
- `g80_m3_snakeeye` and `g87_m2_snakeeye`, built by `kc/cars/_snakeeye.py` on top of the approved G80 and G87, which stay untouched.
- The 7-shaped DRL bars come from the user's own STEP.
- The G87 version uses shorter, more tilted bars, from user feedback.

### On the PC

- `python kc\finish_cars.py` (`rebuild_all`) ran for all 63: `DONE 63 of 63 ok`.
- A check on 2026-10-04 found all 63 folders in Downloads, each with 8 3MFs and 4 STEP files. The 6 sampler plates, the pricing files, the gallery and the master preset folder are there too.

### Extras, built from the user's STEPs

- **Steering-wheel keychain:** `kc/wheel/build_wheel.py`.
  - Scaled to 60 mm, black and gray.
  - Perforated leather grips only.
  - Gray centre disc with no logo.
  - Scroll wheels stay black.
  - Outputs single and 12-up plate 3MFs to `Downloads\GrilleTalk_Extras`.
- **G80 wall key holder, snake-eye, custom colour:** `kc/wall/build_wall_snakeeye.py`.
  - 3 filaments: black back plate, hood in the body colour (user request), white lights.
  - Roundel removed and filled flush.

### Other deliverables

- `WEBSITE_MASTER_PROMPT.md`: the brief for building the Grille Talk Shopify storefront in a later session. Assets are in `brand/`.
- Pricing research: average cost is about $1.10 per keychain. Suggested prices: Etsy $16.99 with free shipping (about $6 profit), car meet $10.
- Business name "Grille Talk", plus logo ideas and a brand identity summary (done in chat).

### In progress, not finished

**Batch H:** `tesla_model3` (Highland) and `tesla_models_plaid`.
- Args are in `kc/batchH_args.json`: pool 2, `max_rounds` 1, cloud mode.
- Commit `602bb37` says "traced drafts (in progress)".
- **Approved by the owner 2026-10-05** ("the teslas look good, approve them"): `spec_APPROVED_by_user.py` written for
  both (copy of `spec_SHOWN_20261004_built.py`) and both added to `cars_pkg.json` (65 entries).

---

## 3. Current state of the code and repo

### Uncommitted on the PC working copy

- `kc/pricing_cars.json`: regenerated for 63 cars by the PC run. This should be committed.
- `kc/cars_pkg.json`: line endings only.
- `kc/rebuild_log.txt`: should be gitignored.

### `main` vs the working branch

- `main` is 24+ commits behind the working branch.
- `main` has ONE commit the branch lacks: `3dadb32`, the finalize safety fix (see section 4). That is why the PC still hit the half-delete error on 2026-10-03.

### Key files

- `kc/lib/`:
  - `geom.py`: spec to 2D maps; holds the `KC_BADGE` switch.
  - `build3d.py`: 3D builds.
  - `export.py` / `export3.py`: 2- and 3-filament outputs.
  - `k2config.py` + `master_preset.py`: slicer config, always from the master preset.
  - `apply_master.py`.
  - `slicecheck.py` / `verify_plate2.py`: real Creality Print 7.3 slices.
  - `package.py`, `plate.py`, `render.py`, `write3mf*.py`.
- `kc/finish_cars.py` / `kc/rebuild_all.py`: build, slice check and package. Use `--only=id,id` for selected cars.
- `kc/finalize.py`: repackages Downloads.
- `kc/add_cars_pkg.py`: adds cars to the package list.
- `kc/cars/<id>/`:
  - `spec.py` and `spec_APPROVED_by_user.py`;
  - `spec_SHOWN_*` snapshots;
  - `ref/`: the reference photo and its `SOURCE.txt`.
- `kc/cars/_snakeeye.py`: builds the snake-eye variants.
- `kc/cars/README_SPEC.md`: the spec format guide.
- `kc/queue_batch6|7|8.json`: queue briefs. Everything is designed except the Teslas (in progress) and the Wrangler (on hold).
- `workflows/car-keychains-next.js`: the design workflow. Stages: trace, critique, revise, then an optional art-director pass.
  - Args: `sp`, `pool`, `max_rounds`, `cars`, `others`, `cloud`, `final_critique`, `consistency`.
  - Example: `kc/batchH_args.json`.
- `previews/`: contact sheets for each batch and the no-logo previews.
- `kc/slicer_presets/`: bundled Creality presets, so the code runs without Creality Print. `k2config` falls back to them when the AppData folders are missing.

### PC vs cloud

| | Cloud session | PC only |
|---|---|---|
| Can do | design, tracing, critique, geometry (`--design-only` / `--no-slice`) | slicing (Creality Print 7.3), `verify_plate2`, `finish_cars` / `rebuild_all` / `finalize`, Downloads, installing the master preset |
| Notes | needs `Xvfb :99` and `DISPLAY=:99` for renders | slicer: `C:\Program Files\Creality\Creality Print 7.1\CrealityPrint.exe` (version 7.3 despite the folder name), `--cli --slice 1 --outputdir DIR --need-gcode-file in.3mf`. `CREALITY_EXE` overrides the path |

The flow: design in the cloud, push, then on the PC `git pull` and `python kc\finish_cars.py --only=<ids>`.

**Build outputs (`kc/cars/*/out/`) are NOT in git.** They are several GB. They exist only on the PC, made by the 63-car run.

---

## 4. Failures and lessons

- **Packaging wiped Downloads halfway (twice).** `finalize.py` deletes the old package first. Whenever a File Explorer window, Creality Print or a terminal had something open inside `Downloads\CarKeychains`, the delete failed midway and left the package half deleted. It happened on 2026-10-01 and again on 2026-10-03 with the snake-eye run.
  - The fix (`3dadb32`, on `main` only) checks that every car has build outputs, then renames the folder in one step. If anything is open it stops and deletes nothing.
  - The fix must be merged into the working branch.
  - Until then: close Explorer and Creality Print windows on that folder before running finish or finalize.
- **The repo was handed over without telling the user that `out/` isn't in git.** So the first `finish_cars --only=gr86` on the PC could not package. It also built a stale GR86 from `main`, because the cloud work was on another branch. Always say which branch to pull, and say when a full rebuild is needed.
- **PowerShell 5.1 has no `&&`.** Give the user one command per line, and real values, not `<placeholders>`.
- **Creality Print 7.1/7.2 CLI:**
  - it crashed without an embedded thumbnail;
  - it crashed on multi-colour 3MFs.
  - The workarounds are obsolete: the 7.3 CLI slices multi-colour files. The old `--export-3mf` syntax no longer works.
- **Shapes in project_settings:** list lengths that don't match the GUI's 2-filament config crash the slicer. `k2config.conform()` handles it.
- **Revise agents overwrote approved designs.** Stop the run first, then restore from `spec_SHOWN_*` and verify it rebuilds pixel-identical.
- **Design bugs fixed:**
  - Audi R8 ring interiors were read as lights (fixed in the `split_white` thresholds);
  - the G2/G3 arcs were drawn as chords in the checker, which reported false lost features;
  - a single-shape fuse returned null in the STEP export (guarded).
- **Workflow script:** CRLF line endings caused "control characters" errors. Keep LF; `.gitattributes` enforces it.
- **Bash heredocs** mangled Windows backslashes. Use the Write/Edit tools for files containing paths.
- **Not verified in the Creality Print GUI**, because the user denied computer-use access:
  - that the master preset shows in the list;
  - that Ctrl+I imports a 3MF as geometry while keeping the per-part filaments.
- **Removed by the user:** Pagani Zonda Cinque, Jeep Trackhawk.
- **The Civic "not a one-swap" report** was the user's own mistake. The Civic is fine.

---

## 5. Plan (next session)

1. **Housekeeping (PC, quick):**
   - Merge `main` into `claude/exciting-pascal-4qpm9o`, which brings in the finalize safety fix.
   - Commit `kc/pricing_cars.json` and gitignore `kc/rebuild_log.txt`.
   - Push, then make the working branch the default, or merge it into `main` and use `main` from then on. Tell the user which one.
2. **Finish batch H:** Tesla Model 3 (Highland) and Model S Plaid.
   - Show the contact sheet and snapshot the specs.
   - On approval: lock the specs, `add_cars_pkg`, then on the PC `python kc\finish_cars.py --only=tesla_model3,tesla_models_plaid`.
3. **Jeep Wrangler:** only if the user explicitly says yes, despite the trade-dress risk.
4. **Extras:** check that the user is happy with the steering-wheel keychain and the G80 wall key holder. Offer the other cars' snake-eye or wall-holder variants only if asked.
5. **Shopify storefront:** build it from `WEBSITE_MASTER_PROMPT.md` and `brand/` when the user asks.
6. **Whenever the user changes slicer settings:** edit the master preset and run `apply_master.py`. Never rebuild per car for settings.
7. **Report briefly** after each step and pause whenever asked.

---

## 8. Shopify storefront (2026-10-04, branch `claude/tender-thompson-6c67sz`)

Built from `WEBSITE_MASTER_PROMPT.md`. Run and setup instructions: `theme/README.md`.

- **Branch:** `claude/tender-thompson-6c67sz` = `claude/exciting-pascal-4qpm9o` + `main` merged (finalize safety fix) + the storefront. No PR.
- **Launch scope (owner decision):** 26 cars (the first 20; M340i, Civic 11th gen, Camry; Kia Stinger; Tesla Model S Plaid, added 2026-10-04/05; the Model 3 was dropped by the owner 2026-10-05), 6 body colors (White $6.99; Matte Red, Matte Yellow, Matte Gray, Matte Blue $7.99; Metallic Silver $8.99) and a Headlight color option (White included; Red, Yellow, Gray, Blue, Silver +$0.50), so 36 variants per product. Source of truth: `site/catalog/launch.json` (ids, colors, tier prices, make/model/generation/short_model naming table).
- **Later, when the owner says so:** add the other 40 cars and the 7 remaining colors (Green, Purple, Gold, Metallic Red/Blue/Green/Purple). Steps in `theme/README.md` > "Adding the rest of the line". Keep the "40+ more cars coming soon" note until then.
- **Pipeline (`site/tools/`, outputs in gitignored `site/build/`):** `build_geometry.py` (logo-free rebuild, never touches `kc/cars/*/out/`) > `make_glb.py` > `compress_glb.mjs` > `make_images_blender.py` (Blender Cycles; `make_images.mjs` is the old three.js fallback) > `make_media.py`, plus `make_svgs.py`, `make_brand.py`, `make_hero_assets.py`, `make_csv.py`, `upload_media.py` (token from env/.env only).
- **Theme (`theme/`):** OS 2.0, `shopify theme check` clean. First-visit loader with the owner's artwork, cinematic hero (3D keychain on jump ring + chain physics), range viewer with arc, pinned detail tour and process chapters (ideas adapted from ciaoenergy.com and kryntixstudio.com, nothing copied), catalog with S&D filters, product page with model-viewer recolor, cart drawer, predictive search, request-a-car, about, contact, FAQ, 404.
- **Preview:** `cd site` then `node preview/server.mjs` (liquidjs + mock data) at http://localhost:4100. `node tools/audit.mjs` runs 90 checks (uses the GPU; set GT_SOFTWARE_GL=1 without one); reports in `site/build/reports/`.
- **Not done (needs the owner):** Shopify store, payments, domain, policies, metafield definitions, menus, CSV import, media upload. Full list in `theme/README.md`.

### Wall-mounted key holder (2026-10-05)

- `kc/wall/build_wall_snakeeye.py` now cuts two countersunk 4.5 mm wall-mounting holes (owner request), placed
  automatically on the outer edges below the headlights. Rebuilt and copied to `Downloads\GrilleTalk_Extras`; the
  owner's previous 3MF is backed up next to it. Not slice-verified in Creality Print here: slice once before printing.
- On the site as its own product type and collection, same options as the keychains, base price $11.99.

### Tesla Model S Plaid approved; Model 3 dropped (2026-10-05)

The owner then dropped the Model 3 ("don't do the model 3"): not on the site, not printed, not approved (its
`spec_APPROVED_by_user.py` was removed, it is out of `cars_pkg.json` and `launch.json`; the draft spec stays in `kc/cars/tesla_model3/`).

The owner approved both from the renders. Specs are locked (`spec_APPROVED_by_user.py`), both are in `cars_pkg.json`,
and `launch.json` no longer marks them unapproved. `finish_cars` built and sliced them, but `finalize.py` stopped
because a window had `Downloads\CarKeychains` open (nothing was deleted): close it and run `python kcinalize.py`.

### Product changes the owner made (2026-10-04)

- Printed face-down on a carbon-fibre build plate, so the back has a woven carbon finish, with GRILLE TALK in white
  sans lettering across the back. The website models and copy show this (`site/tools/make_glb.py`: `back` and
  `lettering` nodes). The print files in `kc/` were not changed here; the owner made that change on their side.
- Custom headlight color option, +$0.50.

### Found while building the site: the PC's print package still has badges

The STLs in `kc/cars/*/out/` and the package in `Downloads\CarKeychains` were built on 2026-10-01 at 13:34 while the PC was still on `main`, before it checked out the logo-free branch (14:23). Seen in the files: the G80 production STL has the BMW roundel; `Downloads\CarKeychains\Porsche_911_GT3RS_992\custom_body_colour\1-swap_style` render shows the Porsche crest. Most likely all of the original 28 cars are affected; the 35 later cars were designed logo-free.

Fix on the PC (close Explorer and Creality Print windows on `Downloads\CarKeychains` first):

```
python kc\finish_cars.py
```

The website is not affected: it uses its own logo-free rebuild in `site/build/geom/`.

### Uncommitted on the PC

`kc/pricing_cars.json` (regenerated by the PC run) is still uncommitted, left as it was.

---

## 8. 2026-10-04 (PC session): back label + Teslas

- **"GRILLE TALK" in white on the back of every keychain** (user decision). `kc/lib/backtext.py`, hooked into all four
  builds in `build3d.py` (`build_production`, `build_classic`, `build_production3`, `build_classic3`; internal `_production`
  / `_classic` are the raw builds). Black label plate + flush white letters in the bottom 0.4 mm (2 layers), DejaVu Sans
  Bold, cap 4.5 mm (shrinks to 3.5 if it does not fit), letter gap ~0.6 mm, mirrored so it reads from the back.
  Custom-colour builds put the letters in filament 3 (white). Switch off with `KC_BACKTEXT=0`. Preview: `previews/back_label.png`.
  Cost, from real slices: 1-swap plate 1 -> 4 filament changes, classic unchanged (15), custom 1-swap 8 -> 11, custom classic ~23.
- **Teslas built and packaged** on the PC: `tesla_model3` (14/plate, 5h07m 1-swap), `tesla_models_plaid` (13/plate, 5h25m).
  Specs snapshotted as `spec_SHOWN_20261004_built.py`; not yet locked as approved (`previews/teslas_built.png`). Line = 65 cars.
- `rebuild_all.py` / `finish_cars.py` no longer build the 5 old NEW cars twice (dedupe).
- Full rebuild of all 65 with the label started on the PC (`python kc/rebuild_all.py --skip-done`).
