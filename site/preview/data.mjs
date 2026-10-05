// Mock Shopify objects for the local preview, built from site/catalog/launch.json, the local renders and GLBs, and the
// prices in launch.json (the same source as the import CSV). Shapes follow the Liquid objects the theme uses.
import fs from 'node:fs';
import path from 'node:path';

const SITE = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/, '$1')), '..');
const launch = JSON.parse(fs.readFileSync(path.join(SITE, 'catalog', 'launch.json'), 'utf8'));
const manifest = JSON.parse(fs.readFileSync(path.join(SITE, 'build', 'media', 'manifest.json'), 'utf8'));

export const cents = (s) => Math.round(parseFloat(s) * 100);
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

export function handleFor(c) {
  return slug(`${c.make}-${c.model}-${c.generation}${c.variant ? '-snake-eye' : ''}${c.wall ? '-wall-key-holder' : '-keychain'}`);
}
export function titleFor(c) {
  return `${c.wall ? 'Wall key holder inspired by the' : 'Inspired by the'} ${c.make} ${c.model} (${c.generation})${c.variant ? `, ${c.variant}` : ''}`;
}

// Image object: prints as its URL, image_url picks the nearest built width.
export class Img {
  constructor(base, alt, w = 2000, h = 2000) { this.base = base; this.alt = alt; this.width = w; this.height = h; this.src = this.url(1200); this.aspect_ratio = w / h; }
  url(width) {
    if (!this.base.includes('{w}')) return this.base;
    const sizes = [600, 1200, 2000];
    const w = sizes.find((s) => s >= (width || 2000)) || 2000;
    return this.base.replace('{w}', w);
  }
  toString() { return this.url(1200); }
}

let nextId = 1000;
const walls = ((launch.wall && launch.wall.items) || []).map((w) => ({ ...w, wall: true }));
export const products = [...launch.cars, ...walls].map((c, idx) => {
  const m = manifest[c.id];
  const handle = handleFor(c);
  const title = titleFor(c);
  const imgs = [];
  const variantImg = {};
  for (const it of m.media) {
    if (!['variant', 'angle', 'back'].includes(it.kind)) continue;   // the flat design drawing stays out of the storefront
    const f = it.files.find((x) => x.endsWith('-2000.webp')).replace('-2000.webp', '-{w}.webp');
    const img = new Img(`/media/${c.id}/${f}`, it.alt);
    img.id = nextId++;
    imgs.push(img);
    if (it.kind === 'variant') variantImg[it.color] = img;
  }
  const media = imgs.map((img) => ({ id: img.id, media_type: 'image', alt: img.alt, preview_image: img, position: 0 }));
  media.push({
    id: nextId++, media_type: 'model', alt: `3D model of the Grille Talk keychain inspired by the ${m.name}`,
    preview_image: imgs[0], sources: [{ format: 'glb', mime_type: 'model/gltf-binary', url: `/glb/${c.id}.glb` }],
  });
  media.forEach((x, i) => { x.position = i + 1; });
  const hl = launch.headlights;
  const hasHl = c.headlights !== false;   // two-part wall key holders: one colour for face and lights
  const variants = launch.colors.flatMap((col) => (hasHl ? hl.values : [null]).map((h) => {
    const id = nextId++;
    const img = variantImg[col.name];
    const price = cents((c.wall ? launch.wall.prices : launch.prices)[col.tier]) + (!h || h.base ? 0 : cents(hl.surcharge));
    return {
      id, title: h ? `${col.name} / ${h.name}` : col.name, option1: col.name, option2: h ? h.name : null, options: h ? [col.name, h.name] : [col.name], price,
      available: true, sku: `GT-${c.id}-${slug(col.name)}${h ? `-hl-${slug(h.name)}` : ''}`, url: `/products/${handle}?variant=${id}`,
      featured_image: img, featured_media: media.find((x) => x.preview_image === img), inventory_management: null, product_id: 0,
    };
  }));
  const prices = variants.map((v) => v.price);
  const care = '<p><strong>Care:</strong> we recommend not leaving it in direct sunlight or anywhere around 130&nbsp;&deg;F (about 55&nbsp;&deg;C), such as a dashboard in summer, for extended periods: the print can soften and warp.</p>';
  const description = c.wall
    ? `<p>The ${c.make} ${c.model} (${c.generation}) front as a wall key holder, four key hooks. Printed in high-quality PLA filament.</p><p><strong>Mounting:</strong> we recommend strong double-sided mounting tape on the back: it sits flat and looks cleanest. There is also a countersunk hole on each side for a screw or nail.</p><p><strong>Keys only:</strong> the hooks are made for keys and light keyrings. We don't recommend hanging coats, bags or anything of the sort on them.</p>${care}`
    : `<p>A straight-on keychain of the ${c.make} ${c.model} (${c.generation}) front. ${c.variant ? 'Snake-eye light bars' : 'The light signature'}, grille texture and intakes are printed in relief, in two colours.</p><ul><li>80.5 mm wide, 3 mm thick</li><li>Two-colour 3D print</li><li>Printed in high-quality PLA filament</li><li>Split ring and short chain included</li><li>Logo-free design</li></ul>${care}`;
  return {
    id: nextId++, index: idx, handle, title, url: `/products/${handle}`, vendor: 'Grille Talk', type: c.wall ? 'Wall key holder' : 'Keychain',
    tags: [`make:${c.make}`, `model:${c.model}`, `generation:${c.generation}`, ...c.aliases.map((a) => `alias:${a}`)],
    description, content: description,
    featured_image: imgs[0], images: imgs, media, featured_media: media[0],
    variants, price: Math.min(...prices), price_min: Math.min(...prices), price_max: Math.max(...prices),
    price_varies: Math.min(...prices) !== Math.max(...prices), available: true, has_only_default_variant: false,
    options: hasHl ? ['Body color', 'Headlight color'] : ['Body color'],
    metafields: { custom: { make: { value: c.make }, model: { value: c.model }, generation: { value: c.generation }, short_model: { value: c.short_model } } },
    _car: c,
  };
});

export function productView(p, variantId) {
  const v = p.variants.find((x) => String(x.id) === String(variantId)) || p.variants[0];
  return {
    ...p,
    selected_variant: variantId ? v : null,
    selected_or_first_available_variant: v,
    first_available_variant: p.variants[0],
    options_with_values: [
      { name: 'Body color', position: 1, values: [...new Set(p.variants.map((x) => x.option1))], selected_value: v.option1 },
      ...(v.option2 ? [{ name: 'Headlight color', position: 2, values: [...new Set(p.variants.map((x) => x.option2))], selected_value: v.option2 }] : []),
    ],
  };
}

export const colors = launch.colors;

export const pages = {
  about: { handle: 'about', title: 'About', template_suffix: 'about', content: '' },
  contact: { handle: 'contact', title: 'Contact', template_suffix: 'contact', content: '' },
  faq: { handle: 'faq', title: 'FAQ', template_suffix: 'faq', content: '' },
  'request-a-car': { handle: 'request-a-car', title: 'Request a car', template_suffix: 'request-a-car', content: '' },
};
Object.values(pages).forEach((p) => { p.url = `/pages/${p.handle}`; p.id = nextId++; });

const link = (title, url) => ({ title, url, links: [] });
export const linklists = {
  'main-menu': { title: 'Main menu', handle: 'main-menu', links: [link('Shop', '/#range'), link('Catalog', '/collections/all'), link('Wall holders', '/collections/wall-key-holders'), link('Request a car', '/pages/request-a-car'), link('About', '/pages/about'), link('FAQ', '/pages/faq'), link('Contact', '/pages/contact')] },
  footer: { title: 'Shop', handle: 'footer', links: [link('Keychains', '/collections/keychains'), link('Wall key holders', '/collections/wall-key-holders'), link('Request a car', '/pages/request-a-car'), link('About', '/pages/about'), link('FAQ', '/pages/faq'), link('Contact', '/pages/contact'), link('Search', '/search')] },
};

// Policies stay empty until the owner writes them in Shopify; the preview shows placeholders as links only.
export const policies = [
  { title: 'Refund policy', url: '/policies/refund-policy' },
  { title: 'Privacy policy', url: '/policies/privacy-policy' },
  { title: 'Terms of service', url: '/policies/terms-of-service' },
  { title: 'Shipping policy', url: '/policies/shipping-policy' },
];
