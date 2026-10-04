// Bundle pinned vendor code into theme/assets (run from site/): three.js subset and GSAP core.
import { build } from 'esbuild';
import fs from 'node:fs';
const banner = { js: '/* Bundled by site/tools/bundle_vendor.mjs. three.js (MIT) and GSAP (standard no-charge license). Do not edit. */' };
await build({ entryPoints: ['tools/vendor_entry_three.js'], bundle: true, format: 'esm', minify: true, target: 'es2020', outfile: '../theme/assets/vendor-three.js', banner, legalComments: 'none' });
fs.writeFileSync('tools/vendor_entry_gsap.js', "export { gsap } from 'gsap';\n");
await build({ entryPoints: ['tools/vendor_entry_gsap.js'], bundle: true, format: 'esm', minify: true, target: 'es2020', outfile: '../theme/assets/vendor-gsap.js', banner, legalComments: 'none' });
fs.copyFileSync('node_modules/@fontsource/michroma/files/michroma-latin-400-normal.woff2', '../theme/assets/michroma-latin-400.woff2');
for (const f of fs.readdirSync('../theme/assets').filter((f) => f.startsWith('vendor-') || f.endsWith('.woff2'))) console.log(f, Math.round(fs.statSync('../theme/assets/' + f).size / 1024), 'KB');
