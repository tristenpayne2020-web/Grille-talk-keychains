// Home hero: boots the 3D keychain (desktop after load, phones on first touch or scroll) and cross-fades it over the
// aligned static render. Announces readiness to the first-visit loader with a 'gt:hero3d' event.
const hero = document.querySelector('[data-hero]');

async function start3D() {
  const url = hero.dataset.model;
  if (!url) return null;
  const { when3D } = await import('when3d');
  await when3D();   // three.js is only fetched after this
  const { KeychainStage, webglAvailable } = await import('keychain3d');
  if (!webglAvailable()) return null;
  const stage = new KeychainStage(hero.querySelector('[data-hero-3d]'), { align: hero.querySelector('[data-hero-art]'), active: false });
  try {
    await stage.load(url);
    return stage;
  } catch (e) {
    stage.dispose();
    return null;
  }
}

if (hero) {
  start3D().then((stage) => {
    window.__gtHero3d = true;
    window.dispatchEvent(new Event('gt:hero3d'));
    if (!stage) return;
    const show = () => { stage.setActive(true); hero.classList.add('is-3d'); stage.nudge(0.4); };
    // if the first-visit loader is up, wait for it so the keychain swings into view as it lifts
    if (document.documentElement.classList.contains('gt-loading') && !window.__gtLoaded) window.addEventListener('gt:loaded', show, { once: true });
    else show();
  });
}
