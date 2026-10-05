import json, math

ACC = '#7A5741'
import os
m = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mapproj.json')))
PROV = m['prov']
HUBPROV = {'서울특별시', '인천광역시', '경기도', '대구광역시', '부산광역시'}
INSET_SET = ['서울특별시', '인천광역시', '경기도', '강원도', '충청남도', '충청북도']

# capital-region inset: source box (190,120)-(310,215) -> dest (320,560) scale 1.92
SX, SY, SC = 190, 120, 1.92
DX, DY = 320, 560


def ins(x, y):
    return DX + (x - SX) * SC, DY + (y - SY) * SC


HUB2PROV = {'서울 강남': '서울특별시', '인천 송도': '인천광역시', '인천 검단': '인천광역시', '경기 용인': '경기도', '대구': '대구광역시', '부산': '부산광역시'}


def prov_paths(names=None, hub_fill='#E6D4C0', fill='#F8F2EA', nonscale=False, hubprov=None):
    hp = hubprov if hubprov is not None else HUBPROV
    out = []
    for name, d in PROV.items():
        if names and name not in names:
            continue
        f = hub_fill if name in hp else fill
        ve = ' vector-effect="non-scaling-stroke"' if nonscale else ''
        out.append(f'<path d="{d}" fill="{f}"{ve}></path>')
    return ''.join(out)


def marker(x, y, r=5.5, pulse=True, delay=0, on=True):
    s = ''
    col = ACC if on else '#B9AC9E'
    if pulse and on:
        s += f'<circle class="ap-pulse" cx="{x:.1f}" cy="{y:.1f}" r="{r*2.2:.1f}" fill="{ACC}" fill-opacity="0.22" style="animation-delay: {delay}s"></circle>'
    s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r if on else r*0.75:.1f}" fill="{col}" stroke="#FFFDF9" stroke-width="2.2"></circle>'
    return s


def text(x, y, t, anchor='start', size=14, weight=500, fill='#2E2119', ls=None):
    l = f' letter-spacing="{ls}"' if ls else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="Noto Sans KR, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}"{l}>{t}</text>'


def map_svg(uid='m', active=None, hide=False):
    H = m['hubs']
    act = set(active) if active else {'서울 강남', '인천 송도', '인천 검단', '경기 용인', '대구', '부산'}
    on = lambda k: k in act
    hp = {HUB2PROV[k] for k in act}
    tc = lambda k: '#2E2119' if on(k) else '#8C7B6D'
    gx, gy = H['서울 강남']
    icx, icy = H['ICN']
    s = []
    shown = [k for k in ['서울 강남', '인천 송도', '인천 검단', '경기 용인', '대구', '부산'] if on(k) or not hide]
    s.append(f'<svg viewBox="0 0 560 760" width="100%" role="img" aria-label="협력 거점 지도: {", ".join(shown)}" style="display: block; width: 100%; height: auto">')
    s.append(f'<defs><clipPath id="apClip{uid}"><rect x="{DX}" y="{DY}" width="230" height="182" rx="12"></rect></clipPath></defs>')
    # arrivals
    s.append(text(6, 24, 'GLOBAL ARRIVALS · ICN', size=11.5, weight=500, fill='#6B5A4E', ls='2.2'))
    for d in [f'M0 52 Q 110 86 {icx:.1f} {icy:.1f}', f'M0 250 Q 100 228 {icx:.1f} {icy:.1f}', f'M0 360 Q 120 300 {icx:.1f} {icy:.1f}']:
        s.append(f'<path class="ap-dash" d="{d}" fill="none" stroke="{ACC}" stroke-opacity="0.55" stroke-width="1.3" stroke-dasharray="3 6" stroke-linecap="round"></path>')
    # provinces
    s.append('<g stroke="#FFFDF9" stroke-width="0.9" stroke-linejoin="round">' + prov_paths(hubprov=hp) + '</g>')
    # network lines
    dx, dy = H['대구']; bx, by = H['부산']
    for d, k in [(f'M{gx:.1f} {gy:.1f} Q 420 250 {dx:.1f} {dy:.1f}', '대구'), (f'M{gx:.1f} {gy:.1f} Q 486 262 {bx:.1f} {by:.1f}', '부산')]:
        if on(k):
            s.append(f'<path d="{d}" fill="none" stroke="{ACC}" stroke-opacity="0.5" stroke-width="1.3"></path>')
    # capital region box + leader
    s.append(f'<rect x="{SX}" y="{SY}" width="120" height="95" rx="8" fill="none" stroke="{ACC}" stroke-opacity="0.7" stroke-width="1" stroke-dasharray="4 4"></rect>')
    cap_n = sum(1 for k in ['서울 강남', '인천 검단', '인천 송도', '경기 용인'] if on(k) or not hide)
    s.append(text(316, 132, f'수도권 {cap_n}개 거점', size=12.5, weight=600))
    s.append(f'<path d="M300 215 L 372 560" fill="none" stroke="{ACC}" stroke-opacity="0.45" stroke-width="1" stroke-dasharray="3 4"></path>')
    # main markers
    for k in ['서울 강남', '인천 검단', '인천 송도', '경기 용인']:
        if hide and not on(k):
            continue
        x, y = H[k]; s.append(marker(x, y, r=3.4, pulse=False, on=on(k)))
    s.append(f'<rect x="{icx-4:.1f}" y="{icy-4:.1f}" width="8" height="8" transform="rotate(45 {icx:.1f} {icy:.1f})" fill="#2E2119"></rect>')
    if not (hide and not on('대구')):
        s.append(marker(dx, dy, r=6, delay=0.6, on=on('대구')))
        s.append(text(dx - 14, dy + 5, '대구', anchor='end', size=15, weight=600, fill=tc('대구')))
    if not (hide and not on('부산')):
        s.append(marker(bx, by, r=6, delay=1.2, on=on('부산')))
        s.append(text(bx + 13, by + 5, '부산', size=15, weight=600, fill=tc('부산')))
    # inset
    s.append(f'<rect x="{DX}" y="{DY}" width="230" height="182" rx="12" fill="#FBF8F3" stroke="#D9C7B2" stroke-width="1"></rect>')
    s.append(f'<g clip-path="url(#apClip{uid})"><g transform="translate({DX} {DY}) scale({SC}) translate({-SX} {-SY})" stroke="#FFFDF9" stroke-width="1.2" stroke-linejoin="round">' + prov_paths(INSET_SET, nonscale=True, hubprov=hp) + '</g></g>')
    s.append(text(DX + 12, DY + 20, '수도권 확대', size=11, weight=500, fill='#6B5A4E', ls='0.5'))
    ix, iy = ins(icx, icy)
    s.append(f'<rect x="{ix-5:.1f}" y="{iy-5:.1f}" width="10" height="10" transform="rotate(45 {ix:.1f} {iy:.1f})" fill="#2E2119"></rect>')
    s.append(text(ix, iy + 22, 'ICN', anchor='middle', size=11, weight=600, ls='1'))
    lab = {'서울 강남': (0, -13, 'middle'), '인천 검단': (0, -13, 'middle'), '인천 송도': (0, 23, 'middle'), '경기 용인': (-12, 5, 'end')}
    for i, (k, (ox, oy, an)) in enumerate(lab.items()):
        if hide and not on(k):
            continue
        x, y = ins(*H[k]); s.append(marker(x, y, r=5, delay=i * 0.4, on=on(k)))
        s.append(text(x + ox, y + oy, k, anchor=an, size=12.5, weight=600, fill=tc(k)))
    # ulleung / dokdo inset
    s.append('<rect x="472" y="12" width="80" height="78" rx="10" fill="none" stroke="#D9C7B2" stroke-width="1"></rect>')
    isl = m['islands'][0][1]
    cx = sum(p[0] for p in isl) / len(isl); cy = sum(p[1] for p in isl) / len(isl)
    pts = ' '.join(f'{498 + (x - cx) * 2.4:.1f},{44 + (y - cy) * 2.4:.1f}' for x, y in isl)
    s.append(f'<polygon points="{pts}" fill="#F8F2EA" stroke="#C9B49C" stroke-width="0.8"></polygon>')
    s.append('<circle cx="531" cy="56" r="2" fill="#C9B49C"></circle><circle cx="535" cy="57" r="1.6" fill="#C9B49C"></circle>')
    s.append(text(498, 80, '울릉도', anchor='middle', size=10, weight=500, fill='#6B5A4E'))
    s.append(text(533, 80, '독도', anchor='middle', size=10, weight=500, fill='#6B5A4E'))
    s.append('</svg>')
    return ''.join(s)


if __name__ == '__main__':
    out = map_svg()
    print(len(out))
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'map_test.svg'), 'w').write(out.replace('class="ap-pulse"', '').replace('class="ap-dash"', ''))
