// Screenshot each ad HTML at its exact size (run from site/ so playwright resolves). Called by make_ads.py.
import { launch } from '../site/tools/browser.mjs';

const jobs = JSON.parse(process.argv[2]);
const browser = await launch();
for (const j of jobs) {
  const p = await browser.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: 1 });
  await p.goto(j.html, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: j.png });
  await p.close();
  console.log(j.png);
}
await browser.close();
