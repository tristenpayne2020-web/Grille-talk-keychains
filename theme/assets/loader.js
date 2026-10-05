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
  let ready = false;
  const ignition = document.querySelector('[data-loader-ignition]');
  const quietPref = () => { try { return localStorage.getItem('gt-sound') === 'off'; } catch (e) { return false; } };
  const setPref = (v) => { try { localStorage.setItem('gt-sound', v); } catch (e) { /* storage blocked */ } };
  let autoEnter = null;

  // at 100%: offer the push-to-start button (browsers only allow sound after a gesture)
  const onReady = () => {
    if (ready) return;
    ready = true;
    if (!ignition || quietPref()) { finish(); return; }
    ignition.hidden = false;
    el.classList.add('is-ready');
    requestAnimationFrame(() => ignition.classList.add('is-in'));
    ignition.querySelector('[data-loader-start]').focus({ preventScroll: true });
    autoEnter = setTimeout(finish, 7000);   // never hold the visitor: enter quietly after 7 s
  };
  ignition?.querySelector('[data-loader-quiet]').addEventListener('click', () => { setPref('off'); finish(); });
  ignition?.querySelector('[data-loader-start]').addEventListener('click', async (e) => {
    const btn = e.currentTarget;
    if (btn.disabled) return;
    btn.disabled = true;
    clearTimeout(autoEnter);
    setPref('on');
    el.classList.add('is-starting');
    let catchAt = 620;   // ms: when the bundled straight-six catches
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      const ctx = new AC();
      await ctx.resume();
      const play = (buffer) => { const src = ctx.createBufferSource(); src.buffer = buffer; const g = ctx.createGain(); g.gain.value = 0.85; src.connect(g).connect(ctx.destination); src.start(); setTimeout(() => ctx.close(), (buffer.duration + 0.3) * 1000); };
      const decode = async (url) => ctx.decodeAudioData(await (await fetch(url)).arrayBuffer());
      const own = window.GT && window.GT.coldstartUrl;   // the owner's own recording (theme setting), if set
      try {
        if (own) { play(await decode(own)); catchAt = 800; }
        else { const { COLDSTART_MP3 } = await import('coldstart-audio'); play(await decode(COLDSTART_MP3)); }
      } catch (e2) {
        const { playColdStart } = await import('coldstart');   // last resort: synthesise live
        playColdStart(ctx, { volume: 0.5 });
        catchAt = 860;
      }
    } catch (err) { /* no audio at all: carry on silently */ }
    setTimeout(() => el.classList.add('is-caught'), catchAt);   // the engine catches: lights flare
    setTimeout(finish, catchAt + 450);
  });

  const finish = () => {
    if (finished) return;
    finished = true;
    clearTimeout(autoEnter);
    ignition?.classList.remove('is-in');
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
      ignition?.remove();
    }, reduce ? 300 : 1100);
  };
  skip?.addEventListener('click', () => finish());

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
    if ((real >= 1 && time >= 1 && pct >= 99) || elapsed > MAX) {
      count.textContent = '100';
      el.style.setProperty('--fill', '1');
      if (bar) bar.style.transform = 'scaleX(1)';
      onReady();
      return;
    }
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
