// Tiny gate for heavy 3D code (three.js, model-viewer), kept apart so importing it costs nothing.
// When to boot 3D: fine-pointer devices once the page has loaded and the main thread is idle; touch devices on the
// first touch, scroll or key press, so phones never pay for WebGL before the visitor does anything.
export function when3D() {
  const afterLoad = () => new Promise((res) => {
    const idle = () => (window.requestIdleCallback ? requestIdleCallback(res, { timeout: 1200 }) : setTimeout(res, 200));
    if (document.readyState === 'complete') idle(); else window.addEventListener('load', idle, { once: true });
  });
  if (!window.matchMedia('(pointer: coarse)').matches) return afterLoad();
  return new Promise((res) => {
    const evs = ['pointerdown', 'touchstart', 'scroll', 'wheel', 'keydown'];
    const go = () => { evs.forEach((e) => window.removeEventListener(e, go, true)); res(); };
    evs.forEach((e) => window.addEventListener(e, go, { capture: true, passive: true }));
  });
}
