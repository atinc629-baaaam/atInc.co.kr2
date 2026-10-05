/* Starts the moving light ([data-fx]) and the 3D cells ([data-cells]) after the page has loaded.
   Without WebGL, or when the page is opened straight from a file, the CSS backgrounds stay as they are. */
const hosts = document.querySelectorAll('[data-fx]');
const cells = document.querySelectorAll('[data-cells]');

function ok(kind) {
  try { const c = document.createElement('canvas'); return !!c.getContext(kind); } catch (e) { return false; }
}

function start() {
  const gl = ok('webgl2') || ok('webgl');
  if (!gl) return;
  if (hosts.length) {
    import('./field.js').then(({ mountField }) => {
      hosts.forEach((h) => {
        const r = mountField(h, { look: h.dataset.fx, seed: h.dataset.fxSeed ? +h.dataset.fxSeed : null });
        if (r) document.documentElement.classList.add('fx-live');
      });
    }).catch(() => {});
  }
  if (cells.length) {
    const io = new IntersectionObserver((es) => {
      es.forEach((e) => {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        import('./cells.js').then(({ mountCells }) => mountCells(e.target)).catch(() => {});
      });
    }, { rootMargin: '400px' });
    cells.forEach((c) => io.observe(c));
  }
}

if (document.readyState === 'complete') requestAnimationFrame(start);
else window.addEventListener('load', () => requestAnimationFrame(start), { once: true });
