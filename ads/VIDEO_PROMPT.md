You are making a premium product video ad for Grille Talk, my small business selling 3D-printed car-front keychains,
wall key holders and a finger spinner. Build it in code with Remotion and render real MP4 files.

## Skills to load first
1. `/remotion`: how to build, preview and render Remotion compositions. Follow it.
2. `/taste-skill`: pick the art direction. The brand is dark, monochrome and cinematic, with a premium hardware-launch feel
   (route to `cinematic-product` or `dark-luxe`). Product is the hero, one idea per scene, generous negative space,
   no generic AI-slop styling.

## Project and assets (all local, Windows)
Repo: `C:\Users\trist\grille-talk-keychains`. Create the Remotion project in `video/` inside it (its own package.json).
Copy the assets you use into `video/public/`.

- **3D models (use these for real 3D motion):** `site/build/glb/<id>.glb`. glTF binary files with KHR_mesh_quantization,
  which three.js GLTFLoader reads natively. Nodes: `keychain` > `body` (body colour), `details` (black), `lights`
  (headlights), `back` (carbon-fibre textured), `lettering` (GRILLE TALK, on the back); `link_0..n` and `ring`
  (jump ring, chain, split ring). Recolour by setting the `body` / `lights` material colour.
  Good hero ids: `g80_m3_snakeeye`, `f90_m5`, `mk5_supra`, `c8_corvette`, `r35_gtr`, `svj_aventador`, `ram_trx`,
  `escalade`, `tesla_models_plaid`. The spinner is `talon_spinner.glb`.
  `theme/assets/keychain3d.js` already loads these GLBs and hangs the chain with verlet physics. Read it and reuse the ideas
  (the physics must be deterministic per frame in Remotion: step it from `useCurrentFrame()`, never real time).
- **Photoreal Blender renders (transparent PNG, 2000 px):** `site/build/renders_png/<id>__<colour>__<view>.png`
  - colours: white, matte-red, matte-yellow, matte-gray, matte-blue, matte-black, metallic-silver
  - views: `front`, `angle` (with chain); `white__back` shows the carbon-fibre back with GRILLE TALK
  - hero with custom headlights: `g80_m3_snakeeye__gray-yellow__front-chain.png`, plus
    `site/build/ads/src/g80se_black-red*.png`, `g80se_white-blue.png`, `g80se_silver-yellow.png`
  - wall key holders: `<car>_wall__<colour>__front.png` (e.g. `mk5_supra_wall`, `f90_m5_wall`, `g80_wall_snakeeye`)
  - spinner: `talon_spinner__black-cf__angle.png`, `talon_spinner__black-cf__front.png`
- **Brand:** logo `theme/assets/logo-metal-1600.webp` (also `logo-flat.svg`, `logo-mark.svg`); display font
  `theme/assets/michroma-latin-400.woff2` (Michroma); owner artwork `brand/concept/hero_halftone_g80.webp`
  (a halftone G80 front, great for an intro or outro).
- **Style reference:** the still ads in `ads/out/*.png` and their layout code in `ads/make_ads.py`. Match their look:
  #070708 background, warm overhead spotlight, film grain, Michroma headlines, white CTA button.

## Facts you may use (nothing else; do not invent claims, reviews, stats or shipping promises)
- 34 car-front keychains, 7 body colours (White, Matte Red/Yellow/Gray/Blue/Black, Metallic Silver)
- Custom headlight colour option (+$0.50). Keychains from $6.99. 80.5 mm wide, 3 mm thick.
- Carbon-fibre textured back with GRILLE TALK lettering. Logo-free designs. Printed in high-quality PLA.
- Wall key holders: 4 hooks, from $14.99, every body colour.
- Talon finger spinner: $12.99, printed in highly durable carbon fiber, made for rigidity and built to last;
  6804 bearing, 20 mm finger hole, topology-optimised lattice frame.
- Site: grilletalk.shop. Prices come from `site/catalog/launch.json`, so read them from there, don't hardcode.

## Legal (must follow)
- Never show any car manufacturer logo, badge or emblem (the models are already logo-free; don't add any).
- Car names only identify which car a design is based on ("Inspired by the BMW M3 (G80)" style).
- End card carries, in small text: "Grille Talk is an independent maker, not affiliated with or endorsed by any
  vehicle manufacturer."
- No copyrighted music. Build sound design from synthesised whooshes and clicks (generate them, e.g. with
  WebAudio offline or ffmpeg), or leave a clean audio track with a `MUSIC_HERE` note for me.

## The video
Three compositions, same story, rendered to `video/out/`:
1. `grilletalk_9x16.mp4`: 1080x1920, 30 fps, ~25 s (TikTok, Reels, Stories). The main one.
2. `grilletalk_1x1.mp4`: 1080x1080, ~15 s cut-down (feed).
3. `grilletalk_16x9.mp4`: 1920x1080, ~25 s (YouTube, website).

Story beats (adapt timings per format, and make the first 2 seconds a hook that works with the sound off):
1. **Hook (0-2 s):** darkness, a spotlight snaps on, the gray snake-eye G80 keychain swings into frame on its chain in
   real 3D. On-screen: "Your keys should match your car."
2. **Detail (2-7 s):** slow 3D orbit and push-in on the light signature and grille; the headlights cycle through
   colours (White > Yellow > Red > Blue) by changing the `lights` material. Text: "Pick the body. Pick the lights."
3. **Flip (7-10 s):** the keychain rotates 180 degrees to show the carbon-fibre back and GRILLE TALK lettering. Text: "Flip it."
4. **Colours (10-14 s):** the same front cycles through all 7 body colours with a match-cut on each beat, or fans out.
   Text: "7 colours."
5. **The garage (14-19 s):** a fast, rhythmic montage or a 3D carousel of different cars (M5, Supra, C8, GT-R,
   Aventador, TRX, Escalade, Model S...). Text: "34 cars and counting."
6. **Wall holder + spinner (19-22 s):** a wall key holder on a lit wall, then the Talon spinner spinning on its bearing.
   Text: "Wall key holders. The Talon spinner."
7. **End card (22-25 s):** logo reveal (use the halftone artwork as a backdrop), "Find your car", "From $6.99",
   grilletalk.shop, legal line.

Motion quality bar:
- Real 3D where it matters (`@remotion/three` with the GLBs, studio lighting, soft shadows, slight depth of field).
  Elsewhere, 2.5D parallax with the Blender PNGs is fine.
- Physically believable motion: springs and eased curves (Remotion `spring`, `interpolate` with easing); the chain
  sways with inertia when the keychain moves.
- Restraint: consistent easing language, no cheap transitions (no star wipes or spins for their own sake),
  typography that animates in with intent (mask reveals, letter-spacing settles).
- Keep text inside platform safe zones: for 9:16, nothing important in the top 220 px or bottom 380 px.

## Process
1. Read the skills, then `ads/make_ads.py` and `theme/assets/keychain3d.js`, before writing code.
2. Scaffold `video/`, get one scene rendering, then build the rest.
3. Check your work: render still frames at each beat (`npx remotion still`), look at them, and fix framing, legibility,
   clipping and overlaps before the full render. Watch for dark-on-dark products, so add rim light.
4. Render all three MP4s (H.264, high quality) and a poster PNG for each.
5. Tell me what you made, where the files are, what assumptions you made, and anything I should change before posting.
   Do not upload or post anything anywhere.
