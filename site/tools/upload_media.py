"""Attach renders and 3D models to the imported products through the Shopify Admin GraphQL API.

Run after importing site/build/shopify_products.csv. Matches products by handle (same rule as make_csv.py).
Per product it uploads: the front render in every body colour (each linked to its variant), the angled render with
chain, and the GLB as a 3D model. Media already present with the same alt text is skipped,
so the script can be re-run safely.

Credentials come from the environment only, never from files in the repo:
  SHOPIFY_STORE         e.g. grille-talk.myshopify.com
  SHOPIFY_ADMIN_TOKEN   Admin API access token of a custom app with write_products and write_files
A local .env file is read if present (it is gitignored).

usage: python site/tools/upload_media.py [--dry-run] [--only=handle,handle]
"""
import json, mimetypes, os, sys, time
import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BUILD = os.path.join(ROOT, 'site', 'build')
API_VERSION = '2025-01'
sys.path.insert(0, os.path.dirname(__file__))
from make_csv import handle  # noqa: E402


def load_env():
    p = os.path.join(ROOT, '.env')
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class Admin:
    def __init__(self, store, token):
        self.url = f'https://{store}/admin/api/{API_VERSION}/graphql.json'
        self.h = {'X-Shopify-Access-Token': token, 'Content-Type': 'application/json'}

    def q(self, query, **variables):
        for attempt in range(5):
            r = requests.post(self.url, headers=self.h, json={'query': query, 'variables': variables}, timeout=60)
            if r.status_code == 429:
                time.sleep(2 + attempt * 2); continue
            r.raise_for_status()
            data = r.json()
            if data.get('errors'):
                if any(e.get('extensions', {}).get('code') == 'THROTTLED' for e in data['errors']):
                    time.sleep(2 + attempt * 2); continue
                raise RuntimeError(json.dumps(data['errors']))
            return data['data']
        raise RuntimeError('throttled too often')


PRODUCT_Q = '''query($h: String!) { productByHandle(handle: $h) { id title
  variants(first: 50) { nodes { id selectedOptions { name value } } }
  media(first: 50) { nodes { id alt mediaContentType status } } } }'''
STAGE_M = '''mutation($input: [StagedUploadInput!]!) { stagedUploadsCreate(input: $input) {
  stagedTargets { url resourceUrl parameters { name value } } userErrors { field message } } }'''
CREATE_M = '''mutation($pid: ID!, $media: [CreateMediaInput!]!) { productCreateMedia(productId: $pid, media: $media) {
  media { id alt status } mediaUserErrors { field message } } }'''
STATUS_Q = '''query($ids: [ID!]!) { nodes(ids: $ids) { ... on Media { id status } } }'''
APPEND_M = '''mutation($pid: ID!, $vm: [ProductVariantAppendMediaInput!]!) { productVariantAppendMedia(productId: $pid, variantMedia: $vm) {
  userErrors { field message } } }'''


def stage_and_upload(api, path, resource):
    size = os.path.getsize(path)
    mime = 'model/gltf-binary' if path.endswith('.glb') else (mimetypes.guess_type(path)[0] or 'image/webp')
    d = api.q(STAGE_M, input=[{'filename': os.path.basename(path), 'mimeType': mime, 'resource': resource,
                                'fileSize': str(size), 'httpMethod': 'POST'}])['stagedUploadsCreate']
    if d['userErrors']:
        raise RuntimeError(d['userErrors'])
    t = d['stagedTargets'][0]
    form = {p['name']: p['value'] for p in t['parameters']}
    with open(path, 'rb') as f:
        r = requests.post(t['url'], data=form, files={'file': (os.path.basename(path), f, mime)}, timeout=300)
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f'upload failed {r.status_code}: {r.text[:300]}')
    return t['resourceUrl']


def wait_ready(api, ids, timeout=180):
    t0 = time.time()
    while time.time() - t0 < timeout:
        nodes = api.q(STATUS_Q, ids=ids)['nodes']
        if all(n and n['status'] == 'READY' for n in nodes):
            return True
        if any(n and n['status'] == 'FAILED' for n in nodes):
            raise RuntimeError('media processing failed: ' + json.dumps(nodes))
        time.sleep(3)
    return False


def main():
    load_env()
    dry = '--dry-run' in sys.argv
    only = next((a.split('=', 1)[1].split(',') for a in sys.argv if a.startswith('--only=')), None)
    launch = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json')))
    manifest = json.load(open(os.path.join(BUILD, 'media', 'manifest.json')))
    store, token = os.environ.get('SHOPIFY_STORE'), os.environ.get('SHOPIFY_ADMIN_TOKEN')
    if not dry and not (store and token):
        sys.exit('Set SHOPIFY_STORE and SHOPIFY_ADMIN_TOKEN (environment or .env), or use --dry-run.')
    api = None if dry else Admin(store, token)

    for car in launch['cars']:
        h = handle(car)
        if only and h not in only:
            continue
        m = manifest[car['id']]
        plan = []   # (path, resource, alt, colour or None)
        for item in m['media']:
            if item['kind'] in ('variant', 'angle'):   # the flat design drawing (face) has a label and grey ground: not for the store
                f = next(x for x in item['files'] if x.endswith('-2000.webp'))
                plan.append((os.path.join(BUILD, 'media', car['id'], f), 'IMAGE', item['alt'],
                             item['color'] if item['kind'] == 'variant' else None))
        plan.append((os.path.join(BUILD, m['glb']), 'MODEL_3D', f"3D model of the Grille Talk keychain inspired by the {m['name']}", None))
        if dry:
            print(f'[dry-run] {h}: {len(plan)} media')
            for p, res, alt, col in plan:
                print(f'   {res:8s} {os.path.basename(p):48s} {os.path.getsize(p) // 1024:5d} KB  variant={col or "-"}')
            continue

        prod = api.q(PRODUCT_Q, h=h)['productByHandle']
        if not prod:
            print(f'skip {h}: product not found (import the CSV first)'); continue
        have = {n['alt'] for n in prod['media']['nodes']}
        variant_of = {next(o['value'] for o in v['selectedOptions'] if o['name'] == 'Body color'): v['id']
                      for v in prod['variants']['nodes']}
        created = []
        for p, res, alt, col in plan:
            if alt in have:
                continue
            src = stage_and_upload(api, p, res)
            d = api.q(CREATE_M, pid=prod['id'], media=[{'originalSource': src, 'mediaContentType': res, 'alt': alt}])['productCreateMedia']
            if d['mediaUserErrors']:
                raise RuntimeError(d['mediaUserErrors'])
            created.append((d['media'][0]['id'], col))
            print(f'  + {os.path.basename(p)}')
        # link each colour's render to its variant once processing is done
        links = [(mid, variant_of[col]) for mid, col in created if col and col in variant_of]
        if links and wait_ready(api, [mid for mid, _ in links]):
            d = api.q(APPEND_M, pid=prod['id'], vm=[{'variantId': vid, 'mediaIds': [mid]} for mid, vid in links])
            errs = d['productVariantAppendMedia']['userErrors']
            if errs:
                print('  variant media errors:', errs)
        print(f'{h}: {len(created)} new media')


if __name__ == '__main__':
    main()
