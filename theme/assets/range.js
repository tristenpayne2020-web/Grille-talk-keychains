// Range viewer: one keychain at a time, neighbours dimmed. Arrows, swipe, arrow keys, dots.
// The centre keychain is 3D on a physics chain when WebGL is available; otherwise its render image stays.
const root = document.querySelector('[data-range]');

if (root) {
  const slides = [...root.querySelectorAll('.range__slide')];
  const n = slides.length;
  const dots = [...root.querySelectorAll('[data-range-dot]')];
  const canvasBox = root.querySelector('[data-range-canvas]');
  const el = (s) => root.querySelector(s);
  const counter = document.querySelector('[data-range-index]');
  let i = 0;
  let stage = null;
  let stagePromise = null;
  let token = 0;

  const pad = (v) => String(v).padStart(2, '0');

  function layout() {
    slides.forEach((s, j) => {
      let d = (((j - i) % n) + n) % n;
      if (d > n / 2) d -= n;
      if (Math.abs(d) <= 2 && n > 1) s.dataset.pos = String(d); else s.removeAttribute('data-pos');
      if (n === 1 && j === 0) s.dataset.pos = '0';
      s.setAttribute('aria-hidden', d === 0 ? 'false' : 'true');
      s.classList.toggle('has-3d', false);
    });
  }

  function info() {
    const s = slides[i];
    el('[data-range-title]').textContent = s.dataset.title;
    el('[data-range-short]').textContent = s.dataset.short;
    el('[data-range-price]').textContent = s.dataset.price;
    const view = el('[data-range-view]');
    view.href = s.dataset.url;
    el('[data-range-view-name]').textContent = `: ${s.dataset.title}`;
    dots.forEach((d, j) => (j === i ? d.setAttribute('aria-current', 'true') : d.removeAttribute('aria-current')));
    if (counter) counter.textContent = pad(i + 1);
  }

  async function ensureStage() {
    if (stagePromise) return stagePromise;
    stagePromise = (async () => {
      const mod = await import('keychain3d');
      if (!mod.webglAvailable()) return null;
      return new mod.KeychainStage(canvasBox, { fit: 0.66, interactive: 'mouse' });
    })().catch(() => null);
    return stagePromise;
  }

  async function show3D(dir = 0) {
    const s = slides[i];
    const url = s.dataset.model;
    const my = ++token;
    canvasBox.classList.remove('is-on');
    if (!url) return;
    stage = await ensureStage();
    if (!stage || my !== token) return;
    try {
      await stage.load(url);
      if (my !== token) return;
      stage.nudge(dir * -1.2);
      canvasBox.classList.add('is-on');
      s.classList.add('has-3d');
    } catch (e) {
      /* keep the render image */
    }
  }

  function go(to, dir) {
    if (n < 2) return;
    const next = ((to % n) + n) % n;
    if (next === i) return;
    if (dir === undefined) dir = next > i ? 1 : -1;
    i = next;
    layout();
    info();
    show3D(dir);
  }

  el('[data-range-prev]').addEventListener('click', () => go(i - 1, -1));
  el('[data-range-next]').addEventListener('click', () => go(i + 1, 1));
  dots.forEach((d, j) => d.addEventListener('click', () => go(j)));
  slides.forEach((s, j) => s.addEventListener('click', () => { if (s.dataset.pos && s.dataset.pos !== '0') go(j, Number(s.dataset.pos) > 0 ? 1 : -1); }));
  root.addEventListener('keydown', (e) => {
    if (e.target.closest('input, textarea, select')) return;
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(i - 1, -1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); go(i + 1, 1); }
  });

  // touch swipe (horizontal intent only, so vertical scrolling stays native)
  const vp = el('[data-range-viewport]');
  let sx = 0, sy = 0, st = 0, tracking = false;
  vp.addEventListener('pointerdown', (e) => { if (e.pointerType === 'mouse') return; tracking = true; sx = e.clientX; sy = e.clientY; st = performance.now(); });
  vp.addEventListener('pointerup', (e) => {
    if (!tracking) return;
    tracking = false;
    const dx = e.clientX - sx, dy = e.clientY - sy, dt = performance.now() - st;
    if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy) * 1.3 && dt < 800) go(i + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
  });
  vp.addEventListener('pointercancel', () => { tracking = false; });

  layout();
  info();
  // start the 3D only when the viewer is about to be seen
  const io = new IntersectionObserver((entries) => {
    if (entries.some((e) => e.isIntersecting)) { io.disconnect(); show3D(0); }
  }, { rootMargin: '300px 0px' });
  io.observe(root);
}
