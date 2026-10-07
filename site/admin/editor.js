/* atInc 홈페이지 편집기
   - 화면(편집용 사본 admin/edit/*.html)에서 글·사진·섹션을 고치면, content/*.json 의 값이 바뀝니다.
   - [저장]을 누르면 바뀐 파일과 올린 사진을 한 번에 GitHub에 커밋합니다 (GitHub API, 토큰 로그인).
   - GitHub Actions가 사이트를 다시 만들고 공개 전 검사를 한 뒤, 1~2분 뒤 홈페이지에 반영됩니다. */
(function () {
  'use strict';

  var REPO = 'atinc629-baaaam/atInc.co.kr2';
  var BRANCH = 'main';
  var params = new URLSearchParams(location.search);
  if (params.get('api')) sessionStorage.setItem('atinc.api', params.get('api'));
  var API = sessionStorage.getItem('atinc.api') || 'https://api.github.com';
  var TOKEN_KEY = 'atinc.editor.token';

  var SECTION_LABELS = {
    hero_slider: '첫 화면 슬라이드', quick_menu: '바로가기 메뉴', marquee: '흐르는 글자 띠', do_dont: '하는 일 / 하지 않는 일',
    field_tiles: '진료 분야 카드', program_tiles: '케어 프로그램 카드', flow: '진행 단계', network_preview: '전국 협력 의료기관',
    intl: '사진과 글', faq_home: '자주 묻는 질문', contact_home: '상담 안내', photo_hero: '첫 화면', ways: '번호 카드',
    services: '진료 목록', photo_band: '넓은 사진 띠', cards: '카드', steps: '진행 과정', guide: '준비·회복 안내',
    faq_more: '질문 + 더 알아보기', cband: '상담 띠', step_cards: '진행 단계 카드', facts: '숫자 카드', journey: '목적 목록',
    program_links: '다른 프로그램 링크', page_hero: '첫 화면', card_grid: '카드 묶음', company_info: '회사 정보',
    field_cards: '진료 분야 목록', access: '그 밖의 전문 진료', cta_row: '한 줄 안내', program_list: '케어 프로그램 목록',
    network: '지도 + 지역', partner_types: '함께 일하는 곳', two_lists: '두 칸 목록', partner_contact: '제휴 문의',
    form_fields: '신청서 항목', doc: '문서', text_block: '글 섹션'
  };
  var KIND_HINT = {
    text: '',
    lines: '줄을 바꾸면 화면에서도 그 자리에서 줄이 바뀝니다.',
    rich: '줄을 바꾸면 화면에서도 줄이 바뀝니다. 링크는 [글자](주소), 굵게는 **글자** 로 씁니다.',
    regions: '{regions} 라고 적힌 자리에 지역 이름(서울, 인천 …)이 자동으로 들어갑니다. 지우지 마세요.',
    paras: '빈 줄로 문단을 나눕니다. 링크는 [글자](주소), 굵게는 **글자** 로 씁니다.',
    doc: '“## 제목” 줄은 소제목, “- ”로 시작하는 줄은 목록, 빈 줄은 문단 나눔입니다. 링크는 [글자](주소).'
  };
  var KEY_LABELS = {
    site: '사이트', name: '이름', url: '사이트 주소', noindex: '검색엔진에 안 나오게 하기 (공개 전 확인 기간에만 켜 두고, 정식 공개 때 끄기)', theme_color: '휴대폰 주소창 색', org_description: '검색엔진용 회사 소개',
    keep_together: '휴대폰에서 줄이 바뀌면 안 되는 말 (한 줄에 하나)', contact: '연락처', email: '이메일', phone: '전화 (화면 표기)',
    phone_tel: '전화 (+82로 시작, 띄어쓰기 없이)', phone_intl: '전화 (해외 표기)', phone_schema: '전화 (검색엔진용)',
    form_url: '상담 신청서 주소 (구글 폼)', partner_mail: '제휴 문의 메일 (mailto:)', company: '회사 정보', legal_name: '법인명', ceo: '대표',
    biz_no: '사업자등록번호', tourism_no: '외국인환자 유치업 등록번호', address: '주소', nav: '메뉴 이름', footer: '바닥글',
    tagline: '한 줄', sub: '영문 한 줄', notice: '고지 문장', copyright: '저작권 표기', appt: '상담 예약 카드', title: '제목', rows: '안내 줄',
    k: '항목', v: '내용', form_note: '버튼 아래 작은 글', line_label: '전화 앞 글자', intl_en: '해외 안내 (영문)', intl_zh: '해외 안내 (중문)',
    cband: '상담 띠 기본값', label: '작은 영문 머리글', promises: '기본 안내 줄 (한 줄에 하나)', regions: '지역', area: '지도 위치 (행정구역, 화면에는 안 나옴)',
    en: '영문', fields: '받을 수 있는 분야', note: '지역 카드 한 줄', hidden: '숨기기', skip: '본문 바로가기', about: '회사소개', medical: '진료 분야',
    care: '케어 프로그램', network: '협력 네트워크', partners: '제휴 안내', consultation: '상담 안내', privacy: '개인정보처리방침',
    cta: '상담 예약 버튼', fab_call: '오른쪽 전화 버튼', fab_top: '맨 위로 버튼', mbar_call: '휴대폰 아래 전화 버튼'
  };
  var PUBLIC_RULES = [/최고/, /완벽/, /보장합/, /효과 보장/, /안전 보장/, /여성 의료진/, /\d[\d,]*\s*(원|만원|USD|\$)/];
  var FOCUS = [['25% 25%', '↖'], ['50% 25%', '↑'], ['75% 25%', '↗'], ['25% 50%', '←'], ['50% 50%', '●'], ['75% 50%', '→'], ['25% 75%', '↙'], ['50% 75%', '↓'], ['75% 75%', '↘']];

  var $ = function (id) { return document.getElementById(id); };
  var token = localStorage.getItem(TOKEN_KEY) || '';
  var index = null;                 // site-index.json
  var docs = {};                    // key → {data, sha, orig}
  var dirty = {};                   // key → true
  var uploads = {};                 // 'static/uploads/x.jpg' → {b64, url}
  var current = null;               // {page, file, label}
  var editOn = true;
  var frame = $('frame');
  var saving = false;

  // ------------------------------------------------------------------ small helpers
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function clone(x) { return JSON.parse(JSON.stringify(x)); }
  function toast(html, ms) {
    var t = $('toast'); t.innerHTML = html; t.hidden = false;
    clearTimeout(toast._t);
    if (ms !== 0) toast._t = setTimeout(function () { t.hidden = true; }, ms || 4200);
  }
  function notice(html, kind) {
    var n = $('notice');
    if (!html) { n.hidden = true; return; }
    n.className = 'notice' + (kind ? ' is-' + kind : ''); n.innerHTML = html; n.hidden = false;
  }
  function parsePath(p) { var i = p.indexOf('#'); var rest = p.slice(i + 1); return { key: p.slice(0, i), parts: rest ? rest.split('.') : [] }; }
  function getAt(o, parts) { for (var i = 0; i < parts.length; i++) { if (o == null) return undefined; o = Array.isArray(o) ? o[+parts[i]] : o[parts[i]]; } return o; }
  function setAt(o, parts, v) {
    for (var i = 0; i < parts.length - 1; i++) {
      var k = parts[i], nx = Array.isArray(o) ? o[+k] : o[k];
      if (nx == null) { nx = /^\d+$/.test(parts[i + 1]) ? [] : {}; if (Array.isArray(o)) o[+k] = nx; else o[k] = nx; }
      o = nx;
    }
    var last = parts[parts.length - 1];
    if (Array.isArray(o)) o[+last] = v; else o[last] = v;
  }
  function b64ToText(b64) { var bin = atob(b64.replace(/\n/g, '')); var u = new Uint8Array(bin.length); for (var i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return new TextDecoder().decode(u); }
  function sendFrame(msg) { msg.source = 'atinc-editor'; if (frame.contentWindow) frame.contentWindow.postMessage(msg, location.origin); }
  function dirtyCount() { return Object.keys(dirty).length + Object.keys(uploads).length; }
  function refreshButtons() {
    var n = dirtyCount(), s = $('btnSave');
    s.disabled = !n || saving; $('btnDiscard').disabled = !n || saving;
    s.classList.toggle('is-dirty', !!n); s.setAttribute('data-count', n);
    s.textContent = saving ? '저장 중…' : '저장';
  }
  function markDirty(key) { dirty[key] = true; refreshButtons(); }

  // ------------------------------------------------------------------ GitHub
  function gh(method, path, body) {
    return fetch(API + path, {
      method: method,
      headers: { 'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined, cache: 'no-store'
    }).then(function (r) {
      if (r.status === 204) return null;
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok) { var e = new Error(j.message || ('HTTP ' + r.status)); e.status = r.status; throw e; }
        return j;
      });
    });
  }
  function explain(e) {
    if (e.status === 401) return '열쇠(토큰)가 맞지 않거나 기간이 끝났습니다. 로그아웃한 뒤 새 토큰으로 다시 로그인하세요.';
    if (e.status === 403 || e.status === 404) return '이 토큰으로는 저장소에 저장할 수 없습니다. 토큰을 만들 때 atInc.co.kr2 저장소를 골랐는지, Contents 권한이 “Read and write”인지 확인하세요.';
    if (e.status === 409 || e.status === 422) return '다른 곳에서 먼저 저장된 내용과 겹쳤습니다. 잠시 뒤 다시 저장해 보세요.';
    return '연결에 문제가 생겼습니다 (' + esc(e.message) + '). 인터넷 연결을 확인하고 다시 시도하세요.';
  }
  function loadDoc(key) {
    if (docs[key]) return Promise.resolve(docs[key]);
    return gh('GET', '/repos/' + REPO + '/contents/content/' + key + '.json?ref=' + BRANCH).then(function (j) {
      var data = JSON.parse(b64ToText(j.content));
      docs[key] = { data: data, sha: j.sha, orig: JSON.stringify(data) };
      return docs[key];
    });
  }

  // ------------------------------------------------------------------ login
  function showLogin(msg) {
    $('app').hidden = true; $('login').hidden = false;
    $('loginMsg').textContent = msg || '';
    var u = new URL('https://github.com/settings/personal-access-tokens/new');
    u.searchParams.set('name', 'atInc 홈페이지 편집');
    u.searchParams.set('description', 'atInc 홈페이지 편집기에서 내용과 사진을 저장합니다');
    u.searchParams.set('target_name', REPO.split('/')[0]);
    u.searchParams.set('expires_in', '365');
    u.searchParams.set('contents', 'write');
    u.searchParams.set('actions', 'read');
    $('tokenLink').href = u.toString();
    $('repoName').textContent = REPO.split('/')[1];
  }
  $('loginForm').addEventListener('submit', function (e) {
    e.preventDefault();
    token = $('tokenInput').value.trim();
    $('loginMsg').textContent = '확인 중…';
    start();
  });
  $('btnLogout').addEventListener('click', function () {
    if (dirtyCount() && !confirm('저장하지 않은 변경이 있습니다. 그래도 로그아웃할까요?')) return;
    localStorage.removeItem(TOKEN_KEY); token = ''; dirty = {}; uploads = {}; docs = {};
    showLogin('로그아웃했습니다.');
  });

  function start() {
    if (!token) { showLogin(); return; }
    gh('GET', '/repos/' + REPO).then(function (repo) {
      if (!repo.permissions || !repo.permissions.push) throw Object.assign(new Error('no push'), { status: 403 });
      localStorage.setItem(TOKEN_KEY, token);
      $('login').hidden = true; $('app').hidden = false;
      return loadIndex().then(function () {
        var want = params.get('page') || sessionStorage.getItem('atinc.page') || 'index.html';
        openPage(want);
      });
    }).catch(function (e) {
      localStorage.removeItem(TOKEN_KEY);
      showLogin(explain(e));
    });
  }

  // ------------------------------------------------------------------ pages
  function loadIndex() {
    return fetch('site-index.json?t=' + Date.now(), { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (j) {
      index = j;
      var sel = $('pageSelect'), keep = sel.value;
      sel.innerHTML = j.pages.map(function (p) { return '<option value="' + esc(p.page) + '">' + esc(p.label) + '</option>'; }).join('');
      if (keep) sel.value = keep;
    });
  }
  function remoteVersions() {
    return gh('GET', '/repos/' + REPO + '/git/trees/' + BRANCH + '?recursive=1').then(function (t) {
      var v = {};
      (t.tree || []).forEach(function (e) { if (/^content\/.*\.json$/.test(e.path)) v[e.path] = e.sha; });
      return v;
    });
  }
  var waitTimer = null;
  function checkFresh() {
    // 화면(편집용 사본)이 GitHub의 최신 내용으로 만들어졌는지 확인합니다. 아니면 다시 만들어질 때까지 기다립니다.
    return Promise.all([loadIndex(), remoteVersions()]).then(function (res) {
      var remote = res[1], built = index.versions || {};
      var stale = Object.keys(remote).filter(function (p) { return built[p] !== remote[p]; });
      Object.keys(built).forEach(function (p) { if (!(p in remote)) stale.push(p); });
      return stale;
    });
  }
  function openPage(page, skipCheck) {
    if (!index) return;
    var p = index.pages.filter(function (x) { return x.page === page; })[0] || index.pages[0];
    if (dirtyCount() && current && p.page !== current.page) {
      if (!confirm('저장하지 않은 변경이 ' + dirtyCount() + '건 있습니다. 먼저 저장한 뒤 이동할까요?')) { $('pageSelect').value = current.page; return; }
      save().then(function (ok) { if (ok) openPage(p.page); else $('pageSelect').value = current.page; });
      return;
    }
    current = p;
    clearTimeout(waitTimer);
    sessionStorage.setItem('atinc.page', p.page);
    $('pageSelect').value = p.page;
    closePanel();
    var isItem = /^(fields|programs)\//.test(p.file);
    $('btnNewItem').hidden = $('btnHideItem').hidden = !isItem;
    $('linkSite').href = '../' + p.page;
    (skipCheck ? Promise.resolve([]) : checkFresh()).then(function (stale) {
      if (stale.length) { waitForBuild(p.page); return; }
      notice('');
      frame.src = 'edit/' + p.page + '?t=' + Date.now();
    }).catch(function (e) { notice(explain(e), 'err'); });
  }
  function waitForBuild(page, n) {
    n = n || 0;
    var now = ' <a href="#" data-open-now="' + esc(page) + '">기다리지 않고 지금 열기</a>';
    if (n < 20) notice('방금 저장한 내용으로 홈페이지를 다시 만드는 중입니다 (보통 1~2분). 다 되면 이 페이지를 자동으로 다시 엽니다.' + now);
    else notice('홈페이지를 다시 만드는 데 평소보다 오래 걸립니다. 공개 전 검사(병원 이름·가격·과장 표현)에서 멈췄을 수 있습니다. <a href="https://github.com/' + REPO + '/actions" target="_blank" rel="noopener">GitHub에서 확인</a> ·' + now, 'err');
    if (n === 0) frame.src = 'about:blank';
    clearTimeout(waitTimer);
    waitTimer = setTimeout(function () {
      checkFresh().then(function (stale) { if (stale.length) waitForBuild(page, n + 1); else { notice('최신 내용으로 다시 열었습니다.', 'ok'); setTimeout(function () { notice(''); }, 2500); frame.src = 'edit/' + page + '?t=' + Date.now(); } })
        .catch(function () { waitForBuild(page, n + 1); });
    }, 12000);
  }
  $('notice').addEventListener('click', function (e) {
    var a = e.target.closest('[data-open-now]');
    if (!a) return;
    e.preventDefault(); clearTimeout(waitTimer); notice('');
    frame.src = 'edit/' + a.getAttribute('data-open-now') + '?t=' + Date.now();
  });
  $('pageSelect').addEventListener('change', function () { openPage(this.value); });

  // ------------------------------------------------------------------ messages from the page
  window.addEventListener('message', function (e) {
    if (e.origin !== location.origin || !e.data || e.data.source !== 'atinc-page') return;
    var m = e.data;
    if (m.type === 'ready') {
      sendFrame({ type: 'labels', labels: SECTION_LABELS });
      sendFrame({ type: 'mode', on: editOn });
      reapplyPending();
    } else if (m.type === 'edit-text') editText(m.path, m.kind);
    else if (m.type === 'edit-img') editImage(m.path);
    else if (m.type === 'item-op') itemOp(m.op, m.path, m.section);
    else if (m.type === 'nav') openPage(m.page);
  });
  function reapplyPending() {
    // 다른 페이지에서 고친 공통 내용(사이트 설정 등)을 지금 화면에도 보여 줍니다
    var d = frame.contentDocument;
    if (!d) return;
    d.querySelectorAll('[data-e]').forEach(function (el) {
      var pp = parsePath(el.getAttribute('data-e'));
      if (dirty[pp.key] && docs[pp.key]) sendFrame({ type: 'set-text', path: el.getAttribute('data-e'), value: getAt(docs[pp.key].data, pp.parts) });
    });
  }

  // ------------------------------------------------------------------ panel
  function openPanel(title, html) {
    $('panelTitle').textContent = title; $('panelBody').innerHTML = html;
    $('panel').hidden = false; $('app').classList.add('panel-open');
  }
  function closePanel() { $('panel').hidden = true; $('app').classList.remove('panel-open'); sendFrame({ type: 'deselect' }); }
  $('panelClose').addEventListener('click', closePanel);
  function sharedNote(key) {
    if (current && key === current.file) return '';
    if (key === 'settings') return '<p class="shared">이 글은 <b>사이트 설정</b>에 있어서 모든 페이지에 함께 바뀝니다.</p>';
    if (/^(fields|programs)\//.test(key)) return '<p class="shared">이 글은 <b>' + (key.indexOf('fields/') === 0 ? '진료 분야' : '케어 프로그램') + '</b>의 이름·소개라서 메뉴와 다른 페이지에도 함께 바뀝니다.</p>';
    return '<p class="shared">다른 페이지의 내용입니다 (' + esc(key) + ').</p>';
  }
  function ruleWarn(text) {
    var hit = PUBLIC_RULES.filter(function (r) { return r.test(text || ''); });
    return hit.length ? '“최고·완벽·보장” 같은 표현이나 가격 표기는 공개 전 검사에서 막힙니다.' : '';
  }

  function editText(path, kind) {
    if (!editOn) return;
    var pp = parsePath(path);
    loadDoc(pp.key).then(function (doc) {
      var val = getAt(doc.data, pp.parts);
      val = val == null ? '' : String(val);
      var single = kind === 'text' && val.indexOf('\n') < 0 && val.length < 90;
      var field = single ? '<input type="text" id="tIn" value="' + esc(val) + '">'
        : '<textarea id="tIn" class="' + (kind === 'doc' ? 'is-big' : '') + '" rows="' + Math.min(14, Math.max(4, Math.ceil(val.length / 34))) + '">' + esc(val) + '</textarea>';
      openPanel('글 고치기', sharedNote(pp.key) + '<label>내용' + field + '</label>' +
        (KIND_HINT[kind] ? '<p class="hint">' + KIND_HINT[kind] + '</p>' : '') +
        '<p class="hint" id="tWarn" style="color: var(--warn)"></p>' +
        '<div class="panel__row"><button type="button" class="ebtn ebtn--main" id="tDone">완료</button><button type="button" class="ebtn" id="tUndo">처음 글로</button></div>');
      var input = $('tIn'), before = val;
      input.focus(); if (input.setSelectionRange) input.setSelectionRange(val.length, val.length);
      function apply(v) {
        setAt(doc.data, pp.parts, v); markDirty(pp.key);
        sendFrame({ type: 'set-text', path: path, value: v });
        $('tWarn').textContent = ruleWarn(v);
      }
      input.addEventListener('input', function () { apply(input.value); });
      input.addEventListener('keydown', function (e) { if (e.key === 'Enter' && single) { e.preventDefault(); closePanel(); } if (e.key === 'Escape') closePanel(); });
      $('tDone').addEventListener('click', closePanel);
      $('tUndo').addEventListener('click', function () { input.value = before; apply(before); });
    }).catch(function (e) { toast(explain(e)); });
  }

  // ------------------------------------------------------------------ photos
  function previewUrl(src) {
    src = String(src || '');
    var m = src.match(/images\.unsplash\.com\/photo-([^?#]+)/) || src.match(/^unsplash:(.+)$/);
    if (m) return 'https://images.unsplash.com/photo-' + m[1] + '?auto=format&fit=crop&w=800&q=70';
    var up = 'static' + (src.charAt(0) === '/' ? '' : '/') + src;
    if (uploads[up]) return uploads[up].url;
    if (/^\/?uploads\//.test(src)) return '../' + src.replace(/^\//, '');
    return src;
  }
  function editImage(path) {
    if (!editOn) return;
    var pp = parsePath(path);
    loadDoc(pp.key).then(function (doc) {
      var ph = getAt(doc.data, pp.parts) || {};
      var cur = ph.pos || '50% 50%';
      openPanel('사진 바꾸기', sharedNote(pp.key) +
        '<img class="imgprev" id="iPrev" alt="" src="' + esc(previewUrl(ph.src)) + '" style="object-position:' + esc(cur) + '">' +
        '<label class="ebtn ebtn--main" style="justify-content:center">내 컴퓨터에서 사진 고르기<input type="file" id="iFile" accept="image/jpeg,image/png,image/webp" hidden></label>' +
        '<p class="hint">사람 얼굴, 간판·로고, 수술·피 장면은 쓰지 않습니다. 협력 병원의 실제 사진은 병원 허락을 받은 것만 씁니다. 큰 사진은 자동으로 알맞게 줄여서 올립니다.</p>' +
        '<label>사진이 잘릴 때 남길 곳</label><div class="focus" id="iFocus">' + FOCUS.map(function (f) { return '<button type="button" data-pos="' + f[0] + '" class="' + (f[0] === cur ? 'is-on' : '') + '" title="' + f[0] + '">' + f[1] + '</button>'; }).join('') + '</div>' +
        '<label>사진 설명 (무엇이 보이는 사진인지)<input type="text" id="iAlt" value="' + esc(ph.alt || '') + '"></label>' +
        '<div class="panel__row"><button type="button" class="ebtn ebtn--main" id="iDone">완료</button></div>');
      $('iDone').addEventListener('click', closePanel);
      $('iFocus').addEventListener('click', function (e) {
        var b = e.target.closest('button[data-pos]'); if (!b) return;
        this.querySelectorAll('button').forEach(function (x) { x.classList.toggle('is-on', x === b); });
        var pos = b.getAttribute('data-pos');
        var o = getAt(doc.data, pp.parts) || {}; o.pos = pos; setAt(doc.data, pp.parts, o); markDirty(pp.key);
        $('iPrev').style.objectPosition = pos;
        sendFrame({ type: 'set-img', path: path, pos: pos });
      });
      $('iAlt').addEventListener('input', function () {
        var o = getAt(doc.data, pp.parts) || {}; o.alt = this.value; setAt(doc.data, pp.parts, o); markDirty(pp.key);
        sendFrame({ type: 'set-img', path: path, alt: this.value });
      });
      $('iFile').addEventListener('change', function () {
        var file = this.files && this.files[0];
        if (!file) return;
        toast('사진을 준비하는 중…', 0);
        shrink(file, 2400).then(function (res) {
          var stamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
          var name = 'uploads/' + stamp + '-' + Math.random().toString(36).slice(2, 7) + '.jpg';
          uploads['static/' + name] = { b64: res.b64, url: res.url };
          var o = getAt(doc.data, pp.parts) || {}; o.src = '/' + name; setAt(doc.data, pp.parts, o); markDirty(pp.key);
          $('iPrev').src = res.url;
          sendFrame({ type: 'set-img', path: path, url: res.url });
          toast('사진을 바꿨습니다. [저장]을 누르면 올라갑니다. (' + res.w + '×' + res.h + ')');
        }).catch(function () { toast('이 사진 파일은 열 수 없습니다. JPG나 PNG로 다시 골라 주세요.'); });
      });
    }).catch(function (e) { toast(explain(e)); });
  }
  function shrink(file, maxW) {
    return new Promise(function (resolve, reject) {
      var url = URL.createObjectURL(file), img = new Image();
      img.onload = function () {
        var w = img.naturalWidth, h = img.naturalHeight, s = Math.min(1, maxW / w);
        var c = document.createElement('canvas'); c.width = Math.round(w * s); c.height = Math.round(h * s);
        var g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height); g.drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        c.toBlob(function (blob) {
          if (!blob) { reject(); return; }
          var fr = new FileReader();
          fr.onload = function () { resolve({ b64: String(fr.result).split(',')[1], url: URL.createObjectURL(blob), w: c.width, h: c.height }); };
          fr.readAsDataURL(blob);
        }, 'image/jpeg', 0.86);
      };
      img.onerror = function () { URL.revokeObjectURL(url); reject(); };
      img.src = url;
    });
  }

  // ------------------------------------------------------------------ sections and list items
  function itemOp(op, path, isSection) {
    if (!editOn) return;
    var pp = parsePath(path);
    loadDoc(pp.key).then(function (doc) {
      var listParts = pp.parts.slice(0, -1), i = +pp.parts[pp.parts.length - 1];
      var list = getAt(doc.data, listParts);
      if (!Array.isArray(list) || i >= list.length) { toast('이 항목을 찾지 못했습니다. 페이지를 다시 열어 주세요.'); return; }
      if (op === 'up' && i === 0) { toast('맨 앞입니다.'); return; }
      if (op === 'down' && i === list.length - 1) { toast('맨 뒤입니다.'); return; }
      if (op === 'del' && !confirm((isSection ? '이 섹션을' : '이 항목을') + ' 지울까요? 저장하기 전에는 [모두 취소]로 되돌릴 수 있습니다.')) return;
      if (op === 'del' && list.length === 1 && !isSection) { toast('마지막 하나는 지울 수 없습니다. 내용을 고쳐 주세요.'); return; }
      if (op === 'up') { var a = list[i - 1]; list[i - 1] = list[i]; list[i] = a; }
      else if (op === 'down') { var b = list[i + 1]; list[i + 1] = list[i]; list[i] = b; }
      else if (op === 'dup') list.splice(i + 1, 0, clone(list[i]));
      else if (op === 'del') list.splice(i, 1);
      else if (op === 'hide') { if (list[i].hidden) delete list[i].hidden; else list[i].hidden = true; }
      markDirty(pp.key);
      closePanel();
      sendFrame({ type: 'apply-op', op: op, path: path });
      var msg = { up: '위로 옮겼습니다.', down: '아래로 옮겼습니다.', dup: '복제했습니다. 복제한 쪽을 눌러 고치세요.', del: '지웠습니다.', hide: list[i] && list[i].hidden ? '숨겼습니다. 홈페이지에는 안 보입니다.' : '다시 보이게 했습니다.' }[op];
      toast(msg + ' [저장]을 눌러야 홈페이지에 반영됩니다.');
    }).catch(function (e) { toast(explain(e)); });
  }

  // ------------------------------------------------------------------ forms (page info, settings, regions)
  function formFor(key, value, parts, depth) {
    var path = key + '#' + parts.join('.');
    var name = parts.length ? parts[parts.length - 1] : '';
    var parent = parts.length > 1 ? parts[parts.length - 2] : '';
    var label = KEY_LABELS[parent + '.' + name] || KEY_LABELS[name] || (/^\d+$/.test(name) ? '' : name);
    if (typeof value === 'boolean') return '<label class="checks"><input type="checkbox" data-path="' + esc(path) + '" data-t="bool"' + (value ? ' checked' : '') + '> ' + esc(label) + '</label>';
    if (typeof value === 'number') return '<label>' + esc(label) + '<input type="text" inputmode="numeric" data-path="' + esc(path) + '" data-t="num" value="' + esc(value) + '"></label>';
    if (typeof value === 'string') {
      var long = value.length > 60 || value.indexOf('\n') >= 0;
      return '<label>' + esc(label) + (long ? '<textarea data-path="' + esc(path) + '" rows="4">' + esc(value) + '</textarea>' : '<input type="text" data-path="' + esc(path) + '" value="' + esc(value) + '">') + '</label>';
    }
    if (Array.isArray(value)) {
      if (name === 'fields' && key === 'regions') {
        var opts = (index.fields || []).map(function (f) { return '<label><input type="checkbox" data-path="' + esc(path) + '" data-t="set" value="' + esc(f.id) + '"' + (value.indexOf(f.id) >= 0 ? ' checked' : '') + '> ' + esc(f.ko) + '</label>'; }).join('');
        return '<div><label>' + esc(label) + '</label><div class="checks">' + opts + '</div></div>';
      }
      if (value.every(function (x) { return typeof x === 'string'; })) {
        return '<label>' + esc(label) + '<textarea data-path="' + esc(path) + '" data-t="lines" rows="' + Math.max(3, value.length + 1) + '">' + esc(value.join('\n')) + '</textarea></label>';
      }
      return '<div class="fset"><div class="fset__head"><span>' + esc(label) + '</span><button type="button" class="mini" data-add="' + esc(path) + '">+ 추가</button></div>' +
        value.map(function (item, i) {
          var p2 = parts.concat([String(i)]);
          var title = item && (item.name || item.title || item.k || item.label) || (i + 1) + '번째';
          return '<div class="fset"><div class="fset__head"><span>' + esc(title) + (item && item.area ? ' · ' + esc(item.area) : '') + '</span>' +
            '<button type="button" class="mini" data-lop="up" data-lp="' + esc(key + '#' + p2.join('.')) + '">▲</button><button type="button" class="mini" data-lop="down" data-lp="' + esc(key + '#' + p2.join('.')) + '">▼</button>' +
            '<button type="button" class="mini" data-lop="del" data-lp="' + esc(key + '#' + p2.join('.')) + '">삭제</button></div>' +
            Object.keys(item || {}).map(function (k) { return formFor(key, item[k], p2.concat([k]), depth + 1); }).join('') + '</div>';
        }).join('') + '</div>';
    }
    if (value && typeof value === 'object') {
      var inner = Object.keys(value).map(function (k) { return formFor(key, value[k], parts.concat([k]), depth + 1); }).join('');
      return depth === 0 ? inner : '<div class="fset"><div class="fset__head"><span>' + esc(label) + '</span></div>' + inner + '</div>';
    }
    return '';
  }
  function bindForm(key, rerender) {
    var body = $('panelBody');
    body.addEventListener('input', function (e) {
      var el = e.target, path = el.getAttribute('data-path'); if (!path) return;
      var pp = parsePath(path), doc = docs[pp.key], t = el.getAttribute('data-t'), v;
      if (t === 'bool') v = el.checked;
      else if (t === 'num') { v = parseInt(el.value, 10); if (isNaN(v)) return; }
      else if (t === 'lines') v = el.value.split('\n').map(function (x) { return x.trim(); }).filter(Boolean);
      else if (t === 'set') { var cur = getAt(doc.data, pp.parts) || []; v = cur.filter(function (x) { return x !== el.value; }); if (el.checked) v.push(el.value); }
      else v = el.value;
      setAt(doc.data, pp.parts, v); markDirty(pp.key);
      if (typeof v === 'string') sendFrame({ type: 'set-text', path: path, value: v });
    });
    body.addEventListener('change', function (e) { if (e.target.type === 'checkbox') e.target.dispatchEvent(new Event('input', { bubbles: true })); });
    body.addEventListener('click', function (e) {
      var add = e.target.closest('[data-add]'), lop = e.target.closest('[data-lop]');
      if (!add && !lop) return;
      var pp = parsePath((add || lop).getAttribute(add ? 'data-add' : 'data-lp')), doc = docs[pp.key];
      if (add) {
        var list = getAt(doc.data, pp.parts);
        var blank = clone(list[list.length - 1] || {});
        Object.keys(blank).forEach(function (k) { if (typeof blank[k] === 'string') blank[k] = ''; else if (Array.isArray(blank[k])) blank[k] = []; else if (typeof blank[k] === 'boolean') blank[k] = false; });
        list.push(blank);
      } else {
        var lp = pp.parts.slice(0, -1), i = +pp.parts[pp.parts.length - 1], l = getAt(doc.data, lp), op = lop.getAttribute('data-lop');
        if (op === 'up' && i > 0) { var a = l[i - 1]; l[i - 1] = l[i]; l[i] = a; }
        if (op === 'down' && i < l.length - 1) { var b = l[i + 1]; l[i + 1] = l[i]; l[i] = b; }
        if (op === 'del') { if (!confirm('지울까요?')) return; l.splice(i, 1); }
      }
      markDirty(pp.key); rerender();
    });
  }
  function openForm(title, key, pick, intro) {
    loadDoc(key).then(function (doc) {
      function draw() {
        var v = pick ? pick(doc.data) : doc.data;
        var html = (intro || '') + (pick ? Object.keys(v).map(function (k) { return formFor(key, v[k].value, v[k].parts, 1).replace(/^<label>[^<]*/, '<label>' + esc(v[k].label)); }).join('') : formFor(key, v, [], 0));
        openPanel(title, html);
        bindForm(key, draw);
      }
      draw();
    }).catch(function (e) { toast(explain(e)); });
  }
  $('btnSettings').addEventListener('click', function () {
    openForm('사이트 설정', 'settings', null, '<p class="shared">연락처·회사 정보·메뉴 이름·바닥글·상담 카드처럼 모든 페이지에 함께 쓰이는 내용입니다.</p>');
  });
  $('btnRegions').addEventListener('click', function () {
    openForm('협력 지역', 'regions', null, '<p class="shared">지도와 지역 카드가 이 목록으로 만들어집니다. 화면에는 시·도 이름만 나오고, 병원 이름이나 병원을 알아볼 수 있는 내용(장비·규모·인증·재단)은 적지 않습니다. 지도는 저장 뒤 다시 만들어질 때 바뀝니다.</p>');
  });
  $('btnPage').addEventListener('click', function () {
    if (!current) return;
    var key = current.file, isItem = /^(fields|programs)\//.test(key);
    openForm('페이지 정보', key, function (d) {
      var out = {
        t: { label: '페이지 제목 (브라우저 탭·검색 결과)', value: (d.seo || {}).title || '', parts: ['seo', 'title'] },
        d: { label: '페이지 설명 (검색 결과 아래 글)', value: (d.seo || {}).description || '', parts: ['seo', 'description'] }
      };
      if (isItem) {
        out.o = { label: '메뉴·카드 순서 (작은 숫자가 먼저)', value: d.order || 0, parts: ['order'] };
        out.f = { label: '상담 신청서에 넘길 분야 이름', value: d.form_label || '', parts: ['form_label'] };
        if ('index_text' in d) out.x = { label: '진료 분야 목록 카드 설명', value: d.index_text, parts: ['index_text'] };
      }
      return out;
    }, isItem ? '<p class="shared">이름·영문 이름·대표 사진은 화면에서 눌러서 고칩니다.</p>' : '');
  });

  // ------------------------------------------------------------------ new / hide field or programme pages
  $('btnMore').addEventListener('click', function (e) { e.stopPropagation(); $('morePop').hidden = !$('morePop').hidden; });
  document.addEventListener('click', function () { $('morePop').hidden = true; });
  $('btnNewItem').addEventListener('click', function () {
    if (!current) return;
    var key = current.file, folder = key.split('/')[0];
    var kind = folder === 'fields' ? '진료 분야' : '케어 프로그램';
    var id = prompt('새 ' + kind + '의 영문 이름을 적어 주세요. 페이지 주소가 됩니다.\n영문 소문자, 숫자, - 만 (예: eye-care)');
    if (!id) return;
    id = id.trim().toLowerCase();
    if (!/^[a-z0-9-]+$/.test(id)) { alert('영문 소문자, 숫자, - 만 쓸 수 있습니다.'); return; }
    if (index.pages.some(function (p) { return p.file === folder + '/' + id; }) || docs[folder + '/' + id]) { alert('이미 있는 이름입니다.'); return; }
    var ko = prompt('한글 이름 (메뉴와 제목에 나옵니다)'); if (!ko) return;
    var en = prompt('영문 이름 (작은 영문 머리글, 예: Eye Care)') || '';
    loadDoc(key).then(function (doc) {
      var d = clone(doc.data);
      d.id = id; d.ko = ko.trim(); d.en = en.trim(); d.form_label = d.ko; delete d.hidden;
      var orders = index.pages.filter(function (p) { return p.file.indexOf(folder + '/') === 0; }).length;
      d.order = orders + 1;
      d.seo = { title: d.ko + ' | atInc', description: (d.seo && d.seo.description) || '' };
      var nk = folder + '/' + id;
      docs[nk] = { data: d, sha: null, orig: null };
      markDirty(nk);
      alert('“' + d.ko + '” 페이지를 지금 페이지 내용으로 복사해 두었습니다.\n[저장]을 누르면 1~2분 뒤 메뉴와 목록에 생깁니다. 그다음 그 페이지를 열어 내용을 고치세요.');
    });
  });
  $('btnHideItem').addEventListener('click', function () {
    if (!current) return;
    var key = current.file;
    if (!confirm('“' + current.label + '” 페이지를 홈페이지에서 숨길까요? 메뉴와 목록에서도 빠집니다. (지우지는 않으니 [숨긴 분야·프로그램 보기]에서 다시 보이게 할 수 있습니다)')) return;
    loadDoc(key).then(function (doc) { doc.data.hidden = true; markDirty(key); toast('숨기기로 표시했습니다. [저장]을 누르면 반영됩니다.'); });
  });
  $('btnHidden').addEventListener('click', function () {
    var list = (index && index.hidden) || [];
    openPanel('숨긴 분야·프로그램', list.length ? list.map(function (h) { return '<div class="fset"><div class="fset__head"><span>' + esc(h.label) + '</span><button type="button" class="mini" data-show="' + esc(h.file) + '">다시 보이기</button></div></div>'; }).join('') : '<p class="hint">숨긴 페이지가 없습니다.</p>');
    $('panelBody').addEventListener('click', function (e) {
      var b = e.target.closest('[data-show]'); if (!b) return;
      var key = b.getAttribute('data-show');
      loadDoc(key).then(function (doc) { delete doc.data.hidden; markDirty(key); b.textContent = '저장하면 보입니다'; b.disabled = true; });
    });
  });

  // ------------------------------------------------------------------ mode / device
  function setMode(on) {
    editOn = on;
    $('modeEdit').classList.toggle('is-on', on); $('modeView').classList.toggle('is-on', !on);
    $('help').hidden = !on;
    if (!on) closePanel();
    sendFrame({ type: 'mode', on: on });
  }
  $('modeEdit').addEventListener('click', function () { setMode(true); });
  $('modeView').addEventListener('click', function () { setMode(false); });
  $('viewPc').addEventListener('click', function () { $('stage').classList.remove('is-mobile'); this.classList.add('is-on'); $('viewMobile').classList.remove('is-on'); });
  $('viewMobile').addEventListener('click', function () { $('stage').classList.add('is-mobile'); this.classList.add('is-on'); $('viewPc').classList.remove('is-on'); });

  // ------------------------------------------------------------------ discard / save
  $('btnDiscard').addEventListener('click', function () {
    if (!confirm('저장하지 않은 변경 ' + dirtyCount() + '건을 모두 취소할까요?')) return;
    Object.keys(docs).forEach(function (k) { if (docs[k].orig === null) delete docs[k]; else docs[k].data = JSON.parse(docs[k].orig); });
    dirty = {}; uploads = {}; refreshButtons(); closePanel();
    if (current) frame.src = 'edit/' + current.page + '?t=' + Date.now();
    toast('변경을 모두 취소했습니다.');
  });
  $('btnSave').addEventListener('click', function () { save(); });
  window.addEventListener('beforeunload', function (e) { if (dirtyCount()) { e.preventDefault(); e.returnValue = ''; } });
  document.addEventListener('keydown', function (e) { if ((e.metaKey || e.ctrlKey) && e.key === 's') { e.preventDefault(); if (dirtyCount()) save(); } });

  function changedTexts() {
    var out = [];
    Object.keys(dirty).forEach(function (k) {
      (function walk(v) {
        if (typeof v === 'string') out.push(v);
        else if (Array.isArray(v)) v.forEach(walk);
        else if (v && typeof v === 'object') Object.keys(v).forEach(function (x) { walk(v[x]); });
      })(docs[k].data);
    });
    return out;
  }
  function save() {
    if (saving || !dirtyCount()) return Promise.resolve(true);
    var bad = changedTexts().filter(function (t) { return PUBLIC_RULES.some(function (r) { return r.test(t); }); });
    if (bad.length && !confirm('“최고·완벽·보장” 같은 표현이나 가격 표기가 있으면 공개 전 검사에서 막혀 홈페이지에 반영되지 않습니다.\n\n' + bad.slice(0, 3).map(function (t) { return '· ' + t.slice(0, 60); }).join('\n') + '\n\n그래도 저장할까요?')) return Promise.resolve(false);
    saving = true; refreshButtons(); closePanel();
    toast('저장하는 중…', 0);
    var files = Object.keys(dirty).map(function (k) { return { path: 'content/' + k + '.json', text: JSON.stringify(docs[k].data, null, 2) + '\n', key: k }; });
    Object.keys(uploads).forEach(function (p) { files.push({ path: p, b64: uploads[p].b64 }); });
    var label = current ? current.label : '';
    var msg = '편집기: ' + label + ' 수정' + (files.length > 1 ? ' 외 ' + (files.length - 1) + '건' : '');
    return commit(files, msg, 0).then(function (res) {
      files.forEach(function (f) { if (f.key) { docs[f.key].sha = res.blobs[f.path]; docs[f.key].orig = JSON.stringify(docs[f.key].data); } });
      dirty = {}; uploads = {};
      saving = false; refreshButtons();
      toast('저장했습니다. 홈페이지에 반영하는 중입니다 (보통 1~2분)…', 0);
      watch(res.sha, 0);
      return true;
    }).catch(function (e) {
      saving = false; refreshButtons();
      toast(e.conflict ? '다른 곳에서 같은 내용을 먼저 고쳐 저장했습니다. 지금 변경을 따로 적어 두고, [모두 취소] 후 다시 고쳐 주세요.' : explain(e), 0);
      return false;
    });
  }
  function commit(files, message, attempt) {
    var R = '/repos/' + REPO, baseSha, baseTree;
    return gh('GET', R + '/git/ref/heads/' + BRANCH).then(function (ref) {
      baseSha = ref.object.sha;
      return gh('GET', R + '/git/commits/' + baseSha);
    }).then(function (c) {
      baseTree = c.tree.sha;
      return gh('GET', R + '/git/trees/' + baseTree + '?recursive=1');
    }).then(function (tree) {
      var remote = {};
      (tree.tree || []).forEach(function (e) { remote[e.path] = e.sha; });
      var clash = files.filter(function (f) { return f.key && docs[f.key].sha && remote[f.path] && remote[f.path] !== docs[f.key].sha; });
      if (clash.length) { var err = new Error('conflict'); err.conflict = true; throw err; }
      return Promise.all(files.map(function (f) {
        return gh('POST', R + '/git/blobs', f.b64 ? { content: f.b64, encoding: 'base64' } : { content: f.text, encoding: 'utf-8' }).then(function (b) { f.sha = b.sha; });
      }));
    }).then(function () {
      return gh('POST', R + '/git/trees', { base_tree: baseTree, tree: files.map(function (f) { return { path: f.path, mode: '100644', type: 'blob', sha: f.sha }; }) });
    }).then(function (t) {
      return gh('POST', R + '/git/commits', { message: message, tree: t.sha, parents: [baseSha] });
    }).then(function (c) {
      return gh('PATCH', R + '/git/refs/heads/' + BRANCH, { sha: c.sha, force: false }).then(function () {
        var blobs = {}; files.forEach(function (f) { blobs[f.path] = f.sha; });
        return { sha: c.sha, blobs: blobs };
      });
    }).catch(function (e) {
      if (!e.conflict && (e.status === 422 || e.status === 409) && attempt < 3) return commit(files, message, attempt + 1);
      throw e;
    });
  }
  function watch(sha, n) {
    // 저장 뒤: GitHub Actions(사이트 빌드와 검사) 결과를 확인합니다
    setTimeout(function () {
      gh('GET', '/repos/' + REPO + '/actions/runs?head_sha=' + sha).then(function (j) {
        var run = (j.workflow_runs || []).filter(function (r) { return /빌드|build/i.test(r.name) && !/pages/i.test(r.name); })[0];
        if (!run || run.status !== 'completed') { if (n < 40) watch(sha, n + 1); else toast('저장은 됐습니다. 반영 결과는 GitHub의 Actions 화면에서 확인할 수 있습니다.'); return; }
        if (run.conclusion === 'success' || run.conclusion === 'cancelled' || run.conclusion === 'skipped') {
          // cancelled: 바로 뒤에 저장한 내용과 함께 한 번에 반영됩니다
          toast('반영됐습니다. 1분 정도 뒤 홈페이지에서 보입니다. <a href="../' + esc(current ? current.page : 'index.html') + '" target="_blank" rel="noopener">홈페이지 열기</a>', 12000);
        } else {
          toast('공개 전 검사에서 멈췄습니다. 병원 이름·가격·과장 표현이 들어갔는지 확인하고 고쳐서 다시 저장하세요. <a href="' + esc(run.html_url) + '" target="_blank" rel="noopener">자세히</a>', 0);
        }
      }).catch(function () { toast('저장했습니다. 1~2분 뒤 홈페이지에 반영됩니다.'); });
    }, n === 0 ? 6000 : 8000);
  }

  // ------------------------------------------------------------------ go
  frame.addEventListener('load', function () { if (frame.contentWindow) sendFrame({ type: 'mode', on: editOn }); });
  start();
})();
