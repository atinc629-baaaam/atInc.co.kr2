# HOME v2 — imported by site_build.py
import re
from site_build import *  # noqa
import site_enrich as SE

SITE_LABEL = {
    'checkup': '프리미엄 정밀검진 센터 · 서울 강남 / 경기 용인 / 부산',
    'regenerative': '프리미엄 셀 케어 센터 · 경기 군포 GMP 시설 / 경기 분당 재생의료 실시기관',
    'aesthetic': '성형외과·피부과 협진 클리닉 · 인천 송도 / 피부 클리닉 · 서울 강남',
    'women': '여성 프라이빗 클리닉 · 서울 강남',
    'men': '남성 프라이빗 클리닉 · 비뇨의학과 연계',
    'korean-medicine': '한·양방 협진 한방병원 · 서울 압구정 / 인천 검단',
}
PANEL_IMG = {
    'checkup': (HERO, '84% 40%'), 'regenerative': (ARCH, '50% 30%'), 'aesthetic': (HERO, '72% 70%'),
    'women': (ARCH, '40% 60%'), 'men': (HERO, '96% 50%'), 'korean-medicine': (ARCH, '64% 46%'),
}


def cat_items(c):
    B = blocks(parse(c['file']))
    t = table(B['03'])
    return [r[0] for r in t['rows']] if t else []


def hubs_for(cid):
    hs = [h['name'] for h in HUBS if cid in h['cats']]
    return ' · '.join(hs) if hs else '지역과 관계없이 상담으로 연결합니다'


def page_home2():
    itin = [('Day 1', '09:00', '정밀검진', '정밀검진 센터, 서울 강남'),
            ('Day 1', '15:30', '결과 상담', '매니저와 의료통역 동행'),
            ('Day 2', '10:30', '셀 케어 상담', '셀 케어 센터, 경기'),
            ('Day 2', '14:00', '피부 시술 상담', '협진 클리닉, 인천 송도'),
            ('Day 30', '—', '귀국 후 화상 상담', '결과자료 전달, 다음 방문 날짜 확인')]
    rows = ''.join(f'<li><time>{E(t)}<small>{E(d)}</small></time><p>{E(a)}<span>{E(b)}</span></p></li>' for d, t, a, b in itin)
    itin_card = (f'<div class="itin" aria-label="예시 일정"><div class="itin__top"><b>어느 해외 고객의 이틀</b><span>예시</span></div>'
                 f'<ol>{rows}</ol><p class="itin__note">실제 일정은 상담 후 정합니다.</p></div>')

    # 1. hero — photographs first
    slides = ''.join(f'<div class="slide{" is-on" if i == 0 else ""}">{pic(k, "", "100vw", (960, 1600, 2400), eager=(i == 0))}</div>'
                     for i, k in enumerate(['hero-consult', 'hero-seoul', 'hero-equipment', 'hero-lab']))
    trust_items = [('외국인환자 유치업 등록', '제 A-2026-08-01-07161 호', ''),
                   ('전담 매니저', '첫 상담부터 귀국 후까지 한 사람이 맡습니다', ''),
                   ('협력 병원', '서울, 인천, 경기, 대구, 부산', ' data-net-regions'),
                   ('민감정보 보호', '처음 상담할 때는 의료자료를 받지 않습니다', '')]
    trust_h = ''.join(f'<li><b>{E(a)}</b><span{attr}>{E(b)}</span></li>' for a, b, attr in trust_items)
    hero = (f'<section class="phx" data-hdr-over><div class="phx__slides" data-slides>{slides}</div><div class="phx__veil" aria-hidden="true"></div>'
            f'<div class="wrap phx__in"><h1 class="phx__h rise">건강을 넘어,<br>삶의 품격을 설계합니다.</h1>'
            f'<p class="phx__lead rise rise-2">목적에 맞는 한국의 병원을 고르고, 예약부터 결과 이후까지 전담 매니저 한 사람이 함께합니다.</p>'
            f'<div class="phx__actions rise rise-3">{form_link("상담 신청하기", "", "btn btn--ivory")}<a class="hx__more" href="#areas">진료 분야 보기</a></div></div>'
            f'<div class="wrap phx__foot"><ul class="hx__trust" aria-label="atInc 회사 정보">{trust_h}</ul></div></section>')

    # 2. six fields — one photograph each
    lines = {c['id']: r[1] for c, r in zip(CATS, table(HB['04'])['rows'])}
    cards = ''.join(f'<a class="fcard" href="{c["page"]}">{pic("cat-" + c["id"], "fcard__img", "(max-width: 600px) 100vw, (max-width: 1100px) 50vw, 33vw", (480, 720, 1080))}'
                    f'<span class="fcard__veil" aria-hidden="true"></span><span class="fcard__txt"><em>{E(c["en"])}</em><b>{E(c["ko"])}</b><span>{E(lines[c["id"]])}</span></span></a>' for c in CATS)
    macc = ''.join(f'<li><a href="medical.html#access">{E(x)}</a></li>' for x in ['암 세컨드 오피니언', '난임·생식의학', '뇌·기억력', '안과'])
    fields_s = (f'<section class="sec fields2" id="areas"><div class="wrap">'
                f'<div class="sh2"><h2 class="disp-2">상담은 한 번이면 됩니다</h2>'
                f'<p class="lead">어느 분야든 맞는 병원을 골라 예약까지 잡아 드립니다.</p></div>'
                f'<div class="fcards">{cards}</div>'
                f'<div class="macc"><p><b>그 밖의 전문 진료</b><span>상담 후 알맞은 병원을 찾아 예약해 드립니다.</span></p><ul>{macc}</ul></div></div></section>')

    # 3. how we take care of you — four scenes
    scenes = [('step-listen', '상담', '지금 상황과 원하시는 일정을 듣습니다.'),
              ('step-arrange', '병원 선택과 예약', '맞는 병원 두세 곳을 비교해 드리고 예약을 잡습니다.'),
              ('step-escort', '동행과 이동', '병원 동행, 의료통역, 차량까지 맡습니다.'),
              ('step-after', '결과 이후', '결과 상담과 다음 일정을 먼저 챙깁니다.')]
    sc = ''.join(f'<li class="scene"><figure>{pic(k, "", "(max-width: 600px) 100vw, (max-width: 1100px) 50vw, 25vw", (480, 720, 1080))}</figure>'
                 f'<span class="scene__no">0{i}</span><h3>{E(t)}</h3><p>{E(d)}</p></li>' for i, (k, t, d) in enumerate(scenes, 1))
    journey = (f'<section class="sec sec--sand journey"><div class="wrap"><div class="sh2"><h2 class="disp-2">처음 상담부터 결과 이후까지</h2>'
               f'<p class="lead">한 사람의 매니저가 모든 단계를 함께합니다.</p></div><ol class="scenes">{sc}</ol></div></section>')

    # 4. programs — photo cards
    sig = [('private-checkup', '프라이빗 정밀검진', '나이와 가족력에 맞춘 검진, 결과 이후 30일까지'),
           ('longevity-90', '90일 롱제비티', '검진 결과를 90일 건강 일정으로'),
           ('executive-365', '연간 헬스 오피스', '1년 동안의 검진과 진료 일정을 한 매니저가'),
           ('global-medical-journey', '글로벌 메디컬 저니', '입국 전부터 귀국 후까지')]
    page_of = {p['id']: p['page'] for p in CARE}
    pc = ''
    for pid, ko, line in sig:
        en = 'Global Medical Journey' if pid == 'global-medical-journey' else [p['en'] for p in CARE if p['id'] == pid][0].title()
        pc += (f'<a class="pcard" href="{page_of[pid]}"><figure>{pic("prog-" + pid, "", "(max-width: 600px) 100vw, (max-width: 1100px) 50vw, 25vw", (480, 720, 1080))}</figure>'
               f'<span class="pcard__en">{E(en)}</span><span class="pcard__ko">{E(ko)}</span><span class="pcard__line">{E(line)}</span></a>')
    progs = (f'<section class="sec progs2"><div class="wrap"><div class="sh2"><h2 class="disp-2">atinc를 대표하는 네 가지 프로그램</h2></div>'
             f'<div class="pcards">{pc}</div></div></section>')

    # 5. network
    net_s = (f'<section class="sec netx" data-net><div class="wrap net__grid"><div style="display: grid; gap: 24px; min-width: 0">'
             f'<h2 class="disp-2">서울에서 시작해,<br>전국으로 넓혀 갑니다</h2><p class="lead">지금은 <span data-net-regions>서울, 인천, 경기, 대구, 부산</span>의 병원과 함께하고, 지역마다 협력 병원을 늘려 가고 있습니다.</p>{filters()}'
             f'<p class="net-empty" hidden>{E(EMPTY_MSG)}</p><div class="atnet-list" data-variant="compact"></div>'
             f'<p><a class="link" href="network.html">지역별로 자세히 보기</a></p></div>'
             f'<div class="map mapcard">{site_map("home")}</div></div></section>')

    # 6. global
    glob = (f'<section class="sec glob2"><div class="wrap glob2__grid"><figure class="glob2__pic">{pic("global", "", "(max-width: 900px) 100vw, 50vw", (720, 1080, 1600))}</figure>'
            f'<div class="glob2__text"><h2 class="disp-2">해외에서 오시는 분께</h2>'
            f'<p class="lead">진료 일정이 먼저이고, 숙소와 이동은 그 일정에 맞춥니다.</p>{itin_card}'
            f'<p><a class="link" href="care-global-medical-journey.html">GLOBAL MEDICAL JOURNEY 보기</a></p></div></div></section>')

    # 7. partners (대표 소개는 당분간 숨김)
    partner = (f'<section class="sec sec--sand pband"><div class="wrap pband__in">'
               f'<h2 class="disp-2">병원, 기업, 해외 에이전시와 함께 일합니다</h2>'
               f'<p class="lead">사전 상담과 자료 준비, 예약, 방문 전후 연락, 후속 관리까지 저희가 맡습니다.</p>'
               f'<p><a class="btn btn--ghost" href="partners.html">제휴 안내 보기</a></p></div></section>')

    # 8. contact — photograph behind glass
    cons = cband('먼저 이야기를 듣겠습니다', '건강 목적과 원하시는 일정을 남겨 주시면, 담당 매니저가 직접 연락드립니다.', '상담 신청하기', '')
    cons = cons.replace('<section class="sec cband" id="contact">', f'<section class="sec cband cband--photo" id="contact"><div class="cband__bg" aria-hidden="true">{pic("contact", "", "100vw", (960, 1600, 2400))}</div>', 1)
    cons = cons.replace('<div class="cband__side">', '<div class="cband__side cband__glass">', 1)
    main = hero + fields_s + journey + progs + net_s + glob + partner + cons
    page('index.html', 'atinc | 프라이빗 헬스케어 컨시어지', '검진, 재생의료, 성형·피부, 여성·남성 진료, 한방까지. 목적에 맞는 한국의 병원을 고르고 예약과 통역, 결과 이후 일정까지 전담 매니저가 맡습니다.', main, 'home', light=False)
