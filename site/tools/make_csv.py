"""Shopify product import CSV for the launch catalog: one product per car, one variant per body colour.

out: site/build/shopify_products.csv
Variants: Body color (6) x Headlight color (6); two-part wall key holders have Body color only. Price = body tier price, plus the headlight surcharge for any
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
    h = f"{c['make']}-{c['model']}-{c['generation']}" + ('-snake-eye' if c.get('variant') else '') + ('-wall-key-holder' if c.get('wall') else '-keychain')
    return ''.join(ch if ch.isalnum() else '-' for ch in h.lower()).replace('--', '-').strip('-').replace('--', '-')


def title(c):
    t = ("Wall key holder inspired by the " if c.get('wall') else "Inspired by the ") + f"{c['make']} {c['model']} ({c['generation']})"
    return t + (f", {c['variant']}" if c.get('variant') else '')


CARE = ("<p><strong>Care:</strong> we recommend not leaving it in direct sunlight or anywhere around 130&nbsp;&deg;F "
        "(about 55&nbsp;&deg;C), such as a dashboard in summer, for extended periods: the print can soften and warp.</p>")


def wall_body(c):
    w, h, d = c.get('size_mm', ['', '', ''])
    return (f"<p>The {c['make']} {c['model']} ({c['generation']}) front, {'with snake-eye light bars, ' if c.get('variant') else ''}"
            "as a wall key holder: hang your keys on the front of your car by the door.</p>"
            f"<ul><li>About {w} x {h} mm, {d} mm deep at the hooks</li><li>Four key hooks</li>"
            + ("<li>Printed in your body color, with black details and white lights (or a custom headlight color)</li>"
               if c.get('headlights', True) else "<li>Printed in your body color (face, lights and hooks), with black details</li>") +
            "<li>Printed in high-quality PLA filament</li><li>Logo-free design</li></ul>"
            "<p><strong>Mounting:</strong> we recommend strong double-sided mounting tape on the back. It sits flat, "
            "looks cleanest and leaves no screws on show. If you would rather screw or nail it up, there is a countersunk "
            "hole on each side.</p>"
            "<p><strong>Keys only:</strong> the hooks are made for keys and light keyrings. We don't recommend hanging "
            "coats, bags or anything of the sort on them.</p>"
            + CARE +
            "<p>Grille Talk is an independent maker. Not affiliated with, endorsed by or sponsored by any vehicle "
            "manufacturer. Make and model names identify the car the design is based on.</p>")


def body(c):
    lights = 'Snake-eye light bars, ' if c.get('variant') else 'The light signature, '
    return (f"<p>A straight-on keychain of the {c['make']} {c['model']} ({c['generation']}) front. "
            f"{lights}grille texture and intakes are printed in relief, in two colours.</p>"
            "<ul><li>80.5 mm wide, 3 mm thick</li><li>Two-colour 3D print</li>"
            "<li>Carbon-fibre back with GRILLE TALK lettering</li><li>Custom headlight color available</li>"
            "<li>Printed in high-quality PLA filament</li>"
            "<li>Split ring and short chain included</li><li>Logo-free design</li></ul>"
            + CARE +
            "<p>Grille Talk is an independent maker. Not affiliated with, endorsed by or sponsored by any vehicle "
            "manufacturer. Make and model names identify the car the design is based on.</p>")


def main():
    L = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json')))
    rows = []
    walls = [dict(w, wall=True) for w in L.get('wall', {}).get('items', [])]
    for c in L['cars'] + walls:
        prices = L['wall']['prices'] if c.get('wall') else L['prices']
        ptype = L['wall']['type'] if c.get('wall') else 'Keychain'
        h_ = handle(c)
        tags = [f"make:{c['make']}", f"model:{c['model']}", f"generation:{c['generation']}"]
        tags += [f'alias:{a}' for a in c.get('aliases', [])]
        if c.get('variant'):
            tags.append('variant:snake-eye')
        seo_t = f"{title(c)} | Grille Talk" if c.get('wall') else f"{title(c)} | Car front keychain | Grille Talk"
        seo_d = (f"3D-printed wall key holder of the {c['make']} {c['model']} ({c['generation']}) front, four key hooks. "
                 + ("Pick your body color and headlight color." if c.get('headlights', True) else "Pick your body color.") if c.get('wall') else
                 f"3D-printed keychain of the {c['make']} {c['model']} ({c['generation']}) front. "
                 "80.5 mm, two colours, split ring and chain included. Pick your body color.")[:320]
        hl = L['headlights']
        has_hl = c.get('headlights', True)
        combos = [(col, h) for col in L['colors'] for h in (hl['values'] if has_hl else [None])]
        for i, (col, h) in enumerate(combos):
            r = dict.fromkeys(FIELDS, '')
            price = float(prices[col['tier']]) + (0 if (h is None or h.get('base')) else float(hl['surcharge']))
            r.update({'Handle': h_, 'Option1 Value': col['name'], 'Option2 Value': h['name'] if h else '',
                      'Variant SKU': f"GT-{c['id']}-{col['name'].lower().replace(' ', '-')}" + (f"-hl-{h['name'].lower()}" if h else ''),
                      'Variant Grams': str(c.get('grams', 150)) if c.get('wall') else '10',   # wall: estimate, owner to weigh 'Variant Weight Unit': 'g', 'Variant Inventory Tracker': '',
                      'Variant Inventory Policy': 'continue', 'Variant Fulfillment Service': 'manual',
                      'Variant Price': f'{price:.2f}', 'Variant Requires Shipping': 'TRUE',
                      'Variant Taxable': 'TRUE'})
            if i == 0:
                r.update({'Title': title(c), 'Body (HTML)': wall_body(c) if c.get('wall') else body(c), 'Vendor': 'Grille Talk',
                          'Product Category': 'Home & Garden > Decor > Key Holders' if c.get('wall') else 'Apparel & Accessories > Clothing Accessories > Keychains',
                          'Type': ptype, 'Tags': ', '.join(tags), 'Published': 'FALSE',
                          'Option1 Name': 'Body color', 'Option2 Name': L['headlights']['option'] if has_hl else '', 'Gift Card': 'FALSE', 'SEO Title': seo_t[:70],
                          'SEO Description': seo_d, 'Make (product.metafields.custom.make)': c['make'],
                          'Model (product.metafields.custom.model)': c['model'],
                          'Generation (product.metafields.custom.generation)': c['generation'],
                          'Short model (product.metafields.custom.short_model)': c['short_model'],
                          'Status': 'draft'})
            rows.append(r)
    for x in L.get('extras', {}).get('items', []):   # non-car products: one default variant
        r = dict.fromkeys(FIELDS, '')
        r.update({'Handle': x['handle'], 'Title': x['title'], 'Body (HTML)': x['description'], 'Vendor': 'Grille Talk',
                  'Type': x['type'], 'Tags': x['type'].lower(), 'Published': 'FALSE', 'Option1 Name': 'Title',
                  'Option1 Value': 'Default Title', 'Variant SKU': f"GT-{x['id']}", 'Variant Grams': str(x['grams']),
                  'Variant Inventory Policy': 'continue', 'Variant Fulfillment Service': 'manual', 'Variant Price': x['price'],
                  'Variant Requires Shipping': 'TRUE', 'Variant Taxable': 'TRUE', 'Gift Card': 'FALSE',
                  'SEO Title': f"{x['title']} | Grille Talk", 'SEO Description': x['seo'], 'Status': 'draft'})
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
