# Grille Talk - car-front keychains

3D-printable car-front keychains in the style of the owner's BMW M3 G80 keychain, built for bulk printing on a
Creality K2 + CFS (0.4 nozzle) and sliced in Creality Print 7.3.

**Start here: [handoff.md](handoff.md)** - goal, current state, file map, what failed, next steps.

## Layout
- `kc/lib/` - pipeline (spec -> 2D maps -> 3D builds -> STL/STEP/3MF -> slice checks -> packaging)
- `kc/cars/<id>/spec.py` - one spec per car (`spec_APPROVED_by_user.py` = locked, user-approved design), `ref/` = reference photo
- `kc/style/` - the design-language references (the user's own G80)
- `kc/slicer_presets/` - Creality presets bundled so it runs without Creality Print installed, incl. the master preset
- `kc/queue_batch*.json` - cars waiting to be designed
- `workflows/car-keychains-next.js` - the multi-agent design workflow (trace -> critique -> revise -> art director)

## Run (from the repo root)
```
pip install -r requirements.txt
python kc/lib/export.py kc/cars/<id>/spec.py kc/cars/<id>/out --design-only   # fast 2D preview (face.png, overlay.png)
python kc/lib/export.py kc/cars/<id>/spec.py kc/cars/<id>/out --no-slice      # full build without the slicer
```
Slicing checks, `verify_plate2.py`, `finalize.py` (packaging into Downloads) and installing the master preset need the
user's Windows PC with Creality Print 7.3 (`CREALITY_EXE` env var overrides the slicer path).
