// Product films: load and play only while on screen (muted, looping), pause when scrolled away or the tab is
// hidden. The sound button unmutes one film at a time. Under reduced motion nothing autoplays: a play button shows
// over the poster instead.
const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const films = [...document.querySelectorAll('[data-film]')].filter((f) => !f.dataset.filmReady);

films.forEach((root) => {
  root.dataset.filmReady = '1';
  const v = root.querySelector('[data-film-video]');
  const sound = root.querySelector('[data-film-sound]');
  const label = root.querySelector('[data-film-sound-label]');
  const play = root.querySelector('[data-film-play]');
  let inView = false;
  let userPlay = !reduce;

  const tryPlay = () => {
    if (!inView || !userPlay || document.hidden) return;
    if (v.preload !== 'auto') v.preload = 'auto';
    const p = v.play();
    if (p && p.catch) p.catch(() => { if (play) play.hidden = false; });
  };
  const stop = () => { if (!v.paused) v.pause(); };

  new IntersectionObserver(([e]) => {
    inView = e.isIntersecting;
    inView ? tryPlay() : stop();
  }, { threshold: 0.35 }).observe(root);
  document.addEventListener('visibilitychange', () => (document.hidden ? stop() : tryPlay()));

  if (play) {
    play.hidden = !reduce;
    play.addEventListener('click', () => { userPlay = true; play.hidden = true; tryPlay(); });
    v.addEventListener('pause', () => { if (reduce && inView) play.hidden = false; });
  }

  sound?.addEventListener('click', () => {
    const on = v.muted;
    document.querySelectorAll('[data-film-video]').forEach((o) => {   // one film with sound at a time
      if (o !== v) { o.muted = true; o.closest('[data-film]')?.querySelector('[data-film-sound]')?.setAttribute('aria-pressed', 'false'); }
    });
    document.querySelectorAll('[data-film-sound-label]').forEach((l) => { if (l !== label) l.textContent = l.dataset.on || l.textContent; });
    v.muted = !on;
    sound.setAttribute('aria-pressed', String(on));
    if (label) {
      label.dataset.on = label.dataset.on || label.textContent;
      label.textContent = on ? (sound.dataset.offLabel || 'Sound off') : label.dataset.on;
    }
    if (on) { userPlay = true; if (play) play.hidden = true; tryPlay(); }
  });
});
