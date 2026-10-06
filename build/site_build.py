import os, re, html, shutil, sys, json
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import mapsvg

SRC = f'{SP}/content'
OUT = os.path.normpath(f'{SP}/../site')  # 배포용 폴더
FONTS = 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap'
PRET = 'https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css'
PROG_KO = {'private-checkup': '프라이빗 정밀검진', 'longevity-90': '90일 롱제비티', 'executive-365': '연간 헬스 오피스', 'global-medical-journey': '글로벌 메디컬 저니'}
FORM_URL = 'https://docs.google.com/forms/d/e/1FAIpQLScWj8HadYKhN0u5T3_wSdlQ-C8OEm1KLfwsCdRxDvk8ebdHuA/viewform'
EMAIL = 'atinc@atinc.co.kr'
VIP = '010-5857-0129'
VIP_TEL = '+821058570129'
SITE_URL = 'https://atinc.co.kr/'
PARTNER_MAIL = 'mailto:atinc@atinc.co.kr?subject=%5B%EC%A0%9C%ED%9C%B4%20%EB%AC%B8%EC%9D%98%5D%20'  # [제휴 문의]
COMPANY_ADDRESS = ''  # 주소가 정해지면 입력하면 푸터·ABOUT·고지에 표시됩니다
HERO = 'assets/img/hero.jpg'
ARCH = 'assets/img/arch.jpg'


def E(s):
    return html.escape(str(s), quote=True)


# ------------------------------------------------------------------ icons
_P = {
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


def ic(n):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_P[n]}</svg>'


# category tile motifs (line drawings for photo slots)
MOTIF = {
    'checkup': '<circle cx="50" cy="50" r="34"/><circle cx="50" cy="50" r="22"/><path d="M18 52h18l6-14 8 26 7-18 5 6h20"/>',
    'regenerative': '<circle cx="50" cy="46" r="15"/><circle cx="27" cy="62" r="10"/><circle cx="73" cy="62" r="10"/><circle cx="36" cy="28" r="7"/><circle cx="66" cy="27" r="6"/><circle cx="50" cy="78" r="7"/>',
    'aesthetic': '<path d="M14 40c12-10 24-10 36 0s24 10 36 0"/><path d="M14 54c12-10 24-10 36 0s24 10 36 0"/><path d="M14 68c12-10 24-10 36 0s24 10 36 0"/>',
    'women': '<circle cx="50" cy="34" r="13"/><circle cx="34" cy="52" r="13"/><circle cx="66" cy="52" r="13"/><circle cx="50" cy="68" r="13"/><circle cx="50" cy="51" r="4"/>',
    'men': '<rect x="24" y="24" width="52" height="52" rx="4"/><circle cx="50" cy="50" r="18"/><path d="M24 76L76 24"/>',
    'korean-medicine': '<path d="M50 84C50 60 30 50 22 26c22 2 34 18 28 58z"/><path d="M50 84c0-24 20-34 28-58-22 2-34 18-28 58z"/><path d="M50 84V44"/>',
    'care': '<path d="M24 82V44a26 26 0 0152 0v38"/><path d="M36 82V48a14 14 0 0128 0v34"/><path d="M16 82h68"/>',
}


def tile(motif='care', cls='ph--45 ph--round', label=''):
    return (f'<div class="tile {cls}" role="img" aria-label="{E(label)}">'
            f'<svg viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{MOTIF[motif]}</svg></div>')


def photo(src, pos='50% 50%', cls='ph--45 ph--arch', label=''):
    return f'<div class="ph {cls}" role="img" aria-label="{E(label)}" style="background-image: url({src}); background-position: {pos}"></div>'


# ------------------------------------------------------------------ markdown
SRC_TAGS = ['기존 의료 고지', '협력기관 자료', '협력사 자료', '공개자료', '기존']


def unesc(t):
    t = t.replace('&#91;', '[')
    return re.sub(r'\\([\[\]_~*#|>\-.!()])', r'\1', t)


def clean(t):
    t = unesc(t)
    for tg in SRC_TAGS:
        t = t.replace(f'[{tg}]', '')
    t = t.replace('**', '')
    return re.sub(r'\s{2,}', ' ', t).strip()


def row(line):
    return [clean(c) for c in re.split(r'(?<!\\)\|', line.strip())[1:-1]]


def parse(fn):
    lines = open(f'{SRC}/{fn}', encoding='utf-8').read().split('\n')
    doc = {'sections': []}
    sec = None
    blk = None

    def cur_sec():
        nonlocal sec
        if sec is None:
            sec = {'title': None, 'intro': [], 'blocks': []}
            doc['sections'].append(sec)
        return sec

    def add(it):
        if blk is not None:
            blk['items'].append(it)
        elif sec is not None:
            sec['intro'].append(it)

    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('# '):
            pass
        elif ln.startswith('## '):
            sec = {'title': clean(ln[3:]), 'intro': [], 'blocks': []}
            doc['sections'].append(sec)
            blk = None
        elif ln.startswith('### '):
            h = clean(ln[4:])
            m = re.match(r'^(\d\d)\s+(.*)$', h)
            blk = {'no': m.group(1) if m else None, 'title': m.group(2) if m else h, 'items': []}
            cur_sec()['blocks'].append(blk)
        elif ln.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append(lines[i]); i += 1
            t = {'type': 'table', 'headers': row(rows[0]), 'rows': [row(r) for r in rows[2:]]}
            add(t) if (blk is not None or sec is not None) else None
            if blk is None and sec is not None and re.match(r'^\d\d ', t['headers'][0]):
                sec['intro'].pop()
                m = re.match(r'^(\d\d)\s+(.*)$', t['headers'][0])
                sec['blocks'].append({'no': m.group(1), 'title': m.group(2), 'items': [t]})
            continue
        elif re.match(r'^\s*- ', ln):
            raw = re.sub(r'^\s*- ', '', ln)
            sub = ln.startswith(' ')
            m = re.match(r'^\*\*(.+?)\*\*\s*(.*)$', raw)
            if m:
                key, val = clean(m.group(1)), clean(m.group(2))
                val = re.sub(r'^—\s*', '', val)
                mm = re.match(r'^(\d\d)\s+(.*)$', key)
                if mm and blk is None and sec is not None and not sub:
                    sec['blocks'].append({'no': mm.group(1), 'title': mm.group(2), 'items': [{'type': 'text', 'text': val}]})
                else:
                    add({'type': 'field', 'key': key, 'value': val, 'sub': sub})
            else:
                add({'type': 'bullet', 'text': clean(raw)})
        elif re.match(r'^\d+\. ', ln):
            raw = re.sub(r'^\d+\. ', '', ln)
            m = re.match(r'^\*\*(.+?)\*\*\s*(?:—\s*)?(.*)$', raw)
            if m:
                add({'type': 'step', 'title': clean(m.group(1)), 'text': clean(m.group(2))})
            else:
                add({'type': 'step', 'title': '', 'text': clean(raw)})
        elif re.match(r'^\*\*[^*]+\*\*$', ln.strip()):
            add({'type': 'subhead', 'text': clean(ln)})
        elif ln.startswith('>') or ln.startswith('!['):
            pass
        elif ln.strip():
            t = clean(ln)
            if t:
                add({'type': 'text', 'text': t})
        i += 1
    return doc


def blocks(doc, section=None):
    out = {}
    for s in doc['sections']:
        if section is None or (s['title'] or '').startswith(section):
            for b in s['blocks']:
                out[b['no'] or b['title']] = b
    return out


def fields(b):
    d = {}
    for it in b['items']:
        if it['type'] == 'field' and it['key'] not in d:
            d[it['key']] = it['value']
    return d


def items(b, t):
    return [it for it in b['items'] if it['type'] == t]


def table(b):
    t = items(b, 'table')
    return t[0] if t else None


def btn_label(v):
    v = re.sub(r'\s*\((?:Google Forms|관심 분야)[^)]*\)', '', v)
    v = re.sub(r'\s*\((?:MEDICAL|ABOUT|FOR PARTNERS|atinc CARE)\)', '', v)
    return v.strip()


def prefill(v, default=''):
    m = re.search(r'관심 분야:\s*([^)]+?)(?:\s*미리 선택)?\)', v)
    return m.group(1).strip() if m else default


def photos(v):
    return [(c, cap.strip(' ,·')) for c, cap in re.findall(r'\[([A-Z]\d?-\d\d[a-z]?)\]\s*([^\[]*)', v)]


def josa(word, a, b):
    ch = word.strip()[-1]
    code = ord(ch) - 0xAC00
    has = 0 <= code <= 11171 and code % 28 != 0
    return word + (a if has else b)


# ------------------------------------------------------------------ site data
CATS = [
    dict(id='checkup', ko='건강검진', en='Precision Checkup', file='03-1_건강검진.md', page='medical-checkup.html', pos='72% 50%', card=(ARCH, '50% 34%')),
    dict(id='regenerative', ko='재생의료·줄기세포', en='Regenerative & Cell Care', file='03-2_재생의료_줄기세포.md', page='medical-regenerative.html', pos='86% 40%', card=(HERO, '78% 48%')),
    dict(id='aesthetic', ko='성형·피부', en='Aesthetic & Dermatology', file='03-3_성형_피부.md', page='medical-aesthetic.html', pos='64% 60%', card=(ARCH, '40% 62%')),
    dict(id='women', ko='여성건강', en="Women's Health", file='03-4_여성건강.md', page='medical-women.html', pos='78% 30%', card=(HERO, '62% 70%')),
    dict(id='men', ko='남성건강', en="Men's Health", file='03-5_남성건강.md', page='medical-men.html', pos='92% 55%', card=(ARCH, '72% 46%')),
    dict(id='korean-medicine', ko='한방·웰니스', en='Korean Medicine & Wellness', file='03-6_한방_웰니스.md', page='medical-korean-medicine.html', pos='70% 72%', card=(HERO, '92% 60%')),
]
CAT_BY_KO = {c['ko']: c for c in CATS}
CARE = [
    dict(id='private-checkup', en='PRIVATE CHECKUP', two=('PRIVATE', 'CHECKUP'), page='care-private-checkup.html', pos='100% 55%'),
    dict(id='longevity-90', en='LONGEVITY 90', two=('LONGEVITY', '90'), page='care-longevity-90.html', pos='88% 90%'),
    dict(id='executive-365', en='EXECUTIVE 365', two=('EXECUTIVE', '365'), page='care-executive-365.html', pos='100% 25%'),
    dict(id='global-medical-journey', en='GLOBAL MEDICAL JOURNEY', two=('GLOBAL MEDICAL', 'JOURNEY'), page='care-global-medical-journey.html', pos='78% 60%'),
]
HUBS = [  # mirrors site/assets/network-data.js (what can be done in each region, never which hospital)
    dict(id='seoul-gangnam', name='서울', en='Seoul', cats=['checkup', 'women', 'korean-medicine'], line='정밀 건강검진과 여성 진료, 한방 미용 진료를 받으실 수 있습니다.'),
    dict(id='incheon-songdo', name='인천', en='Incheon', cats=['aesthetic'], line='공항에서 가까운 곳에서 성형·피부 상담과 시술을 받으실 수 있습니다.'),
    dict(id='incheon-geomdan', name='인천', en='Incheon', cats=['korean-medicine', 'aesthetic'], line='한·양방 협진 진료와 입원 회복, 성형·피부 진료를 받으실 수 있습니다.'),
    dict(id='incheon-bupyeong', name='인천', en='Incheon', cats=['korean-medicine'], line='한방 진료와 재활, 입원 치료를 받으실 수 있습니다.'),
    dict(id='incheon-namdong', name='인천', en='Incheon', cats=['korean-medicine'], line='뇌졸중 재활처럼 회복이 오래 걸릴 때 입원해서 치료받으실 수 있습니다.'),
    dict(id='gyeonggi-bundang', name='경기', en='Gyeonggi', cats=['regenerative'], line='재생의료 진료 상담과 세포 보관 상담을 받으실 수 있습니다.'),
    dict(id='gyeonggi-gunpo', name='경기', en='Gyeonggi', cats=['regenerative'], line='본인 세포의 배양과 보관 상담을 받으실 수 있습니다.'),
    dict(id='gyeonggi-yongin', name='경기', en='Gyeonggi', cats=['checkup'], line='정밀 건강검진을 받으실 수 있습니다.'),
    dict(id='daegu', name='대구', en='Daegu', cats=['women', 'men'], line='난임 검사와 시험관아기, 가임력 보존, 남성 난임 진료를 받으실 수 있습니다.'),
    dict(id='busan', name='부산', en='Busan', cats=['checkup'], line='정밀 건강검진과 외국어 안내를 받으실 수 있습니다.'),
]
HUB = {h['name']: h for h in HUBS}
CAT_KO = {c['id']: c['ko'] for c in CATS}

home = parse('01_HOME.md')
HB = blocks(home)
about = parse('02_ABOUT.md')
AB = blocks(about)
medical = parse('03_MEDICAL_인덱스.md')
care = parse('04_atinc_CARE.md')
net = parse('05_NETWORK_PARTNERS_상담_LEGAL.md')

PROMISES = ['신청서에는 연락처와 관심 분야 같은 기본 정보만 적으시면 됩니다', '고르신 방법(전화·카카오톡·이메일)으로 담당 매니저가 먼저 연락드립니다', '필요한 자료는 통화한 뒤에 알려 드립니다']


# ------------------------------------------------------------------ shell
# ------------------------------------------------------------------ photos (build/photos.json)
PHOTOS = json.load(open(f'{SP}/photos.json', encoding='utf-8'))


def photo_url(key, w):
    src = PHOTOS[key]['src']
    if src.startswith('unsplash:'):
        return f'https://images.unsplash.com/photo-{src[9:]}?auto=format&fit=crop&w={w}&q=72'
    return src


def pic(key, cls='', sizes='100vw', widths=(640, 960, 1400, 2000), eager=False):
    p = PHOTOS[key]
    if p['src'].startswith('unsplash:'):
        srcset = ' srcset="' + ', '.join(f'{photo_url(key, w)} {w}w' for w in widths) + f'" sizes="{sizes}"'
    else:
        srcset = ''
    load = ' fetchpriority="high"' if eager else ' loading="lazy"'
    pos = f' style="object-position: {p["pos"]}"' if p.get('pos') else ''
    return f'<img class="pic {cls}" src="{photo_url(key, widths[min(1, len(widths) - 1)])}"{srcset} alt="{E(p["alt"])}" decoding="async"{load}{pos}>'


def form_link(label, cat='', cls='btn btn--dark', icon='out'):
    return f'<a class="{cls}" href="{FORM_URL}" target="_blank" rel="noopener" data-form="{E(cat)}">{E(label)}{ic(icon) if icon else ""}</a>'


def contact_links(cls='contacts', tel=True, intl=False, style=''):
    st = f' style="{style}"' if style else ''
    t = f'<a href="tel:{VIP_TEL}">{ic("phone")}매니저 직통 {VIP}</a>' if tel else ''
    out = f'<div class="{cls}"{st}><a href="mailto:{EMAIL}">{ic("mail")}{EMAIL}</a>{t}</div>'
    if intl:
        out += (f'<div class="intl"><p lang="en">From overseas, email us or call <a href="tel:{VIP_TEL}">+82 10 5857 0129</a>.</p>'
                f'<p lang="zh-Hans">海外客户请发送电子邮件，或致电 <a href="tel:{VIP_TEL}">+82 10 5857 0129</a>。</p></div>')
    return out


def logo(tag='a', href='index.html', extra=''):
    inner = '<i>at</i><b>Inc</b>'
    if tag == 'a':
        return f'<a class="logo" href="{href}" aria-label="atinc 홈"{extra}>{inner}</a>'
    return f'<span class="logo"{extra}>{inner}</span>'


def header(cur):
    def nl(href, label, key):
        a = ' aria-current="page"' if cur == key else ''
        return f'<a class="nav__link" href="{href}"{a}>{label}</a>'
    med = ''.join(f'<a href="{c["page"]}">{E(c["ko"])}<span>{E(c["en"])}</span></a>' for c in CATS)
    car = ''.join(f'<a href="{p["page"]}">{E(PROG_KO[p["id"]])}<span>{E(p["en"].title() if p["id"] != "global-medical-journey" else "Global Medical Journey")}</span></a>' for p in CARE)
    mcur = ' is-current' if cur == 'medical' else ''
    ccur = ' is-current' if cur == 'care' else ''
    return (f'<a class="sr-only" href="#main">본문 바로가기</a>'
            f'<header class="hdr"><div class="wrap hdr__wrap"><div class="hdr__in" data-glass-hdr>{logo()}'
            f'<nav class="nav" aria-label="주 메뉴">{nl("about.html", "회사소개", "about")}'
            f'<div class="nav__item"><a class="nav__link{mcur}" href="medical.html">진료 분야{ic("chev")}</a><div class="drop">{med}</div></div>'
            f'<div class="nav__item"><a class="nav__link{ccur}" href="care.html">케어 프로그램{ic("chev")}</a><div class="drop">{car}</div></div>'
            f'{nl("network.html", "협력 네트워크", "network")}{nl("partners.html", "제휴 안내", "partners")}</nav>'
            f'<div class="hdr__right"><a class="hdr__tel" href="tel:{VIP_TEL}" aria-label="매니저 직통 {VIP}">{ic("phone")}<span>{VIP}</span></a>{form_link("상담 예약", "", "hdr__cta", None)}'
            f'<button class="menu-btn" id="menu-open" type="button" aria-controls="mnav" aria-expanded="false" aria-label="메뉴 열기">{ic("menu")}</button></div>'
            f'</div></div></header>')


def mnav():
    med = ''.join(f'<a href="{c["page"]}">{E(c["ko"])}</a>' for c in CATS)
    car = ''.join(f'<a href="{p["page"]}">{E(PROG_KO[p["id"]])}</a>' for p in CARE)
    return (f'<div class="mnav" id="mnav" hidden role="dialog" aria-modal="true" aria-label="전체 메뉴">'
            f'<div class="mnav__top">{logo()}<button class="menu-btn" id="menu-close" type="button" aria-label="메뉴 닫기" style="display: inline-flex">{ic("close")}</button></div>'
            f'<div class="mnav__group"><h2 class="eyebrow"><a href="medical.html" style="text-decoration: none">진료 분야</a></h2><div class="mnav__grid">{med}</div></div>'
            f'<div class="mnav__group"><h2 class="eyebrow"><a href="care.html" style="text-decoration: none">케어 프로그램</a></h2><div class="mnav__grid">{car}</div></div>'
            f'<div class="mnav__group mnav__links"><a href="about.html">회사소개</a><a href="network.html">협력 네트워크</a><a href="partners.html">제휴 안내</a><a href="consultation.html">상담 안내</a></div>'
            f'{form_link("상담 예약", "", "btn btn--dark btn--wide")}'
            f'{contact_links("contacts contacts--dark", style="margin-top: 18px")}</div>')


def company_line():
    parts = ['주식회사 애트 (atinc)', '대표 한수연', '사업자등록번호 369-87-03095', '외국인환자 유치업 등록번호 제 A-2026-08-01-07161 호']
    if COMPANY_ADDRESS:
        parts.append(COMPANY_ADDRESS)
    return ' · '.join(parts)


def footer():
    med = ''.join(f'<li><a href="{c["page"]}">{E(c["ko"])}</a></li>' for c in CATS)
    car = ''.join(f'<li><a href="{p["page"]}">{E(PROG_KO[p["id"]])}</a></li>' for p in CARE)
    return (f'<footer class="ftr"><div class="wrap"><div class="ftr__top">'
            f'<div>{logo()}<p class="ftr__tag">엄선된 의료, 조용한 동행</p><p class="ftr__sub">Private Healthcare Concierge</p>'
            f'<p class="ftr__contact"><a href="tel:{VIP_TEL}">{VIP}</a><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>'
            f'<div><h2>진료 분야</h2><ul>{med}</ul></div><div><h2>케어 프로그램</h2><ul>{car}</ul></div>'
            f'<div><h2>atinc</h2><ul><li><a href="about.html">회사소개</a></li><li><a href="network.html">협력 네트워크</a></li><li><a href="partners.html">제휴 안내</a></li><li><a href="consultation.html">상담 안내</a></li></ul></div></div>'
            f'<div class="ftr__bot"><div class="ftr__legal"><a href="privacy.html">개인정보처리방침</a><a href="medical-notice.html">의료서비스 관련 고지</a></div>'
            f'<p>{E(company_line())}</p>'
            f'<p>atinc는 의료기관이 아닌 헬스케어 컨시어지입니다. 검사·진단·치료는 협력 의료기관의 의료진이 맡고, atinc는 그 앞뒤의 상담·예약·통역·사후관리를 맡습니다. 사이트의 사진은 이해를 돕기 위한 참고 이미지이며, 협력 의료기관의 실제 시설이 아닙니다.</p>'
            f'<p>© 2026 atinc. All rights reserved.</p></div></div></footer>')


def quick_contact():
    """Floating consult buttons (desktop) and a bottom bar (phones)."""
    chat = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5h16v10H9l-5 4v-14z"/></svg>'
    tel = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 3.5h3l1.5 4-2 1.3a10 10 0 0 0 6.2 6.2l1.3-2 4 1.5v3a2 2 0 0 1-2 2A16 16 0 0 1 4.5 5.5a2 2 0 0 1 2-2z"/></svg>'
    up = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg>'
    return (f'<div class="fab"><a class="fab__btn fab__btn--main" href="{FORM_URL}" target="_blank" rel="noopener" data-form="">{chat}<span>상담 예약</span></a>'
            f'<a class="fab__btn" href="tel:{VIP_TEL}">{tel}<span>매니저 통화</span></a>'
            f'<button class="fab__btn fab__top" type="button" data-top>{up}<span>맨 위로</span></button></div>'
            f'<nav class="mbar" aria-label="빠른 상담"><a href="tel:{VIP_TEL}">{tel}매니저와 통화</a>'
            f'<a class="mbar__main" href="{FORM_URL}" target="_blank" rel="noopener" data-form="">{chat}상담 예약</a></nav>')


# ------------------------------------------------------------------ notices: same facts, written as atinc's principle (not a disclaimer)
PRINCIPLE = {
    '사이트에는 싣지 않고, 클리닉 상담에서 안내받을 수 있습니다.': '시술 전후 사례는 클리닉 상담에서 직접 안내받으실 수 있습니다.',
    '검사 항목의 필요성, 진단 및 추가 진료 여부는 제휴 의료기관과 담당 의료진의 판단에 따라 결정됩니다.':
        '어떤 검사가 필요한지, 추가 진료가 필요한지는 담당 의료진이 판단합니다. atinc는 그 판단에 필요한 가족력·복용약·기존 자료를 미리 정리해 전달하고, 결과 이후의 일정까지 놓치지 않도록 끝까지 관리합니다.',
    '검사 항목의 필요성, 진단 및 추가 진료 여부는 의료기관과 담당 의료진의 판단에 따라 결정됩니다.':
        '어떤 검사가 필요한지, 추가 진료가 필요한지는 담당 의료진이 판단합니다. atinc는 그 판단에 필요한 가족력·복용약·기존 자료를 미리 정리해 전달하고, 결과 이후의 일정까지 놓치지 않도록 끝까지 관리합니다.',
    '검사의 필요성과 임상적 의미, 치료 및 의학적 관리의 구체적인 내용은 의료기관과 의료진이 판단하고 설명합니다.':
        '검사의 의미와 치료·관리 방향은 의료진이 판단하고 직접 설명합니다. atinc는 그 설명이 실제 90일의 실행으로 이어지도록 기록하고, 점검하고, 다음 진료로 다시 연결합니다.',
    '세포치료·재생의료 등은 국가와 기관별 적용 범위 및 승인 여부가 다르며, atinc는 효과를 보장하거나 직접 판매하지 않습니다. 실제 의료행위는 의료기관의 적법한 상담과 의료진의 판단에 따라 진행됩니다.':
        '세포치료·재생의료처럼 나라와 기관마다 허용 범위가 다른 진료는, 적법한 의료기관의 상담과 의료진의 판단으로만 진행합니다. atinc는 효과를 앞세워 권하거나 의료를 직접 판매하지 않고, 정확한 정보로 결정하실 수 있도록 확인하고 연결합니다.',
    '의학적 응급상황에 직접 대응하는 응급의료 서비스가 아니라, 고객에게 적합한 의료기관과 진료 경로를 신속하게 안내하고 조율하는 비의료 컨시어지 서비스입니다.':
        '응급 상황에서는 119와 가까운 응급실이 먼저입니다. atinc는 그 다음에 필요한 의료기관과 진료 경로를 빠르게 찾고, 이후의 진료와 기록이 한 흐름으로 이어지도록 조율합니다.',
    '시술 여부와 방법은 의료진의 진찰 결과에 따라 결정됩니다. atinc는 특정 결과를 보장하지 않습니다.':
        '시술 여부와 방법은 담당 의료진이 직접 진찰한 뒤 고객님과 충분히 상의해 정합니다. 같은 시술도 사람마다 경과가 다르기에, atinc는 회복 기간과 경과 확인 일정까지 처음부터 함께 계획합니다.',
    '재생의학의 적용 가능성, 검사·시술의 필요성과 시행 여부는 관련 법령과 해당 의료기관의 시행 범위, 담당 의료진의 진료·검사 결과에 따라 결정됩니다. atinc는 특정 효과나 치료 결과를 보장하지 않습니다.':
        '재생의료는 관련 법령과 지정 의료기관의 시행 범위 안에서, 담당 의료진의 진료와 검사로 적용 여부를 정합니다. atinc는 가능성을 먼저 약속하지 않습니다. 판단에 필요한 자료를 준비하고 제도와 기관의 범위를 확인해, 정확한 정보로 결정하실 수 있게 돕습니다.',
    '치료 여부와 방법은 의료진의 진찰 결과에 따라 결정됩니다. atinc는 특정 효과를 보장하지 않습니다.':
        '치료 방법과 기간은 한의사와 의료진이 진찰한 뒤 고객님과 상의해 정합니다. 회복의 속도는 사람마다 다르기에, atinc는 입원·통원 일정과 경과 진료를 그때그때 함께 조정합니다.',
    '프로그램명이나 상담만으로 특정 치료가 결정되는 것은 아니며, 실제 치료와 시술은 의료진의 진료와 검사 결과에 따라 결정됩니다.':
        '어떤 검사와 치료가 필요한지는 전문의가 진료와 검사로 판단합니다. atinc는 말하기 어려운 내용을 필요한 범위에서만 정리해 전달하고, 진료 이후의 일정까지 조용히 이어갑니다.',
    '이 페이지의 내용은 일반 안내입니다. 검사·진단·치료의 필요성과 방법은 의료기관과 담당 의료진이 판단하며, 결과는 개인에 따라 다를 수 있습니다.':
        '이 페이지는 이해를 돕기 위한 안내입니다. 검사와 치료의 필요성은 담당 의료진이 판단하고, 경과는 사람마다 다르기에 상담에서 고객님의 상황에 맞춰 다시 설명드립니다.',
    '라인별 구성과 적용 여부는 협력 의료기관 의료진 상담과 검사 결과로 결정되며, 비용은 상담 후 개별 안내합니다. atinc는 특정 효과나 치료 결과를 보장하지 않습니다.':
        '라인별 구성과 적용 여부는 협력 의료기관 의료진의 상담과 검사 결과로 정하며, 비용은 상담 후 개별로 안내합니다. 가능성을 먼저 약속하기보다, 판단에 필요한 정보를 정확하게 드리는 것이 atinc의 방식입니다.',
}


def principle(h):
    for a, b in PRINCIPLE.items():
        h = h.replace(a, b)
    return h


_COPY = None


def apply_copy(h):
    global _COPY
    if _COPY is None:
        _COPY = {}
        try:
            m1 = json.load(open(f'{SP}/copy_map.json', encoding='utf-8'))
        except Exception:
            m1 = {}
        try:
            m2 = json.load(open(f'{SP}/copy_map2.json', encoding='utf-8'))
        except Exception:
            m2 = {}
        try:
            m3 = json.load(open(f'{SP}/copy_map3.json', encoding='utf-8'))
        except Exception:
            m3 = {}
        # chain: original -> pass 1 -> pass 2 -> manual pass 3
        keys = set(m1) | set(m2) | set(m3)
        for k in keys:
            v = m1.get(k, k)
            v = m2.get(v, v)
            v = m3.get(v, v)
            if v != k:
                _COPY[k] = v
    if not _COPY:
        return h

    def rep(m):
        raw = m.group(1)
        txt = html.unescape(raw)
        key = txt.strip()
        if key in _COPY:
            lead = txt[:len(txt) - len(txt.lstrip())]
            tail = txt[len(txt.rstrip()):]
            return '>' + E(lead + _COPY[key] + tail) + '<'
        return m.group(0)
    return re.sub(r'>([^<>]+)<', rep, h)


BRAND_RE = re.compile(r'(?<![@A-Za-z0-9_./-])atinc(?![@A-Za-z0-9_]|\.co)')


def brand(h):
    return BRAND_RE.sub('atInc', h)


TITLES = {
    'about.html': '회사소개 — 프라이빗 헬스케어 컨시어지 | atInc',
    'medical.html': '의료 분야 안내 — 검진·재생의료·성형·여성·남성·한방 | atInc',
    'medical-checkup.html': '건강검진 — 정밀검진 기관 비교와 예약 | atInc',
    'medical-regenerative.html': '재생의료·줄기세포 — 세포 보관과 전문의 상담 | atInc',
    'medical-aesthetic.html': '성형·피부 — 전문의 협진 클리닉 연결 | atInc',
    'medical-women.html': '여성건강 — 산부인과 진료와 여성 검진 | atInc',
    'medical-men.html': '남성건강 — 비뇨의학과 상담과 남성 검진 | atInc',
    'medical-korean-medicine.html': '한방·웰니스 — 한·양방 협진과 회복 | atInc',
    'care.html': '케어 프로그램 — 검진 이후까지 이어지는 관리 | atInc',
    'care-private-checkup.html': 'PRIVATE CHECKUP — 나에게 맞춘 검진 설계 | atInc',
    'care-longevity-90.html': 'LONGEVITY 90 — 검진 결과 이후 90일 관리 | atInc',
    'care-executive-365.html': 'EXECUTIVE 365 — 연간 헬스 오피스 | atInc',
    'care-global-medical-journey.html': 'GLOBAL MEDICAL JOURNEY — 해외 고객의 한국 의료 일정 | atInc',
    'network.html': '협력 병원 네트워크 — 서울에서 전국으로 | atInc',
    'partners.html': '제휴 안내 — 병원·기업·해외 에이전시 | atInc',
    'consultation.html': '상담 신청 안내 | atInc',
}
DESCS = {
    'network.html': '서울, 인천, 경기, 대구, 부산의 협력 병원과 함께합니다. 지역마다 받으실 수 있는 진료를 안내하고, 병원 이름은 상담에서 알려 드립니다.',
    'medical-regenerative.html': '본인 세포 보관과 지정 재생의료기관 상담을 안내합니다. 협력 기관의 의료진 상담과 채취·배양·보관 일정을 atInc가 하나로 잡아 드립니다.',
    'care-executive-365.html': '경영진과 그 가족처럼 일정이 빠듯한 분들을 위해 1년 동안의 검진, 재검, 전문의 상담 일정을 담당 매니저가 잡고 건강 기록을 한데 정리해 드리는 연간 헬스 오피스입니다.',
    'care.html': '케어 프로그램은 병원 예약에 더해 사전 준비, 일정 조율, 결과 이후 관리까지 atInc가 맡는 서비스입니다. 목적과 기간에 따라 네 가지로 나뉩니다.',
    'partners.html': '병원, 기업, 해외 에이전시와 함께 일합니다. 협력 방식과 진행 절차, 함께 일할 병원을 고르는 기준을 안내합니다.',
    'privacy.html': '주식회사 애트(atInc)가 상담 신청 과정에서 받는 개인정보의 항목과 이용 목적, 보관 기간, 정보주체의 권리를 안내합니다.',
    'medical-notice.html': 'atInc는 의료기관이 아닌 헬스케어 컨시어지입니다. 검사·진단·치료는 협력 의료기관 의료진이 맡습니다. 회사 정보와 의료서비스 관련 고지입니다.',
}


def page(fn, title, desc, main, cur=None, light=False):
    title, desc = TITLES.get(fn, title), DESCS.get(fn, desc)
    main = main.replace(ic('arrow'), '')
    title, desc, main = brand(title), brand(desc), brand(principle(main))
    glass = 'data-fx=' in main or 'data-hdr-over' in main
    hdr = header(cur).replace(' data-glass-hdr', ' data-glass' if glass else '')
    body = apply_copy(brand(f'<div class="page{" hdr-light" if light or glass else ""}{" hdr-glass" if glass else ""}">{hdr}{mnav()}<main id="main">{main}</main>{footer()}{quick_contact()}</div>'))
    body = body.replace('>먼저 이야기를 듣겠습니다</h2>', '>프라이빗 상담</h2>')
    for a_, b_ in MED_FIX:
        body = body.replace(a_, b_)
    import site_revise as RV
    body, title, desc = RV.revise(body, fn), RV.revise(title, fn), RV.revise(desc, fn)
    url = SITE_URL + ('' if fn == 'index.html' else fn)
    ld = [{'@context': 'https://schema.org', '@type': 'Organization', 'name': 'atInc', 'legalName': '주식회사 애트',
           'url': SITE_URL, 'logo': SITE_URL + 'assets/og.png', 'email': EMAIL, 'telephone': '+82-10-5857-0129',
           'areaServed': 'KR',
           'description': '목적에 맞는 한국의 병원을 고르고 예약·통역·결과 이후 일정까지 전담 매니저가 맡는 헬스케어 컨시어지'}] if fn == 'index.html' else []
    cm = re.search(r'<nav class="crumb"[^>]*>(.*?)</nav>', body)
    if cm:
        its = re.findall(r'<a href="([^"]+)">([^<]+)</a>|<span>([^<]+)</span>', cm.group(1))
        el = []
        for i, (h, t, last) in enumerate(its, 1):
            el.append({'@type': 'ListItem', 'position': i, 'name': html.unescape(t or last), 'item': SITE_URL + ('' if h == 'index.html' else (h or fn))})
        ld.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': el})
    faq = re.findall(r'<details><summary>(.*?)<svg.*?</summary><p class="body">(.*?)</p></details>', body)
    if faq:
        tx = lambda h: html.unescape(re.sub(r'<[^>]+>', '', h)).strip()
        ld.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': tx(q), 'acceptedAnswer': {'@type': 'Answer', 'text': tx(a)}} for q, a in faq]})
    ld_h = ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False).replace('</', '<\\/') + '</script>' for x in ld)
    head = (f'<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'<title>{E(title)}</title><meta name="description" content="{E(desc)}">'
            f'<link rel="canonical" href="{url}"><meta name="theme-color" content="#2B211B">'
            f'<link rel="icon" href="assets/favicon-32.png" sizes="32x32" type="image/png"><link rel="icon" href="assets/favicon-192.png" sizes="192x192" type="image/png"><link rel="apple-touch-icon" href="assets/apple-touch-icon.png">'
            f'<meta property="og:site_name" content="atInc"><meta property="og:locale" content="ko_KR">'
            f'<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website">'
            f'<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}assets/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f'<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link rel="stylesheet" href="{PRET}">'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="preload" as="style" href="{FONTS}"><link rel="stylesheet" href="{FONTS}" media="print" onload="this.media=\'all\'">'
            f'<noscript><link rel="stylesheet" href="{FONTS}"></noscript>'
            f'<link rel="stylesheet" href="assets/site.css">{ld_h}')
    scripts = '<script src="assets/network-data.js"></script>'
    if 'class="atmap"' in body:
        scripts += '<script src="assets/map-base.js"></script>'
    scripts += '<script src="assets/map.js"></script><script src="assets/site.js"></script>'
    if 'data-fx=' in body or 'data-cells' in body:
        scripts += '<script type="module" src="assets/fx/boot.js"></script>'
    body = body + scripts
    full = f'<!doctype html>\n<html lang="ko">\n<head>{head}</head>\n<body>\n{body}\n</body>\n</html>\n'
    os.makedirs(OUT, exist_ok=True)
    open(f'{OUT}/{fn}', 'w', encoding='utf-8').write(full)
    PAGES.append(fn)
    if fn == 'index.html':
        art_head = head.replace(f'<title>{E(title)}</title>', '<title>atInc 홈페이지</title>')
        art_head = art_head.replace('<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">', '')
        open(f'{SP}/site_artifact_index.html', 'w', encoding='utf-8').write(art_head + '\n' + body + '\n')  # 미리보기용, git 제외


PAGES = []


# ------------------------------------------------------------------ shared blocks
KEEP_UP = {'CARE', 'VIP', 'FAQ', 'ICN', 'CEO', 'GMP', 'GLP', 'atinc', 'atInc'}


def sentence(t):
    if not re.search(r'[A-Z]{2,}', t) or re.search(r'[가-힣]', t):
        return t
    out = []
    first = True
    for w in t.split(' '):
        if w in KEEP_UP or not w.isalpha():
            out.append(w)
        else:
            out.append(w.capitalize() if first else w.lower())
            first = False
    return ' '.join(out)


def eyebrow(t, light=False):
    return ''  # section labels removed: headings carry the meaning


def appt_card(btn='상담 예약', cat=''):
    """The concierge 'appointment card' used wherever we ask for a consultation."""
    return (f'<aside class="appt"><p class="appt__t">프라이빗 상담 예약</p>'
            f'<dl class="appt__dl"><dt>담당 매니저</dt><dd>첫 통화부터 결과 이후까지 같은 매니저가 맡습니다</dd>'
            f'<dt>첫 상담</dt><dd>진단서나 검사 결과는 아직 보내지 않으셔도 됩니다</dd>'
            f'<dt>비용 안내</dt><dd>병원비와 atInc 조율료, 통역·차량 같은 실비를 나눠서 알려 드립니다</dd></dl>'
            f'{form_link(btn, cat, "btn btn--dark btn--wide")}<p class="appt__form">신청서는 새 창에서 열립니다</p>'
            f'<p class="appt__lines"><a href="tel:{VIP_TEL}">매니저 직통 {VIP}</a><a href="mailto:{EMAIL}">{EMAIL}</a></p>'
            f'<p class="appt__intl" lang="en">From overseas, email us or call <a href="tel:{VIP_TEL}">+82 10 5857 0129</a>.</p>'
            f'<p class="appt__intl" lang="zh-Hans">海外客户请发送电子邮件，或致电 <a href="tel:{VIP_TEL}">+82 10 5857 0129</a>。</p></aside>')


def cband(title, body, btn, cat, eyebrow_t=None, note=None, sid='contact', reasons=None, reasons_title=None, fx=None):
    if title == '먼저 이야기를 듣겠습니다':
        title = '프라이빗 상담'
    lst = reasons if reasons else PROMISES
    pro = ''.join(f'<li>{ic("check")}<span>{E(p)}</span></li>' for p in lst)
    rt = f'<p class="cband__rt">{E(reasons_title)}</p>' if reasons_title else ''
    btn = {'프라이빗 상담 신청': '상담 예약', '상담 예약 요청': '상담 예약'}.get(btn, btn)
    return (f'<section class="sec cband" id="{sid}"><div class="wrap cband__grid">'
            f'<div class="cband__main"><p class="cband__label">Private Consultation</p><h2 class="h1">{E(title)}</h2><p class="lead">{E(body)}</p>'
            f'<div class="cband__why">{rt}<ul class="plist">{pro}</ul></div></div>'
            f'{appt_card(btn, cat)}'
            f'</div></section>')


def checks(lst, cls='checks'):
    return f'<ul class="{cls}">' + ''.join(f'<li class="check">{ic("check")}<span>{E(x)}</span></li>' for x in lst) + '</ul>'


def chips(lst, icon='check'):
    return '<ul class="chips">' + ''.join(f'<li class="chip">{ic(icon)}<span>{E(x)}</span></li>' for x in lst) + '</ul>'


def tbl(t):
    th = ''.join(f'<th scope="col">{E(h)}</th>' for h in t['headers'])
    tr = ''.join('<tr>' + ''.join((f'<td data-label="{E(t["headers"][j])}">' if j and j < len(t['headers']) else '<td>') + f'{E(c)}</td>' for j, c in enumerate(r)) + '</tr>' for r in t['rows'])
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def section_head(no, en, title, lead=None, extra=''):
    lead_h = f'<p class="lead">{E(lead)}</p>' if lead else ''
    return f'<div class="sh"><h2 class="disp-2">{E(title)}</h2>{lead_h}{extra}</div>'


def phero(crumbs, eb, title, lead=None, art='', extra=''):
    cr = ' / '.join(f'<a href="{h}">{E(t)}</a>' if h else f'<span>{E(t)}</span>' for t, h in crumbs)
    lead_h = f'<p class="lead">{E(lead)}</p>' if lead else ''
    art_h = f'<div class="phero__art rise rise-3">{art}</div>' if art else ''
    cols = '' if art else ' style="grid-template-columns: minmax(0, 1fr)"'
    return (f'<section class="phero"><div class="wrap phero__grid"{cols}><div class="phero__text">'
            f'<nav class="crumb" aria-label="현재 위치">{cr}</nav><h1 class="h1 rise">{E(title)}</h1>'
            f'<div class="rise rise-2" style="display: grid; gap: 18px">{lead_h}{extra}</div></div>{art_h}</div></section>')


# ------------------------------------------------------------------ map
def site_map(uid):
    # drawn in the browser from assets/network-data.js (see assets/map.js)
    return (f'<div class="atmap" data-uid="{uid}"></div>'
            f'<p class="atmap__note"><em>Expanding nationwide</em><span>협력 병원을 전국으로 넓혀 가고 있습니다</span></p>')


def site_map_old(uid):
    m = mapsvg.m
    H = m['hubs']
    icx, icy = H['ICN']
    ACC = '#7A5741'
    cats = {h['name']: ','.join(h['cats']) for h in HUBS}
    hid = {h['name']: h['id'] for h in HUBS}

    def mk(x, y, r=5.5, d=0.0):
        return (f'<circle class="pulse" cx="{x:.1f}" cy="{y:.1f}" r="{r * 2.3:.1f}" fill="{ACC}" fill-opacity=".22" style="animation-delay: {d}s"></circle>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{ACC}" stroke="#FFFDF9" stroke-width="2.2"></circle>')

    def g(name, inner):
        return f'<g class="hub" data-cats="{cats[name]}" data-hub="{hid[name]}">{inner}</g>'

    T = mapsvg.text
    s = [f'<svg viewBox="0 0 560 760" role="img" aria-labelledby="map-t-{uid}" xmlns="http://www.w3.org/2000/svg"><title id="map-t-{uid}">atinc 협력 거점 지도: 서울 강남, 인천 송도, 인천 검단, 경기 용인, 대구, 부산</title>',
         f'<defs><clipPath id="clip-{uid}"><rect x="{mapsvg.DX}" y="{mapsvg.DY}" width="230" height="182" rx="12"></rect></clipPath></defs>',
         T(6, 24, 'GLOBAL ARRIVALS · ICN', size=11.5, weight=500, fill='#6B5A4E', ls='2.2')]
    for d in [f'M0 52 Q 110 86 {icx:.1f} {icy:.1f}', f'M0 250 Q 100 228 {icx:.1f} {icy:.1f}', f'M0 360 Q 120 300 {icx:.1f} {icy:.1f}']:
        s.append(f'<path class="arr" d="{d}" fill="none" stroke="{ACC}" stroke-opacity=".55" stroke-width="1.3" stroke-dasharray="3 6" stroke-linecap="round"></path>')
    s.append('<g stroke="#FFFDF9" stroke-width="0.9" stroke-linejoin="round">' + mapsvg.prov_paths() + '</g>')
    gx, gy = H['서울 강남']
    dx, dy = H['대구']
    bx, by = H['부산']
    s.append(g('대구', f'<path d="M{gx:.1f} {gy:.1f} Q 420 250 {dx:.1f} {dy:.1f}" fill="none" stroke="{ACC}" stroke-opacity=".5" stroke-width="1.3"></path>'))
    s.append(g('부산', f'<path d="M{gx:.1f} {gy:.1f} Q 486 262 {bx:.1f} {by:.1f}" fill="none" stroke="{ACC}" stroke-opacity=".5" stroke-width="1.3"></path>'))
    s.append(f'<rect x="{mapsvg.SX}" y="{mapsvg.SY}" width="120" height="95" rx="8" fill="none" stroke="{ACC}" stroke-opacity=".7" stroke-width="1" stroke-dasharray="4 4"></rect>')
    s.append(T(316, 132, '수도권 4개 거점', size=12.5, weight=600))
    s.append(f'<path d="M300 215 L 372 560" fill="none" stroke="{ACC}" stroke-opacity=".45" stroke-width="1" stroke-dasharray="3 4"></path>')
    for k in ['서울 강남', '인천 검단', '인천 송도', '경기 용인']:
        x, y = H[k]
        s.append(g(k, f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{ACC}" stroke="#FFFDF9" stroke-width="1.6"></circle>'))
    s.append(f'<rect x="{icx - 4:.1f}" y="{icy - 4:.1f}" width="8" height="8" transform="rotate(45 {icx:.1f} {icy:.1f})" fill="#2E2119"></rect>')
    s.append(g('대구', mk(dx, dy, 6, .6) + T(dx - 14, dy + 5, '대구', anchor='end', size=15, weight=600)))
    s.append(g('부산', mk(bx, by, 6, 1.2) + T(bx + 13, by + 5, '부산', size=15, weight=600)))
    DX, DY = mapsvg.DX, mapsvg.DY
    s.append(f'<rect x="{DX}" y="{DY}" width="230" height="182" rx="12" fill="#FBF8F3" stroke="#D9C7B2" stroke-width="1"></rect>')
    s.append(f'<g clip-path="url(#clip-{uid})"><g transform="translate({DX} {DY}) scale({mapsvg.SC}) translate({-mapsvg.SX} {-mapsvg.SY})" stroke="#FFFDF9" stroke-width="1.2" stroke-linejoin="round">'
             + mapsvg.prov_paths(mapsvg.INSET_SET, nonscale=True) + '</g></g>')
    s.append(T(DX + 12, DY + 20, '수도권 확대', size=11, weight=500, fill='#6B5A4E', ls='0.5'))
    ix, iy = mapsvg.ins(icx, icy)
    s.append(f'<rect x="{ix - 5:.1f}" y="{iy - 5:.1f}" width="10" height="10" transform="rotate(45 {ix:.1f} {iy:.1f})" fill="#2E2119"></rect>')
    s.append(T(ix, iy + 22, 'ICN', anchor='middle', size=11, weight=600, ls='1'))
    lab = {'서울 강남': (0, -13, 'middle'), '인천 검단': (0, -13, 'middle'), '인천 송도': (0, 23, 'middle'), '경기 용인': (-12, 5, 'end')}
    for i, (k, (ox, oy, an)) in enumerate(lab.items()):
        x, y = mapsvg.ins(*H[k])
        s.append(g(k, mk(x, y, 5, i * .4) + T(x + ox, y + oy, k, anchor=an, size=12.5, weight=600)))
    s.append('<rect x="472" y="12" width="80" height="78" rx="10" fill="none" stroke="#D9C7B2" stroke-width="1"></rect>')
    isl = m['islands'][0][1]
    cx = sum(p[0] for p in isl) / len(isl)
    cy = sum(p[1] for p in isl) / len(isl)
    pts = ' '.join(f'{498 + (x - cx) * 2.4:.1f},{44 + (y - cy) * 2.4:.1f}' for x, y in isl)
    s.append(f'<polygon points="{pts}" fill="#F8F2EA" stroke="#C9B49C" stroke-width="0.8"></polygon>')
    s.append('<circle cx="531" cy="56" r="2" fill="#C9B49C"></circle><circle cx="535" cy="57" r="1.6" fill="#C9B49C"></circle>')
    s.append(T(498, 80, '울릉도', anchor='middle', size=10, weight=500, fill='#6B5A4E'))
    s.append(T(533, 80, '독도', anchor='middle', size=10, weight=500, fill='#6B5A4E'))
    s.append('</svg>')
    return ''.join(s)


def filters():
    b = '<button type="button" data-cat="all" aria-pressed="true">전체</button>'
    b += ''.join(f'<button type="button" data-cat="{c["id"]}" aria-pressed="false">{E(c["ko"])}</button>' for c in CATS)
    return f'<div class="filters" role="group" aria-label="분야로 거점 보기">{b}</div>'


def hub_cats_text(h):
    return ' · '.join(CAT_KO[c] for c in h['cats']) if h['cats'] else '협력 의료기관'


EMPTY_MSG = '남성건강은 지역과 관계없이, 비뇨의학과 전문 클리닉과 상담으로 연결합니다.'


# ------------------------------------------------------------------ HOME
def page_home():
    f1 = fields(HB['01'])
    deliver = [x.strip() for x in fields(HB['06'])['고객이 받는 것'].split('·')]
    en = f1['영문 헤드라인'].split(' ')
    hero = (f'<section class="hero"><div class="hero__bg" style="background-image: url({HERO}); background-position: 72% 50%"></div>'
            f'<div class="wrap hero__in"><p class="eyebrow eyebrow--light eyebrow--ko">{E(f1["작은 제목"])}</p>'
            f'<h1><span class="display rise" style="display: block">{E(" ".join(en[:-1]))}<br><span>{E(en[-1])}</span></span>'
            f'<span class="hero__ko rise rise-2" style="display: block; margin-top: 26px">{E(f1["메인 카피"])}</span></h1>'
            f'<p class="hero__body rise rise-3">{E(f1["본문"])}</p>'
            f'<div class="hero__actions rise rise-4">{form_link("프라이빗 상담 신청", "")}<a class="btn btn--ghost-light" href="medical.html">의료 분야 둘러보기{ic("arrow")}</a></div>'
            f'<div class="hero__card rise rise-4"><p class="eyebrow" style="display: flex; gap: 8px; align-items: center; font-size: 11px">YOUR HEALTH JOURNEY</p><ol>'
            + ''.join(f'<li>{E(d)}</li>' for d in deliver) + '</ol></div></div></section>')
    trust_items = [('doc', '주식회사 애트', '사업자등록번호 369-87-03095'), ('globe', '외국인환자 유치업 등록', '제 A-2026-08-01-07161 호'),
                   ('user', '전담 매니저 1:1 상담', '상담부터 후속관리까지'), ('pin', '협력 네트워크', '서울·인천·경기·대구·부산'),
                   ('lock', '민감정보 보호', '초기 상담에서는 민감한 의료정보를 받지 않습니다')]
    trust = ('<section class="trust" aria-label="atinc 신뢰 정보"><div class="wrap trust__grid">'
             + ''.join(f'<div class="trust__item">{ic(i)}<p><b>{E(a)}</b><span>{E(b)}</span></p></div>' for i, a, b in trust_items) + '</div></section>')
    f3 = fields(HB['03'])
    t3 = f3['제목'].split('. ', 1)
    about_s = (f'<section class="sec"><div class="wrap"><div class="shead" style="align-items: center; margin-bottom: 0">'
               f'<div>{eyebrow("ABOUT atinc")}<h2 class="h1">{E(t3[0])}.<br>{E(t3[1])}</h2><p class="lead">{E(f3["본문"])}</p>'
               f'<p><a class="link" href="about.html">회사 소개 보기{ic("arrow")}</a></p></div>'
               f'<div style="justify-self: end; width: min(100%, 440px)">{photo(ARCH, "50% 40%", "ph--45 ph--arch", "자연광이 드는 아치형 라운지")}</div></div></div></section>')
    f4 = fields(HB['04'])
    cards = ''
    for i, (c, r) in enumerate(zip(CATS, table(HB['04'])['rows']), 1):
        cards += (f'<a class="mcard mcard--pic" href="{c["page"]}"><figure class="mcard__pic">{pic("cat-" + c["id"], "", "(max-width: 600px) 100vw, (max-width: 1100px) 50vw, 33vw", (480, 720, 1080))}</figure>'
                  f'<div class="mcard__txt"><span class="mcard__no">0{i}</span><h3 class="en-title">{E(c["en"])}</h3><p class="mcard__ko">{E(c["ko"])}</p>'
                  f'<p class="body" style="font-size: 14.5px">{E(r[1])}</p><span class="link">자세히 보기{ic("arrow")}</span></div></a>')
    med = (f'<section class="sec sec--sand"><div class="wrap"><div class="shead"><div>{eyebrow("MEDICAL AREAS")}<h2 class="h1">{E(f4["제목"])}</h2></div>'
           f'<p class="lead">{E(f4["본문"])}</p></div><div class="grid3">{cards}</div></div></section>')
    f5 = [it for it in HB['05']['items'] if it['type'] == 'field']
    qs = ''
    for it in f5:
        if not it['key'].startswith('카드'):
            continue
        ans, _, tgt = it['detail'].partition(' → ') if 'detail' in it else (it['value'], '', '')
        q = it['value']
        if ' — ' in q:
            q, ans2 = q.split(' — ', 1)
            ans, _, tgt = ans2.partition(' → ')
        c = CAT_BY_KO[tgt.strip()]
        qs += (f'<a class="qcard" href="{c["page"]}#what"><span class="qcard__q">Q.</span><h3 class="h3">{E(q)}</h3>'
               f'<p class="body" style="font-size: 14.5px">{E(ans)}</p><span class="link">{E(c["ko"])}에서 더 보기{ic("arrow")}</span></a>')
    feat = (f'<section class="sec"><div class="wrap"><div class="shead"><div>{eyebrow("BEFORE YOU ASK")}<h2 class="h1">{E(fields(HB["05"])["제목"])}</h2></div>'
            f'<p class="lead">각 분야 페이지의 자주 묻는 질문에서 골랐습니다.</p></div><div class="grid3">{qs}</div></div></section>')
    f6 = HB['06']['items']
    cols = ''
    for it in f6:
        if it['type'] == 'field' and re.match(r'^0\d ', it['key']):
            no, rest = it['key'].split(' ', 1)
            en_k, ko_k = rest.split(' · ', 1)
            cols += (f'<div class="step"><span class="step__no">{no} &nbsp;{E(en_k)}</span><h3 class="h3">{E(ko_k)}</h3><p class="body">{E(it["value"])}</p></div>')
    how = (f'<section class="sec sec--deep"><div class="wrap"><div class="shead shead--stack"><div>{eyebrow("HOW atinc WORKS")}<h2 class="h1">{E(fields(HB["06"])["제목"])}</h2></div></div>'
           f'<div class="steps" style="grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr))">{cols}</div>'
           f'<div style="display: flex; flex-wrap: wrap; gap: 14px; align-items: center; margin-top: 44px"><span class="small">고객이 받는 것</span>{chips(deliver)}</div></div></section>')
    care_rows = ''
    for i, (p, r) in enumerate(zip(CARE, table(HB['07'])['rows']), 1):
        ko = [s['title'] for s in care['sections'] if (s['title'] or '').startswith(p['en'])][0].split(' · ', 1)[1]
        care_rows += (f'<a href="{p["page"]}"><span class="clist__no">0{i}</span><div><h3 class="en-title">{E(p["en"])}</h3><p class="clist__ko">{E(ko)}</p>'
                      f'<p class="clist__line">{E(r[1])}</p></div><span class="clist__meta">{E(r[2])}</span></a>')
    care_intro = [s for s in care['sections'] if s['title'] == 'CARE 인덱스'][0]
    ci = {it['key']: it['value'] for it in care_intro['intro'] if it['type'] == 'field'}
    care_s = (f'<section class="sec"><div class="wrap"><div class="shead shead--care">'
              f'<div style="gap: 22px">{eyebrow("atinc CARE")}<h2 class="h1">{E(fields(HB["07"])["제목"])}</h2><p class="lead">{E(ci["본문"])}</p>'
              f'<div style="width: min(100%, 360px); margin-top: 18px">{photo(HERO, "80% 50%", "ph--45 ph--arch", "프라이빗 상담 공간")}</div></div>'
              f'<div class="clist">{care_rows}</div></div></div></section>')
    f8 = fields(HB['08'])
    hub_list = ''.join(f'<li data-cats="{",".join(h["cats"])}" data-count><span class="hubs__no">0{i}</span><div><b>{E(h["name"])}</b><small>{E(h["en"])}</small></div><span class="hubs__cats">{E(hub_cats_text(h))}</span></li>'
                       for i, h in enumerate(HUBS, 1))
    net_s = (f'<section class="sec sec--deep" data-net><div class="wrap net__grid"><div style="display: grid; gap: 24px; min-width: 0">{eyebrow("NETWORK")}'
             f'<h2 class="h1">{E(f8["제목"])}</h2><p class="lead">{E(f8["본문"])}</p>{filters()}'
             f'<p class="net-empty" hidden>{E(EMPTY_MSG)}</p><ul class="hubs">{hub_list}</ul>'
             f'<p><a class="link" href="network.html">{E(f8["링크"])}{ic("arrow")}</a></p></div>'
             f'<div class="map">{site_map("home")}</div></div></section>')
    f9 = fields(HB['09'])
    gl = ''
    for k, dark in [('Before Korea · 입국 전', False), ('In Korea · 체류 중', True), ('After Korea · 귀국 후', False)]:
        en_k, ko_k = k.split(' · ')
        lst = ''.join(f'<li>{ic("check")}<span>{E(x.strip())}</span></li>' for x in f9[k].split(', '))
        gl += (f'<div class="card gcard{" card--dark" if dark else ""}"><h3 class="en-title">{E(en_k)}</h3><p class="small">{E(ko_k)}</p>'
               f'<ul class="plist{" plist--light" if dark else ""}">{lst}</ul></div>')
    glob = (f'<section class="sec"><div class="wrap"><div class="shead"><div>{eyebrow("GLOBAL SUPPORT")}<h2 class="h1">{E(f9["제목"])}</h2></div>'
            f'<div><p class="lead">{E(f9["한 줄"])}</p><p><a class="link" href="care-global-medical-journey.html">GLOBAL MEDICAL JOURNEY 보기{ic("arrow")}</a></p></div></div>'
            f'<div class="grid3">{gl}</div></div></section>')
    f10 = fields(HB['10'])
    part = (f'<section class="sec sec--sand sec--tight"><div class="wrap shead" style="margin-bottom: 0; align-items: center">'
            f'<div>{eyebrow("FOR PARTNERS")}<h2 class="h2">{E(f10["제목"])}</h2><p class="lead">{E(f10["본문"])}</p></div>'
            f'<div style="justify-self: end"><a class="btn btn--ghost" href="partners.html">파트너 협력 안내{ic("arrow")}</a></div></div></section>')
    f11 = fields(HB['11'])
    kv = (f'<dl class="kv" style="margin-top: 10px; padding-top: 22px; border-top: 1px solid var(--line)"><dt>상호</dt><dd>주식회사 애트 (atinc)</dd><dt>대표이사</dt><dd>한수연</dd>'
          f'<dt>사업자등록번호</dt><dd>369-87-03095</dd><dt>외국인환자 유치업 등록</dt><dd>제 A-2026-08-01-07161 호</dd></dl>')
    founder = (f'<section class="sec"><div class="wrap founder"><div class="mono" role="img" aria-label="atinc">{logo("span")}</div>'
               f'<div style="display: grid; gap: 22px; align-content: center">{eyebrow("FOUNDER & COMPANY")}<h2 class="h2">{E(f11["제목"])}</h2>'
               f'<p class="lead">{E(f11["본문"])}</p>{kv}<p><a class="link" href="about.html#founder">대표 소개 보기{ic("arrow")}</a></p></div></div></section>')
    f12 = fields(HB['12'])
    cons = cband(f12['제목'], f12['본문'], '프라이빗 상담 신청', '')
    main = hero + trust + about_s + med + feat + how + care_s + net_s + glob + part + founder + cons
    page('index.html', 'atinc · 프라이빗 헬스케어 여정', '국내외 고객의 건강 목적에 맞춰 의료 분야와 의료기관을 검토하고, 상담부터 후속관리까지 조율하는 헬스케어 컨시어지 atinc.', main, 'home', light=True)


# ------------------------------------------------------------------ ABOUT
def page_about():
    f1 = fields(AB['01'])
    hero = phero([('홈', 'index.html'), ('회사소개', None)], 'ABOUT atinc', f1['제목'], f1['본문'],
                 f'<figure class="phero__pic">{pic("office", "", "(max-width: 900px) 100vw, 40vw", (640, 960, 1400), eager=True)}</figure>',
                 f'<p class="notice" style="max-width: 62ch; padding-left: 16px; border-left: 2px solid var(--latte)">{E(f1["고지 문장"])}</p>')
    b2 = AB['02']
    f2 = fields(b2)
    subs = [it for it in b2['items'] if it['type'] == 'field' and it['sub']]
    why = (f'<section class="sec"><div class="wrap"><div class="shead"><div>{eyebrow("WHY atinc")}<h2 class="h1">{E(f2["제목"])}</h2></div><p class="lead">{E(f2["본문"])}</p></div>'
           f'<div class="grid3">' + ''.join(f'<div class="card"><p class="eyebrow eyebrow--ko">{E(s["key"])}</p><p class="body" style="font-size: 16px; color: var(--ink)">{E(s["value"])}</p></div>' for s in subs) + '</div></div></section>')
    do = table(AB['03'])
    work = (f'<section class="sec sec--sand"><div class="wrap"><div class="shead"><div>{eyebrow("WHAT WE DO")}<h2 class="h1">우리가 하는 일</h2></div>'
            f'<p class="lead">의료 판단은 의료진이, 그 앞뒤의 정리와 연결은 atinc가 맡습니다.</p></div><div class="grid3">'
            + ''.join(f'<div class="card"><h3 class="h3">{E(r[0])}</h3><p class="body">{E(r[1])}</p></div>' for r in do['rows']) + '</div></div></section>')
    pr = table(AB['04'])
    prin = (f'<section class="sec"><div class="wrap"><div class="shead"><div>{eyebrow("PRINCIPLES")}<h2 class="h1">운영 원칙</h2></div></div><div class="grid4">'
            + ''.join(f'<div class="card"><p class="en-title">{E(r[0])}</p><p class="body">{E(r[1])}</p></div>' for i, r in enumerate(pr['rows'])) + '</div></div></section>')
    f5 = fields(AB['05'])
    name, role = f5['이름'].split(' · ', 1)
    edu = ''.join(f'<li>{E(x.strip())}</li>' for x in f5['학력'].split(' / '))
    keep = ['병원 코디네이터 교육 강사', '병원 홍보마케팅 교육 수료', 'CS강사·CS강사지도사', '심리상담사 1급', '협상전문가 1급']
    lic = ''.join(f'<li>{E(x.strip())}</li>' for x in f5['자격'].split(', ') if x.strip() in keep)
    cap = ''.join(f'<li>{E(x.strip())}</li>' for x in f5['핵심 역량'].split(' / '))
    fo = (f'<section class="sec sec--deep" id="founder"><div class="wrap fdr">'
          f'<blockquote class="fdr__q"><p>{E(f5["제목"])}</p><footer>{E(name)} <span>{E(role)}</span></footer></blockquote>'
          f'<div class="fdr__grid"><p class="lead">{E(f5["본문"])}</p>'
          f'<div class="fdr__cols"><div><h3>전문 분야</h3><ul>{cap}</ul></div><div><h3>학력</h3><ul>{edu}</ul></div><div><h3>자격</h3><ul>{lic}</ul></div></div></div>'
          f'</div></section>')
    ct = table(AB['06'])
    lk = {'이메일': f'<a href="mailto:{EMAIL}">{EMAIL}</a>', 'VIP 연락처': f'<a href="tel:{VIP_TEL}">{VIP}</a>'}
    ct['rows'] = [['매니저 직통', r[1]] if r[0] == 'VIP 연락처' else r for r in ct['rows']]
    lk['매니저 직통'] = lk['VIP 연락처']
    kv = ''.join(f'<dt>{E(r[0])}</dt><dd>{lk.get(r[0], E(r[1]))}</dd>' for r in ct['rows'] if '입력' not in r[1] or COMPANY_ADDRESS)
    if COMPANY_ADDRESS:
        kv = kv.replace('[회사 주소 입력]', E(COMPANY_ADDRESS))
    comp = (f'<section class="sec"><div class="wrap split"><div class="split__label">{eyebrow("COMPANY")}</div><div class="split__main"><h2 class="h2">회사 정보</h2>'
            f'<dl class="kv" style="font-size: 15.5px; gap: 14px 40px">{kv}</dl></div></div></section>')
    f12 = fields(HB['12'])
    main = hero + why + work + prin + comp + cband(f12['제목'], f12['본문'], '상담 예약', '')  # 대표 소개(fo)는 당분간 숨김
    main = main.replace('건강을 넘어, 삶의 품격을 설계합니다.', '병원을 먼저<br>권하지 않습니다.', 1)
    main = main.replace('<h2 class="h1">병원을 먼저 권하지 않습니다</h2>', '<h2 class="h1">비교하고, 준비하고, 결과 이후까지</h2>', 1)
    page('about.html', 'ABOUT | atinc', f1['본문'], main, 'about')


# ------------------------------------------------------------------ MEDICAL index
def page_medical():
    b = list(blocks(medical).values())[0]
    f = fields(b)
    rows = table(b)['rows']
    cards = ''
    for i, (c, r) in enumerate(zip(CATS, rows), 1):
        cards += (f'<a class="mcard mcard--pic" href="{c["page"]}"><figure class="mcard__pic">{pic("cat-" + c["id"], "", "(max-width: 600px) 100vw, (max-width: 1100px) 50vw, 33vw", (480, 720, 1080))}</figure>'
                  f'<div class="mcard__txt"><span class="mcard__no">0{i}</span><p class="mcard__en">{E(c["en"])}</p><h2 class="mcard__t">{E(c["ko"])}</h2>'
                  f'<p class="body" style="font-size: 14.5px">{E(r[1])}</p><span class="link">자세히 보기{ic("arrow")}</span></div></a>')
    hero = phero([('홈', 'index.html'), ('진료 분야', None)], 'MEDICAL', f['제목'], f['본문'])
    grid = f'<section class="sec" style="padding-top: clamp(48px, 5vw, 72px)"><div class="wrap"><div class="grid3">{cards}</div></div></section>'
    pointer = f['아래 안내'].split(' → ')[0]
    band = (f'<section class="sec sec--sand sec--tight"><div class="wrap shead" style="margin-bottom: 0; align-items: center"><div>{eyebrow("Care Programs")}'
            f'<h2 class="h2">{E(pointer)}</h2><p class="notice">{E(f["공통 고지"])}</p></div>'
            f'<div style="justify-self: end"><a class="btn btn--ghost" href="care.html">케어 프로그램 보기{ic("arrow")}</a></div></div></section>')
    f12 = fields(HB['12'])
    import site_enrich as SE
    band = band.replace('sec sec--sand sec--tight', 'sec sec--tight')
    page('medical.html', 'MEDICAL | atinc', f['본문'], hero + grid + SE.access_section() + band + cband(f12['제목'], f12['본문'], '상담 예약', ''), 'medical')


# ------------------------------------------------------------------ category pages
EN_LABEL = {'02': 'WHAT IT IS', '03': 'TYPES', '04': 'WHY ASK', '05': 'HOW IT WORKS', '06': 'OPTIONS', '07': 'PROCESS', '08': 'FACILITY',
            '09': 'BEFORE YOU GO', '10': 'FAQ', '11': 'atinc SUPPORT'}


def render_rows(its):
    out = []
    n = 0
    for it in its:
        if it['type'] in ('field', 'bullet'):
            n += 1
            if it['type'] == 'field':
                out.append(f'<li><span class="rows__no">{n:02d}</span><div><b>{E(it["key"])}</b><p class="body">{E(it["value"])}</p></div></li>')
            else:
                out.append(f'<li><span class="rows__no">{n:02d}</span><p class="body" style="color: var(--ink); font-size: 16px">{E(it["text"])}</p></li>')
    return f'<ul class="rows" style="max-width: 980px">{"".join(out)}</ul>'


def render_how(its):
    out = []
    group = None
    for it in its:
        if it['type'] == 'subhead':
            if group is not None:
                out.append(group + '</ul></div>')
            group = f'<div class="card"><h3 class="h3">{E(it["text"])}</h3><ul class="plist">'
        elif it['type'] == 'bullet' and group is not None:
            group += f'<li><span class="body">{E(it["text"])}</span></li>'
        elif it['type'] == 'field':
            if group is not None:
                out.append(group + '</ul></div>'); group = None
            out.append(f'<div class="card"><h3 class="h3">{E(it["key"])}</h3><p class="body">{E(it["value"])}</p></div>')
        elif it['type'] == 'bullet':
            out.append(f'<div class="card"><p class="body">{E(it["text"])}</p></div>')
        elif it['type'] == 'text':
            out.append(f'<p class="body">{E(it["text"])}</p>')
    if group is not None:
        out.append(group + '</ul></div>')
    n = len([o for o in out if o.startswith('<div class="card"')])
    cls = 'grid2' if n in (2, 4) else 'grid3' if n in (3, 6) else 'grid2'
    return f'<div class="{cls}">{"".join(out)}</div>'


def render_options(b):
    t = table(b)
    out = ''
    if t:
        hdr = t['headers']
        if len(t['rows']) == 3 and len(hdr) == 3:
            out += '<div class="grid3">' + ''.join(
                f'<div class="card{" card--dark" if i == 2 else ""}"><p class="eyebrow">{E(r[0])}</p><p class="h3" style="font-weight: 400">{E(r[1])}</p>'
                f'<p class="small card__foot">{E(hdr[2])} · {E(r[2])}</p></div>' for i, r in enumerate(t['rows'])) + '</div>'
        else:
            out += '<div class="opts">' + ''.join(
                f'<div class="opt{" opt--2" if len(hdr) == 2 else ""}"><p class="opt__name">{E(r[0])}</p><p class="body">{E(r[1])}</p>'
                + (f'<p class="opt__for"><b>{E(hdr[2])}</b>{E(r[2])}</p>' if len(hdr) > 2 else '') + '</div>' for r in t['rows']) + '</div>'
    extra = ''
    for it in b['items']:
        if it['type'] == 'field':
            extra += f'<p class="body"><b style="color: var(--ink); font-weight: 500">{E(it["key"])}</b> &nbsp;{E(it["value"])}</p>'
        elif it['type'] in ('bullet', 'text'):
            extra += f'<p class="body">{E(it.get("text", ""))}</p>'
    if extra:
        out += f'<div style="display: grid; gap: 10px; margin-top: 28px; max-width: 900px">{extra}</div>'
    return out


def render_facility(b, cid):
    txt = ''
    ph = []
    for it in b['items']:
        if it['type'] == 'field' and it['key'] == '사진':
            ph = photos(it['value'])
        elif it['type'] == 'field' and it['key'] == '전후 사진':
            txt += f'<p class="small">시술 전후 사례는 상담에서 개별로 안내해 드립니다.</p>'
        elif it['type'] == 'field' and it['key'] in ('본문',):
            txt += f'<p class="lead">{E(it["value"])}</p>'
        elif it['type'] == 'field':
            txt += f'<div style="display: grid; gap: 8px"><h3 class="h3">{E(it["key"])}</h3><p class="lead">{E(it["value"])}</p></div>'
        elif it['type'] in ('bullet', 'text'):
            txt += f'<p class="lead">{E(it["text"])}</p>'
    n = len(ph)
    cols = min(max(n, 2), 4)
    tiles = ''.join(f'<figure data-photo="{E(code)}">{tile(cid, "ph--sq ph--round" if i else "ph--sq ph--arch", cap)}<figcaption class="cap">{E(cap)}</figcaption></figure>'
                    for i, (code, cap) in enumerate(ph))
    grid = f'<div class="photos" style="--cols: {cols}">{tiles}</div>' if ph else ''
    return txt, grid


def render_checks(b):
    out = []
    for it in b['items']:
        if it['type'] == 'field':
            dark = it['key'] == '고지'
            out.append(f'<div class="card{" card--dark" if dark else ""}"><h3 class="h3">{"atinc의 원칙" if dark else E(it["key"])}</h3><p class="{"notice" if dark else "body"}">{E(it["value"])}</p></div>')
        elif it['type'] == 'bullet':
            out.append(f'<div class="card"><p class="body">{E(it["text"])}</p></div>')
    if len(out) % 2 == 1:
        out[-1] = out[-1].replace('<div class="card', '<div style="grid-column: 1 / -1" class="card', 1)
    return f'<div class="grid2">{"".join(out)}</div>'


def render_faq(b):
    qs = items(b, 'step')
    return '<div class="faq">' + ''.join(f'<details><summary>{E(q["title"])}{ic("chev")}</summary><p class="body">{E(q["text"])}</p></details>' for q in qs) + '</div>'


def render_checklist(b):
    out = ''
    for it in b['items']:
        if it['type'] == 'field':
            if it['key'] == '고지':
                continue
            out += f'<div><dt>{E(it["key"])}</dt><dd>{E(it["value"])}</dd></div>'
        elif it['type'] == 'bullet':
            out += f'<div><dd>{E(it["text"])}</dd></div>'
    note = [it['value'] for it in b['items'] if it['type'] == 'field' and it['key'] == '고지']
    note_h = f'<div class="principle"><h3>atinc의 원칙</h3><p>{E(note[0])}</p></div>' if note else ''
    return f'<dl class="checklist">{out}</dl>{note_h}'


MEDPAGES = json.load(open(f'{SP}/medical_pages.json', encoding='utf-8'))
# phrases that read as efficacy claims or point to one particular hospital
MED_FIX = [
    ('본인 세포를 쓰기 때문에 면역 거부 부담이 적습니다.', ''),
    ('자가 세포는 본인 것이라 면역 거부 부담이 적습니다.', '어떤 세포가 맞는지, 위험은 무엇인지는 의료진 상담에서 설명을 들으실 수 있습니다.'),
    ('영하 196℃ 초저온으로 냉동해 최대 40년까지 보관할 수 있고', '영하 196℃ 초저온으로 냉동해 오래 보관할 수 있고'),
    ('최대 40년까지 보관할 수 있습니다.', '오래 보관할 수 있으며, 보관 기간은 기관과 계약에 따라 다릅니다.'),
    ('건강할 때 내 세포를 미리 보관해 두는 라인이 있고, 줄기세포 연구 기반의 프리미엄 라인도 있습니다.', '건강할 때 내 세포를 미리 보관해 두는 방법과, 지정 재생의료기관에서 받을 수 있는 진료를 안내해 드립니다.'),
    ('면역과 웰에이징 관리를 시작하고 싶을 때', '웰에이징 관리를 시작하고 싶을 때'),
    ('세포를 이용한 두피·모발 관리가 궁금할 때', '모발 유래 세포 보관이 궁금할 때'),
    ('네. 입원 병동과 1인실을 갖추고 있고, 365일 입원할 수 있습니다.', '네. 입원 병동과 1인실이 있는 협력 병원으로 안내해 드립니다.'),
    ('협력 병원의 한·양방 협진 센터에서는', '한·양방 협진 병원에서는'),
    ('입원 재활까지 같은 재단 병원에서 받으실 수 있습니다.', '입원 재활까지 한 곳에서 받으실 수 있습니다.'),
    ('>조직 재생 관리, 향후 세포 활용 대비<', '>향후 세포 활용 대비 보관<'),
    ('>면역 관리<', '>보관<'),
    ('>두피·모발 관리<', '>보관<'),
    ('>줄기세포 연구 기반 프리미엄 라인<', '>의료진 상담 후 결정<'),
]


def page_category(c):
    doc = parse(c['file'])
    B = blocks(doc)
    f1 = fields(B['01'])
    f12 = fields(B['12'])
    btn = btn_label(f12['버튼'])
    cat = prefill(f12['버튼'], c['ko'])
    M = MEDPAGES[c['id']]
    hero = (f'<section class="hero hero--photo" data-hdr-over><div class="hero__pic" aria-hidden="true">{pic("cat-" + c["id"], "", "100vw", (960, 1600, 2400), eager=True)}</div>'
            f'<div class="wrap hero__in hero__in--short"><nav class="crumb" aria-label="현재 위치"><a href="index.html">홈</a> / <a href="medical.html">진료 분야</a> / <span>{E(c["ko"])}</span></nav>'
            f'<p class="hero__label rise">{E(c["en"])}</p><h1 class="hero__title rise">{E(c["ko"])}</h1>'
            f'<p class="hero__sub rise rise-2">{E(f1["제목"])}</p>'
            f'<div class="hero__row"><p class="hero__body rise rise-3">{E(f1["본문"])}</p>'
            f'<div class="rise rise-4">{form_link(btn, cat, "btn btn--light")}</div></div></div></section>')

    def shd(label, title, more=None, href=None, lead=None):
        # detail pages: Korean heading only (English labels stay on the home page and heroes)
        m = f'<a class="shd__more" href="{href}">{E(more)}</a>' if more else ''
        ld = f'<p class="shd__lead">{E(lead)}</p>' if lead else ''
        return f'<div class="shd"><div><h2 class="shd__t">{E(title)}</h2>{ld}</div>{m}</div>'

    # 1. how atInc works for this field (service first)
    wy = ''.join(f'<li><span class="ways__no">{i:02d}</span><h3>{E(t)}</h3><p>{E(d)}</p></li>' for i, (t, d) in enumerate(M['ways'], 1))
    s2 = (f'<section class="sec msec"><div class="wrap">{shd("Our way", "atInc가 함께하는 방식", lead="병원을 고르고 예약하는 일부터 결과 이후까지, 이 분야에서 저희가 맡는 일입니다.")}'
          f'<ol class="ways">{wy}</ol></div></section>')
    # 2. what the partner institutions offer (information, not promises)
    sv = ''.join(f'<li><details class="fold" open data-fold><summary><h3>{E(sv_[0])}</h3><p>{E(sv_[1])}</p></summary>'
                 + (('<ul class="svcs__sub">' + ''.join(f'<li>{E(x)}</li>' for x in sv_[2]) + '</ul>') if len(sv_) > 2 else '') + '</details></li>'
                 for sv_ in M['services'])
    cols = ' svcs--4' if len(M['services']) % 4 == 0 else ''
    s1 = (f'<section class="sec sec--sand msec" id="services"><div class="wrap">{shd("Services", "협력 기관에서 받으실 수 있는 진료와 상담")}'
          f'<ul class="svcs{cols}">{sv}</ul>'
          f'<p class="msec__note">어떤 검사와 진료를 받을지는 의료진이 진찰한 뒤 정합니다. atInc는 맞는 기관을 찾아 예약하고, 그 앞뒤의 상담과 일정을 맡습니다.</p></div></section>')
    # 3. the kind of places we connect to (never the names)
    pt = ''.join(f'<li><h3>{E(t)}</h3><p>{E(d)}</p></li>' for t, d in M['partners'])
    s3 = (f'<section class="sec msec" id="partners"><div class="wrap">{shd("Partners", "함께하는 의료기관", "지역별로 보기", "network.html")}'
          f'<ul class="ptn">{pt}</ul><p class="msec__note">기관 이름은 상담에서 고객님께만 따로 말씀드립니다.</p></div></section>')
    # 4. process
    st_items = items(B['07'], 'step')
    steps = ''.join(f'<li class="step"><span class="step__no">{i:02d}</span><h3 class="h3">{E(st["title"])}</h3><p class="body">{E(st["text"])}</p></li>'
                    for i, st in enumerate(st_items, 1))
    s4 = f'<section class="sec sec--sand msec" id="process"><div class="wrap">{shd("Process", "진행 과정")}<ol class="steps{" steps--5" if len(st_items) == 5 else ""}">{steps}</ol></div></section>'
    # 5. questions, with the background reading folded underneath
    b2, b3, b5 = B['02'], B['03'], B['05']
    types_h = ''.join(tbl(it) for it in b3['items'] if it['type'] == 'table')
    more = (f'<div class="mmore"><details class="more"><summary>{E(josa(c["ko"], "이란", "란"))}</summary>{render_rows(b2["items"])}{types_h}</details>'
            f'<details class="more"><summary>원리와 방식</summary>{render_how(b5["items"])}</details>'
            f'<details class="more"><summary>가기 전에 확인하세요</summary>{render_checklist(B["09"])}</details></div>')
    s5 = (f'<section class="sec sec--sand msec" id="faq"><div class="wrap mfaq"><div>{shd("FAQ", "자주 묻는 질문")}{render_faq(B["10"])}</div>'
          f'<div>{shd("More", "더 알아보기")}{more}</div></div></section>')
    reasons = [it['text'] for it in B['04']['items'] if it['type'] == 'bullet']
    cta_title = '부담 없이 먼저 물어보세요' if c['id'] == 'men' else f12['문장']
    cta = cband(cta_title, '건강 목적과 일정을 남겨 주시면, 담당 매니저가 직접 연락드립니다.', btn, cat,
                reasons=reasons, reasons_title='이럴 때 상담하세요')
    # 4b. preparation and recovery as the partner institutions explain it (nothing that names them)
    gd = ''.join(f'<div class="guide__col"><details class="fold" open data-fold><summary><h3>{E(t)}</h3></summary><ul>' + ''.join(f'<li>{E(x)}</li>' for x in xs) + '</ul></details></div>' for t, xs in M.get('guide', []))
    s4b = (f'<section class="sec msec" id="guide"><div class="wrap">{shd("Guide", "협력 기관이 안내하는 준비와 회복")}<div class="guide">{gd}</div>'
           f'<p class="msec__note">협력 기관들이 고객에게 안내하는 일반적인 내용입니다. 실제 준비와 회복 일정은 예약하신 기관의 담당 의료진이 정하고, atInc는 그 안내를 일정에 넣어 전날 다시 알려 드립니다.</p></div></section>') if gd else ''
    main = hero + s2 + s1 + s3 + s4 + s4b + s5 + cta
    page(c['page'], f'{c["ko"]} | atinc', f1['본문'], main, 'medical', light=True)


# ------------------------------------------------------------------ CARE
def care_section(p):
    return [s for s in care['sections'] if (s['title'] or '').startswith(p['en'] + ' ·')][0]


def page_care_index():
    s = [x for x in care['sections'] if x['title'] == 'CARE 인덱스'][0]
    f = {it['key']: it['value'] for it in s['intro'] if it['type'] == 'field'}
    t = [it for it in s['intro'] if it['type'] == 'table'][0]
    rows = ''
    for i, (p, r) in enumerate(zip(CARE, t['rows']), 1):
        ko = r[0].split(' · ', 1)[1]
        rows += (f'<a class="clist__row" href="{p["page"]}"><figure class="clist__pic">{pic("prog-" + p["id"], "", "(max-width: 600px) 100vw, 320px", (480, 720))}</figure><span class="clist__no">0{i}</span><div><p class="clist__en">{E(p["en"].title() if p["id"] != "global-medical-journey" else "Global Medical Journey")}</p><h2 class="clist__t">{E(PROG_KO[p["id"]])}</h2>'
                 f'<p class="clist__line">{E(r[1])}</p></div><span class="clist__meta">{E(r[2])}</span></a>')
    hero = phero([('홈', 'index.html'), ('케어 프로그램', None)], 'Care Programs', f['제목'], f['본문'],
                 f'<figure class="phero__pic">{pic("desk", "", "(max-width: 900px) 100vw, 40vw", (640, 960, 1400), eager=True)}</figure>',
                 '')
    lst = f'<section class="sec"><div class="wrap"><div class="clist">{rows}</div></div></section>'
    f12 = fields(HB['12'])
    page('care.html', 'atinc CARE | atinc', f['본문'], hero + lst + cband(f12['제목'], f12['본문'], '케어 프로그램 상담 예약', 'atinc CARE'), 'care')


def page_care(p):
    import site_enrich as SE
    s = care_section(p)
    ko = s['title'].split(' · ', 1)[1]
    B = {b['no']: b for b in s['blocks']}
    rel = [it for it in s['intro'] if it['type'] == 'field' and it['key'] == '연결']

    def T(no):
        return ' '.join(it['text'] for it in B[no]['items'] if it['type'] == 'text')
    parts = [x.strip() for x in T('01').split(' / ')]
    lead_s, overview = parts[0], parts[1]
    trust = [x for x in parts if x.startswith('신뢰 표기')]
    trust_h = f'<p class="small" style="color: var(--on-dark-sub)">{E(trust[0].split(":", 1)[1].strip())}</p>' if trust else ''
    idx = CARE.index(p) + 1
    num = {'private-checkup': '30', 'longevity-90': '90', 'executive-365': '365'}.get(p['id'])
    hero = (f'<section class="hero hero--photo" data-hdr-over><div class="hero__pic" aria-hidden="true">{pic("prog-" + p["id"], "", "100vw", (960, 1600, 2400), eager=True)}</div>'
            f'<div class="wrap hero__in hero__in--short"><nav class="crumb" aria-label="현재 위치"><a href="index.html">홈</a> / <a href="care.html">케어 프로그램</a> / <span>{E(PROG_KO[p["id"]])}</span></nav>'
            f'<p class="hero__label rise">{E(p["en"].title() if p["id"] != "global-medical-journey" else "Global Medical Journey")}</p><h1 class="hero__title rise">{E(PROG_KO[p["id"]])}</h1>'
            f'<p class="hero__sub rise rise-2">{E(lead_s)}</p>'
            f'<p class="hero__body rise rise-3">{E(overview)}</p>{trust_h}<div class="rise rise-4">{SE.care_meta(p["id"])}</div></div></section>')
    def shd(label, title, more=None, href=None):
        m = f'<a class="shd__more" href="{href}">{E(more)}</a>' if more else ''
        return f'<div class="shd"><div><h2 class="shd__t">{E(title)}</h2></div>{m}</div>'
    pj = SE.PROG[p['id']]
    # 1. who it is for
    who = [x.strip() for x in T('02').split(' / ')]
    s_who = (f'<section class="sec msec"><div class="wrap">{shd("For whom", "이런 분께 맞습니다")}<ol class="ways ways--who">'
             + ''.join(f'<li><span class="ways__no">{i:02d}</span><h3>{E(w)}</h3></li>' for i, w in enumerate(who, 1)) + '</ol></div></section>')
    # 2. what atInc does and what you receive
    does = [x.strip() for x in T('05').split(' / ') if x.strip()]
    docs = [x.strip() for x in T('06').split(' / ') if x.strip()]
    s_inc = (f'<section class="sec sec--sand msec"><div class="wrap">{shd("Included", "포함된 것")}<div class="guide">'
             f'<div class="guide__col"><h3>atInc가 맡는 일</h3><ul>' + ''.join(f'<li>{E(x)}</li>' for x in does) + '</ul></div>'
             f'<div class="guide__col"><h3>받으시는 자료</h3><ul>' + ''.join(f'<li>{E(x)}</li>' for x in docs) + '</ul></div></div>'
             f'<p class="msec__note">{E(T("08"))}</p>'
             + ('<p class="msec__note">한국에 계시는 동안 응급 상황이 생기면 먼저 119에 전화하세요. 그다음 담당 매니저에게 연락 주시면 병원 연락과 통역을 돕겠습니다.</p>' if p['id'] == 'global-medical-journey' else '')
             + '</div></section>')
    # 3. stages
    t4 = table(B['04'])
    st = ''
    for i, r in enumerate(t4['rows'], 1):
        nm, en_n = r[0], ''
        if ' · ' in nm:
            en_n, nm = nm.split(' · ', 1)
        items_ = ''.join(f'<li>{E(x.strip())}</li>' for x in r[1].split(' / ') if x.strip())
        st += (f'<li><details class="fold" open data-fold><summary><span class="ways__no">{i:02d}</span><h3>{E(nm)}</h3>' + (f'<p class="svcs__en">{E(en_n)}</p>' if en_n else '')
               + f'</summary><ul class="svcs__sub">{items_}</ul></details></li>')
    cols = ' svcs--4' if len(t4['rows']) == 4 else ''
    s_proc = f'<section class="sec msec" id="process"><div class="wrap">{shd("Process", "진행 단계")}<ol class="svcs svcs--steps{cols}">{st}</ol></div></section>'
    # 4. options
    t7 = T('07')
    if '—' in t7:
        fit = {t['name']: t.get('fit', '') for t in (pj.get('tiers') or [])}
        rows_ = ''
        for a_, b_ in (x.strip().split(' — ', 1) for x in t7.split(' / ')):
            rows_ += (f'<li><h3>{E(SE.tcase(a_))}</h3><p>{E(b_)}' + (f'<span class="ptn__fit">이런 분께 · {E(fit[a_])}</span>' if fit.get(a_) else '') + '</p></li>')
        body7 = f'<ul class="ptn">{rows_}</ul>'
    else:
        body7 = f'<p class="lead">{E(t7)}</p>'
    if pj.get('specialized_journeys'):
        sj = ['정밀검진', '암 세컨드 오피니언', '여성 건강', '롱제비티·웰니스', '회복·재활', '뷰티·웰니스']
        body7 += ('<div class="ojourney"><h3>이런 목적의 일정을 준비해 드립니다</h3><ul>' + ''.join(f'<li>{E(x)}</li>' for x in sj) + '</ul></div>')
    s_opt = (f'<section class="sec sec--sand msec"><div class="wrap">{shd("Options", "구성 선택")}{body7}'
             f'<p class="msec__note">구성별 범위는 상담에서 목적과 일정에 맞춰 정하고, 비용은 상담 뒤 따로 알려 드립니다.</p></div></section>')
    # executive: three questions people always ask
    s_qa = ''
    if p['id'] == 'executive-365':
        pv = [('누가 알게 되는지', '건강 정보와 병원 일정은 본인이 정한 사람에게만 알립니다. 가족이나 비서실과 어디까지 나눌지는 첫 상담에서 함께 정합니다.'),
              ('대신 연락해도 되는지', '비서실이나 가족이 대신 연락하셔도 됩니다. 예약과 일정 변경은 미리 정해 둔 담당자와만 주고받습니다.'),
              ('비용은 어떻게 나뉘는지', '병원에 내는 진료비와 atinc 조율료, 통역·차량 같은 실비를 각각 나눠서 알려 드립니다. 병원비에 다른 비용을 섞지 않습니다.')]
        s_qa = (f'<section class="sec msec"><div class="wrap">{shd("Questions", "많이 물어보시는 세 가지")}<ul class="ptn">'
                + ''.join(f'<li><h3>{E(q)}</h3><p>{E(a_)}</p></li>' for q, a_ in pv) + '</ul></div></section>')
    fx = SE.facts_section('global', cls='sec facts-dark') if p['id'] == 'global-medical-journey' else ''
    # other programmes and the related field
    rel_h = ''
    if rel:
        cname = rel[0]['value'].split(' ', 2)[-1]
        c = CAT_BY_KO.get(cname)
        if c:
            rel_h = f'<a href="{c["page"]}">진료 분야 · {E(c["ko"])}</a>'
    others = ''.join(f'<a href="{q["page"]}">{E(PROG_KO[q["id"]])}</a>' for q in CARE if q is not p)
    s_more = f'<section class="pline"><div class="wrap pline__in"><p><b>다른 케어 프로그램</b></p><p class="pline__links">{others}{rel_h}</p></div></section>'
    cta_t = [x.strip() for x in T('09').split(' / ')]
    btn_raw = cta_t[1].replace('버튼:', '').strip()
    cta = cband(cta_t[0], '목적과 일정을 남겨 주시면, 담당 매니저가 직접 연락드립니다.', btn_label(btn_raw), prefill(btn_raw, 'atinc CARE'))
    main = hero + s_who + s_inc + s_proc + fx + s_opt + s_qa + s_more + cta
    page(p['page'], f'{p["en"]} | atinc CARE', overview, main, 'care', light=True)


# ------------------------------------------------------------------ NETWORK
def page_network():
    B = blocks(net, 'NETWORK')
    f1 = fields(B['01'])
    body1 = '서울, 인천, 경기, 대구, 부산의 협력 의료기관과 함께합니다. 의료기관의 이름과 정확한 위치는 상담에서 목적에 맞춰 개별로 안내해 드립니다.'
    hero = phero([('홈', 'index.html'), ('협력 네트워크', None)], 'NETWORK', f1['제목'], None, '',
                 '<p class="lead">지금은 <span data-net-regions>서울, 인천, 경기, 대구, 부산</span>의 병원과 함께하고, 협력 병원을 지역마다 계속 늘려 가고 있습니다. 병원 이름과 정확한 위치는 상담할 때 알려 드립니다.</p>')
    cards = ''.join(
        f'<div class="hcard" data-cats="{",".join(h["cats"])}" data-count><div class="hcard__top"><h2 class="h3">{E(h["name"])}</h2><span class="small" style="font-family: var(--f-en)">{E(h["en"])}</span></div>'
        f'<div class="chips" style="gap: 6px">' + ''.join(f'<span class="tag">{E(CAT_KO[x])}</span>' for x in h['cats']) + (f'<span class="tag">협력 의료기관</span>' if not h['cats'] else '') + '</div>'
        f'<p class="body">{E(h["line"])}</p></div>' for h in HUBS)
    sec = (f'<section class="sec" data-net style="padding-top: clamp(48px, 5vw, 72px)"><div class="wrap" style="display: grid; gap: 28px">{filters()}'
           f'<p class="net-empty" hidden>{E(EMPTY_MSG)}</p>'
           f'<div class="net__grid" style="align-items: start"><div class="map mapcard" style="position: sticky; top: calc(var(--hdr-h) + 24px)">{site_map("net")}</div>'
           f'<div style="display: grid; gap: 14px; min-width: 0"><div class="atnet-list" data-variant="cards"></div>'
           f'<p class="small" style="margin-top: 8px">의료기관의 이름과 위치는 상담에서 개별로 안내합니다. 남성건강은 지역과 관계없이 비뇨의학과 전문 클리닉과 상담으로 연결합니다.</p></div></div></div></section>')
    cta = cband('가까운 거점과 분야로 상담하기', '관심 분야와 지역을 남겨주시면, 목적에 맞는 협력 의료기관을 상담에서 개별로 안내합니다.', '프라이빗 상담 신청', '')
    page('network.html', 'NETWORK | atinc', f1['본문'], hero + sec + cta, 'network')


# ------------------------------------------------------------------ PARTNERS
def page_partners():
    B = blocks(net, 'FOR PARTNERS')
    f1 = fields(B['01'])
    hero = phero([('홈', 'index.html'), ('제휴 안내', None)], 'FOR PARTNERS', f1['제목'], f1['본문'], f'<figure class="phero__pic">{pic("partners", "", "(max-width: 900px) 100vw, 40vw", (640, 960, 1400), eager=True)}</figure>',
                 f'<div class="hero__actions"><a class="btn btn--dark" href="{PARTNER_MAIL}">제휴 문의 메일 보내기</a>'
                 f'<a class="link" href="#process">제휴 절차 보기</a></div>')
    f4 = {it['key']: [x.strip() for x in it['value'].split(' / ')] for it in B['04']['items'] if it['type'] == 'field'}
    types = [
        ('의료기관', '방문 목적과 기존 검사 자료가 정리된 고객을 소개해 드립니다. 통역과 이동, 방문 전후 연락은 저희가 맡으니 병원은 진료에 집중하시면 됩니다.', f4.get('의료기관', [])),
        ('해외 파트너', f'한국 진료를 원하는 고객을 보내 주시면 병원 선택과 예약, 체류 일정, 귀국 후 결과 전달까지 한 창구에서 맡습니다. atinc는 외국인환자 유치업 등록 사업자(제 A-2026-08-01-07161 호)입니다.',
         ['해외 의료관광 에이전시', '여행사·컨시어지', '현지 병원·클리닉']),
        ('기업·단체', '임원과 가족의 검진·진료 일정을 1년 단위로 맡습니다. 건강 정보는 본인이 동의한 범위 안에서만 회사와 나눕니다.', f4.get('기업·단체', [])),
        ('바이오 헬스케어', '검사나 세포 보관처럼 병원 밖에서 이뤄지는 서비스를 진료 일정과 함께 안내합니다.', f4.get('바이오 헬스케어', [])),
        ('프라이빗 서비스', '숙박, 차량, 의료통역처럼 고객의 체류를 함께 만드는 곳입니다. 진료 일정이 정해지면 그에 맞춰 예약을 드립니다.', f4.get('프라이빗 서비스', [])),
    ]
    rows = ''.join(f'<li><h3>{E(n)}</h3><p class="body">{E(d)}</p><ul>' + ''.join(f'<li>{E(x)}</li>' for x in lst) + '</ul></li>' for n, d, lst in types)
    s1 = (f'<section class="sec"><div class="wrap">{section_head(None, None, "이런 곳과 함께 일합니다", "파트너마다 저희가 맡는 일이 조금씩 다릅니다.")}'
          f'<ul class="ptypes">{rows}</ul></div></section>')
    t2 = table(B['02'])
    s2 = (f'<section class="sec sec--sand"><div class="wrap">{section_head(None, None, "고객 한 분을 맡으면 하는 일")}<ol class="steps steps--5">'
          + ''.join(f'<li class="step"><span class="step__no">{i:02d}</span><h3 class="h3">{E(r[0])}</h3><p class="body">{E(r[1])}</p></li>' for i, r in enumerate(t2['rows'], 1))
          + '</ol></div></section>')
    mou = [('첫 미팅', '서로 어떤 고객을 만나는지, 어떤 분야에서 함께할지 이야기합니다.'),
           ('자료와 현장 확인', '기관 소개 자료와 공개 범위를 받고, 필요하면 현장을 직접 둘러봅니다.'),
           ('협약', '협력 범위와 연락 창구, 정보 공개 범위를 정리해 MOU를 맺습니다.'),
           ('첫 고객 이후 점검', '첫 고객의 진행 과정을 함께 돌아보고, 고칠 부분을 정합니다.')]
    s_mou = (f'<section class="sec" id="process"><div class="wrap">{section_head(None, None, "제휴는 이렇게 진행됩니다")}<ol class="steps">'
             + ''.join(f'<li class="step"><span class="step__no">{i:02d}</span><h3 class="h3">{E(t)}</h3><p class="body">{E(d)}</p></li>' for i, (t, d) in enumerate(mou, 1))
             + '</ol></div></section>')
    b3 = B['03']
    lead3 = [it['text'] for it in b3['items'] if it['type'] == 'text']
    ko_std = {'RESPONSE': '빠른 응답', 'GLOBAL READINESS': '해외 고객 응대', 'TRANSPARENCY': '투명한 비용', 'VIP FLOW': '조용한 동선', 'CONTINUITY': '결과 이후 진료'}
    std = ''.join(f'<li><div><b class="h3">{E(ko_std.get(s_["title"], s_["title"]))}</b><p class="body">{E(s_["text"])}</p></div></li>'
                  for s_ in items(b3, 'step'))
    t5 = ' '.join(it['text'] for it in B['05']['items'] if it['type'] == 'text')
    docs = ''.join(f'<li>{E(x.strip())}</li>' for x in t5.split(' / '))
    s3 = (f'<section class="sec sec--sand"><div class="wrap cf"><div class="cf__col">{section_head(None, None, "함께 일할 병원을 고르는 기준", lead3[0] if lead3 else None)}'
          f'<ul class="rows rows--plain">{std}</ul></div>'
          f'<div class="cf__col">{section_head(None, None, "의료기관에 요청하는 자료", "어디까지 공개할지는 기관과 함께 정하고, 허락해 주신 범위 안에서만 씁니다.")}'
          f'<ul class="doclist">{docs}</ul></div></div></section>')
    f6 = fields(B['06'])
    cta = (f'<section class="sec cband" id="contact"><div class="wrap cband__grid"><div style="display: grid; gap: 22px"><h2 class="h1">{E(f6["제목"])}</h2>'
           f'<p class="lead">제휴 문의는 메일이 가장 빠릅니다. 회사와 담당자, 생각하시는 협력 분야를 적어 보내 주세요.</p></div>'
           f'<div class="cband__side"><a class="btn btn--light btn--wide" href="{PARTNER_MAIL}">제휴 문의 메일 보내기</a>'
           f'{form_link("문의 양식으로 남기기", "제휴 문의", "btn btn--ghost-light btn--wide", None)}'
           f'{contact_links(intl=True)}</div></div></section>')
    page('partners.html', 'FOR PARTNERS | atinc', f1['본문'], hero + s1 + s2 + s_mou + s3 + cta, 'partners')


# ------------------------------------------------------------------ CONSULTATION
def page_consult():
    B = blocks(net, 'CONSULTATION')
    f1 = fields(B['01'])
    hero = phero([('홈', 'index.html'), ('상담 안내', None)], 'PRIVATE CONSULTATION', f1['제목'], f1['본문'], f'<figure class="phero__pic">{pic("notes", "", "(max-width: 900px) 100vw, 40vw", (640, 960, 1400), eager=True)}</figure>',
                 f'<div class="hero__actions">{form_link("상담 신청서 열기", "", "btn btn--dark")}</div>'
                 f'{contact_links("contacts contacts--dark", intl=True)}')
    st = items(B['02'], 'step')
    s2 = (f'<section class="sec"><div class="wrap">{section_head("01", "HOW IT GOES", "상담은 이렇게 진행됩니다")}<ol class="steps">'
          + ''.join(f'<li class="step"><span class="step__no">{i:02d}</span><h3 class="h3">{E(s["title"])}</h3><p class="body">{E(s["text"])}</p></li>' for i, s in enumerate(st, 1))
          + '</ol></div></section>')
    t3 = table(B['03'])
    f3 = fields(B['03'])
    lis = ''.join(f'<li><span class="rows__no">{"필수" if r[1] == "필수" else "선택"}</span><div><b>{E(r[0])}</b>'
                  + (f'<p class="small">{E(r[3])}</p>' if r[3] and '법정' not in r[3] else '') + '</div></li>' for r in t3['rows'])
    s3 = (f'<section class="sec sec--sand"><div class="wrap">{section_head("02", "WHAT WE ASK", "신청서에서 여쭙는 것", f3["폼 상단 안내문"])}'
          f'<ul class="rows" style="max-width: 980px">{lis}</ul>'
          f'<div style="margin-top: 36px">{form_link("상담 신청서 열기", "", "btn btn--dark")}</div></div></section>')
    page('consultation.html', '상담 안내 | atinc', f1['본문'], hero + s2 + s3, 'consult')


# ------------------------------------------------------------------ LEGAL
def todo(t):
    return f'<em class="todo">{E(t)}</em>'


def page_privacy():
    hero = phero([('홈', 'index.html'), ('개인정보처리방침', None)], 'PRIVACY', '개인정보처리방침')
    D = []
    D.append(f'<p>주식회사 애트(atinc, 이하 "회사")는 「개인정보 보호법」에 따라 상담 신청자의 개인정보를 보호하고, 관련 문의를 신속하게 처리하기 위해 다음과 같이 개인정보처리방침을 둡니다.</p>')
    D.append('<section><h2>1. 수집하는 개인정보 항목과 방법</h2><ul class="dots"><li>필수: 성명, 국가·거주지역, 연락처, 선호 연락수단, 관심 분야, 문의내용</li><li>선택: 이메일, 방문 예정일</li>'
             '<li>수집 방법: 홈페이지의 상담 신청서(Google Forms)</li></ul><p>진단서, 검사결과 같은 의료자료는 상담 신청서로 받지 않습니다. 상담 진행에 필요한 자료는 담당자가 별도로 안내하고, 받을 때 따로 동의를 구합니다. 관심 분야와 문의 내용에 건강 상태가 적힐 수 있어, 이 내용은 3항에 따라 다룹니다.</p></section>')
    D.append('<section><h2>2. 수집·이용 목적</h2><ul class="dots"><li>상담 신청 확인과 연락</li><li>의료기관 상담 연결과 일정 조율</li><li>상담 이후 후속 안내</li></ul></section>')
    D.append('<section><h2>3. 민감정보(건강 관련 정보)의 처리</h2><p>상담 신청서의 관심 분야와 문의 내용, 상담하면서 말씀해 주신 병력과 복용 중인 약 같은 건강 관련 정보는 「개인정보 보호법」 제23조의 민감정보에 해당할 수 있습니다. 회사는 이 정보를 상담 연결과 일정 조율에만 쓰고, 다른 개인정보 처리에 대한 동의와 별도로 동의를 받아 처리합니다.</p>'
             '<p>진단서나 검사 결과처럼 의료기관에 전해야 하는 자료는 받는 곳과 항목, 목적, 보유 기간을 먼저 알려 드리고 따로 동의를 받은 뒤 필요한 범위에서만 전합니다.</p></section>')
    D.append(f'<section><h2>4. 보유·이용 기간</h2><p>상담 종료 후 1년 동안 보관한 뒤 지체 없이 파기합니다. 관계 법령에 따라 보존해야 하는 경우에는 그 법령이 정한 기간 동안 보관합니다.</p></section>')
    D.append('<section><h2>5. 제3자 제공</h2><p>회사는 정보주체의 동의 없이 개인정보를 제3자에게 제공하지 않습니다. 의료기관 상담 연결을 위해 제공이 필요한 경우, 제공받는 자, 제공 항목, 이용 목적, 보유 기간을 알리고 별도로 동의를 받은 뒤 필요한 범위에서만 제공합니다.</p></section>')
    D.append('<section><h2>6. 처리 위탁과 국외 이전</h2><p>상담 신청서의 내용은 Google LLC가 제공하는 Google Forms와 Google Sheets에 저장됩니다. 이 과정에서 개인정보가 Google의 해외 데이터센터에 저장될 수 있습니다.</p>'
             '<ul class="dots"><li>이전받는 자: Google LLC(연락처는 Google 개인정보처리방침 policies.google.com/privacy 에 안내되어 있습니다)</li><li>이전 국가: 미국 등 Google 데이터센터가 있는 국가</li><li>이전 항목: 상담 신청서에 입력한 항목</li><li>이전 시기와 방법: 신청서를 제출할 때 네트워크를 통해 전송</li><li>보유 기간: 4항과 같음</li>'
             '<li>거부 방법과 그 효과: 국외 이전을 원하지 않으시면 신청서 대신 전화나 이메일로 상담을 신청하실 수 있습니다. 상담을 받으시는 데 불이익은 없습니다.</li></ul></section>')
    D.append('<section><h2>7. 메신저로 상담하실 때</h2><p>카카오톡, WhatsApp, WeChat 같은 메신저로 상담하실 때는 진단서나 검사 결과지를 보내지 말아 주세요. 자료가 필요하면 담당 매니저가 전달 방법을 따로 안내해 드립니다. 메신저를 쓰시는 동안에는 각 메신저 운영사의 개인정보 처리방침도 함께 적용됩니다.</p></section>')
    D.append(f'<section><h2>8. 정보주체의 권리와 행사 방법</h2><p>정보주체는 언제든지 개인정보의 열람, 정정, 삭제, 처리정지를 요구할 수 있습니다. 요청은 <a href="mailto:{EMAIL}">{EMAIL}</a>로 보내 주시면 지체 없이 처리합니다.</p></section>')
    D.append('<section><h2>9. 파기 절차와 방법</h2><p>보유 기간이 지나거나 처리 목적이 달성된 개인정보는 지체 없이 파기합니다. 전자 파일은 복구할 수 없는 방법으로 삭제합니다.</p></section>')
    D.append(f'<section><h2>10. 개인정보의 안전성 확보 조치</h2><p>회사는 개인정보에 접근할 수 있는 사람을 상담 업무에 필요한 최소 인원으로 정합니다. 상담 신청서 응답은 회사 업무용 계정에서만 관리합니다. 계정에는 2단계 인증을 쓰고, 응답 자료는 상담을 맡은 담당 매니저에게만 공유합니다.</p></section>')
    D.append(f'<section><h2>11. 개인정보 보호책임자</h2><p>개인정보 보호책임자: 한수연(대표이사)<br>문의: <a href="mailto:{EMAIL}">{EMAIL}</a></p></section>')
    D.append('<section><h2>12. 권익침해 구제 방법</h2><p>개인정보 침해에 대한 상담이나 분쟁 해결이 필요하시면 아래 기관에 문의하실 수 있습니다.</p><ul class="dots"><li>개인정보분쟁조정위원회: 1833-6972 (www.kopico.go.kr)</li><li>개인정보침해신고센터: 국번 없이 118 (privacy.kisa.or.kr)</li></ul></section>')
    D.append(f'<section><h2>13. 시행일</h2><p>이 개인정보처리방침은 2026년 10월 7일부터 적용됩니다.</p></section>')
    body = f'<section class="sec" style="padding-top: clamp(48px, 5vw, 72px)"><div class="wrap"><div class="doc">{"".join(D)}</div></div></section>'
    page('privacy.html', '개인정보처리방침 | atinc', '주식회사 애트(atinc)의 개인정보처리방침', hero + body, 'legal')


def page_notice():
    B = blocks(net, 'LEGAL')
    b = [v for k, v in B.items() if k.startswith('Medical Notice')][0]
    paras = ''.join(f'<p>{E(it["text"])}</p>' for it in b['items'] if it['type'] == 'text')
    kv = (f'<dl class="kv"><dt>법인명</dt><dd>주식회사 애트 · 브랜드 atinc</dd><dt>대표</dt><dd>한수연</dd><dt>사업자등록번호</dt><dd>369-87-03095</dd>'
          f'<dt>외국인환자 유치업 등록번호</dt><dd>제 A-2026-08-01-07161 호</dd>' + (f'<dt>주소</dt><dd>{E(COMPANY_ADDRESS)}</dd>' if COMPANY_ADDRESS else '') + f'<dt>문의</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></dl>')
    hero = phero([('홈', 'index.html'), ('의료서비스 관련 고지', None)], 'MEDICAL NOTICE', '의료서비스 관련 고지')
    body = (f'<section class="sec" style="padding-top: clamp(48px, 5vw, 72px)"><div class="wrap"><div class="doc">{paras}'
            f'<section><h2>회사 정보</h2><div style="margin-top: 14px">{kv}</div></section></div></div></section>')
    page('medical-notice.html', 'Medical Notice | atinc', 'atinc 의료서비스 관련 고지', hero + body, 'legal')


# ------------------------------------------------------------------ build
if __name__ == '__main__':
    os.makedirs(f'{OUT}/assets/img', exist_ok=True)
    shutil.copy(f'{SP}/img/hero.jpg', f'{OUT}/assets/img/hero.jpg')
    shutil.copy(f'{SP}/img/arch.jpg', f'{OUT}/assets/img/arch.jpg')
    import site_home2
    site_home2.page_home2(); page_about(); page_medical()
    for c in CATS:
        page_category(c)
    page_care_index()
    for p in CARE:
        page_care(p)
    page_network(); page_partners(); page_consult(); page_privacy(); page_notice()
    import datetime
    today = datetime.date.today().isoformat()
    pri = {'index.html': '1.0', 'privacy.html': '0.2', 'medical-notice.html': '0.2'}
    urls = ''.join(f'<url><loc>{SITE_URL}{"" if f == "index.html" else f}</loc><lastmod>{today}</lastmod><priority>{pri.get(f, "0.7")}</priority></url>' for f in ['index.html'] + [x for x in PAGES if x != 'index.html'])
    open(f'{OUT}/sitemap.xml', 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(f'{OUT}/robots.txt', 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n')
    print(len(PAGES), PAGES)
    import site_revise as RV
    RV.report()
