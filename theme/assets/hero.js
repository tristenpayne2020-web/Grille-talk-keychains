// Home hero intro: black > G80 DRL signatures light up > logo reveal > hand-over to the 3D keychain on its chain.
// Under 3 s, skippable, once per session. Reduced motion or a repeat visit: the end state, no timeline.
// Without WebGL the end state is the static render that the HTML already shows.
const hero = document.querySelector('[data-hero]');

const seen = () => { try { return sessionStorage.getItem('gt-intro') === '1'; } catch (e) { return false; } };
const markSeen = () => { try { sessionStorage.setItem('gt-intro', '1'); } catch (e) { /* storage blocked: intro may replay */ } };

async function start3D() {
  const url = hero.dataset.model;
  if (!url) return null;
  const { KeychainStage, webglAvailable } = await import('keychain3d');
  if (!webglAvailable()) return null;
  const el = hero.querySelector('[data-hero-3d]');
  const stage = new KeychainStage(el, { align: hero.querySelector('[data-hero-art]') });
  try {
    await stage.load(url);
    return stage;
  } catch (e) {
    stage.dispose();
    return null;
  }
}

function show3D(stage) {
  if (!stage) return;
  stage.resize();
  hero.classList.add('is-3d');
}

async function run() {
  if (!hero) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const stagePromise = start3D();
  if (reduce || seen()) {
    show3D(await stagePromise);
    return;
  }
  markSeen();
  const { gsap } = await import('vendor-gsap');
  const q = (s) => hero.querySelectorAll(s);
  const skip = hero.querySelector('[data-hero-skip]');
  const drl = q('.hero__drl path');
  const logo = hero.querySelector('.hero__logo img');
  hero.classList.add('is-intro');
  skip.hidden = false;

  gsap.set(drl, { strokeDasharray: 1, strokeDashoffset: 1, fillOpacity: 0 });
  gsap.set('.hero__body-dots', { opacity: 0 });
  gsap.set(logo, { clipPath: 'inset(0 100% 0 0)', opacity: 1 });
  gsap.set('[data-hero-copy]', { opacity: 0, y: 14 });

  let stage = null;
  stagePromise.then((s) => { stage = s; });

  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
  tl.to(drl, { strokeDashoffset: 0, duration: 0.75, ease: 'power2.inOut', stagger: 0.08 }, 0.25)
    .to(drl, { fillOpacity: 1, duration: 0.3 }, 0.85)
    .to('.hero__body-dots', { opacity: 0.42, duration: 0.7, ease: 'power1.out' }, 0.6)
    .to(logo, { clipPath: 'inset(0 0% 0 0)', duration: 0.6, ease: 'power2.inOut' }, 1.1)
    .add('handover', 1.85)
    .to(logo, { opacity: 0, scale: 0.92, filter: 'blur(6px)', duration: 0.45, ease: 'power2.in' }, 'handover')
    .add(() => { if (stage) show3D(stage); else hero.classList.add('is-done'); }, 'handover+=0.15')
    .to('[data-hero-copy]', { opacity: 1, y: 0, duration: 0.5, stagger: 0.07 }, 'handover+=0.2');

  const finish = () => {
    tl.progress(1);
    skip.hidden = true;
    hero.classList.remove('is-intro');
    gsap.set([drl, logo, '.hero__body-dots', '[data-hero-copy]'], { clearProps: 'all' });
    if (!stage) stagePromise.then(show3D);
  };
  tl.eventCallback('onComplete', finish);
  skip.addEventListener('click', () => { finish(); hero.querySelector('.hero__actions a')?.focus(); });
}

run();
