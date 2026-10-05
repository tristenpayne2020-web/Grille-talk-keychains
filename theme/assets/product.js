// Product page: body color swatches drive the variant id, price, URL, variant image and the 3D body material.
const root = document.querySelector('[data-product]');

if (root) {
  const data = JSON.parse(document.querySelector('[data-product-json]').textContent);
  const form = root.querySelector('form[data-product-form]');
  const idInput = form.querySelector('[data-variant-id]');
  const price = root.querySelector('[data-price]');
  const addBtn = form.querySelector('[type="submit"]');
  const varImg = root.querySelector('[data-variant-image]');
  const viewerBox = root.querySelector('[data-viewer]');
  const mv = viewerBox && viewerBox.querySelector('model-viewer');

  // model-viewer: Shopify loads it on the live store; the local preview serves the pinned npm build.
  if (mv) {
    const ready = () => viewerBox.classList.add('is-ready');
    mv.addEventListener('load', () => { ready(); paint(); });
    mv.addEventListener('error', () => viewerBox.classList.add('no-skeleton'));   // keep the poster image on failure
    const boot = () => {
      if (!customElements.get('model-viewer')) {
        if (window.Shopify && window.Shopify.loadFeatures) {
          window.Shopify.loadFeatures([{ name: 'model-viewer-ui', version: '1.0', onLoad: (err) => { if (err) viewerBox.classList.add('no-skeleton'); } }]);
        } else if (window.__PREVIEW__) {
          const s = document.createElement('script');
          s.type = 'module';
          s.src = '/vendor/model-viewer.min.js';
          document.head.append(s);
        } else {
          viewerBox.classList.add('no-skeleton');
        }
      }
    };
    // load the viewer after the page (desktop) or on the first touch or scroll (phones); the render image covers the wait
    import('when3d').then((m) => m.when3D()).then(boot, boot);
    setTimeout(() => viewerBox.classList.add('no-skeleton'), 8000);   // never leave a skeleton forever
  }

  const groups = [...form.querySelectorAll('fieldset[data-option-index]')];
  const picked = (i) => groups[i] && groups[i].querySelector('input:checked');
  const varAngle = root.querySelector('[data-variant-angle]');
  const swap = (img, src, alt) => { if (img && src) { img.removeAttribute('srcset'); img.src = src; if (alt != null) img.alt = alt; } };

  // body (option 1) and headlights (option 2) on the 3D model, through the model-viewer material API
  function paint() {
    if (!mv || !mv.model) return;
    const tint = (name, sw) => {
      const m = sw && sw.dataset.hex && mv.model.materials.find((x) => x.name === name);
      if (!m) return;
      const pbr = m.pbrMetallicRoughness;
      pbr.setBaseColorFactor(sw.dataset.hex);
      pbr.setMetallicFactor(Number(sw.dataset.metal) || 0);
      pbr.setRoughnessFactor(Number(sw.dataset.rough) || 0.6);
    };
    tint('body', picked(0));
    tint('lights', picked(1));
  }

  // gallery photos: tint the light signature to the chosen headlight color (the first headlight value is the standard white)
  function tintGallery() {
    const g = groups[1];
    const sw = g && g.querySelector('input:checked');
    const base = g && g.querySelector('input');
    const on = !!(sw && base && sw !== base && sw.dataset.hex);
    root.querySelectorAll('[data-lights-tint]').forEach((el) => {
      el.classList.toggle('is-on', on);
      if (on) el.style.setProperty('--tint', sw.dataset.hex);
    });
  }

  function update() {
    const values = groups.map((g, i) => picked(i) && picked(i).value);
    const v = data.variants.find((x) => x.options.every((o, i) => values[i] == null || o === values[i]));
    groups.forEach((g, i) => { const out = g.querySelector('[data-option-name]'); if (out && values[i]) out.textContent = values[i]; });
    if (!v) return;
    idInput.value = v.id;
    price.textContent = v.price;
    addBtn.disabled = !v.available;
    addBtn.querySelector('.btn__label').textContent = v.available ? data.strings.addToCart : data.strings.soldOut;
    swap(varImg, v.image, v.imageAlt || '');
    swap(varAngle, v.angle, v.angleAlt || '');
    swap(root.querySelector('[data-poster]'), v.image, null);
    const url = new URL(window.location.href);
    url.searchParams.set('variant', v.id);
    window.history.replaceState({}, '', url);
    paint();
    tintGallery();
  }

  tintGallery();
  form.addEventListener('change', (e) => { if (e.target.closest('.swatch')) update(); });
  form.addEventListener('click', (e) => {
    const step = e.target.closest('[data-step]');
    if (!step) return;
    const q = form.querySelector('input[name="quantity"]');
    q.value = Math.min(99, Math.max(1, (Number(q.value) || 1) + Number(step.dataset.step)));
  });
}
