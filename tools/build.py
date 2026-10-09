#!/usr/bin/env python3
"""atInc 홈페이지 빌더

content/ (관리자가 고치는 내용, JSON) + templates/ (디자인 틀, Jinja) + static/ (CSS·JS·이미지)
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

from jinja2 import ChainableUndefined, Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'content')
TEMPLATES = os.path.join(ROOT, 'templates')
STATIC = os.path.join(ROOT, 'static')

FONTS = 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Noto+Serif+KR:wght@400;500;600&display=swap'
# 디자인 테마: static/assets/theme-<이름>.css 를 site.css 위에 덧씌웁니다 (사이트 설정 site.theme, 또는 --theme)
THEME_FONTS = {
    'a': 'https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;500&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,400;1,500&display=swap',
    'b': 'https://fonts.googleapis.com/css2?family=Hahmlet:wght@300;400;500&family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;1,6..96,400;1,6..96,500&display=swap',
    'c': 'https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Cormorant+Garamond:ital,wght@0,500;1,400;1,500&display=swap',
}
PRET = 'https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css'


# ------------------------------------------------------------------ content
def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def file_key(path):
    """content/fields/checkup.json → 'fields/checkup' (편집기가 쓰는 파일 이름)"""
    return os.path.splitext(os.path.relpath(path, CONTENT))[0].replace(os.sep, '/')


def load_collection(folder, include_hidden=False):
    items = []
    for p in glob.glob(os.path.join(CONTENT, folder, '*.json')):
        d = load(p)
        d['_key'] = file_key(p)
        items.append(d)
    if not include_hidden:
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

# 편집용 페이지(site/admin/edit/)를 만들 때만 켜집니다. 켜지면 글·사진·항목에 "어느 내용인지" 표시가 붙습니다.
EDIT = {'on': False}


def A(path, kind=None):
    """요소 하나가 값 하나만 담을 때: 그 요소에 편집 표시를 붙입니다."""
    if not EDIT['on']:
        return Markup('')
    k = f' data-k="{kind}"' if kind else ''
    return Markup(f' data-e="{escape(path)}"{k}')


def W(path, value, kind='text'):
    """값을 그대로 쓰되, 편집용 페이지에서는 표시가 붙은 span 으로 감쌉니다 (다른 내용과 섞여 있는 자리)."""
    v = rich(value) if kind == 'rich' else escape('' if value is None else value)
    if not EDIT['on']:
        return Markup(v)
    return Markup(f'<span data-e="{escape(path)}" data-k="{kind}">{v}</span>')


def IT(path):
    """목록 항목(카드·질문·단계 등): 편집기에서 복제·삭제·이동할 수 있게 표시합니다."""
    return Markup(f' data-item="{escape(path)}"') if EDIT['on'] else Markup('')


def unsplash_id(src):
    src = str(src or '')
    if src.startswith('unsplash:'):
        return src[9:]
    m = re.match(r'https?://images\.unsplash\.com/photo-([^?#]+)', src)
    return m.group(1) if m else None


def is_upload(src):
    return str(src or '').lstrip('/').startswith('uploads/')


def img_url(src, w):
    """Unsplash 사진은 크기를 주소로 고르고, 직접 올린 사진은 빌드 때 만든 크기별 사본을 씁니다."""
    src = str(src or '')
    uid = unsplash_id(src)
    if uid:
        return f'https://images.unsplash.com/photo-{uid}?auto=format&fit=crop&w={w}&q=72'
    if is_upload(src):
        path = src.lstrip('/')
        if os.path.exists(os.path.join(STATIC, path)):
            UPLOAD_WIDTHS_NEEDED.add((path, w))
            stem, _ = os.path.splitext(os.path.basename(path))
            return f'uploads/r/{stem}-{w}.jpg'
        return path
    return src


def pic(img, cls='', sizes='100vw', widths=(640, 960, 1400, 2000), eager=False, path=None):
    """<img> for a photo object {src, alt, pos}. Unsplash photos and uploaded photos get a srcset."""
    if not img or not img.get('src'):
        return Markup('')
    src = str(img['src'])
    widths = list(widths)
    if unsplash_id(src) or (is_upload(src) and os.path.exists(os.path.join(STATIC, src.lstrip('/')))):
        srcset = ' srcset="' + ', '.join(f'{img_url(src, w)} {w}w' for w in widths) + f'" sizes="{sizes}"'
    else:
        srcset = ''
    load = ' fetchpriority="high"' if eager else ' loading="lazy"'
    pos = f' style="object-position: {escape(img["pos"])}"' if img.get('pos') else ''
    ed = f' data-img="{escape(path)}"' if (EDIT['on'] and path) else ''
    return Markup(f'<img class="pic {cls}" src="{img_url(src, widths[min(1, len(widths) - 1)])}"{srcset} '
                  f'alt="{escape(img.get("alt", ""))}" decoding="async"{load}{pos}{ed}>')


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
    def __init__(self, out, theme=None, switcher=None, edit=True):
        self.out = out
        self.edit = edit  # False: 편집기 사본 없이 공개 페이지만 (디자인 후보용)
        self.S = load(os.path.join(CONTENT, 'settings.json'))
        self.theme = (theme if theme is not None else self.S['site'].get('theme', '')) or ''
        if self.theme and not os.path.exists(os.path.join(STATIC, 'assets', f'theme-{self.theme}.css')):
            raise SystemExit(f'theme-{self.theme}.css 가 없습니다')
        self.switcher = switcher  # 디자인 후보 비교용: [(이름, 폴더)] — 페이지 구석에 후보 바꾸기 단추
        self.fields = load_collection('fields')
        self.programs = load_collection('programs')
        self.regions = load(os.path.join(CONTENT, 'regions.json')).get('regions', [])
        self.pages = {os.path.splitext(os.path.basename(p))[0]: load(p) for p in glob.glob(os.path.join(CONTENT, 'pages', '*.json'))}
        for f in self.fields:
            f.setdefault('page', f'medical-{f["id"]}.html')
        for p in self.programs:
            p.setdefault('page', f'care-{p["id"]}.html')
        self.env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(['html']),
                               trim_blocks=True, lstrip_blocks=True, undefined=ChainableUndefined)
        self.env.globals.update(A=A, W=W, IT=IT, ic=ic, ic2=ic2, pic=pic, rich=rich, lines=lines, josa=josa, img_url=img_url,
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
        pf = ctx.get('pf', '')
        for i, s in enumerate(sections or []):
            if not s or (s.get('hidden') and not EDIT['on']):
                continue
            P = f'{pf}#sections.{i}'
            t = self.env.get_template(f'sections/{s["type"]}.html')
            h = t.render(s=s, idx=i, P=P, **ctx).strip()
            if EDIT['on']:
                # 섹션 맨 바깥 태그에 '몇 번째 섹션인지' 표시 (편집기에서 이동·숨기기·복제·삭제)
                mark = f' data-item="{escape(P)}" data-sec="{escape(s["type"])}"' + (' data-hidden="1"' if s.get('hidden') else '')
                h = re.sub(r'^<([a-zA-Z0-9]+)', lambda m: '<' + m.group(1) + mark, h, count=1)
            out.append(h)
        return ''.join(out)

    def write_page(self, fn, data, cur=None, light=False, ctx=None, pf=''):
        ctx = dict(ctx or {})
        ctx.setdefault('page', data)
        ctx['fn'] = fn
        ctx['pf'] = pf
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
        if self.theme:
            if THEME_FONTS.get(self.theme):
                head += f'<link rel="stylesheet" href="{THEME_FONTS[self.theme]}">'
            head += f'<link rel="stylesheet" href="assets/theme-{self.theme}.css">'
        scripts = '<script src="assets/network-data.js"></script>'
        if 'class="atmap"' in body:
            scripts += '<script src="assets/map-base.js"></script>'
        scripts += '<script src="assets/map.js"></script><script src="assets/site.js"></script>'
        target = os.path.join(self.out, fn)
        if self.S['site'].get('noindex') and not EDIT['on']:
            # 공개 전 확인 기간: 검색엔진에 안 나오게 합니다 (사이트 설정에서 끕니다)
            head = '<meta name="robots" content="noindex, nofollow">' + head
        if EDIT['on']:
            # 편집용 사본: site/admin/edit/<페이지>. 주소 기준을 사이트 맨 위로 맞추고, 편집기 도구를 붙입니다
            info = json.dumps({'page': fn, 'file': pf, 'title': title}, ensure_ascii=False).replace('</', '<\\/')
            head = ('<base href="../../"><meta name="robots" content="noindex, nofollow">' + head +
                    '<link rel="stylesheet" href="admin/inject.css">'
                    f'<script type="application/json" id="atinc-edit">{info}</script>')
            scripts += '<script src="admin/inject.js"></script>'
            target = os.path.join(self.out, 'admin', 'edit', fn)
            os.makedirs(os.path.dirname(target), exist_ok=True)
        if self.switcher and not EDIT['on']:
            here = self.theme or 'cur'
            links = ''.join(f'<a href="../{folder}/{fn}"{" aria-current=\"true\"" if folder == here else ""}>{escape(name)}</a>' for name, folder in self.switcher)
            body += ('<nav class="cand" aria-label="디자인 후보"><span>디자인 후보</span>' + links + '</nav>'
                     '<style>.cand{position:fixed;z-index:60;left:16px;bottom:16px;display:flex;align-items:center;gap:2px;padding:4px;border-radius:999px;'
                     'background:rgba(20,16,13,.86);box-shadow:0 10px 30px -10px rgba(0,0,0,.5);font:600 13px/1 "Pretendard Variable",Pretendard,sans-serif;letter-spacing:0}'
                     '.cand span{padding:0 10px 0 12px;color:#cdbba5;font-weight:500}.cand a{padding:8px 12px;border-radius:999px;color:#fff;text-decoration:none}'
                     '.cand a[aria-current]{background:#fff;color:#2a1e17}@media(max-width:760px){.cand{left:50%;bottom:68px;transform:translateX(-50%)}.cand span{display:none}}</style>')
        html_attr = f' data-theme="{self.theme}"' if self.theme else ''
        full = f'<!doctype html>\n<html lang="ko"{html_attr}>\n<head>{head}</head>\n<body>\n{body}{scripts}\n</body>\n</html>\n'
        with open(target, 'w', encoding='utf-8') as f:
            f.write(full)
        if not EDIT['on']:
            self.built.append(fn)

    def all_pages(self):
        """(파일 이름, 내용, 메뉴 위치, 밝은 머리글, 추가 값, 내용 파일 이름, 편집기 목록 이름)"""
        P = self.pages
        yield 'index.html', P['home'], None, False, {}, 'pages/home', '홈'
        yield 'about.html', P['about'], 'about', False, {}, 'pages/about', '회사소개'
        yield 'medical.html', P['medical'], 'medical', False, {}, 'pages/medical', '진료 분야 목록'
        for f in self.fields:
            yield f['page'], f, 'medical', True, {'field': f}, f['_key'], '진료 분야 · ' + f['ko']
        yield 'care.html', P['care'], 'care', False, {}, 'pages/care', '케어 프로그램 목록'
        for p in self.programs:
            yield p['page'], p, 'care', False, {'program': p}, p['_key'], '케어 프로그램 · ' + p['ko']
        yield 'network.html', P['network'], 'network', False, {}, 'pages/network', '협력 네트워크'
        yield 'partners.html', P['partners'], 'partners', False, {}, 'pages/partners', '제휴 안내'
        yield 'consultation.html', P['consultation'], 'consult', False, {}, 'pages/consultation', '상담 안내'
        yield 'privacy.html', P['privacy'], 'legal', False, {}, 'pages/privacy', '개인정보처리방침'
        yield 'medical-notice.html', P['notice'], 'legal', False, {}, 'pages/notice', '의료서비스 관련 고지'

    def build(self):
        os.makedirs(self.out, exist_ok=True)
        # 지난번에 만든 파일을 비웁니다 (지운 페이지·사진이 남지 않도록). 이 빌드가 만든 폴더일 때만 비웁니다.
        if os.path.exists(os.path.join(self.out, 'index.html')) and os.path.isdir(os.path.join(self.out, 'assets')):
            for name in os.listdir(self.out):
                p = os.path.join(self.out, name)
                shutil.rmtree(p) if os.path.isdir(p) and not os.path.islink(p) else os.remove(p)
        self.copy_static()
        pages = list(self.all_pages())
        for fn, data, cur, light, ctx, pf, label in pages:
            self.write_page(fn, data, cur=cur, light=light, ctx=ctx, pf=pf)
        if self.edit:
            # 편집기용 사본과 목록
            EDIT['on'] = True
            try:
                for fn, data, cur, light, ctx, pf, label in pages:
                    self.write_page(fn, data, cur=cur, light=light, ctx=ctx, pf=pf)
            finally:
                EDIT['on'] = False
            self.write_editor_index(pages)
        self.write_network_data()
        self.write_sitemap()
        n = make_resized(self.out)
        if n:
            print(n, 'resized photos')
        # 디자인 후보 비교: 사이트 설정 site.candidates 에 적힌 테마마다 candidates/<이름>/ 에 사이트 전체를 한 벌씩 만듭니다
        cands = [c for c in (self.S['site'].get('candidates') or []) if c]
        if cands and self.edit:
            sw = [('현재', 'cur')] + [(c.upper(), c) for c in cands]
            for name, folder in sw:
                Site(os.path.join(self.out, 'candidates', folder), theme='' if folder == 'cur' else folder,
                     switcher=sw, edit=False).build()
            print('디자인 후보:', ', '.join(f for _, f in sw), '→ candidates/')
        return self.built

    def write_editor_index(self, pages):
        """편집기가 읽는 목록: 페이지 목록, 내용 파일 버전(바뀌었는지 확인용), 숨긴 분야·프로그램"""
        import hashlib

        def blob_sha(path):
            data = open(path, 'rb').read()
            return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()
        versions = {}
        for path in glob.glob(os.path.join(CONTENT, '**', '*.json'), recursive=True):
            versions[os.path.relpath(path, ROOT).replace(os.sep, '/')] = blob_sha(path)
        hidden = [{'file': x['_key'], 'label': x.get('ko', x['_key'])} for x in load_collection('fields', True) + load_collection('programs', True) if x.get('hidden')]
        index = {'pages': [{'page': fn, 'file': pf, 'label': label} for fn, data, cur, light, ctx, pf, label in pages],
                 'fields': [{'id': f['id'], 'ko': f['ko']} for f in self.fields],
                 'versions': versions, 'hidden': hidden}
        os.makedirs(os.path.join(self.out, 'admin'), exist_ok=True)
        with open(os.path.join(self.out, 'admin', 'site-index.json'), 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=1)

    def copy_static(self):
        for root, dirs, files in os.walk(STATIC):
            if not self.edit and os.path.relpath(root, STATIC).split(os.sep)[0] == 'admin':
                continue
            for name in files:
                if name.startswith('.'):
                    continue
                src = os.path.join(root, name)
                dst = os.path.join(self.out, os.path.relpath(src, STATIC))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)

    def write_network_data(self):
        """content/regions.json + 진료 분야 목록 → assets/network-data.js (지도와 지역 카드가 읽는 파일)"""
        fields = [{'id': f['id'], 'ko': f['ko']} for f in self.fields]
        regs = [{'area': r['area'], 'name': r['name'], 'short': r['name'], 'en': r.get('en', ''),
                 'cats': r.get('fields', []), 'note': r.get('note', '')} for r in self.regions if not r.get('hidden')]
        js = ('/* 자동으로 만들어지는 파일입니다. 고치지 마세요.\n'
              '   지역은 content/regions.json, 분야 이름은 content/fields/*.json 에서 고칩니다. */\n'
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
            if self.S['site'].get('noindex'):
                f.write('User-agent: *\nDisallow: /\n')
            else:
                f.write(f'User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {site_url}sitemap.xml\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'site'))
    ap.add_argument('--theme', default=None, help='디자인 테마 (a, b, c …). 비워 두면 사이트 설정 site.theme')
    ap.add_argument('--switcher', default=None, help='디자인 후보 비교 단추: "현재:cur,A:a,B:b" (폴더 이름)')
    ap.add_argument('--check', action='store_true', help='만든 뒤 공개 전 검사(금지 표현·비공개 단어)를 하고, 문제가 있으면 실패로 끝냅니다')
    a = ap.parse_args()
    sw = [tuple(x.split(':', 1)) for x in a.switcher.split(',')] if a.switcher else None
    built = Site(a.out, theme=a.theme, switcher=sw).build()
    print(len(built), 'pages →', a.out)
    if a.check:
        import subprocess
        here = os.path.dirname(os.path.abspath(__file__))
        r1 = subprocess.run([sys.executable, os.path.join(here, 'qa', 'site_scan.py'), a.out])
        r2 = subprocess.run([sys.executable, os.path.join(here, 'qa', 'edit_marks.py'), a.out])
        if r2.returncode:
            print('\n편집용 표시가 내용과 맞지 않습니다. 템플릿을 고친 뒤 다시 만드세요.')
            sys.exit(1)
        if r1.returncode:
            print('\n공개 전 검사에서 문제가 나와 공개를 멈춥니다. 위 내용을 고친 뒤 다시 저장하세요.')
            sys.exit(1)


if __name__ == '__main__':
    main()
