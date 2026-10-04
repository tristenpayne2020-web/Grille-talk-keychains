# Grille Talk Shopify theme

Online Store 2.0 theme for grilletalk.shop. Black and white, the keychains are the hero.
Launch catalog: 20 cars × 6 body colors. 43 more cars and 7 more colors are ready to add later
(see "Adding the rest of the line" below).

```
theme/   the Shopify theme (upload this folder)
site/    tools that build the catalog, 3D models and images, plus a local preview (not uploaded)
```

## Preview it on your PC (no store needed)

From the repo root, once:

```
cd site
npm install
```

Then:

```
node preview/server.mjs
```

Open http://localhost:4100. The preview uses mock products made from your renders and 3D models. It cannot
take orders: "Check out" stops at a page that says so.

## Preview it on Shopify (after the store exists)

```
npx @shopify/cli@4.8.4 theme dev --path theme --store YOUR-STORE.myshopify.com
```

That gives you a private preview URL. To upload without publishing:

```
npx @shopify/cli@4.8.4 theme push --unpublished --path theme --store YOUR-STORE.myshopify.com
```

Publish it from Online Store > Themes when you are ready. Nothing in this repo publishes it for you.

## Setup in Shopify admin (in this order)

1. **Store and plan.** Create the store, pick a plan, install Shopify CLI (`npx @shopify/cli@4.8.4`) and log in.
2. **Domain.** Settings > Domains > Connect existing domain > `grilletalk.shop`. In GoDaddy DNS, add the
   A record and the `www` CNAME exactly as Shopify shows. (Nobody else should change your DNS.)
3. **Payments.** Settings > Payments: activate Shopify Payments, then turn on Shop Pay.
   Checkout only works for real once this is done.
4. **Markets, taxes, shipping.** Settings > Markets (United States), Settings > Taxes and duties,
   Settings > Shipping and delivery (your rates).
5. **Policies.** Settings > Policies: refund, privacy, terms of service, shipping. The footer links to
   them automatically once they exist.
6. **Privacy.** Settings > Customer privacy: cookie banner and data sharing. The theme has no tracking
   pixels or third-party scripts; add analytics only through official Shopify apps.
7. **Email.** Settings > Notifications: sender email `tristen@grilletalk.shop`, and authenticate the domain
   for email.
8. **Metafield definitions.** Settings > Custom data > Products > Add definition, type single-line text:
   `custom.make` (Make), `custom.model` (Model), `custom.generation` (Generation),
   `custom.short_model` (Short model). Tick "Filter" on Make.
9. **Search & Discovery.** Install Shopify's free Search & Discovery app, Filters > Add filter >
   Product metafield "Make". Optionally add synonyms: Vette = Corvette, GTR = GT-R, Lambo = Lamborghini.
10. **Import products.** Build the CSV (below), then Products > Import > `site/build/shopify_products.csv`.
    Products arrive as drafts. Inventory is not tracked (made to order).
11. **Collection.** Products > Collections: the theme uses "all" by default. If you make a "Keychains"
    collection, pick it in the Range viewer section.
12. **Images and 3D models.** Run the upload script (below).
13. **Menus.** Online Store > Navigation:
    - `main-menu`: Shop (`/#range`), Catalog (`/collections/all`), Request a car, About, FAQ, Contact
    - `footer`: All keychains, Request a car, About, FAQ, Contact, Search
14. **Pages.** Online Store > Pages, with these templates: About (`page.about`), Contact (`page.contact`),
    FAQ (`page.faq`), Request a car (`page.request-a-car`, handle `request-a-car`). Then in the theme editor >
    Theme settings > Business, pick the Request a car page.
15. **Fill in what only you know** (theme editor):
    - Theme settings > Product facts: production time, shipping note (hidden until filled in)
    - Home > FAQ: answers for production time, shipping, returns, car clubs (questions stay hidden until
      answered)
    - About: the G80 story in your own words
16. **Publish the products** (Products > select > Set as active), then publish the theme.

## Building the catalog, images and 3D models

Everything writes to `site/build/` (gitignored). From the repo root:

```
pip install -r requirements.txt
cd site
npm install
cd ..
python site/tools/build_geometry.py
python site/tools/make_glb.py
python site/tools/make_svgs.py
cd site
node tools/compress_glb.mjs
node tools/make_images.mjs
cd ..
python site/tools/make_media.py
python site/tools/make_brand.py
python site/tools/make_hero_assets.py
python site/tools/make_csv.py
```

- `build_geometry.py` rebuilds each car with `KC_BADGE=0` (logo-free) into `site/build/geom/`.
  It never touches `kc/cars/*/out/` or any spec.
- `make_glb.py` makes one GLB per car: materials `body`, `lights` (always white) and `details` (black),
  plus a split ring and 5-link chain at the keyring hole as separate nodes.
- `compress_glb.mjs` quantizes them to 340-740 KB with no decoder needed.
- `make_images.mjs` renders every car in every color (needs Chrome installed).
- Reference photos in `kc/cars/*/ref/` are never used.

### Upload images and 3D models

Shopify can't import 3D models from a CSV, so this script uploads them through the Admin API.

1. Shopify admin > Settings > Apps and sales channels > Develop apps > Create an app.
2. Admin API scopes: `write_products`, `read_products`, `write_files`. Install it and copy the
   Admin API access token.
3. Create a file `.env` in the repo root (it is gitignored, never commit it):

   ```
   SHOPIFY_STORE=your-store.myshopify.com
   SHOPIFY_ADMIN_TOKEN=paste-the-token-here
   ```

4. Check what will be uploaded, then upload:

   ```
   python site/tools/upload_media.py --dry-run
   python site/tools/upload_media.py
   ```

It is safe to run again: media already on a product is skipped. Each color's render is linked to its variant.

## Checks

```
cd site
node preview/server.mjs
```

In a second terminal:

```
cd site
node tools/audit.mjs
npx @shopify/cli@4.8.4 theme check --path ../theme
```

Results land in `site/build/reports/`.

## Adding the rest of the line later

- **More cars:** add rows to `site/catalog/launch.json` (ids from `kc/cars_pkg.json`, plus make, model,
  generation, short_model, aliases), rerun the build steps and the CSV, import, then run the upload script.
- **More colors:** add them to `colors` in `launch.json` (name, tier, hex, metal, rough). Then update Theme
  settings > Body colors (tiers and swatches) so they group correctly.
- The 7 colors still to add are Green, Purple, Gold, Metallic Red, Metallic Blue, Metallic Green and
  Metallic Purple. Their tier prices are $7.99 (custom) and $8.99 (metallic).
- Then change "40+ more cars coming soon" in the Range viewer and Catalog sections.

## Notes

- Prices live only in Shopify variants (and `launch.json`, which feeds the CSV). The theme never hardcodes them.
- Double purchase protection: Add to cart and Check out lock on the first click until the request settles.
  Shopify checkout itself never charges a checkout twice and shows its own order confirmation page, so the
  theme has no custom thank-you page.
- Customer accounts use Shopify's new customer accounts (no theme templates needed).
- Fonts: Michroma (SIL Open Font License) for headings, the system sans for text.
- Vendored libraries are bundled into `assets/vendor-three.js` (three.js, MIT) and `assets/vendor-gsap.js`
  (GSAP, standard no-charge license) by `site/tools/bundle_vendor.mjs` from pinned npm versions.
