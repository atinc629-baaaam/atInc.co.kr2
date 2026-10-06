"""ECC browser-qa + accessibility(WCAG 2.2 AA, axe 대체 자체 검사) + seo 감사.
사용: python3 ecc_qa.py [out.json]
"""
import os, sys, json, re
from playwright.sync_api import sync_playwright

SP = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(f'{SP}/../../site')
OUT = sys.argv[1] if len(sys.argv) > 1 else f'{SP}/qa_report.json'
pages = sorted(f for f in os.listdir(SITE) if f.endswith('.html'))

INIT = r'''
window.__cls = 0; window.__lcp = 0;
try {
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({type:'layout-shift', buffered:true});
  new PerformanceObserver(l => { const es = l.getEntries(); if (es.length) window.__lcp = es[es.length-1].startTime; }).observe({type:'largest-contentful-paint', buffered:true});
} catch(e) {}
'''

A11Y = r'''() => {
  const out = {contrast:[], alt:[], name:[], label:[], headings:[], dupId:[], landmarks:{}, target:[], focus:null, lang:document.documentElement.lang};
  const parse = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(s=>parseFloat(s)); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; };
  const lum = c => { const f = v => { v/=255; return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4); }; return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b); };
  const blend = (top, bot) => ({r:top.r*top.a+bot.r*(1-top.a), g:top.g*top.a+bot.g*(1-top.a), b:top.b*top.a+bot.b*(1-top.a), a:1});
  const bgOf = el => {
    const stack = []; let e = el;
    while (e && e.nodeType === 1) {
      const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none' && !/data:image\/svg/.test(cs.backgroundImage)) return {img:true};
      const c = parse(cs.backgroundColor); if (c && c.a > 0) { stack.push(c); if (c.a >= 1) break; }
      e = e.parentElement;
    }
    let base = {r:255,g:255,b:255,a:1};
    for (let i = stack.length-1; i>=0; i--) base = blend(stack[i], base);
    return base;
  };
  const vis = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); return r.width>0 && r.height>0 && cs.visibility!=='hidden' && cs.display!=='none' && parseFloat(cs.opacity)>0.05; };
  const seen = new Set();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const t = walker.currentNode; if (!t.textContent.trim()) continue;
    const el = t.parentElement; if (!el || seen.has(el)) continue; seen.add(el);
    if (!vis(el) || el.closest('[aria-hidden="true"],svg,script,style,noscript') || (el.closest('details:not([open])') && !el.closest('summary'))) continue;
    const cs = getComputedStyle(el); const fg = parse(cs.color); if (!fg) continue;
    const bg = bgOf(el); if (bg.img) continue;
    const f = blend(fg, bg);
    const L1 = lum(f), L2 = lum(bg); const ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
    const size = parseFloat(cs.fontSize), wt = parseInt(cs.fontWeight)||400;
    const large = size >= 24 || (size >= 18.66 && wt >= 700);
    const need = large ? 3 : 4.5;
    if (ratio < need) out.contrast.push({txt:t.textContent.trim().slice(0,30), sel:el.tagName.toLowerCase()+(el.className&&typeof el.className==='string'?'.'+el.className.split(' ').join('.'):''), ratio:+ratio.toFixed(2), need, size});
  }
  document.querySelectorAll('img').forEach(i => { if (!i.hasAttribute('alt')) out.alt.push(i.src.slice(-40)); });
  document.querySelectorAll('a[href],button,[role=button]').forEach(a => {
    if (!vis(a) || a.classList.contains('sr-only') || (a.closest('details:not([open])') && !a.closest('summary'))) return;
    const n = (a.getAttribute('aria-label')||a.innerText||a.title||'').trim() || (a.querySelector('img[alt]')||{}).alt;
    if (!n) out.name.push(a.outerHTML.slice(0,80));
    const r = a.getBoundingClientRect();
    const inline = getComputedStyle(a).display === 'inline' && a.closest('p,li,td,dd');
    if (!inline && (r.width < 24 || r.height < 24)) out.target.push({t:(a.innerText||a.getAttribute('aria-label')||'').trim().slice(0,20), w:Math.round(r.width), h:Math.round(r.height)});
  });
  document.querySelectorAll('input,select,textarea').forEach(f => { if (f.type==='hidden') return; const id=f.id; if (!(f.getAttribute('aria-label')||(id&&document.querySelector('label[for="'+id+'"]'))||f.closest('label'))) out.label.push(f.outerHTML.slice(0,60)); });
  let prev = 0; document.querySelectorAll('h1,h2,h3,h4,h5,h6').forEach(h => { const l = +h.tagName[1]; if (prev && l > prev+1) out.headings.push(`h${prev}→h${l} "${h.innerText.trim().slice(0,24)}"`); prev = l; });
  const ids = {}; document.querySelectorAll('[id]').forEach(e => ids[e.id]=(ids[e.id]||0)+1); out.dupId = Object.keys(ids).filter(k=>ids[k]>1);
  out.landmarks = {header:!!document.querySelector('header,[role=banner]'), nav:!!document.querySelector('nav'), main:document.querySelectorAll('main,[role=main]').length, footer:!!document.querySelector('footer'), skip:!!document.querySelector('a[href="#main"],a.skip,a[class*=skip]')};
  out.contrast = out.contrast.slice(0, 40); out.target = out.target.slice(0, 30);
  return out;
}'''

SEO = r'''() => {
  const q = s => document.querySelector(s); const m = n => (q(`meta[name="${n}"]`)||{}).content || '';
  const og = n => (q(`meta[property="og:${n}"]`)||{}).content || '';
  const ld = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => { try { const j = JSON.parse(s.textContent); return j['@type'] || (j['@graph']||[]).map(x=>x['@type']).join('+'); } catch(e) { return 'INVALID'; } });
  const links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
  return {title:document.title, tlen:document.title.length, desc:m('description'), dlen:m('description').length,
    h1:document.querySelectorAll('h1').length, h1t:(q('h1')||{}).innerText||'', canonical:(q('link[rel=canonical]')||{}).href||'',
    ogt:og('title'), ogd:og('description'), ogi:og('image'), ogu:og('url'), tw:m('twitter:card'), ld, favicon:!!q('link[rel~=icon]'),
    robots:m('robots'), viewport:m('viewport'), mailto:links.filter(h=>h.startsWith('mailto:')).length, tel:links.filter(h=>h.startsWith('tel:')).length,
    links, ids:[...document.querySelectorAll('[id]')].map(e=>e.id),
    blockingCss:[...document.querySelectorAll('link[rel=stylesheet]')].filter(l=>/googleapis/.test(l.href) && l.media!=='print').length,
    fontsHref:[...document.querySelectorAll('link[rel=stylesheet],link[rel=preload]')].map(l=>l.href).filter(h=>/fonts/.test(h)).length,
    words:document.body.innerText.length}
}'''

rep = {}
idmap = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (1440, 390):
        ctx = b.new_context(viewport={'width': w, 'height': 900})
        ctx.add_init_script(INIT)
        # photos are hotlinked from Unsplash; stand in for them when the network can't reach it
        ctx.route('https://images.unsplash.com/**', lambda r: r.fulfill(status=200, content_type='image/svg+xml', body='<svg xmlns="http://www.w3.org/2000/svg" width="16" height="10"><rect width="16" height="10" fill="#6b5444"/></svg>'))
        for fn in pages:
            pg = ctx.new_page()
            errs, bad = [], []
            pg.on('console', lambda mm: errs.append(mm.text) if mm.type == 'error' and 'TUNNEL' not in mm.text and 'fonts.g' not in mm.text else None)
            pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
            pg.on('requestfailed', lambda r: bad.append(r.url[-60:]) if 'fonts.g' not in r.url else None)
            pg.goto('http://127.0.0.1:8765/' + fn)
            pg.wait_for_timeout(1500)
            pg.mouse.wheel(0, 3000); pg.wait_for_timeout(400)
            perf = pg.evaluate('({cls:window.__cls, lcp:window.__lcp})')
            pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
            a = pg.evaluate(A11Y)
            key = f'{fn}@{w}'
            r = {'errors': errs[:6], 'failed': bad[:6], 'cls': round(perf['cls'], 3), 'lcp': round(perf['lcp']), 'a11y': a}
            if w == 1440:
                s = pg.evaluate(SEO)
                idmap[fn] = set(s.pop('ids'))
                r['seo'] = s
                # keyboard: first 6 tab stops must show a focus indicator
                foc = []
                for i in range(6):
                    pg.keyboard.press('Tab')
                    foc.append(pg.evaluate('''() => { const e = document.activeElement; if (!e || e===document.body) return null; const cs = getComputedStyle(e); const vis = (cs.outlineStyle!=='none' && parseFloat(cs.outlineWidth)>0) || cs.boxShadow!=='none' || /underline/.test(cs.textDecorationLine); return {t:(e.innerText||e.getAttribute('aria-label')||e.tagName).trim().slice(0,18), vis}; }'''))
                r['tab'] = foc
            rep[key] = r
            pg.close()
        ctx.close()
    b.close()

# broken internal links / anchors
broken = []
for fn, r in ((k.split('@')[0], v) for k, v in rep.items() if k.endswith('@1440')):
    for h in r['seo'].pop('links'):
        if h.startswith(('http', 'mailto:', 'tel:', 'javascript')):
            continue
        path, _, frag = h.partition('#')
        tgt = path or fn
        if path and not os.path.exists(os.path.join(SITE, path)):
            broken.append(f'{fn} → {h} (파일 없음)')
        elif frag and tgt in idmap and frag not in idmap[tgt]:
            broken.append(f'{fn} → {h} (앵커 없음)')
rep['_broken'] = sorted(set(broken))
json.dump(rep, open(OUT, 'w'), ensure_ascii=False, indent=1, default=list)

# summary
print('PAGE                          | ERR | CLS  | LCP  | contrast | target | name | hdg | dupId | lm(main/skip) | title/desc | h1 | can | og:i | ld | tab-vis')
tot = {'contrast': 0, 'target': 0, 'name': 0, 'hdg': 0}
for fn in pages:
    d, m = rep[f'{fn}@1440'], rep[f'{fn}@390']
    a, s = d['a11y'], d['seo']
    c = len(a['contrast']) + len(m['a11y']['contrast'])
    t = len(m['a11y']['target'])
    tot['contrast'] += c; tot['target'] += t; tot['name'] += len(a['name']); tot['hdg'] += len(a['headings'])
    tv = sum(1 for x in d['tab'] if x and x['vis'])
    print(f"{fn[:29]:29} | {len(d['errors'])+len(m['errors']):3} | {max(d['cls'], m['cls']):.2f} | {d['lcp']:4} | {c:8} | {t:6} | {len(a['name']):4} | {len(a['headings']):3} | {len(a['dupId']):5} | {a['landmarks']['main']}/{int(a['landmarks']['skip'])}           | {s['tlen']:3}/{s['dlen']:3}    | {s['h1']}  | {int(bool(s['canonical']))}   | {int(bool(s['ogi']))}    | {len(s['ld'])}  | {tv}/6")
print('TOTAL', tot, 'broken', len(rep['_broken']))
for x in rep['_broken'][:15]:
    print('  BROKEN', x)
