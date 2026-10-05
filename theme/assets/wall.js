// Wall key holder picker: a thumbnail swaps the holder on the lit wall (a short cross-fade), and the price and link
// follow it.
const root = document.querySelector('.wallhold');
if (root) {
  const img = root.querySelector('[data-wall-img]');
  const link = root.querySelector('[data-wall-link]');
  const name = root.querySelector('[data-wall-name]');
  const price = root.querySelector('[data-wall-price]');
  const piece = root.querySelector('.wallhold__piece');
  const picks = [...root.querySelectorAll('[data-wall-pick]')];
  picks.forEach((b) => b.addEventListener('click', () => {
    if (b.getAttribute('aria-pressed') === 'true') return;
    picks.forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    link.href = b.dataset.url;
    if (name) name.textContent = `: ${b.dataset.title}`;
    if (price) price.textContent = b.dataset.price;
    if (!img) return;
    const next = new Image();
    next.sizes = img.sizes;
    next.srcset = b.dataset.srcset;
    next.src = b.dataset.src;
    piece.classList.add('is-swapping');
    const swap = () => {
      img.srcset = b.dataset.srcset;
      img.src = b.dataset.src;
      requestAnimationFrame(() => piece.classList.remove('is-swapping'));
    };
    const later = () => setTimeout(swap, 180);
    (next.decode ? next.decode() : Promise.resolve()).then(later, later);
  }));
}
