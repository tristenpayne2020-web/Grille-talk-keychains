# Master prompt: Grille Talk Shopify storefront

Paste everything below the line into a new Claude Code session opened on this repository
(`tristenpayne2020-web/Grille-talk-keychains`, branch `claude/exciting-pascal-4qpm9o` or `main` after merge).

---

You are a senior Shopify developer, Liquid specialist and e-commerce compliance consultant. Build a complete,
production-quality Shopify Online Store 2.0 theme for **Grille Talk** (grilletalk.shop), plus the catalog import
and 3D assets it needs. Work inside this repository. Do not stop at a plan or mockup: build it, preview it, check
it, fix what you find.

## 0. Before you start

1. Load these skills if they exist in this session, before any design or code work:
   `/design-taste-skill-pack`, `/ui-ux-pro-max`, `/frontend-design`, `/ckm:ui-styling`, `/seo`, `/seo-ecommerce`,
   `/marketing:seo-audit`, `/ai-security`, `/security-review`, `/blender-3d-modeling`, `/image`,
   `/adobe-for-creativity:adobe`, `/context-optimization`, `/using-superpowers`, `/claude-mem:ccs-align`.
   Tell me in one line which ones were missing and carry on without them.
2. Read `handoff.md` (sections 1, 2, 5, 6, 7) and `kc/cars/README_SPEC.md`. They explain the keychain pipeline.
3. Look at every file in `brand/` with the Read tool. Watch `brand/reference/hero_concept.mp4` by extracting
   frames (ffmpeg, about 1 frame per second) and viewing them.
4. If you have browser or web access, look at https://www.ciaoenergy.com/ for pacing only (see section 4).
5. Report in a few lines what you found and your approach, then build. Give short progress updates. Make routine,
   reversible decisions yourself. Ask me only if a missing decision would change the build or block a real purchase.

## 1. The business (facts you may use)

- Grille Talk makes 3D-printed keychains of real car fronts: a simplified but recognisable straight-on view with the
  details enthusiasts notice (light signature, grille texture, intakes, body lines).
- The line started with the owner's BMW M3 (G80), traced from a photo; it set the style for every other car.
- Core line: "We turn the car you love into the keychain you carry."
- Audience: car enthusiasts, car clubs, and people buying a gift for one.
- Every keychain: 80.5 mm wide, 3 mm thick, keyring tab on the left, printed in two colours.
  Ships with a split ring and a short chain.
- **No logos.** No car carries a manufacturer badge (owner's decision, for trademark reasons).
- Contact: email `tristen@grilletalk.shop` (mailto link), phone `229-947-3742` (tel link `+12299473742`).
  No social links, no street address on the site.
- US business, prices in USD.

Facts you must **not** invent: reviews, testimonials, customer counts, production times, shipping prices or speeds,
return windows, stock levels, awards, press, affiliations. Where a page needs one of these, use the matching Shopify
policy or a section setting left empty, and list it in your final report for me to fill in.

## 2. Products and pricing (source of truth)

- Catalog: `kc/cars_pkg.json`, 63 finished and approved designs (`id`, `folder`, `name`, `spec`, `out`). All are
  logo-free (`KC_BADGE=0` is the pipeline default). Nothing else is for sale. Do not list `jeep_wrangler` or any car
  not in that file.
- Two of the 63 are variants of others: `g80_m3_snakeeye` and `g87_m2_snakeeye` (snake-eye DRL versions).
- Option **Body color** (the body changes; lights and black details stay as designed). 13 values:

  | Tier | Values | Price |
  |---|---|---|
  | Standard | White | $6.99 |
  | Custom color (+$1) | Red, Yellow, Blue, Gray, Green, Purple | $7.99 |
  | Metallic (+$2) | Silver, Gold, Metallic Red, Metallic Blue, Metallic Green, Metallic Purple | $8.99 |

  Prices live in Shopify variants only, never in theme code. Inventory: do not track stock (made to order) unless
  I say otherwise; never show stock counts or "only X left".
- Do not show meet-only or wholesale prices anywhere.

### Product naming (legal, see section 3)
- Title pattern: `Inspired by the <Make> <Model> (<Generation>)`, e.g. "Inspired by the BMW M3 (G80)".
  Snake-eye: "Inspired by the BMW M3 (G80), snake-eye lights".
- Short line on cards: "For <Model> owners" (e.g. "For M3 owners").
- Never "BMW M3 keychain" or anything that reads as an official product.
- Derive make, model and generation from `name` in `cars_pkg.json` with a small mapping table you write and show me.
  Keep these as product metafields (`custom.make`, `custom.model`, `custom.generation`) and a `make:<Make>` tag.

## 3. Legal and IP rules (avoid cease-and-desist exposure)

No site can be made immune to legal complaints, but follow every rule below and tell me where risk remains.
- No manufacturer logos, emblems, badge shapes, wordmarks, model-name lettering styles or brand fonts anywhere:
  products, renders, 3D models, filters, icons, favicon, social images.
- Car makes and models appear only as plain text, to identify which car a design is based on (nominative use):
  titles, filters, search.
- Site-wide notice in the footer and on the About page: "Grille Talk is an independent maker. We are not affiliated
  with, endorsed by or sponsored by any vehicle manufacturer. Make and model names are used only to identify the car
  each design is based on, and belong to their owners."
- Do not use manufacturer photos on the site. The reference photos in `kc/cars/*/ref/` were for tracing only: never
  publish them.
- Ciao Energy is a pacing reference only. Copy nothing: no wording, layout, graphics, code or assets.
- In your final report, tell me that some grille shapes are registered trademarks (for example BMW's kidney grille),
  that this cannot be fully engineered away in code, and that a short review by an IP attorney before launch is wise.

## 4. Design direction

- Feel: a curated automotive collectible brand. Confident, graphic, tactile, product first. The keychains are the
  hero; everything else supports seeing them clearly and buying one.
- Palette: black and white. Accent only if the brand files justify one (they currently don't).
- Brand files (use as supplied, do not redraw or invent a new identity):
  - `brand/logo/grille_talk_logo.webp`: the metal-texture wordmark with the grille speech-bubble mark. Use it
    selectively (hero reveal, header, footer). Make a clean transparent version and an SVG trace of the mark for the
    favicon and small sizes; keep the metal texture for large uses only.
  - `brand/logo/chain.webp`, `brand/logo/logo_with_chain.webp`: the chain and ring art.
  - `brand/concept/hero_halftone_g80.webp`: the owner's hero concept (halftone G80 front, glowing DRLs, logo,
    hanging chain). Match this mood.
  - `brand/reference/ciao_*.webp`: reference screenshots of Ciao Energy (pacing only).
  - `brand/reference/hero_concept.mp4`: the owner's video of the intended effect.
- Halftone: keep dots large enough to stay crisp at display size. No fine patterns that moiré on phones. Prefer SVG
  or CSS-generated dots over raster halftone.
- Pacing from Ciao Energy, made original: an immediate hero, a guided way to move through the range, clear benefits,
  FAQ, newsletter/contact.
- Banned "vibe-coded" tells: purple or blue-to-purple gradients; aurora or neon glow backgrounds; nested cards on
  cards; the beige/gray rounded-card drop-shadow look; emojis as icons; carousels that don't move; dead icons or
  toggles; missing loading, empty and error states; generic "Something went wrong" errors; jittery or decorative motion;
  hero copy like "Create without limits"; em dashes in copy; fake testimonials or stock faces.
- Copy voice: enthusiast to enthusiast, specific and a little playful. Talk about the car details (light signature,
  grille texture, intakes). Short declarative sentences. No em dashes. No filler.
- Motion: purposeful and quick, GPU-friendly transforms only, respects `prefers-reduced-motion`, and the site works
  fully without JavaScript animation.

## 5. Experience

### Hero (home page, first visit)
1. Screen starts black.
2. The G80's two DRL signatures light up (draw them from the real G80 design geometry, see section 6).
3. The Grille Talk logo reveals.
4. The logo transitions into the 3D G80 keychain (logo-free) hanging from its chain and split ring.
5. Below it, two clear buttons: **Shop** (goes to the range viewer) and **Search** (opens search with focus in the
   input).
- Total under about 3 seconds. A visible "Skip" control. Plays once per session (sessionStorage, wrapped in
  try/catch). Reduced motion or no JS: show the final state immediately.
- The first screen must say, without scrolling: these are detailed keychains of real car fronts; find your own car or
  browse a dream car; pick a body color; shop now.

### Shop: range viewer
- One keychain at a time in 3D (or its render on devices without WebGL), hanging from the chain, with previous/next
  arrows at the sides, swipe on touch, arrow keys on keyboard, and a position indicator. Shows the "Inspired by"
  name, "For <Model> owners", the From price, and a "View" button to the product page.
- Below or beside it: link to the full catalog grid.

### Catalog (collection page)
- Grid of all 63 with product renders. Filters only on fields that exist (make via tag or metafield, using Shopify's
  native Search & Discovery filters). Sort (featured, A-Z, price). Real empty state when filters match nothing.

### Search
- Shopify predictive search (`/search/suggest`), keyboard navigable, with loading, empty ("No match for X. Request it")
  and error states. Searching a model name (M3, Supra, Corvette) must find the right designs.

### Product page
- 3D model (Shopify `model_viewer_tag`) plus renders. Body color swatches grouped by tier with the price shown;
  choosing a color updates the variant, price, URL and the 3D model's body material color (model-viewer material API).
- Clear add-to-cart, plus the Shop Pay / dynamic checkout button (`{{ form | payment_button }}`).
- Facts: 80.5 mm wide, 3 mm thick, two-colour print, split ring and short chain included, logo-free design.
  Production time and shipping only if I have filled them in.

### Cart
- Cart drawer and `/cart` page using the Cart AJAX API: quantity change, remove, totals, real error messages from the
  API, empty state, checkout button to Shopify checkout. Never simulate checkout.

### Request a car
- "Don't see your car?" page and links from search empty state and catalog. Native `{% form 'contact' %}` with make,
  model, year/generation, optional photo link, email. Success and error messages. No price or time promised.

### Supporting pages
- About (the G80 origin story in the owner's words where available; the legal notice), Contact (email, phone, contact
  form), FAQ (section blocks; only questions you can answer from the facts above, the rest left as empty blocks for me),
  newsletter signup (`{% form 'customer' %}` with tags `newsletter`), Shipping/Returns/Privacy/Terms through Shopify
  policy pages (`shop.policies`), custom 404 with search and shop links.

## 6. Assets pipeline (in this repo, under `site/` or `theme/tools/`)

1. Rebuild every car's geometry (outputs are gitignored): `python kc/lib/export.py kc/<spec> kc/cars/<id>/out --no-slice`
   for each entry in `kc/cars_pkg.json` (specs paths are relative to `kc/`; the G80 spec is
   `kc/cars/g80_m3/spec_from_step.pkl`). Renders need a display: run `Xvfb :99 &` and set `DISPLAY=:99`.
   Install with `pip install -r requirements.txt`.
2. GLB per car: from `out/production/<id>_production_black.stl` and `_white.stl`, export a GLB with two materials
   named `body` (white, PBR, slightly satin) and `details` (black). Add the split ring and a short chain hanging from
   the 4.5 mm tab hole (model them once in Blender or trimesh, place them at the hole centre from
   `geom.build_maps(spec)['tab_center']`). Apply Draco or meshopt compression. Target under about 1 MB each.
   Check three cars by rendering the GLB and viewing it before converting all 63.
3. Images: production renders and flat faces (`out/face.png`) converted to compressed WebP at 2-3 sizes; product
   images get alt text like "Grille Talk keychain inspired by the BMW M3 (G80), white body, front view".
4. SVGs from the 2D design maps (`geom.build_maps`): outline, black and white layers per car. Use the G80's white DRL
   layer for the hero light-up and as clean halftone source art.
5. Product import CSV in Shopify's product CSV format: one product per car, 13 variants (section 2), metafields and
   tags, image and SEO title/description per product. Shopify does not import 3D models by CSV: give me a script using
   the Admin GraphQL API (`stagedUploadsCreate` + `productCreateMedia`) that I run with my own token from an
   environment variable, or clear manual steps.

## 7. Theme architecture rules

- Shopify OS 2.0: JSON templates, sections with valid `{% schema %}`, blocks, snippets. Run `shopify theme check`
  with zero errors.
- No hardcoded prices, product titles or store copy: everything editable via section settings, JSON templates,
  metafields or Shopify data.
- Native forms only (`contact`, `customer`, `product`), for CSRF and spam handling.
- Images: `image_url` with widths + `image_tag` with `loading: 'lazy'` (eager only for the hero), explicit sizes.
- Vanilla ES modules, no jQuery, no heavy frameworks. Inline SVG icons (Lucide-style) with `aria-hidden="true"`.
- Accessibility (WCAG 2.1 AA): semantic landmarks, keyboard-operable drawers, menus, carousel and swatches; focus
  trap and Escape in drawers; visible focus; 4.5:1 text contrast; `aria-live` for cart and form messages.
- Privacy: no tracking pixels or third-party scripts in theme code. Point me to Settings > Customer privacy and
  official apps instead.
- Security: no API keys, tokens or secrets in the repo (use env vars and `.env` in `.gitignore`); escape all output;
  no `eval` or inline event handlers; dependencies pinned.
- SEO: unique `<title>` and meta description per template, canonical URLs, Open Graph and Twitter tags with a real
  share image, Product JSON-LD (no review markup), sitemap via Shopify, descriptive URLs.

## 8. Quality gates

1. Build the home page first. Render it at 1440 px and 390 px wide (Playwright with Chromium is installed; use
   `shopify theme dev` for the preview). Review it against this brief, name the three biggest visual or usability
   problems, fix them, then build the rest in the same design system.
2. Before finishing, check and fix: no horizontal scroll at 320-1920 px; no broken links or dead buttons; mobile menu
   works; favicon; page titles; meta descriptions; OG tags; footer links; 404; copyright year from `{{ 'now' | date: '%Y' }}`;
   compressed images; success and error messages on every form; clickable logo, phone and email; no placeholder or
   lorem text; no unused nav items.
3. Run `shopify theme check`, Lighthouse (mobile) and axe on home, collection, product and cart. Report scores.
4. Run the security review skill on the final diff.

## 9. Setup I must do in Shopify admin (put this list in your final report and in `theme/README.md`)

- Create the store and pick a plan; install Shopify CLI and log in.
- Domains: connect `grilletalk.shop` from GoDaddy (Settings > Domains; A record and `www` CNAME as Shopify shows).
  Do not change DNS yourself.
- Payments: activate Shopify Payments, then enable Shop Pay (Settings > Payments).
- Markets (US), taxes (Settings > Taxes and duties), shipping rates (Settings > Shipping and delivery).
- Policies: refund, privacy, terms, shipping (Settings > Policies).
- Customer privacy and cookie banner (Settings > Customer privacy).
- Sender email `tristen@grilletalk.shop` (Settings > Notifications) and domain email setup.
- Search & Discovery app for filters; metafield definitions for make, model, generation.
- Import the product CSV, then run the 3D model upload script.

## 10. Hard limits

- Never publish the theme, change DNS, buy apps or services, or create paid resources without my explicit request.
- Never collect payment details outside Shopify checkout or fake a successful order.
- Do not edit `kc/cars/*/spec_APPROVED_by_user.py` or any car design.
- Commit to a feature branch and push; do not open a pull request unless I ask.

## 11. Final report

- Preview link (unpublished theme or `theme dev` URL) and how to run it.
- What works end to end, and what needs my admin setup to go live (checkout is only live after Shopify Payments).
- Which assets and data you used (catalog file, renders, GLBs, brand files).
- Every business fact still missing (policies, production time, shipping, FAQ answers).
- Remaining legal risk notes (section 3).
