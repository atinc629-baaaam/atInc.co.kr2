/* atinc site script */
(function () {
  // 상담 신청: 기존 atinc.co.kr Google Form
  var FORM_URL = 'https://docs.google.com/forms/d/e/1FAIpQLScWj8HadYKhN0u5T3_wSdlQ-C8OEm1KLfwsCdRxDvk8ebdHuA/viewform';
  // 관심 분야 문항의 entry 번호를 적으면(예: 'entry.123456789') 버튼마다 해당 분야가 미리 선택됩니다.
  var FORM_CATEGORY_ENTRY = '';

  document.querySelectorAll('a[data-form]').forEach(function (a) {
    var cat = a.getAttribute('data-form');
    var url = FORM_URL;
    if (FORM_CATEGORY_ENTRY && cat) {
      url += '?usp=pp_url&' + FORM_CATEGORY_ENTRY + '=' + encodeURIComponent(cat);
    }
    a.href = url;
    a.target = '_blank';
    a.rel = 'noopener';
  });

  // header: solid after scrolling
  var hdr = document.querySelector('.hdr');
  // pages that open with the moving field keep the glass header until the field has scrolled away
  var over = document.querySelector('[data-hdr-over], .hero[data-fx]');
  function onScroll() {
    if (!hdr) return;
    var limit = over ? Math.max(24, over.offsetTop + over.offsetHeight - hdr.offsetHeight - 8) : 24;
    if (window.scrollY > limit) hdr.classList.add('is-solid');
    else hdr.classList.remove('is-solid');
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // Inside a preview frame the frame keeps its scroll position when a link opens the next page,
  // so the next page opened halfway down (or at its footer). Jump to the top instantly — a smooth
  // scroll gets cut off by the page change — before leaving and again while the new page loads.
  var embedded = false;
  try { embedded = window.self !== window.top; } catch (err) { embedded = true; }
  if (embedded) {
    try { history.scrollRestoration = 'manual'; } catch (err) {}
    var moved = false;
    var toTop = function () {
      if (moved || location.hash) return;
      var de = document.documentElement, prev = de.style.scrollBehavior;
      de.style.scrollBehavior = 'auto';
      try { window.scrollTo(0, 0); de.scrollIntoView({ block: 'start', behavior: 'instant' }); } catch (err) { window.scrollTo(0, 0); }
      de.style.scrollBehavior = prev;
    };
    ['wheel', 'touchmove', 'keydown'].forEach(function (ev) {
      window.addEventListener(ev, function () { moved = true; }, { passive: true, once: true });
    });
    document.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a[href]') : null;
      if (!a || a.target === '_blank' || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      var href = a.getAttribute('href') || '';
      if (!href || href.charAt(0) === '#' || /^(mailto:|tel:|https?:|javascript:)/i.test(href)) return;
      moved = false;
      var de = document.documentElement;
      de.style.scrollBehavior = 'auto';
      try { window.scrollTo(0, 0); de.scrollIntoView({ block: 'start', behavior: 'instant' }); } catch (err) { window.scrollTo(0, 0); }
    }, true);
    toTop();
    document.addEventListener('DOMContentLoaded', toTop);
    window.addEventListener('load', function () { toTop(); setTimeout(toTop, 120); setTimeout(toTop, 450); setTimeout(toTop, 1000); });
    window.addEventListener('pageshow', toTop);
  }

  // main visual: crossfade with counter, progress bar, previous / pause / next
  document.querySelectorAll('.phx').forEach(function (hero) {
    var slides = hero.querySelectorAll('.slide');
    var cur = hero.querySelector('[data-cur]'), bar = hero.querySelector('[data-bar]');
    var pauseBtn = hero.querySelector('[data-pause]');
    var n = slides.length, i = 0, timer = null, inView = true;
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var paused = reduce, DELAY = 6500;
    var ICON_PAUSE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6v12M15 6v12"/></svg>';
    var ICON_PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5l11 6.5-11 6.5z"/></svg>';
    function pad(x) { return (x < 9 ? '0' : '') + (x + 1); }
    function restartBar() {
      if (!bar) return;
      bar.classList.remove('run'); void bar.offsetWidth;
      if (!paused) bar.classList.add('run');
    }
    function show(k) {
      slides[i].classList.remove('is-on');
      i = (k + n) % n;
      slides[i].classList.add('is-on');
      if (cur) cur.textContent = pad(i);
      restartBar(); schedule();
    }
    function schedule() {
      clearTimeout(timer);
      if (paused || n < 2) return;
      timer = setTimeout(function () {
        if (document.hidden || !inView) { schedule(); return; }
        show(i + 1);
      }, DELAY);
    }
    function setPaused(p) {
      paused = p;
      hero.classList.toggle('is-paused', p);
      if (pauseBtn) {
        pauseBtn.innerHTML = p ? ICON_PLAY : ICON_PAUSE;
        pauseBtn.setAttribute('aria-label', p ? '자동 넘김 다시 시작' : '자동 넘김 멈추기');
      }
      if (p) clearTimeout(timer); else { restartBar(); schedule(); }
    }
    var prev = hero.querySelector('[data-prev]'), next = hero.querySelector('[data-next]');
    if (prev) prev.addEventListener('click', function () { show(i - 1); });
    if (next) next.addEventListener('click', function () { show(i + 1); });
    if (pauseBtn) pauseBtn.addEventListener('click', function () { setPaused(!paused); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { inView = en[0].isIntersecting; }).observe(hero);
    }
    setPaused(paused);
  });

  // floating consult buttons: "back to top" appears once the page has moved
  var fab = document.querySelector('.fab');
  if (fab) {
    var fabScroll = function () { fab.classList.toggle('is-scrolled', window.scrollY > 600); };
    fabScroll();
    window.addEventListener('scroll', fabScroll, { passive: true });
  }
  document.querySelectorAll('[data-top]').forEach(function (b) {
    b.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
      var m = document.getElementById('main'); if (m) { m.setAttribute('tabindex', '-1'); m.focus({ preventScroll: true }); }
    });
  });

  // mobile menu
  var mnav = document.getElementById('mnav');
  var openBtn = document.getElementById('menu-open');
  var closeBtn = document.getElementById('menu-close');
  function setMenu(open) {
    if (!mnav) return;
    mnav.hidden = !open;
    if (openBtn) openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.documentElement.style.overflow = open ? 'hidden' : '';
    if (open && closeBtn) closeBtn.focus();
    if (!open && openBtn) openBtn.focus();
  }
  if (openBtn) openBtn.addEventListener('click', function () { setMenu(true); });
  if (closeBtn) closeBtn.addEventListener('click', function () { setMenu(false); });
  if (mnav) mnav.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () { setMenu(false); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mnav && !mnav.hidden) setMenu(false);
  });

  // network filter (home + network page)
  document.querySelectorAll('[data-net]').forEach(function (root) {
    var btns = root.querySelectorAll('.filters button');
    var items = root.querySelectorAll('[data-cats]');
    var empty = root.querySelector('.net-empty');
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        var cat = b.getAttribute('data-cat');
        btns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        var hits = 0;
        items.forEach(function (el) {
          var on = cat === 'all' || (',' + el.getAttribute('data-cats') + ',').indexOf(',' + cat + ',') > -1;
          el.classList.toggle('is-dim', !on);
          if (on && el.hasAttribute('data-count')) hits++;
        });
        if (empty) empty.hidden = !(cat !== 'all' && hits === 0);
      });
    });
  });

  // medical area tabs (home)
  document.querySelectorAll('[role="tablist"]').forEach(function (list) {
    var tabs = Array.prototype.slice.call(list.querySelectorAll('[role="tab"]'));
    function select(t, focus) {
      tabs.forEach(function (x) {
        var on = x === t;
        x.setAttribute('aria-selected', on ? 'true' : 'false');
        x.tabIndex = on ? 0 : -1;
        var p = document.getElementById(x.getAttribute('aria-controls'));
        if (p) p.hidden = !on;
      });
      if (focus) t.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () {
        select(t, false);
        if (window.matchMedia('(max-width: 900px)').matches) {
          var p = document.getElementById(t.getAttribute('aria-controls'));
          if (p) p.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
      t.addEventListener('keydown', function (e) {
        var k = e.key, n = null;
        if (k === 'ArrowDown' || k === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
        if (k === 'ArrowUp' || k === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
  });

  // sub-nav: mark the section in view
  var sub = document.querySelector('.subnav');
  if (sub && 'IntersectionObserver' in window) {
    var links = {};
    sub.querySelectorAll('a[href^="#"]').forEach(function (a) { links[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && links[en.target.id]) {
          Object.keys(links).forEach(function (k) { links[k].classList.remove('is-on'); });
          links[en.target.id].classList.add('is-on');
          var a = links[en.target.id];
          var box = sub.querySelector('.subnav__in');
          if (box) box.scrollTo({ left: a.offsetLeft - 20, behavior: 'smooth' });
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(links).forEach(function (id) { var s = document.getElementById(id); if (s) io.observe(s); });
  }

  // foldable lists ([data-fold]): open on desktop, folded on phones so long lists don't run for screens
  var foldMq = window.matchMedia('(max-width: 700px)');
  var applyFold = function () {
    document.querySelectorAll('details[data-fold]').forEach(function (d) {
      if (foldMq.matches) d.removeAttribute('open'); else d.setAttribute('open', '');
    });
  };
  applyFold();
  if (foldMq.addEventListener) foldMq.addEventListener('change', applyFold);
})();
