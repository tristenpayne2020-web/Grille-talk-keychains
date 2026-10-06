# Prompt: Grille Talk product video ad (Remotion)

Paste everything below the line into a Claude session opened on `C:\Users\trist\grille-talk-keychains` on this PC.
The 3D models and renders live in `site/build/`, which is not in git, so a cloud session cannot see them.

---

You are a senior motion designer and Remotion engineer. Make a premium, launch-quality video ad for **Grille Talk**,
my small business that sells three product lines, all 3D-printed and logo-free:

1. **Car-front keychains:** the front of a real car (lights, grille, intakes in relief), on a chain and split ring.
2. **Wall-mounted key holders:** the same car fronts, scaled up for the wall, with four key hooks.
3. **The Talon finger spinner:** a topology-optimised carbon fiber frame around a ball bearing, on your keys.

The video must feel like a hardware launch film (think Apple or Nothing product films): dark, precise, physical,
product-first. Build it in code with Remotion and render real MP4s. Work autonomously, and check your own output
visually before you call anything done.

## 0. Load these skills first, and follow them

- `/remotion`: project setup, compositions, `useCurrentFrame`, `spring`, `interpolate`, `Sequence`, `@remotion/three`,
  `staticFile`, rendering. If it conflicts with your habits, the skill wins.
- `/taste-skill`: choose the art direction before writing code. Route to `cinematic-product` (fallback `dark-luxe`),
  read its skill file and the matching `components/style-recipes.md` section, and apply them. State the direction you
  chose in one paragraph in `video/DIRECTION.md` before building.

## 1. Read before you build

- `ads/make_ads.py` and the PNGs in `ads/out/`: the 10 still ads already made. The video must look like their moving
  sibling (same palette, type, spotlight, grain, CTA style).
- `theme/assets/keychain3d.js`: how the site loads the keychain GLBs, pivots them and hangs the chain with verlet
  physics. Reuse the approach. In Remotion every simulation must be deterministic per frame: step the physics from
  `useCurrentFrame()` with a fixed dt (re-simulate from frame 0, or cache the states), never `requestAnimationFrame` or
  wall-clock time.
- `theme/assets/display3d.js`: the floating pedestal and spotlight display from the website. It's a good source for a
  "product on a plinth" shot.
- `site/catalog/launch.json`: the product catalog. Read prices, colours, headlight options and product names from it.
  Never hardcode a price.

## 2. Asset inventory (copy what you use into `video/public/`)

### 3D models: `site/build/glb/<id>.glb`
glTF binary with KHR_mesh_quantization (three.js GLTFLoader reads it natively; no Draco or meshopt decoder needed).
Units are metres, but the quantization puts a scale on nodes, so **normalise every model by its bounding box** after
loading, never by assumed numbers. The front face looks along +Z.

| Product | Files | Nodes / materials |
|---|---|---|
| Keychains (34) | `g80_m3_snakeeye`, `g80_m3`, `f90_m5`, `mk5_supra`, `c8_corvette`, `c7_z06`, `r35_gtr`, `gt3rs_992`, `svj_aventador`, `mclaren_720s`, `amg_gt`, `challenger_hellcat`, `charger_srt`, `ram_trx`, `escalade`, `chevy_tahoe`, `tesla_models_plaid`, `kia_stinger`, `lexus_is350`, `ct5v_blackwing`, `elantra_n`, ... (all ids in `launch.json` → `cars`) | `keychain` > `body` (body colour, recolour this), `details` (black), `lights` (headlights, recolour for custom headlights), `back` (carbon-fibre textured), `lettering` (GRILLE TALK on the back); `link_0..n` + `ring` = jump ring, chain, split ring |
| Wall key holders (7) | `g80_wall_snakeeye`, `f90_m5_wall`, `mk5_supra_wall`, `charger_srt_wall`, `gt500_mustang_wall`, `camaro_zl1_wall`, `c8_corvette_wall` | `body` (face + 4 hooks, recolour), `details` (black back plate and recesses), `lights` (headlights). About 241 mm wide, 31.5 mm deep at the hooks. No chain; the flat back goes against the wall. |
| Talon spinner | `talon_spinner` | `talon` (the carbon fiber frame), `outer` / `inner` (steel bearing races), `shield` (bearing shield), `Torus` (split ring). Already stood upright (face +Z). To spin it, rotate the frame (and the outer race with it) about the bearing axis while `inner` stays still on the finger; the ring swings. |

### Photoreal Blender renders (transparent PNG, 2000 px): `site/build/renders_png/`
- Keychains: `<id>__<colour>__front.png` and `<id>__<colour>__angle.png` (angle includes the chain).
  Colours: `white`, `matte-red`, `matte-yellow`, `matte-gray`, `matte-blue`, `matte-black`, `metallic-silver`.
- Carbon back: `<id>__white__back.png` (e.g. `g80_m3__white__back.png`).
- Hero G80 with coloured headlights: `g80_m3_snakeeye__gray-yellow__front-chain.png`, and in `site/build/ads/src/`:
  `g80se_black-red.png`, `g80se_black-red_angle.png`, `g80se_white-blue.png`, `g80se_silver-yellow.png`,
  `g80se_red-white.png` (the `t_` versions are trimmed to the object).
- Wall key holders: `<id>__<colour>__front.png` and `__angle.png` for all 7 ids and all 7 colours.
- Spinner: `talon_spinner__black-cf__angle.png`, `talon_spinner__black-cf__front.png` (top view).
- Use the PNGs for 2.5D shots and as a fallback if a 3D shot can't match their quality. They are the quality bar
  for materials and lighting.

### Brand
- Logo: `theme/assets/logo-metal-1600.webp` (metallic wordmark), `theme/assets/logo-flat.svg`, `logo-mark.svg`.
- Display font: `theme/assets/michroma-latin-400.woff2` (Michroma), for headlines and eyebrows (uppercase, wide
  tracking). Body: a clean system sans (Segoe UI or Inter-like).
- Owner artwork: `brand/concept/hero_halftone_g80.webp`, a halftone G80 front with the logo. Use it for the intro
  or end card, as a backdrop with low opacity and a slow drift.
- Palette: background #070708, panels #0b0b0c to #141416, text #f2f1ee, muted #9b9a97. The CTA is a solid
  #f2f1ee button with #070708 text. Light is warm white (#fff8ee). Accents only come from the products.

## 3. Facts you may say (nothing else)

Do not invent reviews, ratings, sales numbers, "best", shipping times, materials or origin claims.

- **Keychains:** 34 cars and counting; 7 body colours; custom headlight colour (+$0.50, White included); from $6.99;
  80.5 mm wide, 3 mm thick; carbon-fibre textured back with GRILLE TALK; logo-free designs; printed in high-quality
  PLA; "Don't see your car? Request it."
- **Wall key holders:** "Your car, by the front door"; 7 cars (G80 M3 snake-eye, M5 F90, Supra, Charger Hellcat,
  Mustang GT500, Camaro ZL1, Corvette C8); four hooks; every body colour, plus custom headlights; from $14.99;
  double-sided tape recommended, countersunk screw holes on each side (tape, screws and nails are not included);
  for keys only (not coats or bags).
- **Talon spinner:** $12.99; "printed in highly durable carbon fiber material, made for rigidity and built to last";
  6804 ball bearing; 20 mm finger hole; topology-optimised lattice ("solid where it works, light everywhere else");
  about 74 × 42 mm.
- **Site:** grilletalk.shop

## 4. Legal (must follow)
- Never show a car-maker logo, badge, emblem or wordmark. The models are logo-free; don't add any, and don't
  reference brand fonts or marketing lines.
- Car names only identify which car a design is based on ("Inspired by the BMW M5 (F90)").
- The end card carries, small: "Grille Talk is an independent maker, not affiliated with or endorsed by any vehicle
  manufacturer."
- No copyrighted music or samples. Make the sound design yourself:
  - synthesise whooshes, clicks, a bearing whirr for the spinner and a low impact on the logo (e.g. with numpy/scipy
    or ffmpeg's `aevalsrc` and filters, as WAV files in `video/public/sfx/`)
  - leave the music bed empty with a clearly named `music_bed_PLACEHOLDER` track so I can drop in a licensed song
  - everything must also work with the sound off

## 5. Deliverables (render to `video/out/`)

| File | Size | Length | Use |
|---|---|---|---|
| `grilletalk_launch_9x16.mp4` | 1080×1920, 30 fps | 30 s | TikTok, Reels, Stories (main cut) |
| `grilletalk_launch_16x9.mp4` | 1920×1080, 30 fps | 30 s | YouTube, website |
| `grilletalk_cutdown_1x1.mp4` | 1080×1080, 30 fps | 15 s | Feed |
| `grilletalk_spinner_9x16.mp4` | 1080×1920, 30 fps | 12 s | Spinner-only ad |
| `grilletalk_wall_9x16.mp4` | 1080×1920, 30 fps | 12 s | Wall key holder-only ad |

Also deliver a poster PNG per video, plus `video/README.md`: how to preview (`npx remotion studio`), how to re-render
each video, and how to swap in music.

H.264, CRF around 18, yuv420p, AAC audio. Keep each file under 50 MB.

## 6. Shot list: main 30 s cut (9:16; adapt the framing for 16:9)

Every beat has one idea, one line of text and one hero product. The text animates in with mask reveals and a
letter-spacing settle, holds long enough to read (about 0.25 s per word, at least 1.2 s), then clears before the next beat.

| Time | Shot | Motion (3D unless noted) | On-screen text |
|---|---|---|---|
| 0.0-2.0 | **Hook.** Black frame; an overhead spotlight snaps on (light cone, dust in the beam). The gray G80 snake-eye keychain with yellow headlights drops into the light on its chain and settles with a real pendulum swing. | Camera low, slight push-in; chain physics; the yellow lights bloom softly as they catch the light. | YOUR KEYS SHOULD MATCH YOUR CAR. |
| 2.0-6.0 | **Detail macro.** Shallow-depth-of-field orbit across the light signature, grille and intakes; relief edges catch a raking light. | Slow orbit (about 25°) and dolly in; focus pull from the lights to the grille. | Every light. Every intake. |
| 6.0-9.0 | **Headlights.** Same keychain, straight on. The headlights switch White → Yellow → Red → Blue on the beat, with a tiny light-flash on each change. | `lights` material colour keyed per beat; micro camera shake on each change. | PICK THE LIGHTS. +$0.50 |
| 9.0-12.0 | **Colours.** Match-cut through all 7 body colours (same pose, the colour snaps each 0.35 s), then the 7 fan out side by side. | Recolour `body`; the fan-out uses springs with a stagger. | 7 COLORS. |
| 12.0-14.5 | **Flip.** The keychain turns 180° on its chain to show the carbon-fibre back and GRILLE TALK lettering, with a light sweep across the weave. | Y rotation with a spring overshoot; the chain reacts. | FLIP IT. |
| 14.5-18.5 | **The garage.** A fast rhythmic run of different cars: either a 3D carousel orbiting a dark pedestal, or hard cuts in time with the SFX. Use 8-10 cars across makes (M5, Supra, C8, GT-R, 911 GT3 RS, Aventador, Hellcat, TRX, Escalade, Model S), each in a different colour. | Carousel rotation, or per-car push-ins of 4-6 frames. | 34 CARS AND COUNTING. |
| 18.5-23.0 | **Wall key holders.** Cut to a warm, softly lit wall (subtle plaster texture, a lamp glow from above, a skirting line). A Supra holder is on the wall; a set of keys (simple procedural key + ring geometry) swings onto a hook and settles. Rack focus, then a quick lateral pan past two more holders (F90 M5 in blue, G80 snake-eye in black). | Keys on a pendulum; camera pan; holders cast soft contact shadows on the wall. | YOUR CAR, BY THE FRONT DOOR. · WALL KEY HOLDERS FROM $14.99 |
| 23.0-27.0 | **Talon spinner.** Back to black. The Talon spins up on its bearing: the frame rotates fast around the steel races, with motion blur on the lattice. The camera orbits to show the topology-optimised web, then it decelerates and stops with the keyring hanging. | Bearing spin with angular-velocity ease-out (`spring`), frame-blur trails; orbit. | THE TALON. · CARBON FIBER. BUILT TO LAST. · $12.99 |
| 27.0-30.0 | **End card.** The halftone G80 artwork fades up behind; the metallic logo reveals with a light sweep. Then CTA. | Logo mask reveal and light sweep; slow drift on the artwork. | FIND YOUR CAR · grilletalk.shop · legal line (small) |

**15 s 1:1 cut-down:** Hook (2 s), Headlights (2.5 s), Garage (3 s), Wall holder (2.5 s), Spinner (2.5 s), End card
(2.5 s).

**12 s spinner ad:**
1. Macro on the lattice: "Topology optimised."
2. Spin-up with bearing whirr: "Carbon fiber. Built to last."
3. Specs as clean callout lines pointing at the parts: "6804 bearing · 20 mm finger hole · 74 × 42 mm"
4. Price + CTA: "$12.99 · Get the Talon"

**12 s wall ad:**
1. Keys drop onto a hook: "Your car, by the front door."
2. Colour cycle on the wall: "Every body colour."
3. Mounting callouts: "Double-sided tape or two countersunk screws" (small: "Tape and screws not included")
4. Lineup of the 7 holders: "From $14.99 · Shop wall key holders"

## 7. 3D and look-development spec

- **Renderer:** `@remotion/three` (React Three Fiber) with `<ThreeCanvas>`. Physically based materials, ACES or AgX-like
  tone mapping, sRGB output, antialiasing on; render at the composition size (no upscaling).
- **Lighting:** a key area-style light from above-front (warm white), a cool rim light from behind for separation on
  dark products (black keychains must never disappear into the background), a soft fill, and an environment map
  (RoomEnvironment or a neutral studio HDRI) at low intensity for reflections on the steel chain and bearing.
- **Shadows:** soft contact shadows (shadow-catcher plane or `ContactShadows`) under every product.
- **Materials:**
  - PLA body: roughness 0.55-0.65, a faint layer-line bump if feasible
  - details: near-black, roughness 0.4
  - chain, ring and bearing: metalness 1, roughness 0.15-0.25
  - Talon frame: matte carbon fiber (very dark gray, roughness 0.6, fine noise bump)
  - metallic silver body: metalness 0.75, roughness 0.34
- **Camera:** 35-85 mm equivalent; slow, motivated moves; depth of field on macro shots (postprocessing DoF, or a
  stacked-blur 2.5D fake if 3D DoF is too heavy). No dutch angles or spins for their own sake.
- **Physics:** chains and keys on hooks use a deterministic verlet rope, as in `keychain3d.js` (gravity, damping, fixed
  link lengths, the jump ring constrained to the hole). Re-simulate from frame 0 so any frame renders identically.
- **Post:** subtle film grain (match `ads/out`), gentle vignette, a light bloom only on the headlights and spotlight.
  No chromatic aberration or glitch effects.
- **Performance:** load each GLB once (`useGLTF` and `preload`); clone the scene per instance and recolour clones,
  never shared materials.

## 8. Typography and motion system

- Headlines: Michroma, uppercase for short lines, tracking 0.02-0.06em, 72-110 px in 9:16.
- Eyebrows: Michroma 20-24 px, tracking 0.3em, muted colour.
- Prices: same weight as the headline or one step down; never cramped.
- Easing: one family across the film (e.g. `Easing.bezier(0.16, 1, 0.3, 1)` for entrances and a matching exit
  curve); springs for physical objects only.
- Rhythm: cut on the SFX beats; keep a 120 BPM grid (every 15 frames at 30 fps) so a music bed can be laid in later.
- Safe zones: in 9:16, keep text out of the top 220 px and the bottom 380 px (platform UI), and 64 px from the sides.

## 9. Code structure

```
video/
  package.json            remotion, @remotion/three, three, @react-three/fiber, @react-three/drei
  src/Root.tsx            registers all 5 compositions
  src/brand.ts            colours, fonts, easing, safe zones
  src/data.ts             reads ../site/catalog/launch.json at build time (prices, colours, products)
  src/three/              Keychain.tsx, WallHolder.tsx, Spinner.tsx, Studio.tsx (lights, env, shadows), chain physics
  src/scenes/             one file per beat (Hook, Detail, Headlights, Colours, Flip, Garage, Wall, Spinner, EndCard)
  src/compositions/       Launch9x16, Launch16x9, Cutdown1x1, Spinner9x16, Wall9x16 (they reuse the scenes)
  public/                 copied GLBs, PNGs, font, logo, artwork, sfx/
  out/                    the renders
  DIRECTION.md, README.md
```

## 10. Quality gate (do this before the final renders)

1. Render stills at the middle of every beat for every composition (`npx remotion still <comp> --frame=N`), then look
   at each one. Fix anything that fails:
   - products crisp, well lit and separated from the background (especially Matte Black)
   - text legible, inside the safe zones, never overlapping a product's important detail
   - no logos or badges anywhere
   - every number on screen matches `launch.json`
   - no empty frames, popping or z-fighting
2. Scrub the full timeline in Studio for jitter in the physics, and check that each frame renders the same twice.
3. Render all the MP4s, then pull 6 frames from each final file with ffmpeg to confirm the encode and colours.
4. Report back with:
   - the file list with durations and sizes
   - one contact sheet image per video (6 frames)
   - the direction you chose
   - any shot you simplified, and why
   - what I need to do: add music, review the copy
   Do not upload or post anything.
