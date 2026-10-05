// First-visit loader: the counter follows real loading (fonts, the loader art, the hero image, the page load event and,
// on desktop, the 3D keychain), never runs shorter than 1.6 s or longer than 4.5 s, and can be skipped.
const root = document.documentElement;
const el = document.getElementById('loader');

if (el && root.classList.contains('gt-loading')) {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const count = el.querySelector('[data-loader-count]');
  const bar = el.querySelector('[data-loader-bar]');
  const skip = document.querySelector('[data-loader-skip]');
  const status = document.querySelector('[data-loader-status]');
  const MIN = reduce ? 700 : 1600;
  const MAX = 4500;
  const t0 = performance.now();

  const img = (sel) => new Promise((res) => {
    const i = document.querySelector(sel);
    if (!i || i.complete) return res();
    i.addEventListener('load', res, { once: true });
    i.addEventListener('error', res, { once: true });
  });
  const tasks = [
    document.fonts ? document.fonts.ready : Promise.resolve(),
    img('.loader__img--dim'),
    img('[data-hero-static] img'),
    new Promise((res) => (document.readyState === 'complete' ? res() : window.addEventListener('load', res, { once: true }))),
  ];
  // desktop visitors get the 3D keychain ready behind the loader, so the hero opens on it
  if (window.matchMedia('(pointer: fine)').matches) {
    tasks.push(new Promise((res) => {
      if (window.__gtHero3d) return res();
      window.addEventListener('gt:hero3d', res, { once: true });
      setTimeout(res, MAX);
    }));
  }
  let done = 0;
  tasks.forEach((p) => p.then(() => { done += 1; }));

  let shown = 0;
  let finished = false;
  const finish = () => {
    if (finished) return;
    finished = true;
    el.style.setProperty('--fill', '1');
    count.textContent = '100';
    root.classList.add('gt-loaded');
    if (status) status.textContent = '';
    window.__gtLoaded = true;
    window.dispatchEvent(new Event('gt:loaded'));
    setTimeout(() => {
      root.classList.remove('gt-loading', 'gt-loaded');
      el.remove();
      skip?.remove();
    }, reduce ? 300 : 1100);
  };
  skip?.addEventListener('click', finish);

  const tick = () => {
    if (finished) return;
    const elapsed = performance.now() - t0;
    const real = done / tasks.length;
    const time = Math.min(1, elapsed / MIN);
    const target = Math.min(real, time);            // never ahead of real loading, never faster than the minimum
    shown += (target - shown) * (reduce ? 1 : 0.12);
    const pct = Math.min(100, Math.round(shown * 100));
    count.textContent = String(pct);
    el.style.setProperty('--fill', shown.toFixed(4));
    if (bar) bar.style.transform = `scaleX(${shown.toFixed(4)})`;
    if ((real >= 1 && time >= 1 && pct >= 99) || elapsed > MAX) { finish(); return; }
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
