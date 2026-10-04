// Screenshots of preview pages at several widths (preview server must be running).
// usage (from site/): node tools/shoot.mjs <path> [widths=1440,390] [--full] [--wait=ms] [--name=prefix] [--fresh]
// --fresh clears sessionStorage so the hero intro plays; otherwise the intro is marked as seen.
import fs from 'node:fs';
import { launch } from './browser.mjs';

const args = process.argv.slice(2);
const target = args.find((a) => !a.startsWith('--')) || '/';
const widths = (args.find((a, i) => i > 0 && /^\d/.test(a)) || '1440,390').split(',').map(Number);
const opt = (k, d) => (args.find((a) => a.startsWith(`--${k}=`)) || '').split('=')[1] || d;
const full = args.includes('--full');
const fresh = args.includes('--fresh');
const base = process.env.PREVIEW || 'http://localhost:4100';
const name = opt('name', target.replace(/[^a-z0-9]+/gi, '_').replace(/^_|_$/g, '') || 'home');
fs.mkdirSync('build/shots', { recursive: true });

const browser = await launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
for (const w of widths) {
  const h = w < 600 ? 844 : 900;
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1, hasTouch: w < 600, isMobile: w < 600 });
  if (!fresh) await ctx.addInitScript(() => { try { sessionStorage.setItem('gt-intro', '1'); } catch (e) {} });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(base + target, { waitUntil: 'networkidle' });
  if (full) {   // scroll through so scroll-triggered content is revealed, then back to the top
    await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 400) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); } window.scrollTo(0, 0); });
  }
  if (opt('scroll')) await page.evaluate((sel) => document.querySelector(sel)?.scrollIntoView({ block: 'start' }), opt('scroll'));
  await page.waitForTimeout(Number(opt('wait', 2500)));
  const file = `build/shots/${name}-${w}.png`;
  await page.screenshot({ path: file, fullPage: full });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  console.log(file, overflow > 0 ? `HORIZONTAL OVERFLOW ${overflow}px` : 'no overflow', errors.length ? `errors: ${errors.join(' | ')}` : '');
  await ctx.close();
}
await browser.close();
