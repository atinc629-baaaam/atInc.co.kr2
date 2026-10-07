/* 편집기 안에서 열린 페이지에만 붙는 도구입니다 (공개 페이지에는 없습니다).
   글·사진을 누르면 편집기(바깥 창)에 알리고, 섹션·항목 위에 이동·복제·숨기기·삭제 단추를 띄웁니다. */
(function () {
  'use strict';
  var infoEl = document.getElementById('atinc-edit');
  var info = infoEl ? JSON.parse(infoEl.textContent) : {};
  var host = window.parent && window.parent !== window ? window.parent : null;
  var html = document.documentElement;
  var on = false;
  var LABELS = {};
  html.classList.add('atinc-editing');

  function post(msg) { if (host) { msg.source = 'atinc-page'; host.postMessage(msg, location.origin); } }
  function q(v) { return String(v).replace(/\\/g, '\\\\').replace(/"/g, '\\"'); }
  function byAttr(attr, val) { return document.querySelectorAll('[' + attr + '="' + q(val) + '"]'); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  // ---- 글 모양 (빌더와 같은 규칙)
  function rich(t) {
    t = esc(t);
    t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>');
    t = t.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
    return t.replace(/\n/g, '<br>');
  }
  function doc(md) {
    var out = [], open = false;
    String(md || '').trim().split(/\n\s*\n/).forEach(function (block) {
      var ls = block.trim().split('\n').map(function (x) { return x.replace(/(\\| {2,})$/, '').replace(/\s+$/, ''); });
      if (ls.length && ls[0].indexOf('## ') === 0) {
        if (open) out.push('</section>');
        out.push('<section><h2>' + rich(ls[0].slice(3).trim()) + '</h2>');
        open = true; ls = ls.slice(1);
      }
      if (!ls.length) return;
      if (ls.every(function (x) { return /^[-*] /.test(x); })) {
        out.push('<ul class="dots">' + ls.map(function (x) { return '<li>' + rich(x.slice(2).trim()) + '</li>'; }).join('') + '</ul>');
      } else out.push('<p>' + rich(ls.join('\n')) + '</p>');
    });
    if (open) out.push('</section>');
    return out.join('');
  }
  function render(el, kind, value) {
    value = value == null ? '' : String(value);
    if (kind === 'rich') el.innerHTML = rich(value);
    else if (kind === 'lines') el.innerHTML = value.split('\n').map(function (x) { return '<span class="ln"><span>' + esc(x) + '</span></span>'; }).join('');
    else if (kind === 'regions') {
      var r = el.querySelector('[data-net-regions]');
      var regions = r ? r.textContent : '';
      var parts = value.split('{regions}');
      el.innerHTML = rich(parts[0]) + (parts.length > 1 ? '<span data-net-regions>' + esc(regions) + '</span>' + rich(parts[1]) : '');
    } else if (kind === 'paras') el.innerHTML = value.split(/\n\s*\n/).filter(function (p) { return p.trim(); }).map(function (p) { return '<p>' + rich(p.trim()) + '</p>'; }).join('');
    else if (kind === 'doc') el.innerHTML = doc(value);
    else el.textContent = value;
  }

  // ---- 선택 표시
  var active = [];
  function select(nodes) {
    active.forEach(function (n) { n.classList.remove('atinc-active'); });
    active = Array.prototype.slice.call(nodes || []);
    active.forEach(function (n) { n.classList.add('atinc-active'); });
  }

  // ---- 섹션·항목 단추
  function mk(cls) { var d = document.createElement('div'); d.className = cls; d.hidden = true; document.body.appendChild(d); return d; }
  var secBox = mk('atinc-box atinc-box--sec'), secTools = mk('atinc-tools');
  var itemBox = mk('atinc-box'), itemTools = mk('atinc-tools atinc-tools--item');
  var curSec = null, curItem = null;

  function btn(label, op, title, danger) {
    return '<button type="button" data-op="' + op + '" title="' + esc(title) + '"' + (danger ? ' class="is-danger"' : '') + '>' + label + '</button>';
  }
  function headerBottom() {
    // 화면 위에 붙어 있는 머리글(메뉴) 아래로 단추를 내립니다
    var h = document.querySelector('.hdr');
    if (!h) return 0;
    var r = h.getBoundingClientRect();
    return r.bottom > 0 ? Math.min(r.bottom, 160) : 0;
  }
  function place(box, tools, el, below) {
    var r = el.getBoundingClientRect(), sx = window.scrollX, sy = window.scrollY;
    box.style.left = (r.left + sx) + 'px'; box.style.top = (r.top + sy) + 'px';
    box.style.width = r.width + 'px'; box.style.height = r.height + 'px';
    box.hidden = false; tools.hidden = false;
    var tw = tools.offsetWidth, th = tools.offsetHeight || 32;
    var top = Math.max(r.top + sy + 6, sy + headerBottom() + 6);
    if (below && !below.hidden) {
      // 섹션 단추와 겹치면 그 아래로
      var bt = parseFloat(below.style.top) || 0, bl = parseFloat(below.style.left) || 0;
      var left0 = Math.max(sx + 6, r.right + sx - tw - 6);
      if (Math.abs(top - bt) < th + 4 && left0 < bl + below.offsetWidth && left0 + tw > bl) top = bt + th + 6;
    }
    top = Math.min(top, Math.max(r.top + sy + 6, r.bottom + sy - th - 6));
    tools.style.top = top + 'px';
    tools.style.left = Math.max(sx + 6, r.right + sx - tw - 6) + 'px';
  }
  function showSec(el) {
    curSec = el;
    var hidden = el.hasAttribute('data-hidden');
    secTools.innerHTML = '<b>' + esc(LABELS[el.getAttribute('data-sec')] || '섹션') + '</b>' + btn('▲', 'up', '위로') + btn('▼', 'down', '아래로') +
      btn(hidden ? '보이기' : '숨기기', 'hide', hidden ? '다시 보이기' : '홈페이지에서 숨기기') + btn('복제', 'dup', '바로 아래에 복사') + btn('삭제', 'del', '섹션 지우기', true);
    place(secBox, secTools, el);
  }
  function showItem(el) {
    curItem = el;
    itemTools.innerHTML = btn('▲', 'up', '앞으로') + btn('▼', 'down', '뒤로') + btn('복제', 'dup', '바로 뒤에 복사') + btn('삭제', 'del', '지우기', true);
    place(itemBox, itemTools, el, secTools);
  }
  function hideTools() { clearTimeout(hideTimer); [secBox, secTools, itemBox, itemTools].forEach(function (x) { x.hidden = true; }); curSec = curItem = null; }

  // 마우스가 섹션 밖(머리글 위 등)으로 잠깐 나가도 단추가 바로 사라지지 않게 조금 기다립니다
  var hideTimer = null;
  function hideLater() { clearTimeout(hideTimer); hideTimer = setTimeout(hideTools, 700); }
  document.addEventListener('mousemove', function (e) {
    if (!on) return;
    var t = e.target;
    if (!t.closest) return;
    if (t.closest('.atinc-tools')) { clearTimeout(hideTimer); return; }
    var sec = t.closest('[data-sec]'), item = t.closest('[data-item]:not([data-sec])');
    if (!sec) { hideLater(); return; }
    clearTimeout(hideTimer);
    if (sec !== curSec) showSec(sec);
    if (item && item !== curItem) showItem(item);
    if (!item) { itemBox.hidden = itemTools.hidden = true; curItem = null; }
  }, { passive: true });
  document.addEventListener('mouseleave', function () { if (on) hideLater(); });
  window.addEventListener('scroll', function () { if (curSec) place(secBox, secTools, curSec); if (curItem) place(itemBox, itemTools, curItem, secTools); }, { passive: true });
  [secTools, itemTools].forEach(function (tools) {
    tools.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-op]');
      if (!b) return;
      e.preventDefault(); e.stopPropagation();
      var el = tools === secTools ? curSec : curItem;
      if (!el) return;
      post({ type: 'item-op', op: b.getAttribute('data-op'), path: el.getAttribute('data-item'), section: tools === secTools });
    });
  });

  // ---- 누르기: 편집 모드에서는 글·사진 편집, 미리보기에서는 사이트 안 이동
  document.addEventListener('click', function (e) {
    if (e.target.closest('.atinc-tools')) return;
    if (!on) {
      var a = e.target.closest('a[href]');
      if (a) {
        var href = a.getAttribute('href');
        if (/^[a-z0-9-]+\.html(#.*)?$/i.test(href)) { e.preventDefault(); post({ type: 'nav', page: href.split('#')[0] }); }
        else if (href.charAt(0) !== '#' && !/^(https?:|mailto:|tel:)/.test(href)) e.preventDefault();
      }
      return;
    }
    if (e.target.closest('.phx__btn')) return;            // 슬라이드 넘김 단추는 그대로 작동
    e.preventDefault(); e.stopPropagation();
    var t = e.target.closest('[data-e]');
    if (t) {
      select(byAttr('data-e', t.getAttribute('data-e')));
      post({ type: 'edit-text', path: t.getAttribute('data-e'), kind: t.getAttribute('data-k') || 'text' });
      return;
    }
    var stack = document.elementsFromPoint(e.clientX, e.clientY);
    for (var i = 0; i < stack.length; i++) {
      if (stack[i].hasAttribute && stack[i].hasAttribute('data-img')) {
        select(byAttr('data-img', stack[i].getAttribute('data-img')));
        post({ type: 'edit-img', path: stack[i].getAttribute('data-img') });
        return;
      }
    }
  }, true);
  document.addEventListener('submit', function (e) { if (on) e.preventDefault(); }, true);

  // ---- 목록 번호 다시 매기기, 경로 다시 쓰기
  function reindexIn(root, list, map) {
    var attrs = ['data-e', 'data-img', 'data-item'];
    var pre = list + '.';
    var nodes = [];
    if (root.nodeType === 1) nodes.push(root);
    Array.prototype.push.apply(nodes, root.querySelectorAll('[data-e],[data-img],[data-item]'));
    nodes.forEach(function (el) {
      attrs.forEach(function (a) {
        var v = el.getAttribute(a);
        if (!v || v.indexOf(pre) !== 0) return;
        var m = v.slice(pre.length).match(/^(\d+)(.*)$/);
        if (m && Object.prototype.hasOwnProperty.call(map, m[1])) el.setAttribute(a, pre + map[m[1]] + m[2]);
      });
    });
  }
  function split(path) { var i = path.lastIndexOf('.'); return { list: path.slice(0, i), idx: parseInt(path.slice(i + 1), 10) }; }
  function itemEl(path) { return document.querySelector('[data-item="' + q(path) + '"]'); }
  function siblingsOf(list) {
    var out = [], re = new RegExp('^' + list.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\.(\\d+)$');
    document.querySelectorAll('[data-item]').forEach(function (el) { var m = el.getAttribute('data-item').match(re); if (m) out.push(el); });
    return out;
  }
  function renumber(list) {
    siblingsOf(list).forEach(function (el) {
      var n = parseInt(split(el.getAttribute('data-item')).idx, 10);
      var no = el.querySelector('.ways__no, .step__no, .flow__no, .rows__no');
      if (no && no.closest('[data-item]') === el && /^\d{2}$/.test(no.textContent.trim())) no.textContent = (n + 1 < 10 ? '0' : '') + (n + 1);
    });
  }
  function applyOp(op, path) {
    var el = itemEl(path);
    if (!el) return false;
    var s = split(path), list = s.list, i = s.idx, map = {}, k;
    var all = siblingsOf(list).map(function (x) { return split(x.getAttribute('data-item')).idx; });
    var max = Math.max.apply(null, all);
    if (op === 'up' || op === 'down') {
      var j = op === 'up' ? i - 1 : i + 1;
      var other = itemEl(list + '.' + j);
      if (!other) return false;
      if (op === 'up') other.parentNode.insertBefore(el, other); else other.parentNode.insertBefore(other, el);
      map[i] = j; map[j] = i;
      reindexIn(document, list, map);
    } else if (op === 'dup') {
      var clone = el.cloneNode(true);
      for (k = i + 1; k <= max; k++) map[k] = k + 1;
      reindexIn(document, list, map);
      var cm = {}; cm[i] = i + 1;
      reindexIn(clone, list, cm);
      el.parentNode.insertBefore(clone, el.nextSibling);
    } else if (op === 'del') {
      el.parentNode.removeChild(el);
      for (k = i + 1; k <= max; k++) map[k] = k - 1;
      reindexIn(document, list, map);
    } else if (op === 'hide') {
      if (el.hasAttribute('data-hidden')) el.removeAttribute('data-hidden'); else el.setAttribute('data-hidden', '1');
    }
    renumber(list);
    hideTools();
    return true;
  }

  // ---- 편집기에서 오는 말
  window.addEventListener('message', function (e) {
    if (e.origin !== location.origin || !e.data || e.data.source !== 'atinc-editor') return;
    var m = e.data;
    if (m.type === 'mode') {
      on = !!m.on;
      html.classList.toggle('atinc-on', on);
      if (!on) { hideTools(); select([]); }
    } else if (m.type === 'labels') {
      LABELS = m.labels || {};
    } else if (m.type === 'set-text') {
      byAttr('data-e', m.path).forEach(function (el) { render(el, el.getAttribute('data-k') || 'text', m.value); });
    } else if (m.type === 'set-img') {
      byAttr('data-img', m.path).forEach(function (img) {
        if (m.url) { img.removeAttribute('srcset'); img.src = m.url; }
        if (m.pos !== undefined) img.style.objectPosition = m.pos || '';
        if (m.alt !== undefined) img.alt = m.alt;
      });
    } else if (m.type === 'apply-op') {
      applyOp(m.op, m.path);
    } else if (m.type === 'deselect') {
      select([]);
    } else if (m.type === 'scroll-to') {
      var t = document.querySelector('[data-e="' + q(m.path) + '"],[data-img="' + q(m.path) + '"]');
      if (t) t.scrollIntoView({ block: 'center', behavior: 'smooth' });
    }
  });

  // 첫 화면 슬라이드는 편집하는 동안 멈춰 둡니다
  window.addEventListener('load', function () {
    var hero = document.querySelector('.phx'), pause = hero && hero.querySelector('[data-pause]');
    if (pause && !hero.classList.contains('is-paused')) pause.click();
  });
  post({ type: 'ready', page: info.page, file: info.file, title: info.title });
})();
