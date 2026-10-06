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


ICON = {
    'chat': '<path d="M4 5.5h16v10H9.5L4 19.5z"/>',
    'phone': '<path d="M6.5 3.5h3l1.5 4-2 1.3a10 10 0 0 0 6.2 6.2l1.3-2 4 1.5v3a2 2 0 0 1-2 2A16 16 0 0 1 4.5 5.5a2 2 0 0 1 2-2z"/>',
    'medical': '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M12 8.5v7M8.5 12h7"/>',
    'calendar': '<rect x="3.5" y="5" width="17" height="15" rx="1.5"/><path d="M3.5 9.5h17M8 3v4M16 3v4"/>',
    'pin': '<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
    'globe': '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.4 2.5 3.5 5.3 3.5 8.5s-1.1 6-3.5 8.5c-2.4-2.5-3.5-5.3-3.5-8.5s1.1-6 3.5-8.5z"/>',
    'prev': '<path d="M14.5 6l-6 6 6 6"/>', 'next': '<path d="M9.5 6l6 6-6 6"/>',
    'pause': '<path d="M9 6v12M15 6v12"/>', 'play': '<path d="M8 5.5l11 6.5-11 6.5z"/>',
}


def svg(name):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICON[name]}</svg>'


def shd(label, title, more=None, more_href=None, h='h2'):
    m = f'<a class="shd__more" href="{more_href}">{E(more)}</a>' if more else ''
    return f'<div class="shd"><div><p class="shd__label">{E(label)}</p><{h} class="shd__t">{E(title)}</{h}></div>{m}</div>'


def page_home2():
    # 1. main visual: four faceless photographs, one message each
    slides_d = [
        ('hero-lounge', '엄선된 의료 · Private Healthcare Concierge', '병원 선택부터 결과 상담까지,<br>한 매니저가 맡습니다',
         '어느 병원에서 무엇을 받으실지 함께 비교하고, 정하신 병원의 예약과 동행, 결과 상담까지 같은 매니저가 챙깁니다.', form_link('상담 예약하기', '', 'btn btn--light', None)),
        ('hero-equipment', 'Health Checkup', '올해 검진,<br>나이와 가족력에 맞춰 고르세요',
         '검사 항목과 검진기관 정보를 함께 살펴보고, 맞는 곳을 3곳 안으로 추려 드립니다.', '<a class="btn btn--line" href="medical-checkup.html">검진 살펴보기</a>'),
        ('hero-seoul', 'Private Consultation', '어느 병원으로 가야 할지,<br>먼저 물어보세요',
         '목적과 일정을 듣고, 맞는 의료기관을 비교해 차이를 설명해 드립니다.', '<a class="btn btn--line" href="#process">진행 방식 보기</a>'),
        ('hero-arrival', 'Global Medical Journey', '한국에서의 진료 일정,<br>도착 전에 맞춰 둡니다',
         '해외에서 오시는 분께 병원 예약과 의료통역, 공항 픽업과 이동까지 한 번에 준비해 드립니다.', '<a class="btn btn--line" href="care-global-medical-journey.html">해외 고객 안내 보기</a>'),
    ]
    n = len(slides_d)
    sl = ''
    for i, (k, lab, t, d, act) in enumerate(slides_d):
        on = ' is-on' if i == 0 else ''
        sl += (f'<div class="slide{on}" role="group" aria-roledescription="slide" aria-label="{i + 1} / {n}">'
               f'{pic(k, "slide__pic", "100vw", (960, 1600, 2400), eager=(i == 0))}<span class="slide__veil" aria-hidden="true"></span>'
               f'<div class="wrap slide__in"><p class="slide__label">{E(lab)}</p><p class="slide__t">{t}</p>'
               f'<p class="slide__d">{E(d)}</p><div class="slide__act">{act}</div></div></div>')
    hero = (f'<section class="phx" data-hdr-over aria-roledescription="carousel" aria-label="주요 안내"><h1 class="sr-only">atinc 프라이빗 헬스케어 컨시어지</h1>'
            f'<div class="phx__slides" data-slides>{sl}</div>'
            f'<div class="wrap phx__ctrl"><p class="phx__count"><b data-cur>01</b><span> / {n:02d}</span></p>'
            f'<span class="phx__bar" aria-hidden="true"><i data-bar></i></span>'
            f'<button class="phx__btn" type="button" data-prev aria-label="이전 슬라이드">{svg("prev")}</button>'
            f'<button class="phx__btn" type="button" data-pause aria-label="자동 넘김 멈추기">{svg("pause")}</button>'
            f'<button class="phx__btn" type="button" data-next aria-label="다음 슬라이드">{svg("next")}</button></div></section>')

    # 2. quick menu
    q = [('medical', '진료 분야', 'href="medical.html"'),
         ('calendar', '케어 프로그램', 'href="care.html"'),
         ('pin', '지역 안내', 'href="network.html"'),
         ('globe', '해외 고객', 'href="care-global-medical-journey.html"')]
    qm = ''.join(f'<li><a {attr}>{svg(ic_)}<span>{E(lab)}</span></a></li>' for ic_, lab, attr in q)
    quick = f'<nav class="qmenu" aria-label="바로가기"><div class="wrap"><ul class="qmenu__list">{qm}</ul></div></nav>'

    # 2b. why go through atInc rather than straight to a hospital (service, not medical claims)
    why_d = [('비교', '한 병원 안에서만 고르지 않습니다', '목적과 일정을 듣고 맞는 곳을 3곳 안으로 추려, 기관마다 무엇이 다른지 설명해 드립니다.'),
             ('준비', '진료 시간을 꼭 필요한 이야기에', '병력과 복용 중인 약, 이전 검사 자료와 궁금한 점을 미리 정리해 진료에 가져가실 수 있게 합니다.'),
             ('비용', '병원비와 저희 비용을 나눠서', '병원에 내는 진료비와 atInc 조율료, 통역·차량 같은 실비를 각각 나눠 알려 드립니다.')]
    why = (f'<section class="sec hsec hwhy"><div class="wrap">{shd("Why Us", "병원에 바로 가실 때와 무엇이 다를까요")}'
           f'<ol class="ways">' + ''.join(f'<li><span class="ways__no">{i:02d}</span><p class="hwhy__k">{E(k)}</p><h3>{E(t)}</h3><p>{E(d)}</p></li>' for i, (k, t, d) in enumerate(why_d, 1))
           + '</ol><p class="hwhy__line">진료는 병원에서, 그 앞뒤는 atInc가 맡습니다.</p></div></section>')

    # 3. medical areas
    line = {'checkup': '나이와 가족력에 맞춘 검사 항목', 'regenerative': '세포 보관과 재생의료 상담',
            'aesthetic': '전문의 진찰부터 회복 일정까지', 'women': '여성 검진부터 갱년기, 난임까지',
            'men': '비뇨의학과 전문 진료', 'korean-medicine': '한·양방 협진 재활과 한방 미용'}
    tiles = ''.join(f'<a class="tile" href="{c["page"]}"><figure class="tile__pic">{pic("cat-" + c["id"], "", "(max-width: 600px) 82vw, (max-width: 1100px) 50vw, 33vw", (480, 720, 1080))}</figure>'
                    f'<p class="tile__en">{E(c["en"])}</p><h3 class="tile__t">{E(c["ko"])}</h3><p class="tile__d">{E(line[c["id"]])}</p></a>' for c in CATS)
    more = '암 세컨드 오피니언 · 난임·생식의학 · 뇌·기억력 · 안과'
    areas = (f'<section class="sec hsec" id="areas"><div class="wrap">{shd("Medical", "진료 분야", "전체 보기", "medical.html")}'
             f'<div class="tiles tiles--3">{tiles}</div>'
             f'<p class="hnote"><span>그 밖의 전문 진료</span>{E(more)}도 상담 후 알맞은 기관을 안내해 드립니다. <a href="medical.html#access">자세히</a></p></div></section>')

    # 4. programmes
    prog = [('private-checkup', '1일 + 30일', '검진 당일 동행과 결과 이후 30일'),
            ('longevity-90', '90일', '검진 결과를 90일 건강 일정으로'),
            ('executive-365', '12개월', '1년의 검진과 진료 일정을 한 매니저가'),
            ('global-medical-journey', '입국부터 귀국까지', '입국 전 준비부터 귀국 후 상담까지')]
    page_of = {p_['id']: p_['page'] for p_ in CARE}
    en_of = {p_['id']: (p_['en'].title() if p_['id'] != 'global-medical-journey' else 'Global Medical Journey') for p_ in CARE}
    pt = ''.join(f'<a class="tile tile--prog" href="{page_of[pid]}"><figure class="tile__pic">{pic("prog-" + pid, "", "(max-width: 600px) 82vw, (max-width: 1100px) 50vw, 25vw", (480, 720, 1080))}'
                 f'<span class="tile__tag">{E(tag)}</span></figure><p class="tile__en">{E(en_of[pid])}</p><h3 class="tile__t">{E(PROG_KO[pid])}</h3><p class="tile__d">{E(d)}</p></a>'
                 for pid, tag, d in prog)
    progs = (f'<section class="sec hsec hsec--tight"><div class="wrap">{shd("Care Programs", "케어 프로그램", "전체 보기", "care.html")}'
             f'<div class="tiles tiles--4">{pt}</div></div></section>')

    # 5. process
    steps = [('첫 상담', '지금 상황과 원하시는 일정을 듣습니다.'),
             ('병원 선택과 예약', '맞는 곳을 추려 드리고, 정하신 곳을 예약합니다.'),
             ('당일 동행', '병원 동행과 의료통역을 맡습니다.'),
             ('결과 이후', '결과 상담과 다음 일정을 챙깁니다.')]
    fl = ''.join(f'<li><span class="flow__no">{i:02d}</span><h3>{E(t)}</h3><p>{E(d)}</p></li>' for i, (t, d) in enumerate(steps, 1))
    process = (f'<section class="sec sec--sand hsec" id="process"><div class="wrap">{shd("How We Care", "진행 방식", "상담 안내", "consultation.html")}'
               f'<ol class="flow">{fl}</ol></div></section>')

    # 6. network
    net_s = (f'<section class="sec hsec net2" data-net><div class="wrap net2__grid"><div class="net2__txt">{shd("Locations", "전국 협력 의료기관")}'
             f'<p class="net2__d">지금은 <span data-net-regions>서울, 인천, 경기, 대구, 부산</span>의 협력 의료기관과 함께합니다. 기관 이름과 위치는 상담에서 안내해 드립니다.</p>'
             f'<p class="net-empty" hidden>{E(EMPTY_MSG)}</p><div class="atnet-list" data-variant="compact"></div>'
             f'<p><a class="link" href="network.html">지역별로 보기</a></p></div>'
             f'<div class="map mapcard">{site_map("home")}</div></div></section>')

    # 7. international
    intl = (f'<section class="sec hsec intl2"><div class="wrap intl2__grid"><figure class="intl2__pic">{pic("global", "", "(max-width: 900px) 100vw, 50vw", (720, 1080, 1600))}</figure>'
            f'<div class="intl2__txt">{shd("International", "해외에서 오시는 분께")}'
            f'<p class="intl2__d">진료 일정을 먼저 정하고, 숙소와 이동은 그 일정에 맞춥니다.</p>'
            f'<ul class="intl2__list"><li>병원 예약과 진료 일정</li><li>의료통역과 병원 동행</li><li>공항 픽업과 이동</li><li>귀국 후 결과 상담</li></ul>'
            f'<p class="intl2__en" lang="en">Coming from abroad? Write to us in English at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>'
            f'<p><a class="btn btn--dark" href="care-global-medical-journey.html">글로벌 메디컬 저니 보기</a></p></div></div></section>')

    # 8. contact: the appointment card
    contact = (f'<section class="sec hsec contact2" id="contact"><div class="wrap contact2__grid"><div class="contact2__txt">{shd("Private Consultation", "프라이빗 상담")}'
               f'<p class="contact2__d">신청서에 연락처와 관심 분야를 남겨 주시면, 담당 매니저가 고르신 방법으로 먼저 연락드립니다.</p>'
               f'<ul class="contact2__notes"><li>첫 통화에서 목적과 일정을 듣습니다</li><li>맞는 곳을 추려 비교해 드립니다</li><li>정하신 뒤에 예약과 동행을 준비합니다</li></ul>'
               f'<p><a class="link" href="consultation.html">상담 진행 방식 자세히 보기</a></p></div>'
               f'{appt_card("상담 예약", "")}</div></section>')

    main = hero + quick + why + areas + progs + process + net_s + intl + contact
    page('index.html', 'atinc | 프라이빗 헬스케어 컨시어지', '검진, 재생의료, 성형·피부, 여성·남성 진료, 한방까지. 필요한 병원 정보를 정리해 드리고 예약과 통역, 결과 이후 일정까지 전담 매니저가 챙깁니다.', main, 'home', light=False)
