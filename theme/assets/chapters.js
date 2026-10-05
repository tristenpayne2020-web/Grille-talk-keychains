// Scroll chapters: HUD progress and chapter readout, the pinned detail tour (camera push + spotlight + rail), process
// steps, depth drift behind the hero, and magnetic buttons. Everything reads fine without it; reduced motion keeps the
// chapter switching and drops the camera moves and parallax.
const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const fine = window.matchMedia('(pointer: fine)').matches;
const lerp = (a, b, t) => a + (b - a) * t;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const frameTasks = new Set();
let ticking = false;
const loop = () => { frameTasks.forEach((f) => f()); ticking = frameTasks.size > 0 && !document.hidden; if (ticking) requestAnimationFrame(loop); };
const run = (f) => { frameTasks.add(f); if (!ticking) { ticking = true; requestAnimationFrame(loop); } };
document.addEventListener('visibilitychange', () => { if (!document.hidden && frameTasks.size && !ticking) { ticking = true; requestAnimationFrame(loop); } });

/* ---------- HUD ---------- */
const bar = document.querySelector('[data-hud-progress]');
const readout = document.querySelector('[data-hud-chapter]');
if (bar) {
  const onScroll = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = `scaleX(${max > 0 ? clamp(scrollY / max, 0, 1) : 0})`;
  };
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });
}
const chapters = [...document.querySelectorAll('[data-chapter]')];
if (readout && chapters.length) {
  const io = new IntersectionObserver((es) => {
    es.forEach((e) => {
      if (!e.isIntersecting) return;
      const i = chapters.indexOf(e.target);
      readout.textContent = `${String(i + 1).padStart(2, '0')} / ${e.target.dataset.chapter}`;
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  chapters.forEach((c) => io.observe(c));
}

/* ---------- detail tour ---------- */
const tour = document.querySelector('[data-tour]');
if (tour) {
  const items = [...tour.querySelectorAll('[data-tour-item]')];
  const rail = [...tour.querySelectorAll('[data-tour-go]')];
  const stage = tour.querySelector('[data-tour-stage]');
  const frame = tour.querySelector('[data-tour-frame]');
  const spot = tour.querySelector('[data-tour-spot]');
  const reticle = tour.querySelector('[data-tour-reticle]');
  const data = JSON.parse(tour.querySelector('[data-tour-anchors]').textContent);
  const n = items.length;
  tour.classList.add('is-pinned');
  tour.style.setProperty('--chapters', n);
  let active = -1;
  const cur = { s: 1, x: 0, y: 0, sx: 50, sy: 50, sr: 4000 };

  const setActive = (i) => {
    if (i === active) return;
    active = i;
    items.forEach((el, j) => el.classList.toggle('is-active', j === i));
    rail.forEach((el, j) => { el.classList.toggle('is-active', j === i); if (j === i) el.setAttribute('aria-current', 'step'); else el.removeAttribute('aria-current'); });
  };

  const head = tour.querySelector('.tour__head');
  // the opening frame fits the keychain between the headline and the caption, clear of the rail
  const fit = () => {
    const W = stage.clientWidth, H = stage.clientHeight;
    const top = head ? head.getBoundingClientRect().bottom - stage.getBoundingClientRect().top + 16 : 0;
    const act = items[Math.max(0, active)];
    const bottom = H - (act ? act.offsetHeight : 0) - (W >= 990 ? 90 : 150);
    const right = W >= 750 ? 96 : 16;
    const boxW = W - right - 16, boxH = Math.max(120, bottom - top);
    const k = Math.min(boxW / data.w, boxH / data.h);
    return { W, H, fw: data.w * k, fh: data.h * k, ox: 16 + (boxW - data.w * k) / 2, oy: top + (boxH - data.h * k) / 2 };
  };

  const progress = () => {
    const r = tour.getBoundingClientRect();
    const span = tour.offsetHeight - innerHeight;
    return span > 0 ? clamp(-r.top / span, 0, 1) : 0;
  };

  const update = () => {
    const p = progress();
    const { W, H, fw, fh, ox, oy } = fit();
    const wide = W >= 990;
    const intro = 0.1;                                  // first slice of the scroll shows the whole keychain
    const t = clamp((p - intro) / (1 - intro), 0, 0.9999);
    const i = p < intro ? 0 : Math.floor(t * n);
    setActive(i);
    let target = { s: 1, x: ox, y: oy, sx: 50, sy: 50, sr: Math.hypot(W, H) };   // iris fully open
    tour.classList.toggle('is-zoomed', p >= intro * 0.6);
    tour.classList.toggle('is-back', items[i] && items[i].dataset.anchor === 'back' && p >= intro * 0.6);
    if (p >= intro * 0.6) {
      const it = items[i];
      const a = data.anchors[it.dataset.anchor] || [50, 50];
      const s = reduce ? 1 : Number(it.dataset.zoom || 18) / 10;
      const ax = (a[0] / 100) * fw, ay = (a[1] / 100) * fh;
      const cx = wide ? W * 0.6 : W * 0.5, cy = wide ? H * 0.44 : H * 0.36;
      const x = reduce ? ox : cx - ax * s;
      const y = reduce ? oy : cy - ay * s;
      target = { s, x, y, sx: ((x + ax * s) / W) * 100, sy: ((y + ay * s) / H) * 100, sr: Math.min(W, H) * (wide ? 0.2 : 0.26) * (it.dataset.anchor === 'back' ? 1.7 : 1) };
    }
    const k = reduce ? 1 : 0.12;
    for (const key of Object.keys(cur)) cur[key] = lerp(cur[key], target[key], k);
    frame.style.width = `${fw}px`;
    frame.style.height = `${fh}px`;
    frame.style.transform = `translate3d(${cur.x.toFixed(1)}px, ${cur.y.toFixed(1)}px, 0) scale(${cur.s.toFixed(4)})`;
    spot.style.setProperty('--sx', `${cur.sx.toFixed(2)}%`);
    spot.style.setProperty('--sy', `${cur.sy.toFixed(2)}%`);
    spot.style.setProperty('--sr', `${cur.sr.toFixed(1)}px`);
    reticle.style.transform = `translate3d(calc(${(cur.sx / 100) * W}px - 50%), calc(${(cur.sy / 100) * H}px - 50%), 0) scale(${(cur.sr / 100).toFixed(3)})`;
    reticle.style.opacity = cur.sr > 20 && cur.sr < Math.min(W, H) * 0.5 ? '1' : '0';
  };

  const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) run(update); else frameTasks.delete(update); });
  io.observe(tour);
  rail.forEach((btn, j) => btn.addEventListener('click', (e) => {
    e.preventDefault();
    const top = tour.getBoundingClientRect().top + scrollY;
    const span = tour.offsetHeight - innerHeight;
    const intro = 0.1;
    const p = intro + ((j + 0.5) / n) * (1 - intro);
    scrollTo({ top: top + span * p, behavior: reduce ? 'auto' : 'smooth' });
  }));
}

/* ---------- process steps ---------- */
const proc = document.querySelector('[data-process]');
if (proc) {
  const imgs = [...proc.querySelectorAll('[data-process-img]')];
  const steps = [...proc.querySelectorAll('[data-process-step]')];
  const cap = proc.querySelector('[data-process-caption]');
  proc.classList.add('is-live');
  const io = new IntersectionObserver((es) => {
    es.forEach((e) => {
      if (!e.isIntersecting) return;
      const i = Number(e.target.dataset.processStep);
      steps.forEach((s, j) => s.classList.toggle('is-active', j === i));
      imgs.forEach((im, j) => im.classList.toggle('is-active', j === i));
      if (cap) cap.textContent = e.target.querySelector('.process__label').textContent.split('/').pop().trim();
      proc.style.setProperty('--step', i);
    });
  }, { rootMargin: '-45% 0px -45% 0px' });
  steps.forEach((s) => io.observe(s));
}

/* ---------- depth drift behind the hero ---------- */
const drift = document.querySelector('[data-drift]');
if (drift && !reduce) {
  const floats = [...drift.querySelectorAll('.hero__float')];
  let mx = 0, my = 0, cx = 0, cy = 0;
  if (fine) addEventListener('pointermove', (e) => { mx = e.clientX / innerWidth - 0.5; my = e.clientY / innerHeight - 0.5; }, { passive: true });
  const step = () => {
    cx = lerp(cx, mx, 0.06); cy = lerp(cy, my, 0.06);
    const sy = scrollY;
    floats.forEach((f, i) => {
      const depth = 0.4 + (i % 3) * 0.35;
      f.style.transform = `translate3d(${(cx * 40 * depth).toFixed(1)}px, ${(cy * 30 * depth - sy * 0.12 * depth).toFixed(1)}px, 0)`;
    });
  };
  const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) run(step); else frameTasks.delete(step); });
  io.observe(drift);
}

/* ---------- magnetic buttons ---------- */
if (fine && !reduce) {
  document.querySelectorAll('[data-magnetic]').forEach((b) => {
    b.addEventListener('pointermove', (e) => {
      const r = b.getBoundingClientRect();
      b.style.transform = `translate(${((e.clientX - r.left - r.width / 2) * 0.18).toFixed(1)}px, ${((e.clientY - r.top - r.height / 2) * 0.28).toFixed(1)}px)`;
    });
    b.addEventListener('pointerleave', () => { b.style.transform = ''; });
  });
}
