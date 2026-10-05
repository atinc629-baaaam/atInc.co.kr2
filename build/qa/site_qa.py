import os, sys, json
from playwright.sync_api import sync_playwright
SP = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(f'{SP}/../../site')
OUT = f'{SP}/site_qa'
os.makedirs(OUT, exist_ok=True)
pages = sys.argv[1].split(',') if len(sys.argv) > 1 and sys.argv[1] != 'all' else sorted(f for f in os.listdir(SITE) if f.endswith('.html'))
widths = [int(w) for w in (sys.argv[2].split(',') if len(sys.argv) > 2 else ['1440', '390'])]
chunk = int(sys.argv[3]) if len(sys.argv) > 3 else 0
rep = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in widths:
        ctx = b.new_context(viewport={'width': w, 'height': 900}, device_scale_factor=1)
        for fn in pages:
            pg = ctx.new_page()
            errs = []
            pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + os.path.join(SITE, fn))
            pg.wait_for_timeout(1300)
            pg.add_style_tag(content='*,*::before,*::after{animation:none!important;transition:none!important}')
            info = pg.evaluate('''() => {
              const de = document.documentElement;
              const over = [];
              document.querySelectorAll('body *').forEach(el => { const r = el.getBoundingClientRect(); if (r.right > de.clientWidth + 1 && r.width > 0 && getComputedStyle(el).position !== 'fixed') over.push(el.tagName + '.' + (el.className && el.className.baseVal === undefined ? el.className : '')); });
              return {sw: de.scrollWidth, cw: de.clientWidth, h: de.scrollHeight, over: over.slice(0, 8)};
            }''')
            name = fn.replace('.html', '')
            pg.screenshot(path=f'{OUT}/{name}-{w}.png', full_page=True)
            if chunk:
                H = info['h']
                y = 0; k = 0
                while y < H:
                    hh = min(chunk, H - y)
                    pg.screenshot(path=f'{OUT}/{name}-{w}-c{k}.png', full_page=True, clip={'x': 0, 'y': y, 'width': w, 'height': hh})
                    y += chunk; k += 1
            rep[f'{name}@{w}'] = {'h': info['h'], 'hscroll': info['sw'] > info['cw'], 'over': info['over'], 'errors': errs[:5]}
            pg.close()
        ctx.close()
    b.close()
print(json.dumps(rep, ensure_ascii=False, indent=1))
