export const meta = {
  name: 'car-keychains-next',
  description: 'Next batch of car keychains: trace or resume, critique, up to 2 revision rounds, then art-director pass',
  phases: [
    { title: 'Trace', detail: 'one agent per car: reference photo -> spec -> builds' },
    { title: 'Critique', detail: 'two independent critics per car per round (likeness, style+printability)' },
    { title: 'Revise', detail: 'apply critique fixes, rebuild' },
    { title: 'Consistency', detail: 'line-up review across all cars + targeted fixes' },
  ],
}

const SP = args.sp
const CARS = args.cars
const KC = SP + '/kc'
// args.cloud: Linux container without Creality Print. Full builds skip the slicer and render on the Xvfb display :99.
const BUILD = args.cloud ? 'DISPLAY=:99 python kc/lib/export.py' : 'python kc/lib/export.py'
const NOSLICE = args.cloud ? ' --no-slice' : ''
const CLOUD_NOTE = args.cloud ? `
- CLOUD RUN: there is no slicer here. Every FULL build is \`DISPLAY=:99 python kc/lib/export.py <spec> <out> --no-slice\`
  (the 3D renders need DISPLAY=:99). build_report.json then has no slicecheck: report slicecheck_all_ok = true when the
  full build finishes with 0 design errors; the user re-checks on their PC with the real slicer.` : ''

const COMMON = `
WORKING CONTEXT
- Scratchpad root (run all commands from here): ${SP}
- Pipeline library (READ-ONLY for you, never edit): ${KC}/lib   (geom.py, build3d.py, export.py, render.py, trace_tools.py, slicecheck.py)
- Spec guide - READ IT FULLY FIRST: ${KC}/cars/README_SPEC.md
- Style references (look at every one of them with the Read tool before designing): ${KC}/style/
    g80_reference_photo_the_user_traced.png, g80_user_keychain_fusion_screenshot.png, g80_user_keychain_iso.png,
    g80_face_flat.png, g80_production_render.png, g80_classic_render.png
- A rough px-format example spec: ${KC}/cars/_example_g80_px/spec.py (format demo only; the real quality bar is g80_face_flat.png)
- Python 3.11 with shapely, numpy, PIL, cv2, requests is available. Use the Bash tool. Paths contain no spaces.${CLOUD_NOTE}
- Only touch files inside your own car folder ${KC}/cars/<id>/ . Do not install packages. Do not edit kc/lib or other cars.
- Printer: Creality K2, 0.4 mm nozzle, two colours (black + white) - the pipeline handles slicer settings.

THE PRODUCT
The user designed a BMW M3 (G80) front keychain (their photo-trace -> Fusion 360). We are making the same keychain for
other cars so the set looks like one product line. Two builds are generated automatically from ONE 2D design:
  * production "1-swap": black base + white cap, black details recessed 1.4 mm (1 filament change per plate)
  * classic: flush full-depth inlays exactly like the user's G80
You design the 2D artwork (spec.py); the pipeline does the rest.
`

function tracePrompt(car) {
  return `${COMMON}
YOUR CAR: ${car.name}   (folder id: ${car.id})
Brief: ${car.brief}

TASK - produce an excellent, faithful, printable keychain design for this car.
1. REFERENCE PHOTO. Find a straight-on FRONT photo of exactly this model/generation (camera centred on the car, level,
   roughly headlight height or slightly above, little perspective, sharp, >= 1000 px wide, ideally no heavy watermark).
   Search with WebSearch/WebFetch (Wikimedia Commons is a good source - its API gives direct image URLs and licences;
   manufacturer press sites and reviews are fine too). The user has approved downloading reference photos:
   download image files only (no executables), each < 8 MB, with Python requests and a browser-like User-Agent header,
   into ${KC}/cars/${car.id}/ref/ . You may download a few candidates and pick the best; record the source URL
   and licence of the chosen one. If the best photo is slightly tilted, level it (trace_tools.py rotate) and trace the
   levelled copy. Confirm (by looking at it) that it really is the right generation/facelift.
2. STUDY. View the photo at full size and zoomed crops. Write down the car's signature front elements (headlight
   outline + DRL graphic, grille shape + texture, intakes, splitter, vents, creases/shut lines) and decide, the
   way the user did for the G80, what becomes black, what stays white, what becomes a white DRL stroke, where relief
   patterns and engraved lines go, and where the keyring tab sits (viewer's left, on a white area of the fender).
   NO LOGOS (user rule): no badge, emblem, crest or brand lettering anywhere; badge=None, no SHOW_BADGE prims, leave
   that spot as plain body or plain grille.
3. TRACE. Use kc/lib/trace_tools.py (grid / edges / points, with --crop and --scale to zoom; labels are original
   photo pixels) to read precise coordinates. Write ${KC}/cars/${car.id}/spec.py. Iterate many times with
     python kc/lib/export.py kc/cars/${car.id}/spec.py kc/cars/${car.id}/out --design-only
   and LOOK at out/overlay.png (your design drawn on the photo - edges must sit on the real edges) and out/face.png
   after every change. Keep it symmetric, clean and simplified like the G80 (few, well-placed points; smooth curves via
   'smooth'). Get the proportions right: silhouette, headlight size/angle/position, grille size/shape, intake shapes.
   The DRL light signature must be recognisable at a glance - it is what makes a modern car identifiable.
4. PRINTABILITY. 0 design errors before auto-repair is the target (>= 0.5 mm features and gaps). Use strokes of
   width 0.6-0.8 mm for DRL lines, 0.5-0.6 mm for grooves.
5. FULL BUILD. ${BUILD} kc/cars/${car.id}/spec.py kc/cars/${car.id}/out${NOSLICE}
   (Several cars build in parallel on this PC, so the full build is slow: iterate with --design-only and run the full build
   at most 3 times in total, when the 2D design is essentially final.)
   Look at out/production/${car.id}_production_render.png and out/classic/${car.id}_classic_render.png. Read
   out/build_report.json: every slicecheck part must have status ok, n_lost 0, top_layer_coverage >= 0.9.
6. SELF-REVIEW against the style guide: compose a side-by-side with
     python -c "import sys; sys.path.insert(0,'kc/lib'); import render; render.side_by_side(['kc/style/g80_face_flat.png','kc/cars/${car.id}/out/face.png'],'kc/cars/${car.id}/out/vs_g80.png',['G80 (user)','${car.id}'])"
   and view it: same level of detail, same visual weight of black vs white, similar line weights, same kind of tab.
   Fix anything that looks off, rebuild, and look again. Iterate until you would be proud to sell it next to the G80.

Return the structured result. spec_path/ref_path must be absolute paths. In notes, list the design decisions
(what is black/white/relief/grooves and why) and anything you could not do.`
}

const RESULT_SCHEMA = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    spec_path: { type: 'string' },
    ref_path: { type: 'string' },
    ref_url: { type: 'string' },
    ref_license: { type: 'string' },
    size_mm: { type: 'array', items: { type: 'number' } },
    design_errors_before_repair: { type: 'number' },
    design_errors_after_repair: { type: 'number' },
    slicecheck_all_ok: { type: 'boolean' },
    plate_count: { type: 'number' },
    signature_features: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['id', 'spec_path', 'ref_path', 'size_mm', 'slicecheck_all_ok', 'notes'],
}

const CRIT_SCHEMA = {
  type: 'object',
  properties: {
    score: { type: 'number', description: '1-10' },
    pass: { type: 'boolean' },
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          element: { type: 'string' },
          problem: { type: 'string' },
          fix: { type: 'string', description: 'concrete instruction, with px or mm positions where possible' },
        },
        required: ['severity', 'element', 'problem', 'fix'],
      },
    },
    summary: { type: 'string' },
  },
  required: ['score', 'pass', 'issues', 'summary'],
}

function filesFor(car, r) {
  const o = `${KC}/cars/${car.id}/out`
  return `Files (view every image with the Read tool):
- reference photo: ${r.ref_path}
- design painted back on the photo: ${o}/overlay.png
- flat keychain face: ${o}/face.png
- 3D renders: ${o}/production/${car.id}_production_render.png and ${o}/classic/${car.id}_classic_render.png
- side by side with the user's G80: ${o}/vs_g80.png (if missing, compare with ${KC}/style/g80_face_flat.png)
- reports: ${o}/design_report.json, ${o}/build_report.json
- spec: ${r.spec_path}
- style guide: ${KC}/cars/README_SPEC.md and ${KC}/style/*.png (the user's own G80 keychain is the reference)`
}

function likenessPrompt(car, r, round) {
  return `You are an adversarial automotive-design critic (round ${round}). A 2-colour keychain of the front of the
${car.name} was traced from a reference photo. Your job: find EVERYTHING that makes it not read instantly as this exact
car. Be concrete and demanding - a car enthusiast must recognise the model and generation at a glance.
Brief given to the designer: ${car.brief}
${filesFor(car, r)}

Check, comparing against the photo (overlay.png shows the design edges drawn on it) and your knowledge of the car:
silhouette proportions (width:height, hood/fender line, bumper corners), headlight outline size/angle/position, the
DRL light signature shape (most important), grille shape/size/position and its texture pattern, intake shapes, splitter,
vents, any logo (there must be NONE: no badge, emblem, crest or brand lettering - user rule), missing signature elements, wrong generation cues, asymmetry or misalignment with the photo.
Each issue needs a concrete fix (which primitive, which direction, approx px or mm). Score 1-10 for likeness.
pass = score >= 8 and no 'high' issues. Do not edit any files.`
}

function stylePrompt(car, r, round) {
  return `You are an adversarial product-design and 3D-printing reviewer (round ${round}). The user designed a BMW M3 G80 front
keychain; new keychains must look like the same product line and print perfectly on a Creality K2 (0.4 mm nozzle,
2 colours). You are reviewing the ${car.name} one. Find everything inconsistent with the G80 style or risky to print.
${filesFor(car, r)}
Also read ${KC}/cars/README_SPEC.md (design language section) and look at ${KC}/style/g80_user_keychain_fusion_screenshot.png.

Check: level of detail vs the G80 (too busy / too sparse), black vs white balance, line weights (DRL strokes, grooves),
relief pattern scale (ribs/gaps vs the G80 slats), use of grooves (2-6 key lines), keyring tab position (viewer's left,
on white fender area, ~mid height) and strength, outline crop (hood to windshield base, no mirrors/tyres/windshield),
clean simplified shapes (no jagged traced noise), symmetry. Printability: design_report errors, build_report slicecheck
(n_lost must be 0, top_layer_coverage >= 0.9 for all four parts), any feature or gap < 0.5 mm, tiny isolated specks,
white islands that are too small, anything that would look bad when recessed 1.4 mm in the production build.
Each issue needs a concrete fix. Score 1-10 for style consistency + printability. pass = score >= 8, no 'high' issues
and slicecheck all ok.${args.cloud ? ' CLOUD RUN: there is no slicer here, so build_report.json has no slicecheck; judge printability from design_report.json and the renders, and do not fail the design for the missing slicecheck.' : ''} Do not edit any files.`
}

function revisePrompt(car, r, crits, round) {
  const issues = JSON.stringify(crits, null, 1)
  return `${COMMON}
YOUR CAR: ${car.name}   (folder id: ${car.id})
Brief: ${car.brief}
You are continuing the design of this keychain (revision round ${round}). Current spec: ${r.spec_path}
Reference photo: ${r.ref_path}
Designer's previous notes: ${r.notes}

Two independent critics reviewed it. Their findings (address every high and medium issue; low issues when cheap;
if you disagree with an issue after checking the photo, keep your design and explain why in notes):
${issues}

Workflow: read the spec, view the reference photo, out/overlay.png, out/face.png and the renders; apply fixes;
iterate with --design-only (look at overlay.png + face.png every time); then run the full build
  ${BUILD} kc/cars/${car.id}/spec.py kc/cars/${car.id}/out${NOSLICE}
check build_report.json (slicecheck ok, n_lost 0, top_layer_coverage >= 0.9), regenerate vs_g80.png:
  python -c "import sys; sys.path.insert(0,'kc/lib'); import render; render.side_by_side(['kc/style/g80_face_flat.png','kc/cars/${car.id}/out/face.png'],'kc/cars/${car.id}/out/vs_g80.png',['G80 (user)','${car.id}'])"
and look at everything once more. Return the structured result (absolute paths; notes = what changed + any
disagreements with the critics).`
}

async function critique(car, r, round) {
  const [a, b] = await parallel([
    () => agent(likenessPrompt(car, r, round), { label: `likeness:${car.id}:r${round}`, phase: 'Critique', schema: CRIT_SCHEMA }),
    () => agent(stylePrompt(car, r, round), { label: `style:${car.id}:r${round}`, phase: 'Critique', schema: CRIT_SCHEMA }),
  ])
  return { likeness: a, style: b }
}

function passed(c) {
  const ok = x => x && x.pass && x.score >= 8 && !(x.issues || []).some(i => i.severity === 'high')
  return ok(c.likeness) && ok(c.style)
}

const MAX_ROUNDS = args.max_rounds || 2

const traceCar = car => agent(tracePrompt(car), { label: `trace:${car.id}`, phase: 'Trace', schema: RESULT_SCHEMA })
const refineCar = async (r, car) => {
    if (!r) return { car, result: null, history: [], passed: false }
    let cur = r
    const history = []
    for (let round = 1; round <= MAX_ROUNDS; round++) {
      const c = await critique(car, cur, round)
      history.push({ round, likeness: c.likeness && { score: c.likeness.score, pass: c.likeness.pass, n: (c.likeness.issues || []).length, summary: c.likeness.summary },
                     style: c.style && { score: c.style.score, pass: c.style.pass, n: (c.style.issues || []).length, summary: c.style.summary } })
      log(`${car.id} round ${round}: likeness ${c.likeness ? c.likeness.score : '?'} / style ${c.style ? c.style.score : '?'}`)
      if (passed(c)) return { car, result: cur, history, passed: true }
      const issues = { likeness_critic: c.likeness, style_printability_critic: c.style }
      const nr = await agent(revisePrompt(car, cur, issues, round), { label: `revise:${car.id}:r${round}`, phase: 'Revise', schema: RESULT_SCHEMA })
      if (nr) cur = nr
    }
    // one last critique of the final revision so the report is truthful
    const c = await critique(car, cur, MAX_ROUNDS + 1)
    history.push({ round: MAX_ROUNDS + 1, likeness: c.likeness && { score: c.likeness.score, summary: c.likeness.summary }, style: c.style && { score: c.style.score, summary: c.style.summary } })
    return { car, result: cur, history, passed: passed(c), final_issues: { likeness: c.likeness, style: c.style } }
}
const POOL = args.pool || 5
async function runPool(items, n, fn) {
  const out = new Array(items.length); let next = 0
  async function worker() {
    while (next < items.length) {
      const i = next++
      try { out[i] = await fn(items[i], i) } catch (e) { log(`${items[i].id} failed: ${e}`); out[i] = null }
    }
  }
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, () => worker()))
  return out
}
const results = await runPool(CARS, POOL, async (car) => {
  let r = car.prev || await traceCar(car)
  if (!r) { log(`${car.id}: trace failed, retrying once`); r = await traceCar(car) }
  return await refineCar(r, car)
})

// ---------------- consistency pass across the whole line (needs all cars: barrier is intentional)
phase('Consistency')
const done = results.filter(x => x && x.result).concat(args.prev_done || [])
const specList = [KC + '/style/g80_spec_from_user_step.pkl'].concat(args.others || []).concat(done.map(x => x.result.spec_path))
const lineupCmd = `python kc/lib/lineup.py kc/lineup_all.png ${specList.map(s => '"' + s + '"').join(' ')}`
const CONS_SCHEMA = {
  type: 'object',
  properties: {
    cars_to_fix: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, fixes: { type: 'array', items: { type: 'string' } } }, required: ['id', 'fixes'] } },
    summary: { type: 'string' },
  },
  required: ['cars_to_fix', 'summary'],
}
const cons = await agent(`${COMMON}
You are the art director of this keychain product line. First run (from ${SP}):
  ${lineupCmd}
then view kc/lineup_all.png (all keychains at the same mm scale; the first one is the user's own G80 = the reference).
Also view each car's out/production/<id>_production_render.png under ${KC}/cars/<id>/ .
Judge the set AS A LINE: consistent level of detail, line weights (DRL strokes, grooves, rings), black/white balance,
relief pattern scale, tab size/position, outline crop (hood up to the windshield base, no mirrors/tyres), overall
visual weight. The other cars are FINAL; judge ONLY the NEW cars (${CARS.map(c => c.id).join(', ')}, the last ${CARS.length} keychains in the image) against the line and against the real car. Identify real problems that make it look like it is from a different product line, and give
concrete fixes per car id. An empty list is fine if the line is consistent. Do not edit files.`, { label: 'art-director', phase: 'Consistency', schema: CONS_SCHEMA })

const fixed = []
if (cons && cons.cars_to_fix && cons.cars_to_fix.length) {
  const byId = Object.fromEntries(done.map(x => [x.car.id, x]))
  const fixRuns = await parallel(cons.cars_to_fix.filter(f => byId[f.id]).map(f => () =>
    agent(revisePrompt(byId[f.id].car, byId[f.id].result, { art_director_line_consistency: f.fixes }, 'consistency'),
      { label: `consistency-fix:${f.id}`, phase: 'Consistency', schema: RESULT_SCHEMA }).then(nr => ({ id: f.id, nr }))))
  for (const fr of fixRuns.filter(Boolean)) {
    if (fr.nr) { byId[fr.id].result = fr.nr; fixed.push(fr.id) }
  }
}

return {
  cars: results.map(x => x && ({ id: x.car.id, passed: x.passed, result: x.result, history: x.history,
    final_issues: x.final_issues ? { likeness: x.final_issues.likeness && x.final_issues.likeness.issues, style: x.final_issues.style && x.final_issues.style.issues } : null })),
  consistency: cons,
  consistency_fixed: fixed,
}
