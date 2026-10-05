"""Shopify product import CSV for the launch catalog: one product per car, one variant per body colour.

out: site/build/shopify_products.csv
Variants: Body color (6) x Headlight color (6). Price = body tier price, plus the headlight surcharge for any
headlight color other than the base (White). Prices come from site/catalog/launch.json, never from theme code.
Inventory is not tracked (made to order).
Images and 3D models are attached afterwards by upload_media.py, because a CSV can only reference public URLs.
Products import as draft so nothing goes live until the owner publishes them.
usage: python site/tools/make_csv.py
"""
import csv, json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'site', 'build', 'shopify_products.csv')

FIELDS = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tags', 'Published',
          'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker',
          'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price',
          'Variant Requires Shipping', 'Variant Taxable', 'Image Src', 'Image Position', 'Image Alt Text',
          'Gift Card', 'SEO Title', 'SEO Description', 'Variant Weight Unit',
          'Make (product.metafields.custom.make)', 'Model (product.metafields.custom.model)',
          'Generation (product.metafields.custom.generation)', 'Short model (product.metafields.custom.short_model)',
          'Status']


def handle(c):
    h = f"{c['make']}-{c['model']}-{c['generation']}" + ('-snake-eye' if c.get('variant') else '') + '-keychain'
    return ''.join(ch if ch.isalnum() else '-' for ch in h.lower()).replace('--', '-').strip('-').replace('--', '-')


def title(c):
    t = f"Inspired by the {c['make']} {c['model']} ({c['generation']})"
    return t + (f", {c['variant']}" if c.get('variant') else '')


def body(c):
    lights = 'Snake-eye light bars, ' if c.get('variant') else 'The light signature, '
    return (f"<p>A straight-on keychain of the {c['make']} {c['model']} ({c['generation']}) front. "
            f"{lights}grille texture and intakes are printed in relief, in two colours.</p>"
            "<ul><li>80.5 mm wide, 3 mm thick</li><li>Two-colour 3D print</li>"
            "<li>Carbon-fibre back with GRILLE TALK lettering</li><li>Custom headlight color available</li>"
            "<li>Split ring and short chain included</li><li>Logo-free design</li></ul>"
            "<p>Grille Talk is an independent maker. Not affiliated with, endorsed by or sponsored by any vehicle "
            "manufacturer. Make and model names identify the car the design is based on.</p>")


def main():
    L = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json')))
    rows = []
    for c in L['cars']:
        h_ = handle(c)
        tags = [f"make:{c['make']}", f"model:{c['model']}", f"generation:{c['generation']}"]
        tags += [f'alias:{a}' for a in c.get('aliases', [])]
        if c.get('variant'):
            tags.append('variant:snake-eye')
        seo_t = f"{title(c)} | Car front keychain | Grille Talk"
        seo_d = (f"3D-printed keychain of the {c['make']} {c['model']} ({c['generation']}) front. "
                 "80.5 mm, two colours, split ring and chain included. Pick your body color.")[:320]
        hl = L['headlights']
        combos = [(col, h) for col in L['colors'] for h in hl['values']]
        for i, (col, h) in enumerate(combos):
            r = dict.fromkeys(FIELDS, '')
            price = float(L['prices'][col['tier']]) + (0 if h.get('base') else float(hl['surcharge']))
            r.update({'Handle': h_, 'Option1 Value': col['name'], 'Option2 Value': h['name'],
                      'Variant SKU': f"GT-{c['id']}-{col['name'].lower().replace(' ', '-')}-hl-{h['name'].lower()}",
                      'Variant Grams': '10', 'Variant Weight Unit': 'g', 'Variant Inventory Tracker': '',
                      'Variant Inventory Policy': 'continue', 'Variant Fulfillment Service': 'manual',
                      'Variant Price': f'{price:.2f}', 'Variant Requires Shipping': 'TRUE',
                      'Variant Taxable': 'TRUE'})
            if i == 0:
                r.update({'Title': title(c), 'Body (HTML)': body(c), 'Vendor': 'Grille Talk',
                          'Product Category': 'Apparel & Accessories > Clothing Accessories > Keychains',
                          'Type': 'Keychain', 'Tags': ', '.join(tags), 'Published': 'FALSE',
                          'Option1 Name': 'Body color', 'Option2 Name': L['headlights']['option'], 'Gift Card': 'FALSE', 'SEO Title': seo_t[:70],
                          'SEO Description': seo_d, 'Make (product.metafields.custom.make)': c['make'],
                          'Model (product.metafields.custom.model)': c['model'],
                          'Generation (product.metafields.custom.generation)': c['generation'],
                          'Short model (product.metafields.custom.short_model)': c['short_model'],
                          'Status': 'draft'})
            rows.append(r)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(OUT, len(rows), 'rows')
    for c in L['cars']:
        print(f"{handle(c):55s} {title(c)}")


if __name__ == '__main__':
    main()
