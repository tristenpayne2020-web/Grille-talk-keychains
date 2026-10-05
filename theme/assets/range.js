// Range viewer: one keychain at a time, neighbours dimmed. Arrows, drag or swipe (mouse and touch), arrow keys, dots.
// On the 3D display the keychain slides out and the next one slides in; while dragging it follows the pointer.
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
  let loadGLB = null;

  // the backdrop name fills most of the viewer's width, whatever its length
  function fitName() {
    const name = el('[data-range-name]');
    const vp = el('[data-range-viewport]');
    if (!name || !vp.classList.contains('is-3d-display')) return;
    name.style.fontSize = '100px';
    const target = vp.clientWidth * 0.86;
    name.style.fontSize = `${Math.max(40, Math.min(vp.clientHeight * 0.34, (100 * target) / Math.max(1, name.scrollWidth)))}px`;
  }

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
    const name = el('[data-range-name]');
    if (name && s.dataset.name) {
      name.classList.remove('is-in');
      void name.offsetWidth;   // restart the name's entrance
      name.textContent = s.dataset.name;
      fitName();
      name.classList.add('is-in');
    }
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
      await (await import('when3d')).when3D();
      const mod = await import('keychain3d');
      if (!mod.webglAvailable()) return null;
      const name = el('[data-range-name]');
      const vp = el('[data-range-viewport]');
      loadGLB = mod.loadGLB;
      return new mod.KeychainStage(canvasBox, {
        fit: 0.6, interactive: false, float: true, spot: true, display: true,
        // the car's name stands large behind the keychain (like a poster), never over the pedestal
        onLayout: ({ nameX, nameY }) => {
          vp.classList.add('is-3d-display');
          const cb = canvasBox.getBoundingClientRect(), vb = vp.getBoundingClientRect();
          name.style.left = `${cb.left - vb.left + nameX}px`;
          name.style.top = `${cb.top - vb.top + nameY}px`;
          fitName();
        },
      });
    })().catch(() => null);
    return stagePromise;
  }

  async function show3D(dir = 0) {
    const s = slides[i];
    const url = s.dataset.model;
    const my = ++token;
    if (!stage) canvasBox.classList.remove('is-on');
    if (stage && dir) stage.leave(dir);   // the current keychain starts leaving at once, before the next has loaded
    if (!url) return;
    stage = await ensureStage();
    if (!stage || my !== token) return;
    try {
      const color = s.dataset.color ? { hex: s.dataset.color, metal: Number(s.dataset.metal) || 0, rough: Number(s.dataset.rough) || 0.6 } : undefined;
      await stage.load(url, color, { dir });
      if (my !== token) return;
      canvasBox.classList.add('is-on');
      s.classList.add('has-3d');
      // fetch the neighbours now, so the next move is instant
      [1, -1].forEach((k) => { const u = slides[(i + k + n) % n].dataset.model; if (u && loadGLB) loadGLB(u).catch(() => {}); });
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

  // drag (mouse, pen or touch): horizontal intent only, so vertical scrolling stays native. The 3D keychain follows the
  // pointer; let go past a threshold (or flick) and the next one comes in, otherwise it springs back.
  const vp = el('[data-range-viewport]');
  let sx = 0, sy = 0, st = 0, tracking = false, decided = false, horiz = false, dragged = false, lastX = 0, lastT = 0, vx = 0;
  vp.addEventListener('pointerdown', (e) => {
    if (e.button !== 0 || e.target.closest('button, a')) return;
    tracking = true; decided = false; horiz = false; dragged = false;
    sx = lastX = e.clientX; sy = e.clientY; st = lastT = performance.now(); vx = 0;
  });
  vp.addEventListener('pointermove', (e) => {
    if (!tracking) return;
    const dx = e.clientX - sx, dy = e.clientY - sy;
    if (!decided && Math.hypot(dx, dy) > 6) {
      decided = true; horiz = Math.abs(dx) > Math.abs(dy) * 1.1;
      if (horiz) { vp.setPointerCapture?.(e.pointerId); vp.classList.add('is-dragging'); }
      else tracking = false;
    }
    if (!horiz) return;
    dragged = true;
    const now = performance.now();
    vx = (e.clientX - lastX) / Math.max(8, now - lastT);
    lastX = e.clientX; lastT = now;
    if (stage) stage.dragSlide(dx * 0.85);
  });
  const end = (e) => {
    if (!tracking) return;
    tracking = false;
    vp.classList.remove('is-dragging');
    const dx = e.clientX - sx;
    if (!decided) horiz = Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(e.clientY - sy) * 1.1;   // a flick with no moves in between
    if (!horiz) return;
    const far = Math.abs(dx) > Math.min(140, vp.clientWidth * 0.14);
    const flick = Math.abs(vx) > 0.5 && Math.abs(dx) > 30;
    if (stage) stage.releaseSlide();
    if (far || flick) go(i + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
  };
  vp.addEventListener('pointerup', end);
  vp.addEventListener('pointercancel', (e) => { end(e); });
  // a drag is not a click on a side keychain
  vp.addEventListener('click', (e) => { if (dragged) { e.stopPropagation(); e.preventDefault(); dragged = false; } }, true);
  window.addEventListener('resize', fitName);

  layout();
  info();
  // start the 3D only when the viewer is about to be seen
  const io = new IntersectionObserver((entries) => {
    if (entries.some((e) => e.isIntersecting)) { io.disconnect(); show3D(0); }
  }, { rootMargin: '300px 0px' });
  io.observe(root);
}
