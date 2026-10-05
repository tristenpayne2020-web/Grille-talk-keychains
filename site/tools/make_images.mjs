// Render every launch car in every body colour with three.js in headless Chromium.
// Writes 2000 px PNGs to build/renders_png/; tools/make_webp.py turns them into WebP at 600/1200/2000.
// usage (from site/): node tools/make_images.mjs [id,id,...] [--white-only]
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { launch as launchBrowser } from './browser.mjs';

const SITE = path.resolve('.');
const OUT = path.resolve('build/renders_png');
fs.mkdirSync(OUT, { recursive: true });
const launch = JSON.parse(fs.readFileSync('catalog/launch.json', 'utf8'));
const args = process.argv.slice(2);
const only = args.find((a) => !a.startsWith('--'))?.split(',');
const whiteOnly = args.includes('--white-only');
const cars = launch.cars.filter((c) => !only || only.includes(c.id));
const colors = whiteOnly ? launch.colors.slice(0, 1) : launch.colors;

const types = { '.html': 'text/html', '.js': 'text/javascript', '.glb': 'model/gltf-binary', '.wasm': 'application/wasm' };
const server = http.createServer((req, res) => {
  const p = path.join(SITE, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!p.startsWith(SITE) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const port = server.address().port;

const browser = await launchBrowser();
const page = await browser.newPage();
page.on('pageerror', (e) => console.error('page error', e.message));
await page.goto(`http://localhost:${port}/tools/render.html`);
await page.waitForFunction(() => window.ready);

const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-');
const save = async (name, opts) => {
  const data = await page.evaluate((o) => window.renderCar(o), opts);
  fs.writeFileSync(path.join(OUT, name), Buffer.from(data.split(',')[1], 'base64'));
};
for (const car of cars) {
  const url = `/build/glb/${car.id}.glb`;
  for (const c of colors) {
    const base = { url, size: 2000, color: c.hex, metal: c.metal, rough: c.rough, chain: false, angle: 0 };
    await save(`${car.id}__${slug(c.name)}__front.png`, { ...base, bg: null });
    await save(`${car.id}__${slug(c.name)}__front-white.png`, { ...base, bg: '#ffffff' });
    // angled view with ring and chain, in every body color, so the gallery follows the swatch
    await save(`${car.id}__${slug(c.name)}__angle.png`, { ...base, chain: true, angle: -0.45, bg: null });
  }
  const w = launch.colors[0];
  // back view: carbon-fibre finish and lettering (the black base, so one render covers every body color)
  await save(`${car.id}__white__back.png`, { url, size: 2000, color: w.hex, metal: w.metal, rough: w.rough, chain: true, angle: Math.PI - 0.32, bg: null });
  if (car.id === 'g80_m3') {   // detail tour: the back seen straight on
    await save(`${car.id}__white__back-straight.png`, { url, size: 2000, color: w.hex, metal: w.metal, rough: w.rough, chain: true, angle: Math.PI, bg: null });
  }
  if (car.id === 'g80_m3') {   // hero static end state: front view hanging from its chain
    await save(`${car.id}__white__front-chain.png`, { url, size: 2000, color: w.hex, metal: w.metal, rough: w.rough, chain: true, angle: 0, bg: null });
  }
  console.log('rendered', car.id);
}
await browser.close();
server.close();
