// Local preview of the Shopify theme: liquidjs plus shims for the Shopify tags, filters and objects the theme uses,
// with mock store data. It exists so screenshots, Playwright, Lighthouse and axe can run without a store.
// It is a preview aid, not a Shopify replacement: checkout, customer accounts and real search ranking are Shopify's.
// usage (from site/): node preview/server.mjs [port]     then open http://localhost:4100
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { Liquid, Tag, Hash, Value } from 'liquidjs';
import * as data from './data.mjs';

const SITE = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/, '$1')), '..');
const THEME = path.resolve(SITE, '..', 'theme');
const PORT = Number(process.argv[2] || process.env.PORT || 4100);
const read = (p) => fs.readFileSync(p, 'utf8');
const locales = JSON.parse(read(path.join(THEME, 'locales', 'en.default.json')));
const settingsData = JSON.parse(read(path.join(THEME, 'config', 'settings_data.json'))).current;

const liquid = new Liquid({
  root: [path.join(THEME, 'snippets')],
  partials: path.join(THEME, 'snippets'),
  layouts: path.join(THEME, 'layout'),
  extname: '.liquid',
  cache: false,
  dynamicPartials: true,
  relativeReference: false,
});

/* ---------------- filters ---------------- */
const money = (c) => `$${(Number(c || 0) / 100).toFixed(2)}`;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
liquid.registerFilter('money', money);
liquid.registerFilter('money_with_currency', (c) => `${money(c)} USD`);
liquid.registerFilter('money_without_currency', (c) => (Number(c || 0) / 100).toFixed(2));
liquid.registerFilter('money_without_trailing_zeros', (c) => money(c).replace('.00', ''));
liquid.registerFilter('asset_url', (f) => `/assets/${f}`);
liquid.registerFilter('inline_asset_content', (f) => read(path.join(THEME, 'assets', f)));
liquid.registerFilter('stylesheet_tag', (u) => `<link rel="stylesheet" href="${u}" media="all">`);
liquid.registerFilter('script_tag', (u) => `<script src="${u}"></script>`);
liquid.registerFilter('handleize', (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''));
liquid.registerFilter('image_url', (img, ...args) => {
  if (!img) return '';
  const o = Object.fromEntries(args.filter(Array.isArray));
  const u = img.url ? img.url(o.width) : String(img);
  return { __img: img, url: u, toString: () => u, width: o.width };
});
liquid.registerFilter('image_tag', (u, ...args) => {
  const o = Object.fromEntries(args.filter(Array.isArray));
  const img = u && u.__img;
  const src = String(u);
  const attrs = [];
  let srcset = '';
  if (img && img.url && o.widths) {
    srcset = String(o.widths).split(',').map((w) => `${img.url(Number(w))} ${Math.min(Number(w), 2000)}w`).filter((v, i, a) => a.indexOf(v) === i).join(', ');
  }
  const w = o.width || (img && img.width) || '';
  const h = o.height || (img && img.height) || '';
  attrs.push(`src="${src}"`);
  if (srcset) attrs.push(`srcset="${srcset}"`);
  if (o.sizes) attrs.push(`sizes="${o.sizes}"`);
  attrs.push(`alt="${esc(o.alt ?? (img && img.alt) ?? '')}"`);
  if (w) attrs.push(`width="${w}"`);
  if (h) attrs.push(`height="${h}"`);
  for (const [k, v] of Object.entries(o)) {
    if (['widths', 'sizes', 'alt', 'width', 'height'].includes(k)) continue;
    attrs.push(v === '' || v === true ? k : `${k}="${esc(v)}"`);
  }
  return `<img ${attrs.join(' ')}>`;
});
liquid.registerFilter('t', (key, ...args) => {
  const o = Object.fromEntries(args.filter(Array.isArray));
  let v = String(key).split('.').reduce((a, k) => (a ? a[k] : undefined), locales);
  if (v && typeof v === 'object') v = o.count === 1 ? v.one : v.other;
  if (v === undefined) return `translation missing: en.${key}`;
  return String(v).replace(/\{\{\s*(\w+)\s*\}\}/g, (_, k) => (o[k] !== undefined ? o[k] : ''));
});
liquid.registerFilter('payment_button', () => '<div class="shopify-payment-button"><button type="button" class="shopify-payment-button__button btn btn--ghost btn--block" disabled title="Dynamic checkout (Shop Pay) renders here on the live store">Buy with Shop Pay (live store only)</button></div>');
liquid.registerFilter('model_viewer_tag', (media, ...args) => {
  const o = Object.fromEntries(args.filter(Array.isArray));
  const src = media.sources[0].url;
  const extra = Object.entries(o).map(([k, v]) => (v === true ? k : `${k}="${esc(v)}"`)).join(' ');
  return `<model-viewer src="${src}" alt="${esc(media.alt)}" camera-controls ${extra}></model-viewer>`;
});
liquid.registerFilter('default_errors', (errs) => (errs && errs.messages ? `<ul>${Object.values(errs.messages).map((m) => `<li>${esc(m)}</li>`).join('')}</ul>` : ''));
liquid.registerFilter('placeholder_svg_tag', () => '<svg viewBox="0 0 10 10"></svg>');
liquid.registerFilter('within', (u) => u);
liquid.registerFilter('link_to', (t, u) => `<a href="${u}">${t}</a>`);

/* ---------------- tags ---------------- */
liquid.registerTag('schema', {
  parse(token, remain) { this.tpl = []; let t; while ((t = remain.shift())) { if (t.name === 'endschema') return; } },
  render() { return ''; },
});
for (const [name, wrap] of [['style', ['<style>', '</style>']], ['javascript', ['<script>', '</script>']], ['stylesheet', ['<style>', '</style>']]]) {
  liquid.registerTag(name, {
    parse(token, remain) { this.tpls = []; const s = liquid.parser.parseStream(remain); s.on(`tag:end${name}`, () => s.stop()).on('template', (t) => this.tpls.push(t)).on('end', () => { throw new Error(`tag ${name} not closed`); }); s.start(); },
    * render(ctx, emitter) { emitter.write(wrap[0]); yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter); emitter.write(wrap[1]); },
  });
}
liquid.registerTag('paginate', {
  parse(token, remain) {
    this.args = token.args; this.tpls = [];
    const s = liquid.parser.parseStream(remain);
    s.on('tag:endpaginate', () => s.stop()).on('template', (t) => this.tpls.push(t)).on('end', () => { throw new Error('paginate not closed'); });
    s.start();
  },
  * render(ctx, emitter) {
    ctx.push({ paginate: { pages: 1, current_page: 1, items: 0, previous: null, next: null, parts: [] } });
    yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter);
    ctx.pop();
  },
});
liquid.registerTag('form', {
  parse(token, remain) {
    const m = token.args.match(/^\s*(['"])([\w-]+)\1\s*(?:,\s*(.*))?$/s);
    this.type = m[2];
    const rest = m[3] || '';
    const parts = rest.split(',').map((x) => x.trim()).filter(Boolean);
    this.objExpr = parts.length && !parts[0].includes(':') ? parts.shift() : null;
    this.hash = new Hash(parts.join(', '));
    this.tpls = [];
    const s = liquid.parser.parseStream(remain);
    s.on('tag:endform', () => s.stop()).on('template', (t) => this.tpls.push(t)).on('end', () => { throw new Error('form not closed'); });
    s.start();
  },
  * render(ctx, emitter) {
    const h = yield this.hash.render(ctx);
    const formState = ctx.environments.__forms?.[this.type] || {};
    const action = { product: '/cart/add', contact: '/contact', customer: '/contact', customer_login: '/account/login', create_customer: '/account', recover_customer_password: '/account/recover', localization: '/localization' }[this.type] || '/';
    const attrs = Object.entries(h).filter(([k]) => !['return_to'].includes(k)).map(([k, v]) => `${k}="${esc(v)}"`).join(' ');
    emitter.write(`<form method="post" action="${action}" accept-charset="UTF-8" ${attrs}><input type="hidden" name="form_type" value="${this.type}"><input type="hidden" name="utf8" value="✓">`);
    ctx.push({ form: { errors: formState.errors || null, 'posted_successfully?': !!formState.ok, posted_successfully: !!formState.ok, id: h.id } });
    yield this.liquid.renderer.renderTemplates(this.tpls, ctx, emitter);
    ctx.pop();
    emitter.write('</form>');
  },
});

/* ---------------- sections ---------------- */
function schemaOf(file) {
  const m = read(file).match(/{%-?\s*schema\s*-?%}([\s\S]*?){%-?\s*endschema\s*-?%}/);
  return m ? JSON.parse(m[1]) : {};
}
function resolveSetting(type, v) {
  if (v === undefined || v === null || v === '') return v;
  if (type === 'link_list') return data.linklists[v] || null;
  if (type === 'product') return data.products.find((p) => p.handle === v) || null;
  if (type === 'collection') return v === 'all' ? allCollection() : null;
  if (type === 'page') return data.pages[v] || null;
  return v;
}
function settingsFrom(schemaSettings = [], values = {}) {
  const out = {};
  for (const s of schemaSettings) {
    if (!s.id) continue;
    const v = values[s.id] !== undefined ? values[s.id] : s.default;
    out[s.id] = resolveSetting(s.type, v);
  }
  return out;
}
const themeSettings = (() => {
  const schema = JSON.parse(read(path.join(THEME, 'config', 'settings_schema.json')));
  const all = schema.flatMap((g) => g.settings || []);
  const s = settingsFrom(all, settingsData);
  s.request_page = data.pages['request-a-car'];
  return s;
})();

async function renderSection(type, id, cfg, ctxBase) {
  const file = path.join(THEME, 'sections', `${type}.liquid`);
  const schema = schemaOf(file);
  const blocks = (cfg.block_order || Object.keys(cfg.blocks || {})).map((bid) => {
    const b = cfg.blocks[bid];
    const bs = (schema.blocks || []).find((x) => x.type === b.type) || {};
    return { id: bid, type: b.type, settings: settingsFrom(bs.settings, b.settings || {}), shopify_attributes: '' };
  });
  const section = { id, settings: settingsFrom(schema.settings, cfg.settings || {}), blocks };
  const scope = { ...ctxBase, section };
  const html = await liquid.parseAndRender(read(file), scope, { globals: scope });
  return `<div id="shopify-section-${id}" class="shopify-section">${html}</div>`;
}

liquid.registerTag('section', {
  parse(token) { this.name = token.args.replace(/['"\s]/g, ''); },
  * render(ctx, emitter) { emitter.write(yield renderSection(this.name, this.name, {}, ctx.getAll())); },
});
liquid.registerTag('sections', {
  parse(token) { this.name = token.args.replace(/['"\s]/g, ''); },
  * render(ctx, emitter) {
    const g = JSON.parse(read(path.join(THEME, 'sections', `${this.name}.json`)));
    for (const id of g.order) emitter.write(yield renderSection(g.sections[id].type, `sections--${id}`, g.sections[id], ctx.getAll()));
  },
});

/* ---------------- store state ---------------- */
function allCollection(query = {}) {
  let items = data.products.map((p) => data.productView(p));
  const make = [].concat(query['filter.p.m.custom.make'] || []);
  const makes = [...new Set(data.products.map((p) => p.metafields.custom.make.value))].sort();
  const base = '/collections/all';
  const qs = (params) => { const u = new URLSearchParams(); for (const [k, v] of params) u.append(k, v); const s = u.toString(); return s ? `${base}?${s}` : base; };
  const current = [...make.map((m) => ['filter.p.m.custom.make', m])];
  if (query.sort_by) current.push(['sort_by', query.sort_by]);
  const values = makes.map((m) => {
    const active = make.includes(m);
    return {
      label: m, value: m, param_name: 'filter.p.m.custom.make', active,
      count: data.products.filter((p) => p.metafields.custom.make.value === m).length,
      url_to_add: qs([...current, ['filter.p.m.custom.make', m]]),
      url_to_remove: qs(current.filter(([k, v]) => !(k === 'filter.p.m.custom.make' && v === m))),
    };
  });
  if (make.length) items = items.filter((p) => make.includes(p.metafields.custom.make.value));
  const sort = query.sort_by || 'manual';
  const by = {
    'title-ascending': (a, b) => a.title.localeCompare(b.title), 'title-descending': (a, b) => b.title.localeCompare(a.title),
    'price-ascending': (a, b) => a.price - b.price || a.index - b.index, 'price-descending': (a, b) => b.price - a.price || a.index - b.index,
  }[sort];
  if (by) items = [...items].sort(by);
  return {
    id: 1, handle: 'all', title: 'All keychains', url: base, description: '', products: items, products_count: items.length,
    all_products_count: data.products.length, sort_by: sort, default_sort_by: 'manual',
    sort_options: [['manual', 'Featured'], ['title-ascending', 'Alphabetically, A-Z'], ['title-descending', 'Alphabetically, Z-A'], ['price-ascending', 'Price, low to high'], ['price-descending', 'Price, high to low']].map(([value, name]) => ({ value, name })),
    filters: [{ label: 'Make', param_name: 'filter.p.m.custom.make', type: 'list', values, active_values: values.filter((v) => v.active), url_to_remove: qs(current.filter(([k]) => k !== 'filter.p.m.custom.make')) }],
  };
}

const cart = { items: [], note: '' };
function cartView() {
  const items = cart.items.map((it, i) => {
    const p = data.products.find((x) => x.variants.some((v) => v.id === it.variant_id));
    const v = p.variants.find((x) => x.id === it.variant_id);
    return {
      key: `${v.id}:k`, id: v.id, variant_id: v.id, quantity: it.quantity, title: `${p.title} - ${v.title}`, product: data.productView(p),
      variant: v, url: v.url, image: v.featured_image, price: v.price, final_price: v.price, final_line_price: v.price * it.quantity,
      line_price: v.price * it.quantity, options_with_values: [{ name: 'Body color', value: v.title }], url_to_remove: `/cart/change?line=${i + 1}&quantity=0`,
    };
  });
  const total = items.reduce((a, b) => a + b.final_line_price, 0);
  return { items, item_count: items.reduce((a, b) => a + b.quantity, 0), total_price: total, items_subtotal_price: total, currency: { iso_code: 'USD' }, note: cart.note };
}
function cartJson() {
  const c = cartView();
  return { ...c, items: c.items.map((i) => ({ key: i.key, id: i.id, variant_id: i.variant_id, quantity: i.quantity, title: i.title, price: i.price, final_line_price: i.final_line_price, url: i.url, product_title: i.product.title, variant_title: i.variant.title })) };
}
function addToCart(variantId, qty) {
  const id = Number(variantId);
  if (!data.products.some((p) => p.variants.some((v) => v.id === id))) return { status: 404, message: 'Cart Error', description: 'This variant no longer exists.' };
  if (!(qty >= 1)) return { status: 422, message: 'Cart Error', description: 'Quantity must be 1 or more.' };
  const line = cart.items.find((x) => x.variant_id === id);
  if (line) line.quantity += qty; else cart.items.push({ variant_id: id, quantity: qty });
  return null;
}

/* ---------------- request handling ---------------- */
function baseContext(req, extra = {}) {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  return {
    shop: { name: 'Grille Talk', url: `http://localhost:${PORT}`, money_format: '${{amount}}', description: '', policies: data.policies, email: 'tristen@grilletalk.shop' },
    settings: themeSettings,
    routes: { root_url: '/', cart_url: '/cart', cart_add_url: '/cart/add', cart_change_url: '/cart/change', search_url: '/search', predictive_search_url: '/search/suggest', collections_url: '/collections', account_url: '/account', account_login_url: '/account/login' },
    request: { locale: { iso_code: 'en' }, page_type: extra.page_type || 'index', path: url.pathname, host: url.host },
    canonical_url: `http://localhost:${PORT}${url.pathname}`,
    content_for_header: '<!-- content_for_header (Shopify injects scripts here on the live store) -->',
    cart: cartView(),
    collections: { all: allCollection() },
    linklists: data.linklists,
    pages: data.pages,
    current_page: 1,
    __forms: extra.forms || {},
    ...extra,
  };
}

async function renderTemplate(name, ctx, suffix) {
  const file = path.join(THEME, 'templates', `${name}${suffix ? `.${suffix}` : ''}.json`);
  const tpl = JSON.parse(read(file));
  let out = '';
  for (const id of tpl.order) {
    const s = tpl.sections[id];
    if (s.disabled) continue;
    out += await renderSection(s.type, `template--${name}__${id}`, s, ctx);
  }
  return out;
}

async function page(req, res, name, extra, suffix, status = 200) {
  const ctx = baseContext(req, extra);
  ctx.template = { name, suffix: suffix || null, directory: null };
  ctx.content_for_layout = await renderTemplate(name, ctx, suffix);
  const html = await liquid.parseAndRender(read(path.join(THEME, 'layout', 'theme.liquid')), ctx, { globals: ctx });
  res.writeHead(status, { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' });
  res.end(html.replace('</head>', '<script>window.__PREVIEW__=true</script></head>'));
}

const types = { '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.glb': 'model/gltf-binary', '.json': 'application/json' };
function serveFile(res, file) {
  if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end('not found'); }
  res.writeHead(200, { 'content-type': types[path.extname(file)] || 'application/octet-stream', 'cache-control': 'public, max-age=300' });
  fs.createReadStream(file).pipe(res);
}
const body = (req) => new Promise((ok) => { let b = ''; req.on('data', (c) => { b += c; }); req.on('end', () => ok(b)); });
async function formBody(req) {
  const raw = await body(req);
  const ct = req.headers['content-type'] || '';
  if (ct.includes('application/json')) return JSON.parse(raw || '{}');
  if (ct.includes('multipart/form-data')) {
    const boundary = ct.split('boundary=')[1];
    const out = {};
    for (const part of raw.split(`--${boundary}`)) {
      const m = part.match(/name="([^"]+)"\r\n\r\n([\s\S]*?)\r\n$/);
      if (m) out[m[1]] = m[2];
    }
    return out;
  }
  return Object.fromEntries(new URLSearchParams(raw));
}
const json = (res, status, obj) => { res.writeHead(status, { 'content-type': 'application/json' }); res.end(JSON.stringify(obj)); };

async function sectionsPayload(names, req) {
  const out = {};
  for (const n of [].concat(names || []).flatMap((x) => String(x).split(',')).filter(Boolean)) {
    out[n] = await renderSection(n, n, {}, baseContext(req));
  }
  return out;
}

function search(q) {
  const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
  return data.products.filter((p) => {
    const hay = [p.title, p.vendor, p.type, ...p.tags, ...p.variants.map((v) => v.title)].join(' ').toLowerCase();
    const words = hay.split(/[^a-z0-9-]+/);
    return terms.every((t) => words.some((w) => w.startsWith(t)) || hay.includes(t));
  }).map((p) => data.productView(p));
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const q = Object.fromEntries(url.searchParams);
  const qa = (k) => url.searchParams.getAll(k);
  const p = decodeURIComponent(url.pathname);
  try {
    if (p.startsWith('/assets/')) return serveFile(res, path.join(THEME, 'assets', path.basename(p)));
    if (p.startsWith('/media/')) return serveFile(res, path.join(SITE, 'build', p.replace(/\.\./g, '')));
    if (p.startsWith('/glb/')) return serveFile(res, path.join(SITE, 'build', 'glb', path.basename(p)));
    if (p === '/vendor/model-viewer.min.js') return serveFile(res, path.join(SITE, 'node_modules', '@google', 'model-viewer', 'dist', 'model-viewer.min.js'));

    // section rendering API
    if (q.sections && req.method === 'GET') return json(res, 200, await sectionsPayload(q.sections, req));
    if (q.section_id && !p.startsWith('/search/suggest')) {
      const ctx = baseContext(req);
      return res.end(await renderSection(q.section_id, q.section_id, {}, ctx));
    }

    if (p === '/cart.js') return json(res, 200, cartJson());
    if (p === '/cart/add.js' && req.method === 'POST') {
      const b = await formBody(req);
      const err = addToCart(b.id, Number(b.quantity || 1));
      if (err) return json(res, err.status, err);
      const c = cartView();
      const line = c.items.find((i) => i.variant_id === Number(b.id));
      return json(res, 200, { ...line, product: undefined, variant: undefined, sections: await sectionsPayload(b.sections, req) });
    }
    if (p === '/cart/change.js' && req.method === 'POST') {
      const b = await formBody(req);
      const idx = Number(b.line) - 1;
      if (!cart.items[idx]) return json(res, 400, { status: 400, message: 'Cart Error', description: 'That line is no longer in your cart.' });
      const qn = Number(b.quantity);
      if (qn <= 0) cart.items.splice(idx, 1); else cart.items[idx].quantity = Math.min(qn, 99);
      return json(res, 200, { ...cartJson(), sections: await sectionsPayload(b.sections, req) });
    }
    if (p === '/cart/change') {   // no-JS remove link
      const idx = Number(q.line) - 1; if (cart.items[idx]) cart.items.splice(idx, 1);
      res.writeHead(302, { location: '/cart' }); return res.end();
    }
    if (p === '/cart/add' && req.method === 'POST') {
      const b = await formBody(req); addToCart(b.id, Number(b.quantity || 1));
      res.writeHead(302, { location: '/cart' }); return res.end();
    }
    if (p === '/cart' && req.method === 'POST') {
      const b = await formBody(req);
      if ('checkout' in b) {
        res.writeHead(200, { 'content-type': 'text/html' });
        return res.end('<!doctype html><title>Checkout (preview)</title><body style="font:16px system-ui;background:#000;color:#fff;padding:40px"><h1>Shopify checkout</h1><p>On the live store this request goes to Shopify checkout. The preview does not take orders or payments.</p><p><a style="color:#fff" href="/cart">Back to cart</a></p>');
      }
      const ups = [].concat(qa('updates[]'));
      ups.forEach((v, i) => { if (cart.items[i]) cart.items[i].quantity = Number(v); });
      cart.items = cart.items.filter((x) => x.quantity > 0);
      res.writeHead(302, { location: '/cart' }); return res.end();
    }
    if (p === '/cart') return await page(req, res, 'cart', { page_type: 'cart', page_title: 'Your cart' });

    if (p === '/search/suggest') {
      const terms = q.q || '';
      const ctx = baseContext(req, { predictive_search: { performed: !!terms, terms, resources: { products: search(terms).slice(0, Number(q['resources[limit]'] || 6)) } } });
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      return res.end(await renderSection('predictive-search', 'predictive-search', {}, ctx));
    }
    if (p === '/search') {
      const terms = q.q || '';
      const results = terms ? search(terms) : [];
      return await page(req, res, 'search', { page_type: 'search', page_title: terms ? `Search: ${terms}` : 'Search', search: { performed: !!terms, terms, results, results_count: results.length } });
    }
    if (p === '/' ) return await page(req, res, 'index', { page_type: 'index', page_title: 'Grille Talk: car-front keychains' });
    if (p === '/collections/all' || p === '/collections') {
      const filterQ = { 'filter.p.m.custom.make': qa('filter.p.m.custom.make'), sort_by: q.sort_by };
      const col = allCollection(filterQ);
      return await page(req, res, 'collection', { page_type: 'collection', page_title: col.title, collection: col, page_description: 'Every Grille Talk design: car-front keychains with light signatures, grilles and intakes in two colours.' });
    }
    const pm = p.match(/^\/products\/([\w-]+)$/);
    if (pm) {
      const prod = data.products.find((x) => x.handle === pm[1]);
      if (prod) {
        const view = data.productView(prod, q.variant);
        return await page(req, res, 'product', { page_type: 'product', page_title: prod.title, product: view, page_description: `3D-printed keychain of the ${prod._car.make} ${prod._car.model} (${prod._car.generation}) front. 80.5 mm, two colours, split ring and chain included.` });
      }
    }
    const pg = p.match(/^\/pages\/([\w-]+)$/);
    if (pg && data.pages[pg[1]]) {
      const pageObj = data.pages[pg[1]];
      return await page(req, res, 'page', { page_type: 'page', page_title: pageObj.title, page: pageObj }, pageObj.template_suffix);
    }
    if (p === '/contact' && req.method === 'POST') {
      const b = await formBody(req);
      const email = b['contact[email]'] || '';
      const ok = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
      const forms = { [b.form_type]: ok ? { ok: true } : { errors: { messages: { email: 'is invalid' }, translated_fields: { email: 'Email' } } } };
      const back = new URL(req.headers.referer || '/', `http://localhost:${PORT}`).pathname;
      const pgm = back.match(/^\/pages\/([\w-]+)$/);
      if (pgm && data.pages[pgm[1]]) return await page(req, res, 'page', { page_type: 'page', page_title: data.pages[pgm[1]].title, page: data.pages[pgm[1]], forms }, data.pages[pgm[1]].template_suffix);
      return await page(req, res, 'index', { page_type: 'index', page_title: 'Grille Talk', forms });
    }
    if (p.startsWith('/policies/')) {
      res.writeHead(200, { 'content-type': 'text/html' });
      return res.end('<!doctype html><title>Policy (preview)</title><body style="font:16px system-ui;background:#000;color:#fff;padding:40px"><p>Shopify renders this policy from Settings &gt; Policies on the live store. Not written yet.</p><a style="color:#fff" href="/">Home</a>');
    }
    return await page(req, res, '404', { page_type: '404', page_title: 'Page not found' }, null, 404);
  } catch (e) {
    console.error(e);
    res.writeHead(500, { 'content-type': 'text/plain' });
    res.end(`Preview error: ${e.message}`);
  }
});
server.listen(PORT, () => console.log(`Grille Talk preview on http://localhost:${PORT}`));
