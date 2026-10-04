// Home hero intro: black > G80 DRL signatures light up > logo reveal > hand-over to the 3D keychain on its chain.
// Under 3 s, skippable, once per session. Reduced motion or a repeat visit: the end state, no timeline.
// Without WebGL the end state is the static render that the HTML already shows.
const hero = document.querySelector('[data-hero]');

const seen = () => { try { return sessionStorage.getItem('gt-intro') === '1'; } catch (e) { return false; } };
const markSeen = () => { try { sessionStorage.setItem('gt-intro', '1'); } catch (e) { /* storage blocked: intro may replay */ } };

async function start3D() {
  const url = hero.dataset.model;
  if (!url) return null;
  const { when3D } = await import('when3d');
  await when3D();   // until then the matching static render shows; three.js is only fetched after this
  const { KeychainStage, webglAvailable } = await import('keychain3d');
  if (!webglAvailable()) return null;
  const el = hero.querySelector('[data-hero-3d]');
  const stage = new KeychainStage(el, { align: hero.querySelector('[data-hero-art]'), active: false });
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
  stage.setActive(true);
  hero.classList.add('is-3d');
}

async function run() {
  if (!hero) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || seen()) {
    show3D(await start3D());
    return;
  }
  markSeen();
  const { gsap } = await import('vendor-gsap');
  gsap.ticker.lagSmoothing(0);   // wall-clock timing: on a slow device frames drop, the intro still ends on time
  const q = (s) => hero.querySelectorAll(s);
  const skip = hero.querySelector('[data-hero-skip]');
  const drl = q('.hero__drl path');
  const logo = hero.querySelector('.hero__logo img');
  hero.classList.add('is-intro');
  skip.hidden = false;

  gsap.set(drl, { strokeDasharray: 1, strokeDashoffset: 1, fillOpacity: 0 });
  gsap.set('.hero__body-dots', { opacity: 0 });
  gsap.set(logo, { clipPath: 'inset(0 100% 0 0)', opacity: 1 });
  gsap.set('.hero__actions', { opacity: 0, y: 14 });   // headline and copy are on screen from the first frame

  // 3D boots only after the intro: compiling shaders mid-animation would stall it. The aligned static render
  // covers the hand-over, then the 3D keychain cross-fades in on top of it.

  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
  tl.to(drl, { strokeDashoffset: 0, duration: 0.75, ease: 'power2.inOut', stagger: 0.08 }, 0.25)
    .to(drl, { fillOpacity: 1, duration: 0.3 }, 0.85)
    .to('.hero__body-dots', { opacity: 0.42, duration: 0.7, ease: 'power1.out' }, 0.6)
    .to(logo, { clipPath: 'inset(0 0% 0 0)', duration: 0.6, ease: 'power2.inOut' }, 1.1)
    .add('handover', 1.85)
    .to(logo, { opacity: 0, scale: 0.92, filter: 'blur(6px)', duration: 0.45, ease: 'power2.in' }, 'handover')
    .add(() => hero.classList.add('is-handover'), 'handover')
    .to('.hero__actions', { opacity: 1, y: 0, duration: 0.5 }, 'handover+=0.2');

  let finished = false;
  const finish = () => {
    if (finished) return;
    finished = true;
    tl.progress(1);
    skip.hidden = true;
    hero.classList.remove('is-intro', 'is-handover');
    gsap.set([drl, logo, '.hero__body-dots', '.hero__actions'], { clearProps: 'all' });
    start3D().then(show3D);
  };
  const guard = setTimeout(() => { if (tl.progress() < 1) finish(); }, 4000);   // never hold the page longer than this
  tl.eventCallback('onComplete', () => { clearTimeout(guard); finish(); });
  skip.addEventListener('click', () => { finish(); hero.querySelector('.hero__actions a')?.focus(); });
}

run();
