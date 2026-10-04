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
  return slug(`${c.make}-${c.model}-${c.generation}${c.variant ? '-snake-eye' : ''}-keychain`);
}
export function titleFor(c) {
  return `Inspired by the ${c.make} ${c.model} (${c.generation})${c.variant ? `, ${c.variant}` : ''}`;
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
export const products = launch.cars.map((c, idx) => {
  const m = manifest[c.id];
  const handle = handleFor(c);
  const title = titleFor(c);
  const imgs = [];
  const variantImg = {};
  for (const it of m.media) {
    if (!['variant', 'angle'].includes(it.kind)) continue;   // the flat design drawing stays out of the storefront
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
  const variants = launch.colors.map((col) => {
    const id = nextId++;
    const img = variantImg[col.name];
    return {
      id, title: col.name, option1: col.name, options: [col.name], price: cents(launch.prices[col.tier]),
      available: true, sku: `GT-${c.id}-${slug(col.name)}`, url: `/products/${handle}?variant=${id}`,
      featured_image: img, featured_media: media.find((x) => x.preview_image === img), inventory_management: null,
    };
  });
  const prices = variants.map((v) => v.price);
  const description = `<p>A straight-on keychain of the ${c.make} ${c.model} (${c.generation}) front. ${c.variant ? 'Snake-eye light bars' : 'The light signature'}, grille texture and intakes are printed in relief, in two colours.</p><ul><li>80.5 mm wide, 3 mm thick</li><li>Two-colour 3D print</li><li>Split ring and short chain included</li><li>Logo-free design</li></ul>`;
  return {
    id: nextId++, index: idx, handle, title, url: `/products/${handle}`, vendor: 'Grille Talk', type: 'Keychain',
    tags: [`make:${c.make}`, `model:${c.model}`, `generation:${c.generation}`, ...c.aliases.map((a) => `alias:${a}`)],
    description, content: description,
    featured_image: imgs[0], images: imgs, media, featured_media: media[0],
    variants, price: Math.min(...prices), price_min: Math.min(...prices), price_max: Math.max(...prices),
    price_varies: Math.min(...prices) !== Math.max(...prices), available: true, has_only_default_variant: false,
    options: ['Body color'],
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
    options_with_values: [{ name: 'Body color', position: 1, values: p.variants.map((x) => x.title), selected_value: v.title }],
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
  'main-menu': { title: 'Main menu', handle: 'main-menu', links: [link('Shop', '/#range'), link('Catalog', '/collections/all'), link('Request a car', '/pages/request-a-car'), link('About', '/pages/about'), link('FAQ', '/pages/faq'), link('Contact', '/pages/contact')] },
  footer: { title: 'Shop', handle: 'footer', links: [link('All keychains', '/collections/all'), link('Request a car', '/pages/request-a-car'), link('About', '/pages/about'), link('FAQ', '/pages/faq'), link('Contact', '/pages/contact'), link('Search', '/search')] },
};

// Policies stay empty until the owner writes them in Shopify; the preview shows placeholders as links only.
export const policies = [
  { title: 'Refund policy', url: '/policies/refund-policy' },
  { title: 'Privacy policy', url: '/policies/privacy-policy' },
  { title: 'Terms of service', url: '/policies/terms-of-service' },
  { title: 'Shipping policy', url: '/policies/shipping-policy' },
];
