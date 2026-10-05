// Compress site/build/glb_raw/*.glb -> site/build/glb/*.glb with KHR_mesh_quantization (+ dedup, vertex reorder).
// No meshopt/Draco: those need a decoder script, and Shopify's own model-viewer and AR viewers must open the file as is.
// Quantized files land at 550-750 KB, under the 1 MB target.
// usage: node tools/compress_glb.mjs [id,id,...]   (run from site/)
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, quantize, reorder, weld, simplify } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder, MeshoptSimplifier } from 'meshoptimizer';
import fs from 'node:fs';
import path from 'node:path';

const RAW = path.resolve('build/glb_raw');
const OUT = path.resolve('build/glb');
fs.mkdirSync(OUT, { recursive: true });
await MeshoptEncoder.ready;
await MeshoptDecoder.ready;
await MeshoptSimplifier.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.encoder': MeshoptEncoder,
  'meshopt.decoder': MeshoptDecoder,
});

const only = process.argv[2] ? process.argv[2].split(',') : null;
const files = fs.readdirSync(RAW).filter((f) => f.endsWith('.glb') && (!only || only.includes(f.slice(0, -4))));
for (const f of files) {
  // the big wall key holders (fine hooks, stepped countersinks) get a geometry-preserving simplify until under 1 MB;
  // the full-detail raw file is still what Blender renders
  let kb = 0;
  for (const ratio of [1, 0.5, 0.33, 0.22, 0.15, 0.1]) {
    const doc = await io.read(path.join(RAW, f));
    const steps = [dedup(), prune()];
    if (ratio < 1) steps.push(weld(), simplify({ simplifier: MeshoptSimplifier, ratio, error: ratio < 0.15 ? 0.0008 : 0.0004 }));
    steps.push(reorder({ encoder: MeshoptEncoder }), quantize({ quantizePosition: 14, quantizeNormal: 8 }));
    await doc.transform(...steps);
    const out = path.join(OUT, f);
    await io.write(out, doc);
    kb = Math.round(fs.statSync(out).size / 1024);
    if (kb <= 1024) { console.log(f, kb, 'KB', ratio < 1 ? `ok (simplified, ratio ${ratio})` : 'ok'); break; }
  }
  if (kb > 1024) console.log(f, kb, 'KB', 'OVER 1 MB');
}
