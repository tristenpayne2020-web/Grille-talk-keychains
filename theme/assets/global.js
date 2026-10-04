// Site-wide behaviour: dialogs (menu, search, cart) with focus trap and Escape, header state, cart through the
// Cart AJAX API with a one-request-at-a-time guard, checkout lock, predictive search, reveal on scroll.
const GT = window.GT || { routes: {}, strings: {} };
const live = (msg) => { const r = document.getElementById('live-region'); if (r) { r.textContent = ''; requestAnimationFrame(() => { r.textContent = msg; }); } };

/* ---------- dialogs ---------- */
const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select, textarea, [tabindex]:not([tabindex="-1"])';
let openDialog = null;
let returnFocus = null;

function trap(e) {
  if (!openDialog) return;
  if (e.key === 'Escape') { e.preventDefault(); closeDialog(); return; }
  if (e.key !== 'Tab') return;
  const f = [...openDialog.querySelectorAll(FOCUSABLE)].filter((el) => el.offsetParent !== null);
  if (!f.length) return;
  const first = f[0], last = f[f.length - 1];
  if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
  else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
}

export function openDialogById(id, opener) {
  const d = document.getElementById(id);
  if (!d) return false;
  if (openDialog && openDialog !== d) closeDialog(false);
  returnFocus = opener || document.activeElement;
  d.hidden = false;
  d.classList.add('is-open');
  document.body.classList.add('is-locked');
  requestAnimationFrame(() => d.classList.add('is-visible'));
  openDialog = d;
  document.addEventListener('keydown', trap);
  const target = d.querySelector('input[type="search"]') || d.querySelector('[data-close]');
  setTimeout(() => target && target.focus(), 30);
  if (opener) opener.setAttribute('aria-expanded', 'true');
  return true;
}

export function closeDialog(restore = true) {
  const d = openDialog;
  if (!d) return;
  d.classList.remove('is-visible');
  openDialog = null;
  document.removeEventListener('keydown', trap);
  document.body.classList.remove('is-locked');
  const done = () => { d.classList.remove('is-open'); d.hidden = true; };
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) done(); else setTimeout(done, 320);
  if (returnFocus) { returnFocus.setAttribute?.('aria-expanded', 'false'); if (restore) returnFocus.focus?.(); }
}

document.addEventListener('click', (e) => {
  const opener = e.target.closest('[data-open]');
  if (opener) {
    if (openDialogById(opener.dataset.open, opener)) e.preventDefault();
    return;
  }
  if (e.target.closest('[data-close]')) closeDialog();
});

/* ---------- header ---------- */
const header = document.querySelector('[data-header]');
if (header) {
  const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 24);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
}

/* ---------- cart ---------- */
let cartBusy = false;

function setCount(n) {
  document.querySelectorAll('[data-cart-count]').forEach((el) => { el.dataset.count = n; el.textContent = n > 0 ? n : ''; });
}

async function errorText(res) {
  try { const j = await res.json(); return j.description || j.message || GT.strings.cartError; } catch (e) { return GT.strings.cartError; }
}

async function refreshCart(sectionsHtml) {
  const drawer = document.getElementById('cart-drawer');
  let html = sectionsHtml && sectionsHtml['cart-drawer'];
  if (!html) {
    const r = await fetch(`${GT.routes.root || '/'}?sections=cart-drawer`.replace('//?', '/?'));
    html = (await r.json())['cart-drawer'];
  }
  const doc = new DOMParser().parseFromString(html, 'text/html');
  const fresh = doc.querySelector('[data-cart-content]');
  const title = doc.querySelector('#cart-drawer-title');
  if (drawer && fresh) {
    drawer.querySelector('[data-cart-content]').replaceWith(fresh);
    drawer.querySelector('#cart-drawer-title').replaceWith(title);
  }
  const pageItems = document.querySelector('[data-cart-page]');
  if (pageItems) {
    const r = await fetch(`${GT.routes.cart}?section_id=main-cart`);
    const d = new DOMParser().parseFromString(await r.text(), 'text/html');
    const n = d.querySelector('[data-cart-page]');
    if (n) pageItems.replaceWith(n);
  }
  const c = await (await fetch(`${GT.routes.cart}.js`, { headers: { Accept: 'application/json' } })).json();
  setCount(c.item_count);
}

function showCartError(scope, msg) {
  const el = (scope || document).querySelector('[data-cart-error]') || document.querySelector('[data-cart-error]');
  if (el) { el.textContent = msg; el.hidden = false; }
  live(msg);
}

async function changeLine(line, quantity, scope) {
  if (cartBusy) return;
  cartBusy = true;
  const dlg = document.getElementById('cart-drawer');
  dlg?.classList.add('is-loading');
  try {
    const res = await fetch(GT.routes.cartChange, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ line, quantity, sections: ['cart-drawer'], sections_url: window.location.pathname }),
    });
    if (!res.ok) { showCartError(scope, await errorText(res)); return; }
    const data = await res.json();
    await refreshCart(data.sections);
    live(GT.strings.cartUpdated || '');
  } catch (e) {
    showCartError(scope, GT.strings.cartError);
  } finally {
    cartBusy = false;
    dlg?.classList.remove('is-loading');
  }
}

document.addEventListener('click', (e) => {
  const step = e.target.closest('[data-qty-step]');
  const line = e.target.closest('[data-line]');
  if (step && line) {
    const input = line.querySelector('[data-qty-input]');
    const q = Math.max(0, Number(input.value) + Number(step.dataset.qtyStep));
    input.value = q;
    changeLine(Number(line.dataset.line), q, line.closest('[data-cart-form]')?.parentElement);
    return;
  }
  const rm = e.target.closest('[data-remove]');
  if (rm && line) { e.preventDefault(); changeLine(Number(line.dataset.line), 0, line.closest('[data-cart-form]')?.parentElement); }
});
document.addEventListener('change', (e) => {
  const input = e.target.closest('[data-qty-input]');
  const line = e.target.closest('[data-line]');
  if (input && line) changeLine(Number(line.dataset.line), Math.max(0, Number(input.value) || 0), line.closest('[data-cart-form]')?.parentElement);
});

// product forms: one request in flight, button locked until it settles
document.addEventListener('submit', async (e) => {
  const form = e.target.closest('form[data-product-form]');
  if (!form) return;
  e.preventDefault();
  const btn = form.querySelector('[type="submit"]');
  if (cartBusy || btn.getAttribute('aria-busy') === 'true') return;
  cartBusy = true;
  btn.setAttribute('aria-busy', 'true');
  btn.disabled = true;
  const err = form.querySelector('[data-form-error]');
  if (err) { err.hidden = true; err.textContent = ''; }
  try {
    const body = new FormData(form);
    body.append('sections', 'cart-drawer');
    body.append('sections_url', window.location.pathname);
    const res = await fetch(GT.routes.cartAdd, { method: 'POST', body, headers: { Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest' } });
    if (!res.ok) {
      const msg = await errorText(res);
      if (err) { err.textContent = msg; err.hidden = false; }
      live(msg);
      return;
    }
    const data = await res.json();
    await refreshCart(data.sections);
    live(GT.strings.added);
    openDialogById('cart-drawer', btn);
  } catch (ex) {
    if (err) { err.textContent = GT.strings.cartError; err.hidden = false; }
    live(GT.strings.cartError);
  } finally {
    cartBusy = false;
    btn.removeAttribute('aria-busy');
    btn.disabled = false;
  }
});

// checkout: the first submit navigates; repeat clicks do nothing. Shopify checkout itself never charges twice.
document.addEventListener('submit', (e) => {
  const form = e.target.closest('form[data-checkout-form]');
  if (!form) return;
  if (form.dataset.submitted === '1') { e.preventDefault(); return; }
  form.dataset.submitted = '1';
  const btn = form.querySelector('[data-checkout]');
  if (btn) { btn.setAttribute('aria-busy', 'true'); btn.setAttribute('aria-disabled', 'true'); }
  // the name="checkout" value must still be sent, so the button is not disabled before submit
});
window.addEventListener('pageshow', (e) => {
  if (e.persisted) document.querySelectorAll('form[data-checkout-form]').forEach((f) => {
    delete f.dataset.submitted;
    f.querySelector('[data-checkout]')?.removeAttribute('aria-busy');
    f.querySelector('[data-checkout]')?.removeAttribute('aria-disabled');
  });
});

/* ---------- predictive search ---------- */
class PredictiveSearch extends HTMLElement {
  connectedCallback() {
    this.input = this.querySelector('input[type="search"]');
    this.results = this.querySelector('#predictive-results');
    this.tpl = this.querySelector('template[data-loading]');
    this.active = -1;
    this.ctrl = null;
    let t;
    this.input.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => this.search(), 220); });
    this.input.addEventListener('keydown', (e) => this.keys(e));
  }

  options() { return [...this.results.querySelectorAll('[role="option"]')]; }

  async search() {
    const q = this.input.value.trim();
    if (this.ctrl) this.ctrl.abort();
    if (!q) { this.results.innerHTML = ''; this.input.setAttribute('aria-expanded', 'false'); return; }
    this.ctrl = new AbortController();
    this.results.innerHTML = this.tpl.innerHTML;
    const params = new URLSearchParams({
      q, section_id: 'predictive-search', 'resources[type]': 'product', 'resources[limit]': '6',
      'resources[options][fields]': 'title,product_type,variants.title,vendor,tag', 'resources[options][prefix]': 'last',
    });
    try {
      const res = await fetch(`${GT.routes.predictiveSearch}?${params}`, { signal: this.ctrl.signal });
      if (!res.ok) throw new Error(String(res.status));
      const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
      const box = doc.querySelector('#predictive-search-results');
      this.results.innerHTML = box ? box.innerHTML : '';
      this.active = -1;
      this.input.setAttribute('aria-expanded', this.options().length ? 'true' : 'false');
      this.input.removeAttribute('aria-activedescendant');
    } catch (e) {
      if (e.name === 'AbortError') return;
      this.results.innerHTML = '';
      const p = document.createElement('p');
      p.className = 'predictive__status';
      p.setAttribute('role', 'alert');
      p.textContent = GT.strings.searchError;
      this.results.append(p);
    }
  }

  keys(e) {
    const opts = this.options();
    if (!opts.length) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      this.active = (this.active + (e.key === 'ArrowDown' ? 1 : -1) + opts.length) % opts.length;
      opts.forEach((o, j) => o.setAttribute('aria-selected', j === this.active ? 'true' : 'false'));
      this.input.setAttribute('aria-activedescendant', opts[this.active].id);
      opts[this.active].scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter' && this.active >= 0) {
      e.preventDefault();
      window.location.href = opts[this.active].querySelector('a').href;
    }
  }
}
if (!customElements.get('predictive-search')) customElements.define('predictive-search', PredictiveSearch);
