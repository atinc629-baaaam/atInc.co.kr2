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

    # 1. hero — moving light, glass header and glass company bar
    trust_items = [('외국인환자 유치업 등록', '제 A-2026-08-01-07161 호', ''),
                   ('전담 매니저', '첫 상담부터 귀국 후까지 한 사람이 맡습니다', ''),
                   ('협력 병원', '서울, 인천, 경기, 대구, 부산', ' data-net-regions'),
                   ('민감정보 보호', '처음 상담할 때는 의료자료를 받지 않습니다', '')]
    trust_h = ''.join(f'<li><b>{E(a)}</b><span{attr}>{E(b)}</span></li>' for a, b, attr in trust_items)
    hero = (f'<section class="hx" data-fx="hero" data-hdr-over>'
            f'<div class="hx__veil" aria-hidden="true"></div>'
            f'<div class="wrap hx__grid"><div class="hx__text">'
            f'<h1 class="hx__h rise">건강을 넘어,<br>삶의 품격을 설계합니다.</h1>'
            f'<p class="hx__lead rise rise-2">검진부터 재생의료, 성형·피부, 여성·남성 진료, 한방까지. 목적에 맞는 병원을 고르고, '
            f'예약과 통역, 결과가 나온 뒤의 일정까지 전담 매니저 한 사람이 맡습니다.</p>'
            f'<div class="hx__actions rise rise-3">{form_link("상담 신청하기", "", "btn btn--ivory")}<a class="hx__more" href="#areas">의료 분야 보기</a></div>'
            f'</div></div>'
            f'<div class="wrap hx__foot"><ul class="hx__trust" data-glass aria-label="atInc 회사 정보">{trust_h}</ul></div>'
            f'</section>')

    # 2. intro — one sentence, then the three ways people come to us
    paths = [('Private Health Office', '꾸준히 관리받고 싶다면', '검진, 재검, 전문의 진료, 가족의 병원 일정까지 1년 단위 달력으로 챙깁니다. 결과지와 진료 기록은 한곳에 모아 둡니다.', 'care-executive-365.html', 'EXECUTIVE 365 보기'),
             ('Medical Access', '특정 진료가 필요하다면', '갖고 계신 검사 결과와 원하시는 바를 듣고, 맞는 진료과와 병원을 골라 예약까지 잡습니다.', 'medical.html', '의료 분야 보기'),
             ('Global Medical Journey', '해외에서 오신다면', '입국 전에 의료자료를 병원에 먼저 보내 상담하고, 체류 중에는 통역과 이동을, 귀국 후에는 결과자료와 후속 상담을 챙깁니다.', 'care-global-medical-journey.html', 'GLOBAL MEDICAL JOURNEY 보기')]
    paths_h = ''.join(f'<a class="path" href="{href}"><span class="path__en">{E(en)}</span><span class="path__q">{E(q)}</span>'
                      f'<span class="path__d">{E(d)}</span><span class="path__go">{E(lk)}</span></a>' for en, q, d, href, lk in paths)
    intro = (f'<section class="sec intro"><div class="wrap">'
             f'<h2 class="intro__h">프리미엄의 기준은 더 많은 선택이 아니라,<br>더 정확한 관리에 있습니다.</h2>'
             f'<p class="intro__lead">병원이나 패키지부터 권하지 않습니다. 상황을 먼저 듣고, 비교할 수 있게 보여드리고, 결과가 나온 뒤의 일정까지 챙깁니다.</p>'
             f'<div class="paths">{paths_h}</div></div></section>')

    # 3. six fields — an index, not a tab widget
    lines = {c['id']: r[1] for c, r in zip(CATS, table(HB['04'])['rows'])}
    rows_f = ''.join(f'<li><a class="fx-row" href="{c["page"]}"><span class="fx-row__ko">{E(c["ko"])}</span>'
                     f'<span class="fx-row__en">{E(c["en"])}</span><span class="fx-row__d">{E(lines[c["id"]])}</span>'
                     f'<span class="fx-row__where" data-net-for="{c["id"]}">{E(hubs_for(c["id"]))}</span></a></li>' for c in CATS)
    macc = ''.join(f'<li><a href="medical.html#access">{E(x)}</a></li>' for x in ['암 세컨드 오피니언', '난임·생식의학', '뇌·기억력', '안과'])
    fields_s = (f'<section class="sec sec--sand fields" id="areas"><div class="wrap">'
                f'<div class="fields__head"><h2 class="disp-2">상담은 한 번이면 됩니다</h2>'
                f'<p class="lead">여러 분야가 궁금하셔도 따로따로 문의하실 필요가 없습니다. 병원 이름은 상담할 때 알려 드립니다.</p></div>'
                f'<ul class="fx-index">{rows_f}</ul>'
                f'<div class="macc"><p><b>그 밖의 전문 진료</b><span>아래 분야는 정해 둔 협력 병원 없이, 상담 후 알맞은 병원을 찾아 예약해 드립니다.</span></p>'
                f'<ul>{macc}</ul></div></div></section>')

    # 4. programs — glass cards over the moving light
    sig = [('private-checkup', '프라이빗 정밀검진', '나이와 가족력에 맞춰 검사를 고르고, 결과 이후 30일을 챙깁니다.', '1일 검진 · 30일 후속 관리'),
           ('longevity-90', '90일 롱제비티', '검진 결과를 90일 동안 실천할 건강 일정으로 바꿉니다.', '정밀평가 · 30·60·90일 점검'),
           ('executive-365', '연간 헬스 오피스', '1년 동안 검진, 재검, 진료 일정을 한 매니저가 맡습니다.', '12개월 관리'),
           ('global-medical-journey', '글로벌 메디컬 저니', '해외에서 오시는 분의 한국 진료를 입국 전부터 귀국 후까지 맡습니다.', '맞춤 일정')]
    page_of = {p['id']: p['page'] for p in CARE}
    cards = ''
    for pid, ko, line, meta in sig:
        en = 'Global Medical Journey' if pid == 'global-medical-journey' else [p['en'] for p in CARE if p['id'] == pid][0].title()
        cards += (f'<a class="gcard" data-glass href="{page_of[pid]}"><span class="gcard__en">{E(en)}</span><span class="gcard__ko">{E(ko)}</span>'
                  f'<span class="gcard__line">{E(line)}</span><span class="gcard__meta">{E(meta)}</span></a>')
    progs = (f'<section class="sec progx" data-fx="deep" data-fx-seed="90"><div class="progx__veil" aria-hidden="true"></div><div class="wrap">'
             f'<div class="progx__head"><h2 class="disp-2">atinc를 대표하는<br>네 가지 프로그램</h2>'
             f'<p class="lead">검진 하루부터 1년 관리, 해외에서 오시는 일정까지. 관리 기간과 범위에 따라 고르시면 됩니다.</p></div>'
             f'<div class="gcards">{cards}</div></div></section>')

    # 5. how a consultation goes
    hiw_items = [('상황을 듣습니다', '지금의 고민, 갖고 계신 검사 결과와 진료 기록, 원하시는 날짜를 확인합니다.'),
                 ('병원을 비교합니다', '맞는 진료과와 병원을 두세 곳 골라 차이를 설명드립니다. 결정은 고객이 합니다.'),
                 ('일정을 잡습니다', '예약과 검사 순서, 통역과 이동을 하루 동선에 맞춰 잡습니다.'),
                 ('결과 이후를 챙깁니다', '결과 상담, 재검, 다음 진료 날짜를 정해 두고 때가 되면 먼저 연락드립니다.')]
    steps = ''.join(f'<li><span class="num-en">0{i}</span><div><h3>{E(t)}</h3><p class="body">{E(d)}</p></div></li>'
                    for i, (t, d) in enumerate(hiw_items, 1))
    files = [('상담 목적', '이번 방문에서 확인하고 싶은 것'), ('의료자료 요약', '기존 검사 결과, 복용 중인 약, 가족력'),
             ('병원 비교표', '두세 곳의 진료 방식과 일정 차이'), ('전체 일정표', '날짜와 시간, 이동과 통역'), ('후속 일정', '결과 상담, 재검, 다음 방문')]
    dossier = ''.join(f'<li><span>{i:02d}</span><b>{E(t)}</b><em>{E(d)}</em></li>' for i, (t, d) in enumerate(files, 1))
    method = (f'<section class="sec"><div class="wrap method"><div style="display: grid; gap: 26px">'
              f'<h2 class="disp-2">상담은 이렇게 진행됩니다</h2>'
              f'<ol class="msteps">{steps}</ol></div>'
              f'<div class="dossier"><p class="dossier__t">개인 일정 파일<small>상담이 끝나면 한 파일로 드립니다</small></p><ol>{dossier}</ol></div></div></section>')

    # 6. cell care — glass cells drawn in 3D
    rg = blocks(parse('03-2_재생의료_줄기세포.md'))
    lt = table(rg['06'])['rows']
    badges = {0: ['−196℃', '최대 40년', '보관증서'], 1: ['1회', '3회', '7회'], 2: ['1989년부터 연구'], 3: ['52주 GLP 시험', '허가 절차 진행 중'], 4: ['LONGEVITY 90 연계']}
    lst = ''
    for i, r in enumerate(lt):
        nm = r[0].split(' · ')[0]
        bd = ''.join(f'<i>{E(x)}</i>' for x in badges.get(i, []))
        lst += (f'<li class="line"><div class="line__name"><b>{E(nm)}</b><span>{bd}</span></div><p>{E(r[1])}</p>'
                f'<p class="line__for"><b>이런 분께</b>{E(r[2])}</p></li>')
    cell = (f'<section class="sec sec--sand cell" id="cell-care"><div class="wrap">'
            f'<div class="cellx"><div class="cellx__text"><h2 class="disp-2">내 세포로 준비하는<br>셀 케어</h2>'
            f'<p class="lead">건강할 때 내 세포를 채취해 보관해 두거나, 줄기세포 연구기관과 협력하는 라인을 고를 수 있습니다. 채취와 보관 날짜는 atinc가 병원과 맞춥니다.</p>'
            f'<dl class="specs specs--col"><div><dt>초저온 보관 온도</dt><dd>−196℃</dd></div><div><dt>최대 보관 기간</dt><dd>40<span>년</span></dd></div>'
            f'<div><dt>차세대 세포 플랫폼의 GLP 안전성 시험</dt><dd>52<span>주</span></dd></div></dl></div>'
            f'<div class="cellx__art" data-cells aria-hidden="true"></div></div>'
            f'<ul class="lines">{lst}</ul>'
            f'<div class="cell__foot"><p class="notice">어떤 라인이 맞는지는 의료진 상담과 검사 후에 정해집니다. 비용은 상담에서 안내합니다.</p>'
            f'<div style="display: flex; flex-wrap: wrap; gap: 12px">{form_link("셀 케어 상담하기", "재생의료·줄기세포", "btn btn--dark")}<a class="btn btn--ghost" href="medical-regenerative.html">라인업 자세히 보기</a></div></div>'
            f'</div></section>')

    # 7. network
    net_s = (f'<section class="sec netx" data-net><div class="wrap net__grid"><div style="display: grid; gap: 24px; min-width: 0">'
             f'<h2 class="disp-2">서울에서 시작해,<br>전국으로 넓혀 갑니다</h2><p class="lead">지금은 <span data-net-regions>서울, 인천, 경기, 대구, 부산</span>의 병원과 함께합니다. 같은 기준으로 고른 협력 병원을 지역마다 계속 늘려 가고 있습니다. 병원 이름은 상담하실 때 따로 말씀드립니다.</p>{filters()}'
             f'<p class="net-empty" hidden>{E(EMPTY_MSG)}</p><div class="atnet-list" data-variant="compact"></div>'
             f'<p><a class="link" href="network.html">지역별로 자세히 보기</a></p></div>'
             f'<div class="map mapcard">{site_map("home")}</div></div></section>')

    # 8. global
    f9 = fields(HB['09'])
    jb = ''
    for k, ko_k in [('Before Korea · 입국 전', '입국 전'), ('In Korea · 체류 중', '체류 중'), ('After Korea · 귀국 후', '귀국 후')]:
        lst2 = ''.join(f'<li>{ic("check")}<span>{E(x.strip())}</span></li>' for x in f9[k].split(', '))
        jb += f'<div><h3>{E(ko_k)}</h3><ul class="plist">{lst2}</ul></div>'
    glob = (f'<section class="sec"><div class="wrap"><div class="glob__top"><div class="glob__text"><h2 class="disp-2">해외에서 오시는 분께</h2>'
            f'<p class="lead">진료 일정이 먼저이고, 숙소와 이동은 그 일정에 맞춥니다.</p>'
            f'<p><a class="link" href="care-global-medical-journey.html">GLOBAL MEDICAL JOURNEY 보기</a></p><div class="jband">{jb}</div></div>{itin_card}</div>'
            f'<div class="gfacts"><h3 class="gfacts__t">숫자로 보는 한국 의료</h3>{SE.fact_cards([SE.FACTS["global"]["items"][i] for i in (0, 1, 3)])}</div></div></section>')

    # 9. partners (대표 소개는 당분간 숨김)
    partner = (f'<section class="sec sec--sand pband"><div class="wrap pband__in">'
               f'<h2 class="disp-2">병원, 기업, 해외 에이전시와 함께 일합니다</h2>'
               f'<p class="lead">환자를 소개하는 데서 끝내지 않습니다. 사전 상담과 자료 준비, 예약, 방문 전후 연락, 후속 관리까지 저희가 맡습니다.</p>'
               f'<p><a class="btn btn--ghost" href="partners.html">제휴 안내 보기</a></p></div></section>')

    # 10. contact — moving light again, the form button on glass
    cons = cband('먼저 이야기를 듣겠습니다', '건강 목적과 원하시는 일정을 남겨 주시면, 담당 매니저가 직접 연락드립니다.', '상담 신청하기', '', fx='deep')
    cons = cons.replace('<div class="cband__side">', '<div class="cband__side cband__glass" data-glass>', 1)
    main = hero + intro + fields_s + progs + method + cell + net_s + glob + partner + cons
    page('index.html', 'atinc | 프라이빗 헬스케어 컨시어지', '검진, 재생의료, 성형·피부, 여성·남성 진료, 한방까지. 목적에 맞는 한국의 병원을 고르고 예약과 통역, 결과 이후 일정까지 전담 매니저가 맡습니다.', main, 'home', light=False)
