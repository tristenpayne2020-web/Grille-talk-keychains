"""Local gallery page (open index.html in any browser) for the delivery folder."""
import json, os, sys, html
dest = sys.argv[1]
rows = json.load(open(os.path.join(dest, 'summary.json')))
cards = []
for r in rows:
    f = r['folder']
    img = lambda p: f'{f}/{p}'
    stats = ''
    if r.get('swap_plate_time'):
        stats = (f"<table><tr><th></th><th>1-swap plate</th><th>classic plate</th></tr>"
                 f"<tr><td>keychains</td><td>{r['per_plate']}</td><td>{r['per_plate']}</td></tr>"
                 f"<tr><td>time</td><td>{r['swap_plate_time']}</td><td>{r['classic_plate_time']}</td></tr>"
                 f"<tr><td>colour changes</td><td>{r['swap_plate_changes']}</td><td>{r['classic_plate_changes']}</td></tr>"
                 f"<tr><td>filament</td><td>{r['swap_plate_grams']} g</td><td>{r['classic_plate_grams']} g</td></tr>"
                 f"<tr><td>per keychain</td><td>{r['swap_min_per_keychain']} min, {r['swap_g_per_keychain']} g</td>"
                 f"<td>{r['classic_min_per_keychain']} min, {r['classic_g_per_keychain']} g</td></tr></table>")
    cards.append(f"""<section><h2>{html.escape(r['car'])}</h2><p class=sub>{r['size_mm']} mm &middot; folder <code>{f}</code></p>
<div class=imgs><img src="{img(f + '_face.png')}" alt="face"><img src="{img(f + '_1swap_render.png')}" alt="1-swap render"><img src="{img(f + '_classic_render.png')}" alt="classic render"></div>
{stats}</section>""")
page = f"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Car Front Keychains</title><style>
:root{{--bg:#f4f4f2;--fg:#1d1d1f;--card:#fff;--mut:#666;--line:#ddd}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16181d;--fg:#eee;--card:#20232a;--mut:#aaa;--line:#333}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,Segoe UI,sans-serif;margin:0;padding:16px;max-width:1200px;margin:auto}}
section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin:14px 0}}
h1{{font-size:22px}} h2{{margin:0;font-size:18px}} .sub{{color:var(--mut);margin:2px 0 10px}}
.imgs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:8px}} .imgs img{{width:100%;border-radius:6px}}
table{{border-collapse:collapse;margin-top:10px;font-size:14px}} td,th{{border:1px solid var(--line);padding:4px 10px;text-align:left}}
code{{font-size:13px}}</style></head><body>
<h1>Car front keychains &mdash; Creality K2, 0.4 mm nozzle, black + white</h1>
<p>Each car: flat face design, the 1-swap production build (recommended for bulk) and the classic full-inlay build (same construction as your G80). Numbers are for a full plate, sliced with Creality Print's engine. See README.txt.</p>
{''.join(cards)}
</body></html>"""
open(os.path.join(dest, 'index.html'), 'w', encoding='utf-8').write(page)
print('wrote', os.path.join(dest, 'index.html'))
