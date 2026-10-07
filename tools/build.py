#!/usr/bin/env python3
"""atInc 홈페이지 빌더

content/ (관리자가 고치는 내용, YAML) + templates/ (디자인 틀, Jinja) + static/ (CSS·JS·이미지)
→ site/ (공개되는 HTML)

    python3 tools/build.py            # site/ 에 만들기
    python3 tools/build.py --out DIR  # 다른 폴더에 만들기
"""
import argparse
import glob
import html
import json
import os
import re
import shutil
import sys

import yaml
from jinja2 import ChainableUndefined, Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'content')
TEMPLATES = os.path.join(ROOT, 'templates')
STATIC = os.path.join(ROOT, 'static')

FONTS = 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap'
PRET = 'https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css'


# ------------------------------------------------------------------ content
def load(path):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def load_collection(folder):
    items = [load(p) for p in glob.glob(os.path.join(CONTENT, folder, '*.yml'))]
    items = [x for x in items if not x.get('hidden')]
    return sorted(items, key=lambda x: (x.get('order', 999), x.get('id', '')))


# ------------------------------------------------------------------ helpers used by templates
ICONS = {
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'out': '<path d="M7 17L17 7M9 7h8v8"/>',
    'chev': '<path d="M6 9l6 6 6-6"/>',
    'check': '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    'menu': '<path d="M4 9h16M4 15h16"/>',
    'close': '<path d="M6 6l12 12M18 6L6 18"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 7l8.5 6 8.5-6"/>',
    'phone': '<path d="M6 3.5h3l1.6 4.4-2.1 1.3a11 11 0 006.3 6.3l1.3-2.1 4.4 1.6v3a2 2 0 01-2.2 2A16.5 16.5 0 014 5.7a2 2 0 012-2.2z"/>',
    'doc': '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 010 18M12 3a14 14 0 000 18"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0116 0"/>',
    'pin': '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0114 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'lock': '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/>',
    'file': '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/>',
}
# simple line icons (quick menu, slider buttons)
ICONS2 = {
    'chat': '<path d="M4 5.5h16v10H9.5L4 19.5z"/>',
    'bubble': '<path d="M4 5.5h16v10H9l-5 4v-14z"/>',
    'up': '<path d="M12 19V5M6 11l6-6 6 6"/>',
    'phone': '<path d="M6.5 3.5h3l1.5 4-2 1.3a10 10 0 0 0 6.2 6.2l1.3-2 4 1.5v3a2 2 0 0 1-2 2A16 16 0 0 1 4.5 5.5a2 2 0 0 1 2-2z"/>',
    'medical': '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M12 8.5v7M8.5 12h7"/>',
    'calendar': '<rect x="3.5" y="5" width="17" height="15" rx="1.5"/><path d="M3.5 9.5h17M8 3v4M16 3v4"/>',
    'pin': '<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
    'globe': '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.4 2.5 3.5 5.3 3.5 8.5s-1.1 6-3.5 8.5c-2.4-2.5-3.5-5.3-3.5-8.5s1.1-6 3.5-8.5z"/>',
    'prev': '<path d="M14.5 6l-6 6 6 6"/>', 'next': '<path d="M9.5 6l6 6-6 6"/>',
    'pause': '<path d="M9 6v12M15 6v12"/>', 'play': '<path d="M8 5.5l11 6.5-11 6.5z"/>',
}


def ic(name):
    return Markup('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
                  f'stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def ic2(name):
    return Markup(f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS2[name]}</svg>')


UPLOAD_WIDTHS_NEEDED = set()


def is_upload(src):
    return str(src or '').lstrip('/').startswith('uploads/')


def img_url(src, w):
    """Unsplash 사진은 크기를 주소로 고르고, 직접 올린 사진은 빌드 때 만든 크기별 사본을 씁니다."""
    src = str(src or '')
    if src.startswith('unsplash:'):
        return f'https://images.unsplash.com/photo-{src[9:]}?auto=format&fit=crop&w={w}&q=72'
    if is_upload(src):
        path = src.lstrip('/')
        if os.path.exists(os.path.join(STATIC, path)):
            UPLOAD_WIDTHS_NEEDED.add((path, w))
            stem, _ = os.path.splitext(os.path.basename(path))
            return f'uploads/r/{stem}-{w}.jpg'
        return path
    return src


def pic(img, cls='', sizes='100vw', widths=(640, 960, 1400, 2000), eager=False):
    """<img> for a photo object {src, alt, pos}. Unsplash photos and uploaded photos get a srcset."""
    if not img or not img.get('src'):
        return Markup('')
    src = str(img['src'])
    widths = list(widths)
    if src.startswith('unsplash:') or (is_upload(src) and os.path.exists(os.path.join(STATIC, src.lstrip('/')))):
        srcset = ' srcset="' + ', '.join(f'{img_url(src, w)} {w}w' for w in widths) + f'" sizes="{sizes}"'
    else:
        srcset = ''
    load = ' fetchpriority="high"' if eager else ' loading="lazy"'
    pos = f' style="object-position: {escape(img["pos"])}"' if img.get('pos') else ''
    return Markup(f'<img class="pic {cls}" src="{img_url(src, widths[min(1, len(widths) - 1)])}"{srcset} '
                  f'alt="{escape(img.get("alt", ""))}" decoding="async"{load}{pos}>')


def make_resized(out):
    """직접 올린 사진을 화면 크기별로 줄여 둡니다 (원본보다 크게 늘리지는 않습니다)."""
    if not UPLOAD_WIDTHS_NEEDED:
        return 0
    from PIL import Image, ImageOps
    n = 0
    for path, w in sorted(UPLOAD_WIDTHS_NEEDED):
        src = os.path.join(STATIC, path)
        stem, _ = os.path.splitext(os.path.basename(path))
        dst = os.path.join(out, 'uploads', 'r', f'{stem}-{w}.jpg')
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert('RGB')
            if im.width > w:
                im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            im.save(dst, 'JPEG', quality=80, optimize=True, progressive=True)
        n += 1
    return n


def rich(text):
    """Plain text with three small extras: line breaks, [링크](주소), and **굵게**."""
    if text is None:
        return Markup('')
    t = str(escape(str(text)))
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = t.replace('\n', '<br>')
    return Markup(t)


def doc(md):
    """문서 본문: '## 제목'은 소제목, '- '로 시작하는 줄은 목록, 빈 줄은 문단 나눔, 문단 안 줄바꿈은 그대로."""
    out, open_sec = [], False
    for block in re.split(r'\n\s*\n', str(md or '').strip()):
        ls = [re.sub(r'(\\| {2,})$', '', x.rstrip()) for x in block.strip().split('\n')]
        if ls and ls[0].startswith('## '):
            if open_sec:
                out.append('</section>')
            out.append(f'<section><h2>{rich(ls[0][3:].strip())}</h2>')
            open_sec = True
            ls = ls[1:]
        if not ls:
            continue
        if all(re.match(r'^[-*] ', x) for x in ls):
            out.append('<ul class="dots">' + ''.join(f'<li>{rich(x[2:].strip())}</li>' for x in ls) + '</ul>')
        else:
            out.append(f'<p>{rich(chr(10).join(ls))}</p>')
    if open_sec:
        out.append('</section>')
    return Markup(''.join(out))


def lines(text):
    return [x for x in str(text or '').split('\n')]


def josa(word, a, b):
    ch = str(word).strip()[-1]
    code = ord(ch) - 0xAC00
    has = 0 <= code <= 11171 and code % 28 != 0
    return str(word) + (a if has else b)


# ------------------------------------------------------------------ page assembly
def minify(h):
    return re.sub(r'>\s+<', '><', h.strip())


def typeset(body, keep):
    """Korean line-break care on phones: '…ㄹ 수 있다/없다' and listed phrases never split (text only)."""
    def fix(m):
        t = re.sub(r'(?<=\S) 수 (있|없)', ' 수 \\1', m.group(1))
        for k in keep:
            t = t.replace(k, k.replace(' ', ' '))
        return t
    return re.sub(r'(>[^<]*)', fix, body)


def structured_data(fn, body, S):
    site_url = S['site']['url']
    ld = []
    if fn == 'index.html':
        ld.append({'@context': 'https://schema.org', '@type': 'Organization', 'name': S['site']['name'],
                   'legalName': S['company']['legal_name'], 'url': site_url, 'logo': site_url + 'assets/og.png',
                   'email': S['contact']['email'], 'telephone': S['contact']['phone_schema'], 'areaServed': 'KR',
                   'description': S['site']['org_description']})
    cm = re.search(r'<nav class="crumb"[^>]*>(.*?)</nav>', body)
    if cm:
        its = re.findall(r'<a href="([^"]+)">([^<]+)</a>|<span>([^<]+)</span>', cm.group(1))
        el = []
        for i, (h, t, last) in enumerate(its, 1):
            el.append({'@type': 'ListItem', 'position': i, 'name': html.unescape(t or last),
                       'item': site_url + ('' if h == 'index.html' else (h or fn))})
        ld.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': el})
    faq = re.findall(r'<details><summary>(.*?)<svg.*?</summary><p class="body">(.*?)</p></details>', body)
    if faq:
        def tx(h):
            return html.unescape(re.sub(r'<[^>]+>', '', h)).strip()
        ld.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': tx(q), 'acceptedAnswer': {'@type': 'Answer', 'text': tx(a)}} for q, a in faq]})
    return ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False).replace('</', '<\\/') + '</script>' for x in ld)


class Site:
    def __init__(self, out):
        self.out = out
        self.S = load(os.path.join(CONTENT, 'settings.yml'))
        self.fields = load_collection('fields')
        self.programs = load_collection('programs')
        self.regions = load(os.path.join(CONTENT, 'regions.yml')).get('regions', [])
        self.pages = {os.path.splitext(os.path.basename(p))[0]: load(p) for p in glob.glob(os.path.join(CONTENT, 'pages', '*.yml'))}
        for f in self.fields:
            f.setdefault('page', f'medical-{f["id"]}.html')
        for p in self.programs:
            p.setdefault('page', f'care-{p["id"]}.html')
        self.env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(['html']),
                               trim_blocks=True, lstrip_blocks=True, undefined=ChainableUndefined)
        self.env.globals.update(ic=ic, ic2=ic2, pic=pic, rich=rich, lines=lines, josa=josa, img_url=img_url,
                                S=self.S, site=self.S, fields=self.fields, programs=self.programs, regions=self.regions,
                                form_url=self.S['contact']['form_url'])
        self.env.filters['rich'] = rich
        self.env.filters['josa'] = josa
        self.env.filters['doc'] = doc
        names = []
        for r in self.regions:
            if r.get('name') and r['name'] not in names:
                names.append(r['name'])
        self.env.globals['regions_text'] = ', '.join(names)
        self.built = []

    def render_sections(self, sections, ctx):
        out = []
        for i, s in enumerate(sections or []):
            if not s or s.get('hidden'):
                continue
            t = self.env.get_template(f'sections/{s["type"]}.html')
            out.append(t.render(s=s, idx=i, **ctx))
        return ''.join(out)

    def write_page(self, fn, data, cur=None, light=False, ctx=None):
        ctx = dict(ctx or {})
        ctx.setdefault('page', data)
        ctx['fn'] = fn
        main = minify(self.render_sections(data.get('sections'), ctx))
        glass = 'data-hdr-over' in main
        shell = self.env.get_template('base.html')
        body = minify(shell.render(main=Markup(main), cur=cur, glass=glass, light=light or glass, fn=fn))
        body = typeset(body, self.S['site'].get('keep_together', []))
        seo = data.get('seo') or {}
        title, desc = seo.get('title', ''), seo.get('description', '')
        url = self.S['site']['url'] + ('' if fn == 'index.html' else fn)
        head = minify(self.env.get_template('head.html').render(title=title, desc=desc, url=url, PRET=PRET, FONTS=FONTS))
        head += structured_data(fn, body, self.S)
        scripts = '<script src="assets/network-data.js"></script>'
        if 'class="atmap"' in body:
            scripts += '<script src="assets/map-base.js"></script>'
        scripts += '<script src="assets/map.js"></script><script src="assets/site.js"></script>'
        full = f'<!doctype html>\n<html lang="ko">\n<head>{head}</head>\n<body>\n{body}{scripts}\n</body>\n</html>\n'
        with open(os.path.join(self.out, fn), 'w', encoding='utf-8') as f:
            f.write(full)
        self.built.append(fn)

    def build(self):
        os.makedirs(self.out, exist_ok=True)
        self.copy_static()
        P = self.pages
        self.write_page('index.html', P['home'])
        self.write_page('about.html', P['about'], cur='about')
        self.write_page('medical.html', P['medical'], cur='medical')
        for f in self.fields:
            self.write_page(f['page'], f, cur='medical', light=True, ctx={'field': f})
        self.write_page('care.html', P['care'], cur='care')
        for p in self.programs:
            self.write_page(p['page'], p, cur='care', ctx={'program': p})
        self.write_page('network.html', P['network'], cur='network')
        self.write_page('partners.html', P['partners'], cur='partners')
        self.write_page('consultation.html', P['consultation'], cur='consult')
        self.write_page('privacy.html', P['privacy'], cur='legal')
        self.write_page('medical-notice.html', P['notice'], cur='legal')
        self.write_network_data()
        self.write_sitemap()
        n = make_resized(self.out)
        if n:
            print(n, 'resized photos')
        return self.built

    def copy_static(self):
        for root, dirs, files in os.walk(STATIC):
            for name in files:
                if name.startswith('.'):
                    continue
                src = os.path.join(root, name)
                dst = os.path.join(self.out, os.path.relpath(src, STATIC))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)

    def write_network_data(self):
        """content/regions.yml + 진료 분야 목록 → assets/network-data.js (지도와 지역 카드가 읽는 파일)"""
        fields = [{'id': f['id'], 'ko': f['ko']} for f in self.fields]
        regs = [{'area': r['area'], 'name': r['name'], 'short': r['name'], 'en': r.get('en', ''),
                 'cats': r.get('fields', []), 'note': r.get('note', '')} for r in self.regions if not r.get('hidden')]
        js = ('/* 자동으로 만들어지는 파일입니다. 고치지 마세요.\n'
              '   지역은 content/regions.yml, 분야 이름은 content/fields/*.yml 에서 고칩니다. */\n'
              'window.ATINC_FIELDS = ' + json.dumps(fields, ensure_ascii=False) + ';\n'
              'window.ATINC_NETWORK = ' + json.dumps(regs, ensure_ascii=False, indent=1) + ';\n')
        os.makedirs(os.path.join(self.out, 'assets'), exist_ok=True)
        with open(os.path.join(self.out, 'assets', 'network-data.js'), 'w', encoding='utf-8') as f:
            f.write(js)

    def write_sitemap(self):
        import datetime
        site_url = self.S['site']['url']
        today = datetime.date.today().isoformat()
        pri = {'index.html': '1.0', 'privacy.html': '0.2', 'medical-notice.html': '0.2'}
        urls = ''.join(f'<url><loc>{site_url}{"" if f == "index.html" else f}</loc><lastmod>{today}</lastmod><priority>{pri.get(f, "0.7")}</priority></url>' for f in self.built)
        with open(os.path.join(self.out, 'sitemap.xml'), 'w', encoding='utf-8') as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
        with open(os.path.join(self.out, 'robots.txt'), 'w', encoding='utf-8') as f:
            f.write(f'User-agent: *\nAllow: /\n\nSitemap: {site_url}sitemap.xml\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'site'))
    ap.add_argument('--only', help='comma separated page names (debug)')
    a = ap.parse_args()
    built = Site(a.out).build()
    print(len(built), 'pages →', a.out)


if __name__ == '__main__':
    main()
