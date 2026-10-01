"""Copy the finished cars into the user's delivery folder with friendly names + a summary table.
usage: python kc/lib/package.py <dest_dir> <cars.json>
cars.json: [{"id":..., "folder": "BMW_M2_G87", "name": "...", "spec": path, "out": out_dir, "ref_url": ..., "ref_license": ...}]
"""
import os, sys, json, shutil, csv
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

STYLE_DIR = {'production': '1-swap_production', 'classic': 'classic_full_inlay'}
STYLE_TAG = {'production': '1swap', 'classic': 'classic'}


def fmt_t(s):
    if s is None:
        return '-'
    h, m = divmod(int(round(s / 60.0)), 60)
    return f'{h}h {m:02d}m' if h else f'{m}m'


def package(dest, cars):
    os.makedirs(dest, exist_ok=True)
    rows = []
    for c in cars:
        cid, out = c['id'], c['out']
        base = os.path.join(dest, c['folder'])
        if os.path.isdir(base):
            shutil.rmtree(base)
        os.makedirs(base)
        br = json.load(open(os.path.join(out, 'build_report.json')))
        vr = json.load(open(os.path.join(out, 'verify_report.json'))) if os.path.exists(os.path.join(out, 'verify_report.json')) else {}
        shutil.copy(os.path.join(out, 'face.png'), os.path.join(base, f"{c['folder']}_face.png"))
        for st in ('production', 'classic'):
            sd = os.path.join(out, st)
            dd = os.path.join(base, STYLE_DIR[st]); os.makedirs(os.path.join(dd, 'STL_parts'))
            tag = f"{c['folder']}_{STYLE_TAG[st]}"
            n = br['styles'][st]['plate']['count']
            shutil.copy(os.path.join(sd, f'{cid}_{st}_single.3mf'), os.path.join(dd, f'{tag}_single.3mf'))
            shutil.copy(os.path.join(sd, f'{cid}_{st}_PLATE_{n}x.3mf'), os.path.join(dd, f'{tag}_PLATE_{n}x.3mf'))
            if os.path.exists(os.path.join(sd, f'{cid}_{st}.step')):
                shutil.copy(os.path.join(sd, f'{cid}_{st}.step'), os.path.join(dd, f'{tag}.step'))
            for col in ('black', 'white'):
                shutil.copy(os.path.join(sd, f'{cid}_{st}_{col}.stl'), os.path.join(dd, 'STL_parts', f'{tag}_{col}.stl'))
            shutil.copy(os.path.join(sd, f'{cid}_{st}_render.png'), os.path.join(base, f"{tag}_render.png"))
            shutil.copy(os.path.join(sd, f'{cid}_{st}_plate_layout.png'), os.path.join(dd, f'{tag}_plate_layout.png'))
        # custom body colour (3 filaments)
        cr_path = os.path.join(out, 'custom_colour_report.json')
        cr = json.load(open(cr_path)) if os.path.exists(cr_path) else None
        if cr:
            cc = os.path.join(base, 'custom_body_colour')
            for st, sub in (('production3', '1-swap_style'), ('classic3', 'classic_style')):
                sd = os.path.join(out, st); dd = os.path.join(cc, sub); os.makedirs(os.path.join(dd, 'STL_parts'))
                tag = f"{c['folder']}_custom_{'1swap' if st == 'production3' else 'classic'}"
                n = cr['plate_count']
                shutil.copy(os.path.join(sd, f'{cid}_{st}_single.3mf'), os.path.join(dd, f'{tag}_single.3mf'))
                shutil.copy(os.path.join(sd, f'{cid}_{st}_PLATE_{n}x.3mf'), os.path.join(dd, f'{tag}_PLATE_{n}x.3mf'))
                if os.path.exists(os.path.join(sd, f'{cid}_{st}.step')):
                    shutil.copy(os.path.join(sd, f'{cid}_{st}.step'), os.path.join(dd, f'{tag}.step'))
                for col in ('black', 'body', 'light'):
                    p = os.path.join(sd, f'{cid}_{st}_{col}.stl')
                    if os.path.exists(p):
                        shutil.copy(p, os.path.join(dd, 'STL_parts', f'{tag}_{col}.stl'))
                shutil.copy(os.path.join(sd, f'{cid}_{st}_render_red.png'), os.path.join(dd, f'{tag}_render_red.png'))
            for nm in ('red', 'blue', 'yellow', 'grey'):
                p = os.path.join(out, f'face_body_{nm}.png')
                if os.path.exists(p):
                    shutil.copy(p, os.path.join(cc, f"{c['folder']}_preview_{nm}.png"))
        row = {'car': c['name'], 'folder': c['folder'], 'size_mm': 'x'.join(f'{v:.1f}' for v in br['size_mm']),
               'per_plate': br['styles']['production']['plate']['count']}
        if vr:
            cl = vr['classic']['plate'].get('two_colour', {}); pr = vr['production']['plate'].get('estimate', {})
            n = vr['plate_count']
            row.update({
                'classic_plate_time': fmt_t(cl.get('time_s')), 'classic_plate_changes': cl.get('filament_changes'),
                'classic_plate_grams': round(sum(cl.get('grams_per_filament') or [0]), 1),
                'swap_plate_time': fmt_t(pr.get('time_s')), 'swap_plate_changes': pr.get('filament_changes'),
                'swap_plate_grams': pr.get('grams_total'),
                'swap_min_per_keychain': round(pr['time_s'] / 60 / n, 1) if pr.get('time_s') else None,
                'swap_g_per_keychain': round(pr['grams_total'] / n, 2) if pr.get('grams_total') else None,
                'classic_min_per_keychain': round(cl['time_s'] / 60 / n, 1) if cl.get('time_s') else None,
                'classic_g_per_keychain': round(sum(cl['grams_per_filament']) / n, 2) if cl.get('grams_per_filament') else None,
            })
        if cr:
            row['custom_1swap_changes'] = cr['production3']['changes_per_plate']
            row['custom_classic_changes'] = cr['classic3']['changes_per_plate']
        rows.append(row)
        with open(os.path.join(base, 'SOURCE.txt'), 'w', encoding='utf-8') as f:
            f.write(f"{c['name']}\nTraced from reference photo: {c.get('ref_url', 'n/a')}\nPhoto licence: {c.get('ref_license', 'n/a')}\n"
                    "(the photo was only used as a tracing reference and is not included)\n")
    with open(os.path.join(dest, 'summary.csv'), 'w', newline='', encoding='utf-8') as f:
        keys = list(rows[0].keys()) if rows else []
        for r in rows:
            for k in r:
                if k not in keys:
                    keys.append(k)
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    json.dump(rows, open(os.path.join(dest, 'summary.json'), 'w'), indent=1)
    return rows


if __name__ == '__main__':
    rows = package(sys.argv[1], json.load(open(sys.argv[2])))
    for r in rows:
        print(r)
