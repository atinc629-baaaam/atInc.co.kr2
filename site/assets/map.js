/* atInc network map + lists — everything is drawn from assets/network-data.js */
(function () {
  var M = window.ATMAP;
  var DATA = window.ATINC_NETWORK || [];
  var CAT = { checkup: '건강검진', regenerative: '재생의료·줄기세포', aesthetic: '성형·피부', women: '여성건강', men: '남성건강', 'korean-medicine': '한방·웰니스' };
  var CAT_ORDER = ['checkup', 'regenerative', 'aesthetic', 'women', 'men', 'korean-medicine'];
  var ORDER = ['11', '23', '31', '25', '29', '33', '34', '32', '24', '35', '36', '22', '37', '26', '21', '38', '39'];
  var SHORT = { '11': '서울', '21': '부산', '22': '대구', '23': '인천', '24': '광주', '25': '대전', '26': '울산', '29': '세종', '31': '경기', '32': '강원', '33': '충북', '34': '충남', '35': '전북', '36': '전남', '37': '경북', '38': '경남', '39': '제주' };
  var EN = { '11': 'Seoul', '21': 'Busan', '22': 'Daegu', '23': 'Incheon', '24': 'Gwangju', '25': 'Daejeon', '26': 'Ulsan', '29': 'Sejong', '31': 'Gyeonggi', '32': 'Gangwon', '33': 'Chungbuk', '34': 'Chungnam', '35': 'Jeonbuk', '36': 'Jeonnam', '37': 'Gyeongbuk', '38': 'Gyeongnam', '39': 'Jeju' };
  var CAPITAL = { '11': 1, '23': 1, '31': 1 };
  var GOLD = '#E3C394', IVORY = '#F6EFE3';
  var REDUCE = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var LITE = REDUCE || (window.matchMedia && window.matchMedia('(max-width: 700px), (hover: none) and (pointer: coarse)').matches);

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function norm(s) { return String(s || '').replace(/\s+/g, '').replace(/특별자치시|특별자치도|특별시|광역시/g, ''); }
  function provOfName(a) { for (var p in SHORT) { if (a === SHORT[p]) return p; } return null; }

  // ---- resolve each site's area to districts and coordinates
  var keys = [];
  if (M) for (var code in M.muni) keys.push([norm(SHORT[M.muni[code].p] + M.muni[code].n), code]);
  var sites = DATA.map(function (s, i) {
    var a = norm(s.area), codes = [], prov = null;
    keys.forEach(function (k) { if (k[0].indexOf(a) === 0) codes.push(k[1]); });
    if (codes.length) prov = codes[0].slice(0, 2);
    else prov = provOfName(a) || provOfName(norm(s.area).slice(0, 2));
    var x = 0, y = 0, ix = 0, iy = 0, inInset = !!codes.length;
    if (M) {
      if (codes.length) {
        codes.forEach(function (c) { x += M.muni[c].c[0]; y += M.muni[c].c[1]; if (M.muni[c].i) { ix += M.muni[c].i[0]; iy += M.muni[c].i[1]; } else inInset = false; });
        x /= codes.length; y /= codes.length; ix /= codes.length; iy /= codes.length;
      } else if (prov && M.prov[prov]) { x = M.prov[prov].c[0]; y = M.prov[prov].c[1]; inInset = false; }
    }
    return { i: i, area: s.area, name: s.name || s.area, short: s.short || s.name || s.area, en: s.en || '', cats: s.cats || [], note: s.note || '',
             prov: prov, codes: codes, x: x, y: y, ix: ix, iy: iy, inset: inInset && !!CAPITAL[prov] };
  }).filter(function (s) { return s.prov; });

  function union(list) { var u = {}; list.forEach(function (s) { s.cats.forEach(function (c) { u[c] = 1; }); }); return CAT_ORDER.filter(function (c) { return u[c]; }); }
  function catsText(cats) { return cats.length ? cats.map(function (c) { return CAT[c]; }).join(' · ') : '협력 의료기관'; }
  function byProv() {
    var g = {};
    sites.forEach(function (s) { (g[s.prov] = g[s.prov] || []).push(s); });
    return ORDER.filter(function (p) { return g[p]; }).map(function (p) { return { prov: p, sites: g[p] }; });
  }
  var GROUPS = byProv();
  // public view is by province: a dot or card never pairs one district with one specialty
  GROUPS.forEach(function (gp) { var u = union(gp.sites); gp.sites.forEach(function (s) { s.pcats = u; }); });
  function punion(list) { var u = {}; list.forEach(function (s) { (s.pcats || s.cats).forEach(function (c) { u[c] = 1; }); }); return CAT_ORDER.filter(function (c) { return u[c]; }); }

  // ---- text placeholders that depend on the data
  document.querySelectorAll('[data-net-regions]').forEach(function (el) { el.textContent = GROUPS.map(function (g) { return SHORT[g.prov]; }).join(', '); });
  document.querySelectorAll('[data-net-for]').forEach(function (el) {
    var cat = el.getAttribute('data-net-for');
    var hit = [];
    sites.forEach(function (s) { if (s.cats.indexOf(cat) > -1 && hit.indexOf(SHORT[s.prov]) < 0) hit.push(SHORT[s.prov]); });
    el.textContent = hit.length ? hit.join(' · ') : '지역과 관계없이 상담 후 병원을 찾아 드립니다';
  });

  // ---- lists (the last row says the network keeps growing)
  var NEXT_LI = '<li class="hubs__next"><div><b>그 밖의 지역</b><small>협력 병원을 계속 늘려 가고 있습니다</small></div><span class="hubs__cats">가까운 병원은 상담 후 찾아 드립니다</span></li>';
  var NEXT_CARD = '<section class="netgroup netgroup--next"><h2 class="netgroup__h"><span>그 밖의 지역</span><em>Expanding nationwide</em></h2>' +
    '<p class="body">같은 기준으로 고른 협력 병원을 지역마다 계속 늘려 가고 있습니다. 지금 목록에 없는 지역이라도, 상담하시면 가까운 곳에서 맞는 병원을 찾아 드립니다.</p></section>';
  document.querySelectorAll('.atnet-list').forEach(function (box) {
    var v = box.getAttribute('data-variant') || 'compact', h = '';
    if (v === 'compact') {
      h = '<ul class="hubs">' + GROUPS.map(function (g) {
        var cats = union(g.sites);
        return '<li data-cats="' + cats.join(',') + '" data-count><div><b>' + esc(SHORT[g.prov]) + '</b><small>' +
          esc(EN[g.prov]) + '</small></div><span class="hubs__cats">' + esc(catsText(cats)) + '</span></li>';
      }).join('') + NEXT_LI + '</ul>';
    } else {
      h = GROUPS.map(function (g) {
        return '<section class="netgroup"><h2 class="netgroup__h"><span>' + esc(SHORT[g.prov]) + '</span><em>' + esc(EN[g.prov]) + '</em>' +
          '</h2><div class="hubgrid">' + (function () {
            var cats = union(g.sites), notes = [];
            g.sites.forEach(function (s) { if (s.note && notes.indexOf(s.note) < 0) notes.push(s.note); });
            return '<div class="hcard" data-cats="' + cats.join(',') + '" data-count><div class="chips">' +
              (cats.length ? cats.map(function (c) { return '<span class="tag">' + esc(CAT[c]) + '</span>'; }).join('') : '<span class="tag">협력 의료기관</span>') +
              '</div><ul class="hcard__notes">' + notes.map(function (t) { return '<li>' + esc(t).replace(/(\S) 수 (있|없)/g, '$1\u00a0수\u00a0$2') + '</li>'; }).join('') + '</ul></div>';
          })() + '</div></section>';
      }).join('') + NEXT_CARD;
    }
    box.innerHTML = h;
  });

  if (!M) return;

  // ---- map
  var W = M.W, H = M.H, I = M.inset;
  function textW(t, size) { var w = 0; for (var k = 0; k < t.length; k++) w += /[가-힣]/.test(t[k]) ? size * 0.98 : size * 0.58; return w; }
  function overlap(a, b) { return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y; }
  function T(x, y, t, anchor, size, weight, fill, italic) {
    return '<text x="' + x.toFixed(1) + '" y="' + y.toFixed(1) + '" text-anchor="' + anchor + '" font-family="' + "'Pretendard Variable',Pretendard,'Apple SD Gothic Neo','Noto Sans KR',sans-serif" +
      '" font-size="' + size + '" font-weight="' + weight + '" fill="' + fill + '"' + (italic ? ' letter-spacing=".03em"' : '') +
      ' stroke="#1A120D" stroke-opacity=".9" stroke-width="4" stroke-linejoin="round" paint-order="stroke">' + esc(t) + '</text>';
  }
  function cluster(list, px, py, dist) {
    var out = [];
    list.forEach(function (s) {
      var x = s[px], y = s[py], hit = null;
      out.forEach(function (c) { if (!hit && Math.hypot(c.x - x, c.y - y) < dist) hit = c; });
      if (hit) { hit.sites.push(s); hit.x = (hit.x * (hit.sites.length - 1) + x) / hit.sites.length; hit.y = (hit.y * (hit.sites.length - 1) + y) / hit.sites.length; }
      else out.push({ x: x, y: y, sites: [s] });
    });
    return out;
  }
  function placeLabels(items, taken, bounds) {
    items.forEach(function (it) {
      var cands = [[14, 5, 'start'], [-14, 5, 'end'], [0, -14, 'middle'], [0, 24, 'middle'], [14, -10, 'start'], [-14, -10, 'end'],
                   [14, 20, 'start'], [-14, 20, 'end'], [22, 5, 'start'], [-22, 5, 'end'], [0, -24, 'middle'], [0, 34, 'middle']];
      it.label = null;
      for (var k = 0; k < cands.length; k++) {
        var c = cands[k], w = it.w, h = it.h;
        var lx = c[2] === 'start' ? it.x + c[0] : c[2] === 'end' ? it.x + c[0] - w : it.x - w / 2;
        var r = { x: lx - 2, y: it.y + c[1] - it.size - 2, w: w + 4, h: h + 4 };
        if (bounds && (r.x < bounds.x || r.x + r.w > bounds.x + bounds.w || r.y < bounds.y || r.y + r.h > bounds.y + bounds.h)) continue;
        if (taken.some(function (t) { return overlap(t, r); })) continue;
        taken.push(r); it.label = { x: it.x + c[0], y: it.y + c[1], anchor: c[2] }; break;
      }
    });
  }

  function attachOrphans(items, maxd, fmt) {
    items.forEach(function (it) {
      if (it.label) return;
      var best = null, bd = 1e9;
      items.forEach(function (o) { if (o.label && o !== it) { var d = Math.hypot(o.x - it.x, o.y - it.y); if (d < bd) { bd = d; best = o; } } });
      if (best && bd < maxd) { best.extra = (best.extra || 0) + it.sites.length; it.orphan = true; }
    });
    items.forEach(function (it) { if (it.extra) fmt(it); });
  }

  var lit = {}, provOn = {};
  sites.forEach(function (s) { s.codes.forEach(function (c) { lit[c] = 1; }); provOn[s.prov] = 1; });

  document.querySelectorAll('.atmap').forEach(function (host, n) {
    var uid = (host.getAttribute('data-uid') || 'm') + n;
    var K = Math.min(1.5, Math.max(1, W / (host.clientWidth || W) * 0.82));  // ~1.3 on a 390px phone
    var s = ['<svg class="atmap__svg" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="atInc 협력 네트워크 지도: ' +
      esc(GROUPS.map(function (g) { return SHORT[g.prov]; }).join(', ')) + '" xmlns="http://www.w3.org/2000/svg">',
      '<defs><radialGradient id="gl-' + uid + '"><stop offset="0" stop-color="' + GOLD + '" stop-opacity=".55"/><stop offset="1" stop-color="' + GOLD + '" stop-opacity="0"/></radialGradient>' +
      '<linearGradient id="rt-' + uid + '" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="' + GOLD + '"/><stop offset="1" stop-color="' + GOLD + '" stop-opacity=".35"/></linearGradient></defs>'];
    // base dots
    var b = '';
    for (var c in M.muni) {
      var m = M.muni[c];
      if (!m.d) continue;
      b += '<path class="dm' + (lit[c] ? ' on' : provOn[m.p] ? ' pv' : '') + '" d="' + m.d + '"/>';
    }
    s.push('<g class="atmap__base">' + b + '</g>');
    // expansion: light keeps spreading from the capital across the whole country
    if (!LITE) {
      var cap0 = sites.filter(function (x) { return CAPITAL[x.prov]; });
      var hub0 = cap0.filter(function (x) { return x.prov === '11'; })[0] || cap0[0];
      var wx = hub0 ? hub0.x : M.prov['11'].c[0], wy = hub0 ? hub0.y : M.prov['11'].c[1];
      var all = '';
      for (c in M.muni) { if (M.muni[c].d) all += M.muni[c].d; }
      var ring = function (begin) {
        return '<circle cx="' + wx.toFixed(1) + '" cy="' + wy.toFixed(1) + '" r="0" fill="url(#wr-' + uid + ')">' +
          '<animate attributeName="r" values="0;720" dur="10s" begin="' + begin + 's" repeatCount="indefinite"/>' +
          '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.12;.72;1" dur="10s" begin="' + begin + 's" repeatCount="indefinite"/></circle>';
      };
      s.push('<defs><radialGradient id="wr-' + uid + '"><stop offset=".7" stop-color="#fff" stop-opacity="0"/><stop offset=".9" stop-color="#fff" stop-opacity="1"/>' +
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>' +
        '<mask id="wm-' + uid + '" maskUnits="userSpaceOnUse" x="0" y="0" width="' + W + '" height="' + H + '">' + ring(-1) + ring(-6) + '</mask></defs>');
      s.push('<path class="dw" d="' + all + '" mask="url(#wm-' + uid + ')"/>');
    }
    s.push('<rect x="' + I.x + '" y="' + I.y + '" width="' + I.w + '" height="' + I.h + '" rx="14" fill="#1F1611"/>');
    var bi = '';
    for (c in M.muni) {
      m = M.muni[c];
      if (!m.di) continue;
      bi += '<path class="di' + (lit[c] ? ' on' : provOn[m.p] ? ' pv' : '') + '" d="' + m.di + '"/>';
    }
    s.push('<g class="atmap__base">' + bi + '</g>');

    function route(id, d, width, op, dur, begin) {
      return '<path id="' + id + '" d="' + d + '" fill="none" stroke="url(#rt-' + uid + ')" stroke-opacity="' + op + '" stroke-width="' + width + '"/>' +
        '<circle r="2.2" fill="' + IVORY + '" class="spark"><animateMotion dur="' + dur + 's" begin="-' + begin.toFixed(2) + 's" repeatCount="indefinite"><mpath href="#' + id + '"/></animateMotion></circle>';
    }
    function curve(x1, y1, x2, y2, bend) {
      var mx = (x1 + x2) / 2, my = (y1 + y2) / 2, dx = x2 - x1, dy = y2 - y1;
      return 'M' + x1.toFixed(1) + ' ' + y1.toFixed(1) + ' Q ' + (mx - dy * bend).toFixed(1) + ' ' + (my + dx * bend).toFixed(1) + ' ' + x2.toFixed(1) + ' ' + y2.toFixed(1);
    }
    function mk(x, y, r, d) {
      return '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="' + (r * 5).toFixed(1) + '" fill="url(#gl-' + uid + ')"/>' +
        '<circle class="pulse" cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="' + (r * 2.4).toFixed(1) + '" fill="none" stroke="' + GOLD + '" stroke-width="1" style="animation-delay: ' + d + 's"/>' +
        '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="' + r + '" fill="' + GOLD + '" stroke="#20160F" stroke-width="1.6"/>';
    }
    function g(cats, inner) { return '<g class="hub" data-cats="' + cats.join(',') + '">' + inner + '</g>'; }

    var icn = M.icn;
    // global arrivals into ICN
    [['M-6 70', 6], ['M-6 250', 7], ['M-6 420', 8]].forEach(function (a, k) {
      var sx = -6, sy = [70, 250, 420][k];
      s.push(route('a' + k + '-' + uid, curve(sx, sy, icn[0], icn[1], k === 2 ? -0.18 : 0.12), 1, .45, a[1], k * 1.3));
    });
    s.push(T(12, 36, K > 1.1 ? 'Arrivals · ICN' : 'Global arrivals · Incheon (ICN)', 'start', 14 * K, 500, GOLD, true));

    // capital hub (Seoul if present, else first capital site)
    var cap = sites.filter(function (x) { return CAPITAL[x.prov]; });
    var hub = cap.filter(function (x) { return x.prov === '11'; })[0] || cap[0];
    var hx = hub ? hub.x : M.prov['11'].c[0], hy = hub ? hub.y : M.prov['11'].c[1];
    s.push(route('r0-' + uid, curve(icn[0], icn[1], hx, hy, -0.25), 1.2, .7, 2.6, .2));
    // capital box + leader to inset
    var bx0 = I.sx, by0 = I.sy, bw = I.sw, bh = I.sh;
    s.push('<rect x="' + bx0 + '" y="' + by0 + '" width="' + bw + '" height="' + bh + '" rx="8" fill="none" stroke="' + GOLD + '" stroke-opacity=".55" stroke-width=".9" stroke-dasharray="3 4"/>');
    s.push('<path d="M' + (bx0 + bw / 2) + ' ' + (by0 + bh) + ' C ' + (bx0 + bw / 2 + 11) + ' 360, 330 470, ' + (I.x + 82) + ' ' + I.y + '" fill="none" stroke="' + GOLD + '" stroke-opacity=".3" stroke-width=".9" stroke-dasharray="2 4"/>');
    cap.forEach(function (x) { s.push(g(x.pcats || x.cats, '<circle cx="' + x.x.toFixed(1) + '" cy="' + x.y.toFixed(1) + '" r="2.6" fill="' + GOLD + '"/>')); });
    s.push('<rect x="' + (icn[0] - 3.5) + '" y="' + (icn[1] - 3.5) + '" width="7" height="7" transform="rotate(45 ' + icn[0] + ' ' + icn[1] + ')" fill="' + IVORY + '"/>');

    // regional clusters outside the capital area: one per province, routes from the capital hub
    var regional = GROUPS.filter(function (gp) { return !CAPITAL[gp.prov]; }).map(function (gp) {
      var x = 0, y = 0; gp.sites.forEach(function (q) { x += q.x; y += q.y; });
      return { prov: gp.prov, sites: gp.sites, x: x / gp.sites.length, y: y / gp.sites.length };
    });
    var taken = [{ x: I.x - 4, y: I.y - 4, w: I.w + 8, h: I.h + 8 }, { x: 0, y: 0, w: 360, h: 48 }, { x: 466, y: 10, w: 90, h: 84 }];
    regional.forEach(function (r) { taken.push({ x: r.x - 9, y: r.y - 9, w: 18, h: 18 }); });
    regional.forEach(function (r) {
      r.size = 16 * K; var en = EN[r.prov];  // no counts: region + field + number could point to one institution
      r.ko = SHORT[r.prov]; r.enT = en; r.w = Math.max(textW(r.ko, 16 * K), textW(en, 13 * K)); r.h = 34 * K;
    });
    placeLabels(regional, taken, { x: 0, y: 0, w: W, h: H });
    attachOrphans(regional, 90, function (r) { r.enT = EN[r.prov]; });
    var rop = regional.length > 6 ? .42 : .7;
    regional.forEach(function (r, k) {
      var cats = union(r.sites);
      var inner = route('r' + (k + 1) + '-' + uid, curve(hx, hy, r.x, r.y, -0.22), 1.2, rop, 4.4 + (k % 5) * .5, .4 + k * .5) + mk(r.x, r.y, r.orphan ? 3.6 : 5, (k * .4).toFixed(1));
      if (r.label) inner += T(r.label.x, r.label.y - 2, r.ko, r.label.anchor, 16 * K, 600, IVORY) + T(r.label.x, r.label.y + 14 * K, r.enT, r.label.anchor, 13 * K, 500, GOLD, true);
      s.push(g(cats, inner));
    });

    // inset: capital-area clusters
    s.push('<rect x="' + I.x + '" y="' + I.y + '" width="' + I.w + '" height="' + I.h + '" rx="14" fill="none" stroke="' + GOLD + '" stroke-opacity=".5" stroke-width=".9"/>');
    s.push(T(I.x + 4, I.y - 9, 'Seoul Capital Area', 'start', 13.5 * K, 500, GOLD, true));
    var ins = cluster(cap.filter(function (x) { return x.inset; }), 'ix', 'iy', 14);
    var hubIns = ins.filter(function (cl) { return cl.sites.indexOf(hub) > -1; })[0] || ins[0];
    var takenI = [{ x: icn[2] - 14, y: icn[3] - 8, w: 28, h: 34 }];
    ins.forEach(function (cl) { takenI.push({ x: cl.x - 8, y: cl.y - 8, w: 16, h: 16 }); });
    ins.forEach(function (cl) {
      cl.size = 12.5 * K; cl.ko = SHORT[cl.sites[0].prov];
      cl.w = textW(cl.ko, 12.5 * K); cl.h = 16 * K;
    });
    placeLabels(ins, takenI, { x: I.x + 2, y: I.y + 2, w: I.w - 4, h: I.h - 4 });
    attachOrphans(ins, 60, function (cl) { cl.ko = SHORT[cl.sites[0].prov]; });
    var seenP = {};
    ins.forEach(function (cl) { var p = cl.sites[0].prov; if (cl.label) { if (seenP[p]) cl.label = null; else seenP[p] = 1; } });
    if (hubIns) s.push(route('ci-' + uid, curve(icn[2], icn[3], hubIns.x, hubIns.y, -0.25), 1, .45, 3.4, .3));
    ins.forEach(function (cl, k) {
      var cats = punion(cl.sites), inner = '';
      if (hubIns && cl !== hubIns) inner += route('c' + k + '-' + uid, curve(hubIns.x, hubIns.y, cl.x, cl.y, -0.18), 1, .5, 2.4 + (k % 4) * .4, k * .45);
      inner += mk(cl.x, cl.y, cl.orphan ? 3.2 : 4.2, (k * .35).toFixed(2));
      if (cl.label) inner += T(cl.label.x, cl.label.y, cl.ko, cl.label.anchor, 12.5 * K, 600, IVORY);
      s.push(g(cats, inner));
    });
    s.push('<rect x="' + (icn[2] - 4.5) + '" y="' + (icn[3] - 4.5) + '" width="9" height="9" transform="rotate(45 ' + icn[2] + ' ' + icn[3] + ')" fill="' + IVORY + '"/>');
    s.push(T(icn[2], icn[3] + 20, 'ICN', 'middle', 10.5 * K, 600, IVORY));
    // Ulleung / Dokdo
    s.push('<rect x="470" y="14" width="80" height="76" rx="10" fill="none" stroke="' + GOLD + '" stroke-opacity=".35" stroke-width=".9"/>' +
      '<polygon points="' + M.islands + '" fill="#6E5646" fill-opacity=".7"/><circle cx="529" cy="56" r="2" fill="#9C7C62"/><circle cx="533" cy="57" r="1.6" fill="#9C7C62"/>' +
      T(496, 80, '울릉도', 'middle', 9.5, 500, '#B9A58F') + T(531, 80, '독도', 'middle', 9.5, 500, '#B9A58F'));
    s.push('</svg>');
    host.innerHTML = s.join('');
    // stop every map animation while the map is off screen
    var svgEl = host.querySelector('svg');
    if ('IntersectionObserver' in window && svgEl && svgEl.pauseAnimations) {
      new IntersectionObserver(function (es) {
        var on = es[0].isIntersecting;
        host.classList.toggle('is-off', !on);
        if (on) svgEl.unpauseAnimations(); else svgEl.pauseAnimations();
      }).observe(host);
    }
  });
})();
