// Product page: body color swatches drive the variant id, price, URL, variant image and the 3D body material.
const root = document.querySelector('[data-product]');

if (root) {
  const data = JSON.parse(document.querySelector('[data-product-json]').textContent);
  const form = root.querySelector('form[data-product-form]');
  const idInput = form.querySelector('[data-variant-id]');
  const price = root.querySelector('[data-price]');
  const nameOut = root.querySelector('[data-color-name]');
  const addBtn = form.querySelector('[type="submit"]');
  const varImg = root.querySelector('[data-variant-image]');
  const viewerBox = root.querySelector('[data-viewer]');
  const mv = viewerBox && viewerBox.querySelector('model-viewer');

  // model-viewer: Shopify loads it on the live store; the local preview serves the pinned npm build.
  if (mv) {
    const ready = () => viewerBox.classList.add('is-ready');
    mv.addEventListener('load', () => { ready(); paint(); });
    mv.addEventListener('error', ready);
    if (!customElements.get('model-viewer')) {
      if (window.Shopify && window.Shopify.loadFeatures) {
        window.Shopify.loadFeatures([{ name: 'model-viewer-ui', version: '1.0', onLoad: (err) => { if (err) ready(); } }]);
      } else if (window.__PREVIEW__) {
        const s = document.createElement('script');
        s.type = 'module';
        s.src = '/vendor/model-viewer.min.js';
        document.head.append(s);
      } else {
        ready();
      }
    }
    setTimeout(ready, 8000);   // never leave a skeleton forever
  }

  const current = () => form.querySelector('.swatch input:checked');

  function paint() {
    const sw = current();
    if (!mv || !sw || !mv.model) return;
    const body = mv.model.materials.find((m) => m.name === 'body');
    if (!body) return;
    const pbr = body.pbrMetallicRoughness;
    pbr.setBaseColorFactor(sw.dataset.hex);
    pbr.setMetallicFactor(Number(sw.dataset.metal) || 0);
    pbr.setRoughnessFactor(Number(sw.dataset.rough) || 0.6);
  }

  function update() {
    const sw = current();
    if (!sw) return;
    const v = data.variants.find((x) => String(x.id) === sw.dataset.variant);
    if (!v) return;
    idInput.value = v.id;
    price.textContent = v.price;
    if (nameOut) nameOut.textContent = v.option1;
    addBtn.disabled = !v.available;
    addBtn.querySelector('.btn__label').textContent = v.available ? data.strings.addToCart : data.strings.soldOut;
    if (varImg && v.image) { varImg.removeAttribute('srcset'); varImg.src = v.image; varImg.alt = v.imageAlt || ''; }
    const url = new URL(window.location.href);
    url.searchParams.set('variant', v.id);
    window.history.replaceState({}, '', url);
    paint();
  }

  form.addEventListener('change', (e) => { if (e.target.closest('.swatch')) update(); });
  form.addEventListener('click', (e) => {
    const step = e.target.closest('[data-step]');
    if (!step) return;
    const q = form.querySelector('input[name="quantity"]');
    q.value = Math.min(99, Math.max(1, (Number(q.value) || 1) + Number(step.dataset.step)));
  });
}
