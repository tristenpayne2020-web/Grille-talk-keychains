// End-to-end checks against the local preview (start it first: node preview/server.mjs).
// Writes site/build/reports/audit.json and screenshots to site/build/shots/audit-*.png.
// usage (from site/): node tools/audit.mjs
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import AxeBuilder from '@axe-core/playwright';
import { launch } from './browser.mjs';

const BASE = process.env.PREVIEW || 'http://localhost:4100';
fs.mkdirSync('build/reports', { recursive: true });
fs.mkdirSync('build/shots', { recursive: true });
const results = [];
const check = (name, ok, detail = '') => { results.push({ name, ok: !!ok, detail }); console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? `  (${detail})` : ''}`); };
const shot = (p, n) => p.screenshot({ path: `build/shots/audit-${n}.png` });

const browser = await launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
async function newPage(width = 1440, opts = {}) {
  const ctx = await browser.newContext({ viewport: { width, height: width < 600 ? 844 : 900 }, hasTouch: width < 600, isMobile: width < 600, ...opts });
  if (!opts.fresh) await ctx.addInitScript(() => { try { sessionStorage.setItem('gt-intro', '1'); } catch (e) {} });
  const page = await ctx.newPage();
  page.errors = [];
  page.on('pageerror', (e) => page.errors.push(e.message));
  return page;
}
const reset = () => fetch(`${BASE}/cart.js`).then((r) => r.json()).then(async (c) => { for (let i = c.items.length; i > 0; i--) await fetch(`${BASE}/cart/change.js`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ line: 1, quantity: 0 }) }); });

/* first-visit loader (the owner's artwork) and hero */
{
  const p = await newPage(1440, { fresh: true });
  await p.goto(BASE + '/', { waitUntil: 'commit' });
  await p.waitForSelector('#loader', { timeout: 10000 });
  const t0 = Date.now();
  await p.waitForTimeout(400);
  await shot(p, 'loader-early');
  const c1 = Number(await p.textContent('[data-loader-count]'));
  await p.waitForTimeout(700);
  await shot(p, 'loader-mid');
  const c2 = Number(await p.textContent('[data-loader-count]').catch(() => '100'));
  check('loader shows the supplied artwork', await p.evaluate(() => /loader-art-/.test(document.querySelector('.loader__img--dim')?.getAttribute('src') || '')));
  check('loader counter climbs', c2 >= c1, `${c1} -> ${c2}`);
  // at 100% the push-to-start button appears; pressing it plays the procedural cold start and opens the site
  await p.evaluate(() => { const AC = window.AudioContext; window.__audio = 0; window.AudioContext = class extends AC { constructor(...a) { super(...a); window.__audio += 1; } }; });
  await p.waitForSelector('[data-loader-start]', { state: 'visible', timeout: 9000 });
  const took = Date.now() - t0;
  check('loader reaches 100% and offers the engine start button', true, `${took} ms`);
  await shot(p, 'loader-ignition');
  await p.click('[data-loader-start]');
  await p.waitForTimeout(300);
  check('engine start plays the cold-start sound (AudioContext running)', await p.evaluate(() => window.__audio > 0));
  await p.waitForFunction(() => !document.getElementById('loader'), null, { timeout: 5000 }).catch(() => {});
  check('loader lifts after the engine catches', !(await p.$('#loader')));
  await p.waitForTimeout(1500);
  await shot(p, 'hero-after-loader');
  check('hero shows 3D keychain after loader', await p.evaluate(() => document.querySelector('[data-hero]').classList.contains('is-3d')));
  await p.reload();
  await p.waitForTimeout(300);
  check('loader once per session', !(await p.$('#loader')));
  const sk = await newPage(1440, { fresh: true });
  await sk.goto(BASE + '/', { waitUntil: 'commit' });
  await sk.waitForSelector('[data-loader-skip]', { state: 'attached', timeout: 10000 });
  const tSkip = Date.now();
  await sk.evaluate(() => document.querySelector('[data-loader-skip]').click());
  await sk.waitForFunction(() => !document.getElementById('loader'), null, { timeout: 10000 }).catch(() => {});
  check('loader skip works', !(await sk.$('#loader')), `${Date.now() - tSkip} ms`);
  const qq = await newPage(1440, { fresh: true });
  await qq.goto(BASE + '/', { waitUntil: 'commit' });
  await qq.waitForSelector('[data-loader-quiet]', { state: 'visible', timeout: 9000 });
  await qq.click('[data-loader-quiet]');
  await qq.waitForFunction(() => !document.getElementById('loader'), null, { timeout: 5000 }).catch(() => {});
  check('enter without sound works and is remembered', !(await qq.$('#loader')) && (await qq.evaluate(() => localStorage.getItem('gt-sound'))) === 'off');
  const nojs = await browser.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: false });
  const np = await nojs.newPage();
  await np.goto(BASE + '/');
  await np.screenshot({ path: 'build/shots/audit-home-nojs-390.png' });
  check('no JS: no loader, hero image and buttons visible', await np.evaluate(() => {
    const img = document.querySelector('[data-hero-static] img');
    const btn = document.querySelector('.hero__actions .btn');
    return !document.getElementById('loader') && img && btn && btn.getBoundingClientRect().bottom < window.innerHeight * 1.05;
  }));
  check('hero JS errors', p.errors.length + sk.errors.length === 0, [...p.errors, ...sk.errors].join(' | '));
}

/* detail tour and process chapters */
{
  const p = await newPage(1440);
  await p.goto(BASE + '/');
  const geo = await p.evaluate(() => { const t = document.querySelector('[data-tour]'); return { top: t.getBoundingClientRect().top + scrollY, h: t.offsetHeight }; });
  const seen = [];
  for (const f of [0.05, 0.3, 0.52, 0.74, 0.95]) {
    await p.evaluate((y) => scrollTo(0, y), geo.top + (geo.h - 900) * f);
    await p.waitForTimeout(500);
    seen.push(await p.evaluate(() => [...document.querySelectorAll('[data-tour-item]')].findIndex((e) => e.classList.contains('is-active'))));
  }
  check('tour steps through every detail on scroll', [0, 1, 2, 3].every((i) => seen.includes(i)), seen.join(','));
  await p.evaluate(() => scrollTo(0, 0));
  await p.click('[data-tour-go="2"]').catch(async () => { await p.evaluate(() => document.querySelector('[data-tour-go="2"]').click()); });
  await p.waitForTimeout(1500);
  check('tour rail jumps to a detail', await p.evaluate(() => document.querySelectorAll('[data-tour-item]')[2].classList.contains('is-active')));
  await p.evaluate(() => { document.documentElement.style.scrollBehavior = 'auto'; document.querySelectorAll('[data-process-step]')[2].scrollIntoView({ block: 'center' }); });
  await p.waitForTimeout(1200);
  check('process visual follows the active step', await p.evaluate(() => document.querySelector('[data-process-img="2"]').classList.contains('is-active')));
  check('chapters JS errors', p.errors.length === 0, p.errors.join(' | '));
}

/* range viewer */
{
  const p = await newPage(1440);
  await p.goto(BASE + '/');
  await p.evaluate(() => document.querySelector('#range').scrollIntoView());
  await p.waitForTimeout(1500);
  const title = () => p.textContent('[data-range-title]');
  const t1 = await title();
  await p.click('[data-range-next]');
  await p.waitForTimeout(800);
  const t2 = await title();
  check('range next arrow changes keychain', t1 !== t2, `${t1} -> ${t2}`);
  await p.focus('[data-range]');
  await p.keyboard.press('ArrowLeft');
  await p.waitForTimeout(500);
  check('range arrow key goes back', (await title()) === t1);
  await p.click('[data-range-dot="9"]');
  await p.waitForTimeout(600);
  check('range dot jumps to position 10', (await p.textContent('[data-range-index]')).trim() === '10');
  check('range View link points at product', (await p.getAttribute('[data-range-view]', 'href')).startsWith('/products/'));
  await p.waitForTimeout(1500);
  await shot(p, 'range');
  check('range 3D canvas on', await p.evaluate(() => document.querySelector('[data-range-canvas]').classList.contains('is-on')));
  // the chain must sway, not spin: largest angle of the jump ring from hanging straight down while switching cars
  await p.evaluate(() => { window.__maxSwing = 0; const st = (window.__gtStages || []).find((x) => x.container.matches('[data-range-canvas]')); window.__rangeStage = st; const tick = () => { if (st && st.p) { const a = st.p[0], b = st.p[1], c = st.p[st.p.length - 1]; const ang = Math.atan2(Math.abs(c.x - a.x), a.y - c.y) * 180 / Math.PI; window.__maxSwing = Math.max(window.__maxSwing, ang); } requestAnimationFrame(tick); }; tick(); });
  for (let k = 0; k < 3; k++) { await p.click('[data-range-next]'); await p.waitForTimeout(700); }
  await p.waitForTimeout(1200);
  const swing = await p.evaluate(() => window.__maxSwing);
  check('range chain sways gently on next (under 35 degrees)', swing < 35, `${swing.toFixed(1)} deg`);
  const m = await newPage(390);
  await m.goto(BASE + '/');
  await m.evaluate(() => document.querySelector('#range').scrollIntoView());
  await m.waitForTimeout(1000);
  const before = await m.textContent('[data-range-title]');
  const box = await m.locator('[data-range-viewport]').boundingBox();
  const y = box.y + box.height / 2;
  await m.evaluate(({ x1, x2, y }) => {
    const vp = document.querySelector('[data-range-viewport]');
    const ev = (type, x) => vp.dispatchEvent(new PointerEvent(type, { pointerType: 'touch', clientX: x, clientY: y, bubbles: true }));
    ev('pointerdown', x1); ev('pointerup', x2);
  }, { x1: box.x + box.width * 0.8, x2: box.x + box.width * 0.2, y });
  await m.waitForTimeout(600);
  check('range swipe on touch advances', (await m.textContent('[data-range-title]')) !== before);
  check('range JS errors', p.errors.length + m.errors.length === 0, [...p.errors, ...m.errors].join(' | '));
}

/* product: swatches, price, URL, 3D colour; cart double-click guard */
{
  await reset();
  const p = await newPage(1440);
  await p.goto(BASE + '/products/toyota-gr-supra-a90-keychain');
  await p.waitForFunction(() => document.querySelector('[data-viewer]').classList.contains('is-ready'), null, { timeout: 15000 }).catch(() => {});
  const price0 = (await p.textContent('[data-price]')).trim();
  await p.click('label:has-text("Matte Red")');
  await p.waitForTimeout(400);
  const price1 = (await p.textContent('[data-price]')).trim();
  check('swatch updates price', price0 === '$6.99' && price1 === '$7.99', `${price0} -> ${price1}`);
  const vid = await p.inputValue('[data-variant-id]');
  check('swatch updates URL', p.url().includes(`variant=${vid}`));
  await p.waitForTimeout(800);
  const vimg = await p.evaluate(() => { const i = document.querySelector('[data-variant-image]'); return i && i.complete && i.naturalWidth > 0 && /matte-red/.test(i.currentSrc); });
  check('swatch swaps the variant image and it loads', vimg);
  const aimg = await p.evaluate(() => { const i = document.querySelector('[data-variant-angle]'); return !!i && i.complete && i.naturalWidth > 0 && /matte-red-angle/.test(i.currentSrc); });
  check('swatch swaps the angled image to the same body color', aimg);
  await p.click('label[for="opt-2-yellow"]');
  await p.waitForTimeout(400);
  check('custom headlight color tints the gallery photos', await p.evaluate(() => [...document.querySelectorAll('[data-lights-tint]')].every((e) => e.classList.contains('is-on') && /#f0b70f/i.test(e.style.getPropertyValue('--tint')))));
  await p.click('label[for="opt-2-blue"]');
  await p.waitForTimeout(500);
  const price2 = (await p.textContent('[data-price]')).trim();
  check('custom headlight color adds the surcharge', price2 === '$8.49', price2);
  const lights = await p.evaluate(() => { const mv = document.querySelector('model-viewer'); const m = mv?.model?.materials.find((x) => x.name === 'lights'); return m ? m.pbrMetallicRoughness.baseColorFactor[2] > m.pbrMetallicRoughness.baseColorFactor[0] : null; });
  check('custom headlight color recolours the 3D lights', lights === true);
  check('carbon-fibre back image in the gallery', await p.evaluate(() => [...document.querySelectorAll('.product__gallery img')].some((i) => /carbon-fibre/i.test(i.alt) && i.naturalWidth > 0)));
  await p.click('label[for="opt-2-white"]');
  await p.waitForTimeout(300);
  const color = await p.evaluate(() => {
    const mv = document.querySelector('model-viewer');
    const m = mv && mv.model && mv.model.materials.find((x) => x.name === 'body');
    return m ? m.pbrMetallicRoughness.baseColorFactor.map((v) => v.toFixed(2)).join(',') : null;
  });
  check('swatch recolours 3D body material', color && !color.startsWith('0.8') && color !== '0.95,0.95,0.94,1.00', String(color));
  await shot(p, 'product-red');
  // rapid double click on add to cart
  await p.click('form[data-product-form] [type="submit"]', { clickCount: 1 });
  await p.click('form[data-product-form] [type="submit"]', { force: true }).catch(() => {});
  await p.click('form[data-product-form] [type="submit"]', { force: true }).catch(() => {});
  await p.waitForTimeout(1500);
  const cart = await (await fetch(`${BASE}/cart.js`)).json();
  check('rapid clicks add once', cart.items.length === 1 && cart.items[0].quantity === 1, `lines=${cart.items.length} qty=${cart.items[0]?.quantity}`);
  check('cart drawer opens after add', await p.evaluate(() => document.getElementById('cart-drawer').classList.contains('is-open')));
  check('cart count updates', (await p.textContent('[data-cart-count]')).trim() === '1');
  await shot(p, 'cart-drawer');
  await p.click('#cart-drawer [data-qty-step="1"]');
  await p.waitForTimeout(800);
  check('drawer quantity +1', (await (await fetch(`${BASE}/cart.js`)).json()).item_count === 2);
  await p.keyboard.press('Escape');
  await p.waitForTimeout(400);
  check('Escape closes drawer', !(await p.evaluate(() => document.getElementById('cart-drawer').classList.contains('is-visible'))));
  // cart page remove
  await p.goto(BASE + '/cart');
  await p.click('[data-cart-page] [data-remove]');
  await p.waitForTimeout(1000);
  check('cart page remove empties cart', (await (await fetch(`${BASE}/cart.js`)).json()).item_count === 0);
  check('cart empty state shown', await p.isVisible('.cart-empty'));
  // checkout single navigation
  await fetch(`${BASE}/cart/add.js`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ id: Number(vid), quantity: 1 }) });
  await p.goto(BASE + '/cart');
  let navs = 0;
  p.on('request', (r) => { if (r.method() === 'POST' && r.url().endsWith('/cart')) navs++; });
  await Promise.all([p.waitForNavigation().catch(() => {}), p.dblclick('[data-cart-page] [data-checkout]')]);
  check('checkout double click submits once', navs === 1, `posts=${navs}`);
  check('product/cart JS errors', p.errors.length === 0, p.errors.join(' | '));
  await reset();
}

/* predictive search */
{
  const p = await newPage(1440);
  await p.goto(BASE + '/collections/all');
  await p.click('.header-actions [data-open="search-dialog"]');
  await p.waitForTimeout(300);
  check('search opens with focus in input', await p.evaluate(() => document.activeElement && document.activeElement.id === 'search-dialog-input'));
  for (const [q, want] of [['M3', 'M3'], ['Supra', 'Supra'], ['Corvette', 'Corvette'], ['vette', 'Corvette'], ['GTR', 'GT-R']]) {
    await p.fill('#search-dialog-input', q);
    await p.waitForTimeout(700);
    const titles = await p.$$eval('.predictive__title', (els) => els.map((e) => e.textContent));
    check(`search "${q}" finds ${want}`, titles.length > 0 && titles.every((t) => t.includes(want)), titles.join('; '));
  }
  await p.keyboard.press('ArrowDown');
  check('search listbox keyboard selection', await p.evaluate(() => document.querySelector('#search-dialog-input').getAttribute('aria-activedescendant') === 'predictive-option-1'));
  await p.fill('#search-dialog-input', 'zonda');
  await p.waitForTimeout(700);
  const empty = await p.textContent('#predictive-results');
  check('search empty state offers request', /No match for "zonda"/.test(empty) && (await p.isVisible('#predictive-results a[href*="request"]')));
  await shot(p, 'search-empty');
  await p.route('**/search/suggest**', (r) => r.abort());
  await p.fill('#search-dialog-input', 'm4');
  await p.waitForTimeout(700);
  check('search error state', /not responding/.test(await p.textContent('#predictive-results')));
}

/* mobile menu, focus trap */
{
  const p = await newPage(390);
  await p.goto(BASE + '/pages/about');
  await p.click('.menu-btn');
  await p.waitForTimeout(400);
  check('mobile menu opens', await p.isVisible('#menu-dialog .menu-list'));
  for (let i = 0; i < 12; i++) await p.keyboard.press('Tab');
  check('focus stays in menu', await p.evaluate(() => !!document.activeElement.closest('#menu-dialog')));
  await p.keyboard.press('Escape');
  await p.waitForTimeout(400);
  check('Escape closes menu and returns focus', await p.evaluate(() => document.activeElement.classList.contains('menu-btn')));
}

/* forms */
{
  const p = await newPage(1440);
  await p.goto(BASE + '/pages/request-a-car');
  await p.fill('#r-make', 'Pagani'); await p.fill('#r-model', 'Huayra'); await p.fill('#r-email', 'test@example.com');
  await p.click('#request-form [type="submit"]');
  check('request form success message', await p.waitForSelector('text=Request received', { timeout: 10000 }).then(() => true, () => false));
  await p.goto(BASE + '/');
  await p.evaluate(() => { const i = document.querySelector('#newsletter-email'); i.removeAttribute('required'); i.type = 'text'; i.value = 'nope'; });
  await Promise.all([p.waitForURL('**/contact', { timeout: 10000 }).catch(() => {}), p.click('#newsletter-form [type="submit"]')]);
  const nl = await p.evaluate(() => ({ url: location.pathname, err: document.querySelector('#newsletter-error')?.textContent.trim() || null }));
  check('newsletter error message', !!nl.err, JSON.stringify(nl));
}

/* links, titles, meta, overflow */
{
  const pages = ['/', '/collections/all', '/products/bmw-m3-g80-keychain', '/search?q=m3', '/cart', '/pages/about', '/pages/contact', '/pages/faq', '/pages/request-a-car', '/missing-page'];
  const p = await newPage(1440);
  const links = new Set();
  const titles = new Set();
  for (const u of pages) {
    const res = await p.goto(BASE + u);
    const meta = await p.evaluate(() => ({
      title: document.title, desc: document.querySelector('meta[name="description"]')?.content, og: document.querySelector('meta[property="og:image"]')?.content,
      canonical: document.querySelector('link[rel="canonical"]')?.href, h1: document.querySelectorAll('h1').length,
      icon: !!document.querySelector('link[rel="icon"]'), lorem: /lorem|ipsum|placeholder text/i.test(document.body.innerText), emdash: /—/.test(document.body.innerText),
      year: document.querySelector('.site-footer__legal')?.textContent.includes(String(new Date().getFullYear())),
    }));
    titles.add(meta.title);
    check(`page ${u}: status`, u === '/missing-page' ? res.status() === 404 : res.status() === 200, String(res.status()));
    check(`page ${u}: title, description, OG image, canonical, favicon, one h1`, meta.title && meta.desc && meta.og && meta.canonical && meta.icon && meta.h1 === 1, JSON.stringify({ t: meta.title, h1: meta.h1, d: !!meta.desc }));
    check(`page ${u}: no lorem, no em dash, footer year`, !meta.lorem && !meta.emdash && meta.year);
    (await p.$$eval('a[href]', (as) => as.map((a) => a.getAttribute('href')))).forEach((h) => links.add(h));
  }
  check('unique page titles', titles.size === pages.length, [...titles].join(' | '));
  const internal = [...links].filter((h) => h.startsWith('/') && !h.startsWith('//'));
  let bad = [];
  for (const h of internal) { const r = await fetch(BASE + h.split('#')[0]); if (r.status >= 400) bad.push(`${h} ${r.status}`); }
  check(`internal links resolve (${internal.length})`, bad.length === 0, bad.join(', '));
  const ext = [...links].filter((h) => /^(mailto|tel):/.test(h));
  check('mailto and tel links present', ext.includes('mailto:tristen@grilletalk.shop') && ext.includes('tel:+12299473742'), ext.join(', '));
  let over = [];
  for (const w of [320, 375, 768, 1024, 1440, 1920]) {
    const q = await newPage(w);
    for (const u of pages) {
      await q.goto(BASE + u);
      const o = await q.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      if (o > 0) over.push(`${u}@${w}:${o}px`);
    }
    await q.context().close();
  }
  check('no horizontal scroll 320-1920', over.length === 0, over.join(', '));
}

/* axe */
{
  const axe = {};
  for (const u of ['/', '/collections/all', '/products/bmw-m3-g80-keychain', '/cart']) {
    for (const w of [1440, 390]) {
      const p = await newPage(w);
      await p.goto(BASE + u);
      await p.waitForTimeout(1500);
      const r = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
      axe[`${u}@${w}`] = r.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help, targets: v.nodes.slice(0, 3).map((n) => n.target.join(' ')) }));
      check(`axe ${u} @${w}`, r.violations.length === 0, r.violations.map((v) => `${v.id}(${v.nodes.length})`).join(', '));
      await p.context().close();
    }
  }
  fs.writeFileSync('build/reports/axe.json', JSON.stringify(axe, null, 1));
}

/* publishing guard: reference photos and secrets */
{
  const grep = (args) => { try { return execSync(`git grep -n -I ${args}`, { encoding: 'utf8' }).trim(); } catch (e) { return ''; } };   // exit 1 = no match
  const out = grep('-e "/ref/" -- ../theme').split(/\r?\n/).filter((l) => l && !/\.md:/.test(l)).join(' | ');   // docs may mention the rule
  const built = [];
  const walk = (d) => { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); if (fs.statSync(p).isDirectory()) walk(p); else if (/ref[\\/]/.test(p)) built.push(p); } };
  walk('build/media');
  check('no kc/cars/*/ref/ paths in theme or published media', !out && built.length === 0, out + built.join(','));
  const secrets = grep('-E "shpat_[0-9a-f]|shpss_[0-9a-f]" -- ..');
  check('no Shopify tokens committed', !secrets, secrets);
}

await browser.close();
fs.writeFileSync('build/reports/audit.json', JSON.stringify(results, null, 1));
const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} passed`);
if (failed.length) process.exitCode = 1;
