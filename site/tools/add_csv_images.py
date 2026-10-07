"""Add image columns to the product CSV, pointing at renders already uploaded to Shopify Files (no API token needed).

Shopify downloads each Image Src during the import. Images keep the manifest order and alt text (the theme matches
colour images by alt text); every variant gets the front render of its body colour as its Variant Image.
usage: python site/tools/add_csv_images.py <files base URL>
  e.g. https://cdn.shopify.com/s/files/1/0773/0593/8076/files
in : site/build/shopify_products.csv, site/build/media/manifest.json
out: site/build/shopify_products_with_images.csv
"""
import csv, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BUILD = os.path.join(ROOT, 'site', 'build')
sys.path.insert(0, os.path.dirname(__file__))
from make_csv import handle  # noqa: E402


def main():
    base = sys.argv[1].rstrip('/')
    L = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json'), encoding='utf-8'))
    manifest = json.load(open(os.path.join(BUILD, 'media', 'manifest.json')))
    ids = {handle(c): c['id'] for c in L['cars']}
    ids |= {handle(dict(w, wall=True)): w['id'] for w in L['wall']['items']}
    ids |= {x['handle']: x['id'] for x in L.get('extras', {}).get('items', [])}

    rows = list(csv.DictReader(open(os.path.join(BUILD, 'shopify_products.csv'), encoding='utf-8')))
    fields = list(rows[0].keys())
    if 'Variant Image' not in fields:
        fields.insert(fields.index('Image Alt Text') + 1, 'Variant Image')
    out, by_handle = [], {}
    for r in rows:
        by_handle.setdefault(r['Handle'], []).append(r)
    for h, prows in by_handle.items():
        cid = ids[h]
        imgs, front = [], {}
        for it in manifest[cid]['media']:
            if it['kind'] not in ('variant', 'angle', 'back'):
                continue
            url = f"{base}/{[f for f in it['files'] if f.endswith('-2000.webp')][0]}"
            imgs.append((url, it['alt']))
            if it['kind'] == 'variant':
                front[it['color']] = url
        for r in prows:
            r['Product Category'] = ''           # Shopify rejects our free-text categories; set later in admin
            r['Variant Image'] = front.get(r['Option1 Value'], '') if r.get('Variant SKU') else ''
        for i, (url, alt) in enumerate(imgs):
            if i < len(prows):
                r = prows[i]
            else:
                r = dict.fromkeys(fields, '')
                r['Handle'] = h
                prows.append(r)
            r.update({'Image Src': url, 'Image Position': str(i + 1), 'Image Alt Text': alt})
        out += prows
    path = os.path.join(BUILD, 'shopify_products_with_images.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(out)
    print(path, len(out), 'rows,', sum(1 for r in out if r['Image Src']), 'images')


if __name__ == '__main__':
    main()
