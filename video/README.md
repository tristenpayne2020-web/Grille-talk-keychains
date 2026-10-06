# Grille Talk launch films

Every 3D shot is rendered photoreal in **Blender** (EEVEE on the GPU): a real spotlight beam through haze, emissive headlights, bloom, depth of field and motion blur. The edit, the type, the light leaks and the music sync are done in **Remotion**. The soundtrack is "Ritual" by BalloonPlanet (Artlist licence). Art direction is in `DIRECTION.md`.

| File (in `out/`) | Composition | Size | Length |
|---|---|---|---|
| `grilletalk_launch_9x16.mp4` | `Launch9x16` | 1080 × 1920 | 30 s |
| `grilletalk_launch_16x9.mp4` | `Launch16x9` | 1920 × 1080 | 30 s |
| `grilletalk_cutdown_1x1.mp4` | `Cutdown1x1` | 1080 × 1080 | 15 s (re-uses the 9:16 shots, cropped) |
| `grilletalk_spinner_9x16.mp4` | `Spinner9x16` | 1080 × 1920 | 12 s |
| `grilletalk_wall_9x16.mp4` | `Wall9x16` | 1080 × 1920 | 12 s |

## How it is built

1. **`python timeline.py`** writes `src/timeline.json`.
   - It holds the song's bar and beat grid (about 95 BPM, drop at 94.69 s) and every shot's start frame and length, for all four timelines.
   - Blender and Remotion both read it, so every cut sits on a bar or a beat.
2. **`python render_all.py`** renders every Blender shot into `public/shots/<film>_<shape>/<shot>/0000.jpg ...`.
   - It runs `blender/shots.py`, which uses the shared library `blender/gt.py`.
   - It is resumable: frames already on disk are skipped.
   - It takes about 1.5 h on the RTX 5070 at roughly 2.2 s per 1080p frame.
   - `blender/gt.py` holds:
     - the scene, haze, beam, floor and lights;
     - the look-dev reused from `site/tools/blender_render.py`;
     - the compositor "aura";
     - the keychain with its deterministic chain;
     - the wall holder with hook detection;
     - the Talon;
     - the modelled keyring and keys.
   - Look-dev one shot: `blender -b --factory-startup -P blender/shots.py -- shot=hook w=540 h=960 frames=152 out=renders/test test=30,90`.
3. **Remotion** plays the frames, adds the type, the callouts, the light leaks, the drop flash, the beat punch, grain and the music.
   - Bundle: `npx remotion bundle --out-dir=build`
   - Render: `npx remotion render build Launch9x16 out/_raw/grilletalk_launch_9x16.mp4`, and the same for each composition.
   - Encode: `python encode_final.py` re-encodes to the delivery spec (H.264 CRF 18, yuv420p limited range, BT.709, AAC, faststart).
4. **Preview:** `npx remotion studio`.

## Files not in git

- **The song:** `public/music/ritual.mp3`. Copy it from Artlist again if needed.
- **The rendered frames:** `public/shots`. Re-render them with `render_all.py`.
- **The renders:** `out/`.
- **The GLBs:** they come from `../site/build/glb_raw` and `../site/build/glb`, which are not in git either.

## Changing the music

- Replace `public/music/ritual.mp3`.
- Set `DROP` and `BAR` in `timeline.py` to the new track (find the drop's kick onset and measure the bar length).
- Re-run `timeline.py`, re-render the shots whose length changed, then re-render the films.

## Legal

- No car-maker logos, badges or wordmarks appear, and the models are logo-free.
- Car names are not shown.
- The end card carries the independent-maker line.
- The licence for "Ritual" is tagged in the MP3 ("Licensed for video by Artlist.io"). Keep your Artlist licence record for paid ads.
