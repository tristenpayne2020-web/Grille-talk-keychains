"""Grille Talk ad creatives: HTML layouts with the real Blender renders, screenshotted at platform sizes.
usage: python ads/make_ads.py      (renders to ads/out/*.png; needs node + playwright from site/)
Every claim is from site/catalog/launch.json or the product pages (34 cars, 7 colours, from $6.99, wall from $14.99).
"""
import json, os, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / 'site/build/ads/src').as_uri()
THEME = (ROOT / 'theme/assets').as_uri()
OUT = ROOT / 'ads/out'
L = json.load(open(ROOT / 'site/catalog/launch.json', encoding='utf-8'))
N_CARS = len(L['cars'])
FROM = '$' + min(L['prices'].values(), key=float)
WALL_FROM = '$' + min(L['wall']['prices'].values(), key=float)

CSS = f"""
@font-face {{ font-family: Michroma; src: url('{THEME}/michroma-latin-400.woff2'); }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: var(--w); height: var(--h); overflow: hidden; background: #070708; color: #f2f1ee;
  font-family: 'Segoe UI', system-ui, sans-serif; position: relative; }}
.d {{ font-family: Michroma, sans-serif; letter-spacing: .01em; line-height: 1.08; }}
.eye {{ font-family: Michroma; font-size: 20px; letter-spacing: .32em; text-transform: uppercase; color: #9b9a97; }}
.logo {{ position: absolute; top: 56px; left: 64px; width: 230px; }}
.cta {{ display: inline-flex; align-items: center; gap: 14px; padding: 22px 38px; background: #f2f1ee; color: #070708;
  font-family: Michroma; font-size: 22px; letter-spacing: .14em; text-transform: uppercase; }}
.legal {{ position: absolute; bottom: 26px; left: 64px; right: 64px; font-size: 13px; color: #5d5c59; letter-spacing: .02em; }}
.grain {{ position: absolute; inset: 0; pointer-events: none; opacity: .5; mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='.35'/%3E%3C/svg%3E"); }}
.spot {{ position: absolute; inset: 0; background: radial-gradient(60% 45% at 50% 40%, rgba(255,250,240,.16), transparent 70%); }}
.chip {{ display: inline-block; padding: 9px 16px; border: 1px solid #3a3a3d; font-size: 17px; color: #c9c8c4; letter-spacing: .04em; }}
img {{ display: block; }}
"""
LEGAL = 'Grille Talk is an independent maker, not affiliated with or endorsed by any vehicle manufacturer.'
LOGO = f'<img class="logo" src="{THEME}/logo-metal-800.webp">'


def page(w, h, body):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>:root{{--w:{w}px;--h:{h}px}}{CSS}</style></head><body>{body}<div class="grain"></div></body></html>'


ADS = {}

# 1 - hero: the snake-eye front in gray with yellow lights
ADS['01_hero_4x5'] = (1080, 1350, f"""
<div class="spot"></div>{LOGO}
<img src="{SRC}/t_g80se_gray-yellow.png" style="position:absolute;left:50%;top:300px;width:900px;transform:translateX(-50%) rotate(-4deg);filter:drop-shadow(0 50px 50px rgba(0,0,0,.7))">
<div style="position:absolute;left:64px;right:64px;bottom:120px">
  <p class="eye">3D-printed car-front keychains</p>
  <h1 class="d" style="font-size:76px;margin:22px 0 26px">Your car.<br>On your keys.</h1>
  <div style="display:flex;justify-content:space-between;align-items:center">
    <span class="cta">Find your car &rarr;</span><span style="font-size:24px;color:#c9c8c4">{N_CARS} cars &middot; from {FROM}</span></div>
</div><p class="legal">{LEGAL}</p>""")

# 2 - headlight colours, story
quad = [('black-red', 'Matte Black', 'Red lights'), ('white-blue', 'White', 'Blue lights'),
        ('red-white', 'Matte Red', 'White lights'), ('silver-yellow', 'Metallic Silver', 'Yellow lights')]
cells = ''.join(f"""<div style="text-align:center"><img src="{SRC}/t_g80se_{k}.png" style="width:440px;margin:0 auto 18px;filter:drop-shadow(0 26px 26px rgba(0,0,0,.65))">
<p style="font-size:22px">{a}</p><p style="font-size:19px;color:#9b9a97">{b}</p></div>""" for k, a, b in quad)
ADS['02_headlights_9x16'] = (1080, 1920, f"""
<div class="spot" style="background:radial-gradient(70% 40% at 50% 45%, rgba(255,250,240,.12), transparent 70%)"></div>{LOGO}
<div style="position:absolute;top:250px;left:64px;right:64px"><p class="eye">Same car. Your spec.</p>
<h1 class="d" style="font-size:80px;margin-top:24px">Pick the body.<br>Pick the lights.</h1></div>
<div style="position:absolute;top:720px;left:40px;right:40px;display:grid;grid-template-columns:1fr 1fr;row-gap:70px">{cells}</div>
<div style="position:absolute;left:64px;right:64px;bottom:150px;display:flex;justify-content:space-between;align-items:center">
<span class="cta">Build yours &rarr;</span><span style="font-size:24px;color:#c9c8c4">Custom headlights +${L['headlights']['surcharge']}</span></div>
<p class="legal">{LEGAL}</p>""")

# 3 - seven colours fanned out
cols = ['white', 'matte-red', 'matte-yellow', 'matte-gray', 'matte-blue', 'matte-black', 'metallic-silver']
fan = ''.join(f"""<img src="{SRC}/t_front_{c}.png" style="position:absolute;width:360px;left:{360 + (i - 3) * 78}px;top:{500 + abs(i - 3) * 22}px;
transform:rotate({(i - 3) * 7}deg);transform-origin:50% 140%;z-index:{10 - abs(i - 3)};filter:drop-shadow(0 22px 24px rgba(0,0,0,.7))">""" for i, c in enumerate(cols))
ADS['03_colors_1x1'] = (1080, 1080, f"""
<div class="spot" style="background:radial-gradient(60% 50% at 50% 60%, rgba(255,250,240,.13), transparent 70%)"></div>{LOGO}
<div style="position:absolute;top:150px;left:64px;right:64px"><h1 class="d" style="font-size:68px">7 colors.<br>1 front.<br>Yours.</h1></div>
{fan}
<div style="position:absolute;left:64px;right:64px;bottom:80px;display:flex;justify-content:space-between;align-items:center">
<span class="cta">Shop colors &rarr;</span><span style="font-size:22px;color:#c9c8c4">From {FROM}</span></div><p class="legal">{LEGAL}</p>""")

# 4 - the garage grid
tiles = ''.join(f"""<div style="background:linear-gradient(180deg,#141416,#0b0b0c);border:1px solid #1f1f22;display:grid;place-items:center;height:178px">
<img src="{SRC}/t_grid_{i}.png" style="max-width:86%;max-height:78%;filter:drop-shadow(0 14px 14px rgba(0,0,0,.6))"></div>""" for i in range(12))
ADS['04_garage_4x5'] = (1080, 1350, f"""{LOGO}
<div style="position:absolute;top:150px;left:64px;right:64px;display:flex;justify-content:space-between;align-items:end">
<h1 class="d" style="font-size:64px">{N_CARS} cars<br>and counting.</h1><p class="eye" style="text-align:right">The Grille Talk<br>garage</p></div>
<div style="position:absolute;top:360px;left:64px;right:64px;display:grid;grid-template-columns:repeat(3,1fr);gap:12px">{tiles}</div>
<div style="position:absolute;left:64px;right:64px;bottom:72px;display:flex;justify-content:space-between;align-items:center">
<span class="cta">Find your car &rarr;</span><span style="font-size:21px;color:#c9c8c4">Not here? Request it.</span></div>""")

# 5 - flip it: front and carbon back
ADS['05_flip_1x1'] = (1080, 1080, f"""
<div style="position:absolute;inset:0 50% 0 0;background:#0b0b0c"></div><div style="position:absolute;inset:0 0 0 50%;background:#121214"></div>
{LOGO}
<img src="{SRC}/t_front_matte-blue.png" style="position:absolute;left:30px;top:340px;width:500px;transform:rotate(-8deg);filter:drop-shadow(0 30px 30px rgba(0,0,0,.7))">
<img src="{SRC}/t_back.png" style="position:absolute;right:20px;top:320px;width:520px;transform:rotate(7deg);filter:drop-shadow(0 30px 30px rgba(0,0,0,.7))">
<div style="position:absolute;top:170px;left:64px;right:64px;display:flex;justify-content:space-between"><h1 class="d" style="font-size:72px">Flip it.</h1>
<p style="font-size:22px;color:#c9c8c4;max-width:430px;text-align:right;line-height:1.45">Every keychain has a carbon-fibre textured back, signed GRILLE TALK.</p></div>
<div style="position:absolute;left:64px;right:64px;bottom:90px;display:flex;justify-content:space-between;align-items:center">
<span class="chip">Front</span><span class="cta">Shop now &rarr;</span><span class="chip">Back</span></div><p class="legal">{LEGAL}</p>""")

# 6 - wall key holders
ADS['06_wall_4x5'] = (1080, 1350, f"""
<div style="position:absolute;inset:0;background:radial-gradient(55% 45% at 50% 30%, #3a3936 0%, #1b1a18 55%, #0b0b0a 100%)"></div>
<div style="position:absolute;top:0;left:50%;width:360px;height:26px;transform:translateX(-50%);border-radius:0 0 50% 50%;background:#111;box-shadow:0 10px 60px rgba(255,248,230,.5)"></div>
{LOGO}
<img src="{SRC}/t_wall.png" style="position:absolute;left:50%;top:330px;width:880px;transform:translateX(-50%);filter:drop-shadow(0 40px 34px rgba(0,0,0,.6))">
<div style="position:absolute;left:64px;right:64px;bottom:120px"><p class="eye" style="color:#b9b5ad">Wall key holders</p>
<h1 class="d" style="font-size:70px;margin:22px 0 28px">Your car,<br>by the front door.</h1>
<div style="display:flex;justify-content:space-between;align-items:center"><span class="cta">Shop holders &rarr;</span>
<span style="font-size:23px;color:#d9d5cc">4 hooks &middot; from {WALL_FROM}</span></div></div><p class="legal">{LEGAL}</p>""")

# 7 - TikTok / Reels hook
ADS['07_pov_9x16'] = (1080, 1920, f"""
<div class="spot" style="background:radial-gradient(60% 35% at 50% 52%, rgba(255,60,40,.20), transparent 70%)"></div>{LOGO}
<h1 class="d" style="position:absolute;top:260px;left:64px;right:64px;font-size:88px">POV:<br>your keys<br>match your car.</h1>
<img src="{SRC}/t_g80se_black-red_angle.png" style="position:absolute;left:50%;top:860px;width:1000px;transform:translateX(-50%) rotate(-6deg);filter:drop-shadow(0 60px 50px rgba(0,0,0,.8))">
<div style="position:absolute;left:64px;right:64px;bottom:170px"><p style="font-size:30px;margin-bottom:28px">Matte Black &middot; red headlights &middot; snake-eye</p>
<span class="cta">Build yours &rarr;</span></div><p class="legal">{LEGAL}</p>""")

# 8 - the owner's halftone artwork, poster style
ADS['08_poster_4x5'] = (1080, 1350, f"""
<img src="{(ROOT / 'brand/concept/hero_halftone_g80.webp').as_uri()}" style="position:absolute;left:0;right:0;top:0;height:560px;width:100%;object-fit:cover;object-position:50% 70%;opacity:.6">
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,7,8,.7),rgba(7,7,8,0) 22%,rgba(7,7,8,.4) 32%,#070708 42%)"></div>
<div class="spot" style="background:radial-gradient(50% 30% at 50% 55%, rgba(255,250,240,.14), transparent 70%)"></div>
{LOGO}
<img src="{SRC}/t_g80se_silver-yellow.png" style="position:absolute;left:50%;top:600px;width:640px;transform:translateX(-50%);filter:drop-shadow(0 40px 40px rgba(0,0,0,.8))">
<div style="position:absolute;left:64px;right:64px;bottom:110px;text-align:center"><h1 class="d" style="font-size:62px;margin-bottom:26px">Built from the real car.</h1>
<p style="font-size:24px;color:#c9c8c4;margin-bottom:34px">Every light, every intake. Logo-free. Printed in PLA.</p><span class="cta">Shop the range &rarr;</span></div>
<p class="legal">{LEGAL}</p>""")


# 9 - Talon spinner, feed: a cold, technical look (owner's carbon-fibre line)
SP = next(x for x in L.get('extras', {}).get('items', []) if x['id'] == 'talon_spinner')
ADS['09_spinner_4x5'] = (1080, 1350, f"""
<div class="spot" style="background:radial-gradient(55% 40% at 50% 46%, rgba(180,200,230,.16), transparent 70%)"></div>
<div style="position:absolute;inset:0;opacity:.07;background-image:linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px);background-size:54px 54px"></div>
{LOGO}
<div style="position:absolute;top:150px;left:64px;right:64px"><p class="eye">New &middot; Talon finger spinner</p>
<h1 class="d" style="font-size:78px;margin-top:22px">Spin it.<br>Clip it.<br>Keep it.</h1></div>
<img src="{SRC}/t_spinner_angle.png" style="position:absolute;left:50%;top:470px;width:740px;transform:translateX(-44%) rotate(-6deg);filter:drop-shadow(0 50px 40px rgba(0,0,0,.75))">
<div style="position:absolute;left:64px;right:64px;bottom:120px">
<p style="font-size:24px;color:#c9c8c4;margin-bottom:30px;max-width:780px;line-height:1.45">Printed in highly durable carbon fiber, made for rigidity and built to last. 6804 bearing, 20 mm finger hole.</p>
<div style="display:flex;justify-content:space-between;align-items:center"><span class="cta">Get the Talon &rarr;</span><span style="font-size:30px">${SP['price']}</span></div></div>""")

# 10 - Talon spinner, story: top view with callouts
ADS['10_spinner_9x16'] = (1080, 1920, f"""
<div class="spot" style="background:radial-gradient(70% 35% at 50% 50%, rgba(180,200,230,.14), transparent 70%)"></div>{LOGO}
<h1 class="d" style="position:absolute;top:240px;left:64px;right:64px;font-size:86px">Topology<br>optimised.</h1>
<p style="position:absolute;top:500px;left:64px;font-size:28px;color:#c9c8c4">Solid where it works. Light everywhere else.</p>
<img src="{SRC}/t_spinner_front.png" style="position:absolute;left:50%;top:640px;width:900px;transform:translateX(-50%) rotate(-90deg)">
<div style="position:absolute;left:64px;right:64px;top:1470px;display:flex;gap:14px;flex-wrap:wrap">
<span class="chip">Carbon fiber PETG</span><span class="chip">6804 bearing</span><span class="chip">20 mm finger hole</span><span class="chip">74 x 42 mm</span></div>
<div style="position:absolute;left:64px;right:64px;bottom:170px;display:flex;justify-content:space-between;align-items:center">
<span class="cta">Spin yours &rarr;</span><span style="font-size:34px">${SP['price']}</span></div>""")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for name, (w, h, body) in ADS.items():
        p = OUT / f'{name}.html'
        p.write_text(page(w, h, body), encoding='utf-8')
        jobs.append(dict(html=p.as_uri(), png=str(OUT / f'{name}.png'), w=w, h=h))
    js = ROOT / 'ads/shoot_ads.mjs'
    subprocess.run(['node', str(js), json.dumps(jobs)], cwd=ROOT / 'site', check=True)


if __name__ == '__main__':
    main()
