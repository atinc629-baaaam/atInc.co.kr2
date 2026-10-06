# Shared enrichment blocks: existing atinc.co.kr program copy (programs.json) + partner facts without names
import json, math, os, re
from site_build import E, ic, form_link, SP

PROG = json.load(open(os.path.join(SP, 'programs.json'), encoding='utf-8'))


def fix(t):
    return (t or '').replace('at PRIVÉ', 'atinc')


KEEP = {'MDT', 'PGT', 'IVF', 'NK', 'GMP', 'CT', 'MRI', '&', 'VIP', 'CEO'}


def tcase(s):
    out = []
    for w in s.split(' '):
        if w in KEEP:
            out.append(w)
        elif '-' in w:
            out.append('-'.join(p.capitalize() if not p.isdigit() else p for p in w.split('-')))
        elif "'" in w:
            out.append(w[:1].upper() + w[1:].lower())
        else:
            out.append(w.capitalize())
    return ' '.join(out)


# ------------------------------------------------------------------ insight orbit
def orbit(center, nodes, label=''):
    n = len(nodes)
    r = 36
    lis = ''
    for i, (en, ko) in enumerate(nodes):
        a = math.radians(-90 + 360 / n * i)
        x, y = 50 + r * math.cos(a), 50 + r * math.sin(a)
        lis += f'<li style="--x: {x:.1f}%; --y: {y:.1f}%"><i aria-hidden="true"></i><span>{E(ko)}</span></li>'
    return (f'<div class="orbit"><div class="orbit__core"><small>{E(label)}</small><b>{E(tcase(center))}</b></div>'
            f'<ul class="orbit__nodes">{lis}</ul></div>')


def access_cards(pa):
    return '<ul class="acc">' + ''.join(
        f'<li><h3>{E(a["ko"])}</h3><p class="body">{E(fix(a["copy"]))}</p></li>' for a in pa) + '</ul>'


def insight_section(ins, pa=None, positioning=None, sid='approach', cls='sec sec--sand', statement=None, head_no=None, extra=''):
    # 선언 문장 하나 + 설명 한 단락. 장식 도형(오빗)은 쓰지 않습니다.
    return (f'<section class="{cls} sec--st" id="{sid}"><div class="wrap"><div class="stmt">'
            f'<h2 class="stmt__h">{E(fix(ins["title"]))}</h2>'
            f'<p class="lead">{E(fix(ins["copy"]))}</p></div>'
            + (access_cards(pa) if pa else '') + extra + '</div></section>')


# ------------------------------------------------------------------ category data
CAT_PROG = {'checkup': 'private-checkup', 'regenerative': 'regenerative', 'women': 'womens-private', 'men': 'mens-private'}

CUSTOM = {
    'aesthetic': dict(
        statement='시술 하나를 고르기보다, 회복과 일정까지 함께 설계합니다.',
        insight=dict(eyebrow='AESTHETIC PLAN', title='시술 하나를 고르기보다, 회복과 일정까지 함께 설계합니다.',
                     copy='수술·리프팅·스킨부스터·레이저 가운데 무엇이 맞는지는 피부 상태와 회복에 쓸 수 있는 기간, 한국 체류 일정에 따라 달라집니다. 성형외과와 피부과 전문의 상담으로 방법을 조합하고, 시술 간격과 경과 확인 날짜까지 한 번에 정리합니다.',
                     center='PERSONAL AESTHETIC PLAN',
                     nodes=[['Surgery', '성형 수술'], ['Lifting', '리프팅 장비·실리프팅'], ['Skin Booster', '스킨부스터·쁘띠'], ['Laser', '색소·혈관·모공'], ['Recovery', '회복·경과 일정']]),
        private_access=[
            dict(title='CO-CONSULTATION', ko='성형외과·피부과 협진 상담', copy='수술과 시술 가운데 피부 상태와 목적에 맞는 방법을 두 분야 전문의 상담으로 함께 검토합니다.'),
            dict(title='INTERVAL DESIGN', ko='시술 순서와 간격 설계', copy='리프팅·스킨부스터·쁘띠처럼 함께 받는 시술의 순서와 간격을 의료진의 판단에 따라 하나의 계획으로 정리합니다.'),
            dict(title='STAY-AWARE RECOVERY', ko='체류 일정에 맞춘 회복', copy='붓기와 회복 기간, 출국 일정을 함께 고려해 상담·시술·경과 확인 날짜를 미리 잡습니다.')],
        positioning='가격표와 전후 사진 대신, 상담에서 고객님의 피부 상태와 일정에 맞춘 계획과 회복 기간을 직접 설명해 드립니다.'),
    'korean-medicine': dict(
        statement='치료 이후의 회복도, 하나의 의료 여정으로 이어져야 합니다.',
        insight=dict(eyebrow='RECOVERY MAP', title='치료가 끝난 뒤의 회복까지, 한·양방이 함께 봅니다.',
                     copy='수술이나 사고, 뇌졸중 이후의 회복은 한 번의 진료로 끝나지 않습니다. 한의 진찰과 체질 상담에서 시작해 비수술 척추·관절 치료, 전문 재활, 입원 회복까지 필요한 단계를 한·양방 협진으로 이어갑니다.',
                     center='RECOVERY & BALANCE',
                     nodes=[['Diagnosis', '한의 진찰·체질 상담'], ['Spine · Joint', '비수술 척추·관절'], ['Rehabilitation', '수술 후·중풍 재활'], ['Inpatient', '입원형 회복'], ['Continuity', '경과·재방문 일정']]),
        private_access=[
            dict(title='INTEGRATED REVIEW', ko='한·양방 협진 상담', copy='한의사와 양방 의료진이 함께 상태를 보고, 치료 방법과 기간을 한 번의 상담 흐름 안에서 정리합니다.'),
            dict(title='RECOVERY PROGRAM', ko='회복·재활 프로그램', copy='추나·약침과 도수치료·체외충격파 같은 비수술 치료, 전문 재활과 입원 회복을 목적에 맞게 구성합니다.'),
            dict(title='CONTINUITY', ko='경과와 다음 일정', copy='입원·통원 일정과 경과 진료, 필요한 다음 전문 진료가 끊기지 않도록 atinc가 일정을 이어 관리합니다.')],
        positioning='효과를 앞세우지 않습니다. 치료 방법과 기간은 한의사와 의료진의 진찰로 정해지며, 비용은 상담 후 개별 안내합니다.'),
}

PROFILE = {
    'checkup': dict(
        title='세 곳의 프리미엄 정밀검진 센터',
        lead='서울 강남·경기 용인·부산의 정밀검진 센터는 같은 의료재단이 운영합니다. 지역이 달라도 검진 체계와 결과 관리 방식이 이어집니다.',
        where=['서울 강남', '경기 용인', '부산'],
        rows=[('코스 구성', '기본 코스부터 최상위 코스까지 5~6단계 등급 코스. 상위 코스는 CT·MRI 부위와 위 검사 방식을 하나씩 골라 구성하고, 유전체 검사를 더할 수 있습니다.'),
              ('주요 장비', '3.0T MRI, 128채널 MDCT, AI 기반 유방 진단 장비, 고해상도 내시경'),
              ('특화 검진', '뇌 정밀, 여성의학, 심장, 대장암, 몸통암(상체 장기), 돌연사 예방, 안티에이징, 면역증진'),
              ('공간', 'VIP와 남녀 동선을 나눈 공간, 여성 전용 검진 공간, 약 6,600㎡ 복층 센터(부산), 하루 안에 마치는 원스톱 진행'),
              ('국제진료', '국제진료센터의 의료통역과 외국인 전담 코디네이터, 한·영·중·일·몽골어 안내, 필요할 때 영문 결과지'),
              ('예약과 결과', '예약 확정 뒤 문진표를 미리 받고, 결과지는 약 2주 뒤 나옵니다. 결과에 따라 상급 의료기관 진료로 이어집니다.')]),
    'regenerative': dict(
        title='역할을 나눈 셀 케어 협력 네트워크',
        lead='세포를 처리·보관하는 시설, 첨단재생의료 실시기관, 줄기세포 연구기관이 각자의 역할로 협력합니다.',
        where=['경기 군포 · 세포처리시설', '경기 분당 · 재생의료 실시기관'],
        rows=[('세포 처리·보관', 'GMP 기준 세포처리시설에서 지방줄기세포·NK 면역세포·모유두세포를 배양하고, 영하 196℃로 최대 40년 보관합니다. 보관을 마치면 보관증서를 발급합니다.'),
              ('채취와 배양', '감염병 검사를 거쳐 협력 병원에서 채취합니다. 모발 채취는 약 30분이면 끝나고, NK 면역세포는 약 14일간 배양합니다.'),
              ('재생의료 실시기관', '보건복지부가 지정한 첨단재생의료 실시기관(2022년 지정). 첨단바이오의약품 제조업, 인체세포등 관리업, 세포처리시설 허가를 갖춘 의료 그룹의 병원입니다.'),
              ('통합 세포은행', '자가 NK·활성 T림프구, 지방줄기세포, 말초혈액 줄기세포를 보관합니다. 줄기세포는 20년, 면역세포는 35년 단위로 보관할 수 있습니다.'),
              ('연구 기반 라인', '1989년부터 줄기세포를 연구해 온 연구기관, 그리고 52주 GLP 안전성 시험을 마치고 국내외 허가 절차를 밟고 있는 차세대 세포 플랫폼(아직 허가 전)과 협력합니다.'),
              ('제도', '2025년 2월 시행된 개정 첨단재생바이오법에 따라, 지정된 재생의료기관이 심의를 거친 계획 범위에서 시행하며, 치료 전에 비용을 포함한 서면 동의를 받습니다.')]),
    'aesthetic': dict(
        title='성형외과·피부과 협진 클리닉',
        lead='인천국제공항과 가까운 송도국제도시의 협진 클리닉, 서울 강남의 피부 클리닉과 연결합니다.',
        where=['인천 송도', '서울 강남'],
        rows=[('협진', '성형외과와 피부과 전문의가 한 곳에서 협진합니다. 수술과 시술을 한 동선 안에서 상담할 수 있습니다.'),
              ('해외 고객', '인천 지역 의료관광 인증, 외국인 환자 유치 우수기관 선정 이력. 중국·태국·베트남·일본 고객 진료 경험이 있습니다.'),
              ('성형 수술', '눈, 3D 맞춤 코성형, 가슴, 얼굴 윤곽, 바디, 재수술'),
              ('리프팅', '울쎄라, 써마지 CTP·FLX, 슈링크, 덴서티 등 리프팅 장비와 실리프팅, 안면거상'),
              ('스킨부스터·쁘띠', '리쥬란, 리쥬란HB+, 스킨바이브, 보툴리눔 톡신, 필러, 윤곽주사, 콜라겐'),
              ('레이저·두피', '색소·혈관·모공·제모 레이저, 탈모 진료와 모발이식. 평일과 토요일에 진료합니다.')]),
    'women': dict(
        title='여성 프라이빗 클리닉',
        lead='서울 강남역 가까이에 있는 산부인과 전문의 클리닉입니다. 민감한 상담일수록 동선과 창구를 따로 둡니다.',
        where=['서울 강남'],
        rows=[('비공개 상담', '비공개 상담 창구를 따로 운영하고, 간호사 면허를 가진 상담 인력이 1:1로 응대합니다.'),
              ('갱년기·폐경', '진찰과 골반 초음파로 평가한 뒤, 호르몬 요법(국소 크림·먹는 약·질정), 비수술(윤활제·레이저), 수술 가운데 의료진과 상의해 정합니다.'),
              ('골반저 재건', '자궁탈출, 질 이완, 방광류·직장류, 요실금. 인공 메쉬 대신 본인의 조직으로 재건합니다.'),
              ('여성 성형', '질성형, 소음순·대음순 수술, 재수술. 국소마취로 당일 퇴원합니다.'),
              ('검진·예방', '자궁경부 세포검사와 HPV 검사, 부인과 초음파, 자궁경부암 예방백신'),
              ('해외 고객', '중국어·영어·일본어 안내를 갖추고 있습니다.')]),
    'men': dict(
        title='비뇨의학과 전문 진료로 연결합니다',
        lead='남성건강은 지역과 관계없이, 목적에 맞는 비뇨의학과 전문 클리닉과 상담 일정을 조율합니다. 진료는 보통 아래 순서로 진행됩니다.',
        where=['지역 무관 · 비뇨의학과 전문 클리닉'],
        rows=[('문진·설문', '증상과 병력, 복용 약을 확인하고 국제적으로 쓰이는 표준 설문(전립선 증상 점수, 발기 기능 지수)으로 평가합니다.'),
              ('신체·영상 검사', '직장수지검사, 전립선 초음파, 요속검사와 잔뇨 측정으로 전립선 크기와 배뇨 기능을 봅니다.'),
              ('혈액·호르몬', 'PSA, 신장기능, 테스토스테론 검사. 테스토스테론은 보통 오전에 공복으로 채혈하고 반복 측정합니다.'),
              ('정밀검사', 'PSA 이상 등으로 필요할 때만 경직장 초음파, MRI, 조직검사 순으로 진행합니다.'),
              ('치료 방향', '경과 관찰과 생활습관 교정부터 약물, 시술·수술까지 단계적으로 검토하며, 덜 침습적인 방법부터 시작합니다.'),
              ('프라이버시', '방문 목적은 필요한 범위에서만 정리하고, 다른 진료와 동선이 겹치지 않도록 시간과 순서를 미리 조율합니다.')]),
    'korean-medicine': dict(
        title='한·양방 협진 한방병원',
        lead='서울 압구정과 인천 검단에서, 같은 의료재단이 운영하는 한방병원과 연결합니다.',
        where=['서울 압구정', '인천 검단'],
        rows=[('진료과목', '한방내과, 한방부인과, 침구과, 한방재활의학과, 사상체질과, 한방신경정신과, 한방안·이비인후·피부과'),
              ('협진 센터', '한·양방 협진 센터, 전문 재활 센터, 중풍 재활 센터'),
              ('비수술 치료', '추나, 약침, 봉침과 도수치료, 체외충격파, 증식치료'),
              ('입원 회복', '84병상 입원 병동과 1인실, 365일 입원(인천 검단)'),
              ('재단 연계', '같은 의료재단 병원의 암 수술 후 면역·회복 프로그램과 연결합니다.'),
              ('한의 치료', '침·약침, 뜸, 추나, 한약. 한약은 안전 기준 검사를 거친 의약품용 규격 한약재로 조제합니다.')]),
}


def profile_section(cid, sid='profile'):
    p = PROFILE[cid]
    pins = ''.join(f'<span class="prof__pin">{ic("pin")}{E(w)}</span>' for w in p['where'])
    rows = ''.join(f'<div><dt>{E(a)}</dt><dd>{E(b)}</dd></div>' for a, b in p['rows'])
    return (f'<section class="sec prof" id="{sid}"><div class="wrap prof__grid">'
            f'<div class="prof__head"><h2 class="disp-2">{E(p["title"])}</h2>'
            f'<p class="lead">{E(p["lead"])}</p><div class="prof__where">{pins}</div>'
            f'<p class="prof__note">협력 의료기관의 이름과 위치는 상담에서 고객님의 목적에 맞춰 개별로 안내해 드립니다.</p></div>'
            f'<dl class="prof__dl">{rows}</dl></div></section>')


def support_list(items):
    if not items:
        return ''
    lis = ''.join(f'<li>{ic("check")}<span>{E(x)}</span></li>' for x in items)
    return f'<div class="support"><h3>atinc가 맡는 일</h3><ul>{lis}</ul></div>'


def category_approach(cid, support=None):
    ins, pa = (PROG[CAT_PROG[cid]]['insight'], PROG[CAT_PROG[cid]]['private_access']) if cid in CAT_PROG else (CUSTOM[cid]['insight'], CUSTOM[cid]['private_access'])
    return insight_section(ins, pa, extra=support_list(support))


def fertility_section():
    p = PROG['fertility']
    fields = ''.join(f'<span class="tag">{E(x)}</span>' for x in p['medical_fields'])
    sec = insight_section(p['insight'], p['private_access'], p['positioning'], sid='fertility', cls='sec sec--sand', statement=p['statement'])
    foot = (f'<div class="fert__foot"><div class="chips" style="gap: 8px">{fields}</div>'
            f'{form_link("난임·생식의학 상담하기", "여성건강", "btn btn--dark")}</div>')
    tail = '</div></section>'
    return sec[:-len(tail)] + foot + tail


# ------------------------------------------------------------------ Medical Access (specialties)
ACCESS = [('cancer-second-opinion', '암 진료·세컨드 오피니언'), ('fertility', '난임·생식의학'),
          ('brain-memory', '뇌·기억력·인지건강'), ('vision-care', '프리미엄 아이케어')]


BTN = {'암 진료·세컨드 오피니언': '세컨드 오피니언 상담 예약', '난임·생식의학': '난임 상담 예약', '뇌·기억력·인지건강': '뇌·기억력 상담 예약', '프리미엄 아이케어': '안과 상담 예약'}


def access_section():
    cards = ''
    for pid, ko in ACCESS:
        p = PROG[pid]
        nodes = ''.join(f'<li><span>{E(k)}</span></li>' for en, k in p['insight']['nodes'])
        m = p['detail_meta']
        cards += (f'<article class="mac"><div class="mac__top"><p class="mac__en">{E(tcase(p["title"]))}</p><h3>{E(ko)}</h3></div>'
                  f'<p class="mac__st">{E(p["statement"])}</p><p class="body">{E(fix(p["summary"]))}</p>'
                  f'<ul class="mac__nodes">{nodes}</ul>'
                  f'<div class="mac__foot"><span class="small">{E(m["format"])} · {E(m["timeline"])}</span>'
                  f'{form_link(BTN.get(ko, ko + " 상담 예약"), ko, "link", "out")}</div></article>')
    return (f'<section class="sec sec--sand" id="access"><div class="wrap"><div class="idx__head"><div style="display: grid; gap: 18px">'
            f'<h2 class="disp-2">특정 진료가 필요하다면,<br>전문 분야로 바로 연결합니다</h2></div>'
            f'<p class="lead">고객의 목적과 기존 자료를 기준으로 필요한 전문 분야와 의료기관의 상담 접근을 선별합니다. '
            f'아래 네 분야는 지정 거점 없이, 목적에 맞는 전문 의료기관을 상담에서 개별로 찾아 연결합니다.</p></div>'
            f'<div class="macs">{cards}</div></div></section>')


# ------------------------------------------------------------------ CARE helpers
def care_meta(pid):
    m = PROG[pid]['detail_meta']
    return (f'<dl class="pmeta"><div><dt>형태</dt><dd>{E(m["format"])}</dd></div><div><dt>기간</dt><dd>{E(m["timeline"])}</dd></div>'
            f'<div><dt>초점</dt><dd>{E(m["focus"])}</dd></div></dl>')


# ------------------------------------------------------------------ official facts (public sources only)
U = dict(
    cancer_surv='https://www.cancer.go.kr/lay1/S1T648C649/contents.do',
    cancer_screen='https://www.cancer.go.kr/lay1/S1T261C262/contents.do',
    cancer_surv_type='https://www.cancer.go.kr/lay1/S1T648C650/contents.do',
    koreanet='https://www.korean-culture.org/koreanet/view.do?seq=1054339',
    cancer_stat='https://www.cancer.go.kr/download.do?uuid=cfcd35c3-391f-4060-9688-641db3d86cbd.pdf',
    general='https://www.nrc.go.kr/portal/html/content.do?depth=ph&menu_cd=03_02_00_01',
    law_regen='https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=210283',
    law_regen25='https://www.law.go.kr/LSW/lsInfoR.do?lsiSeq=260591&efYd=20250221',
    karm='https://www.k-arm.go.kr/medi/audit/list.do?key=2109297497027',
    mfds_stem='https://www.mfds.go.kr/brd/m_100/view.do?seq=29365',
    khidi='https://www.koreahealthtour.co.kr/post/12984',
    specialty='https://elaw.klri.re.kr/kor_service/lawViewMultiContent.do?hseq=67704',
    hira='https://www.korea.kr/news/reporterView.do?newsId=148927444',
    hpv='https://www.kdca.go.kr/bbs/kdca/45/310771/artclView.do',
    infert='https://www.korea.kr/news/reporterView.do?newsId=148959999',
    infert_born='https://www.korea.kr/briefing/pressReleaseView.do?newsId=156761495',
    meno='https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoView.do?cntnts_sn=6687',
    chuna='https://www.korea.kr/news/policyNewsView.do?newsId=148859526',
    cheop='https://www.korea.kr/news/policyNewsView.do?newsId=148928658',
    gmp='https://impfood.mfds.go.kr/CFBBB02F02/getCntntsDetail?cntntsSn=281375',
    nhis='https://www.nhis.or.kr/announce/wbhaec11404m01.do',
    medlaw5='https://www.law.go.kr/LSW//lsLinkCommonInfo.do?lsJoLnkSeq=1018922505',
    law_attract='https://www.law.go.kr/LSW/lsLawLinkInfo.do?lsJoLnkSeq=1000834802&chrClsCd=010202',
)

FACTS = {
    'checkup': dict(
        title='공식 자료로 보는 건강검진',
        items=[('73.7', '%', '최근 5년(2019~2023년)에 암을 진단받은 환자의 5년 상대생존율입니다. 2001~2005년 진단 환자(54.2%)보다 19.5%p 높아졌습니다.', '국가암정보센터 · 2023년 국가암등록통계(2026년 1월 발표)', 'cancer_surv'),
               ('6', '종', '국가암검진은 위암·대장암·간암·유방암·자궁경부암·폐암 여섯 가지를 대상으로 합니다. 전립선암(PSA)은 포함되지 않아, 필요하면 개인 정밀검진에서 선택합니다.', '국가암정보센터 · 국가암검진 사업(2026년 8월 기준)', 'cancer_screen'),
               ('2', '년마다', '국가 일반건강검진은 2년마다 받고, 비사무직 근로자는 매년 받습니다. 종합검진은 이 기본 항목 위에 필요한 정밀검사를 더해 구성합니다.', '국민건강보험공단 일반건강검진 기준 · 국립재활원 안내', 'general')],
        table=dict(title='국가암검진, 언제 무엇을 받나요', headers=['암', '대상', '주기', '검사 방법'],
                   rows=[['위암', '만 40세 이상 남녀', '2년', '위내시경 (어려우면 위장조영검사)'],
                         ['대장암', '만 50세 이상 남녀', '1년', '분변잠혈검사 (이상 소견 시 대장내시경)'],
                         ['간암', '만 40세 이상 고위험군', '6개월', '간초음파 + 혈청알파태아단백검사'],
                         ['유방암', '만 40세 이상 여성', '2년', '유방촬영술'],
                         ['자궁경부암', '만 20세 이상 여성', '2년', '자궁경부세포검사'],
                         ['폐암', '만 54~74세 고위험군', '2년', '저선량 흉부 CT']],
                   note='간암 고위험군은 간경변증, B형·C형 간염 바이러스에 의한 만성 간질환 등이 있는 경우, 폐암 고위험군은 30갑년 이상 흡연력이 있는 현재 흡연자 등입니다.',
                   src=('국가암정보센터 · 국가암검진 사업(2026년 8월 기준)', 'cancer_screen'))),
    'regenerative': dict(
        title='공식 자료로 보는 재생의료',
        items=[('2020', '.8.28', '「첨단재생바이오법」이 시행되며, 국내 재생의료를 관리하는 제도가 만들어졌습니다.', '국가법령정보센터 · 첨단재생의료 및 첨단바이오의약품 안전 및 지원에 관한 법률', 'law_regen'),
               ('2025', '.2.21', '개정법 시행으로, 지정된 재생의료기관은 심의를 거친 치료계획 범위 안에서 첨단재생의료 \'치료\'를 할 수 있게 되었습니다. 그 전에는 임상연구로만 가능했습니다.', '국가법령정보센터 · 개정 첨단재생바이오법 제12조의2', 'law_regen25'),
               ('200', '곳 이상', '2026년 기준, 전국 200곳이 넘는 의료기관이 첨단재생의료 실시기관으로 지정되어 있습니다.', '첨단재생의료포털 실시기관 지정 현황 · 보건복지부 발표(2026년)', 'karm'),
               ('2011', '년', '식품의약품안전처(당시 식품의약품안전청)는 2011년 세계 최초로 줄기세포치료제를 허가했습니다.', '식품의약품안전처 설명자료(2015년)', 'mfds_stem')],
        rules=[('세포 처리는 허가제입니다', '사람의 세포를 채취·처리해 공급하려면 세포처리시설과 인체세포등 관리업에 대해 식약처장의 허가를 받아야 합니다(법 제15조·제28조).', 'law_regen25'),
               ('서면 동의가 먼저입니다', '재생의료기관은 치료 전에 비용을 포함한 내용을 설명하고 서면 동의를 받아야 합니다(법 제11조의2).', 'law_regen25'),
               ('치료 승인은 이제 시작 단계입니다', '2026년 4월, 희귀 림프종 환자 대상 자가 면역세포 치료가 첫 첨단재생의료 치료계획으로 승인되었습니다. 줄기세포 치료로 승인된 치료계획은 아직 확인되지 않습니다.', None)]),
    'aesthetic': dict(
        title='공식 자료로 보는 성형·피부',
        items=[('62.9', '%', '2025년 외국인 환자의 진료과 이용 가운데 피부과가 131.3만 명으로 가장 많았습니다.', '보건복지부·한국보건산업진흥원 · 2025년 외국인환자 유치 실적(2026년 4월)', 'khidi'),
               ('11.2', '%', '성형외과가 23.3만 명으로 피부과 다음으로 많았습니다.', '보건복지부·한국보건산업진흥원 · 2025년 외국인환자 유치 실적(2026년 4월)', 'khidi'),
               ('26', '개 전문과목', '피부과와 성형외과는 법령상 26개 전문과목 가운데 서로 다른 전문과목입니다. 원하는 시술에 맞는 전문의를 찾는 일이 중요한 이유입니다.', '「전문의의 수련 및 자격 인정 등에 관한 규정」 제3조', 'specialty')],
        rules=[('간판의 과목명을 확인하세요', '의료기관 이름에 전문과목(예: OO피부과의원)을 넣을 수 있는 곳은 그 과목 전문의가 개설한 곳입니다. 그 밖의 곳은 \'진료과목\'이라는 글자를 붙여 표시합니다(의료법 시행규칙 제40조·제41조).', None),
               ('공개 정보로 확인할 수 있습니다', '건강보험심사평가원 누리집과 \'건강e음\' 앱에서 의료기관의 진료과목, 전문의 수, 병상 수, 진료시간을 확인할 수 있습니다.', 'hira'),
               ('주입 제품은 허가품만', '피부 안에 주입하는 시술에는 식약처 허가를 받은 의약품이나 의료기기만 쓸 수 있고, 화장품은 주입할 수 없습니다(식약처 안내).', None)]),
    'women': dict(
        title='공식 자료로 보는 여성건강',
        items=[('20', '세부터', '자궁경부암 국가검진은 만 20세 이상 여성이 2년마다 자궁경부세포검사를 받습니다.', '국가암정보센터 · 국가암검진 사업(2026년 8월 기준)', 'cancer_screen'),
               ('40', '세부터', '유방암 국가검진은 만 40세 이상 여성이 2년마다 유방촬영술을 받습니다.', '국가암정보센터 · 국가암검진 사업(2026년 8월 기준)', 'cancer_screen'),
               ('12', '세', 'HPV 국가예방접종은 12~17세 여성 청소년과 18~26세 저소득층 여성이 대상입니다. 2026년 5월부터 12세 남성 청소년도 무료로 접종받을 수 있습니다.', '질병관리청(2026년 4월)', 'hpv'),
               ('12', '개월', '폐경은 마지막 월경 후 12개월 동안 월경이 없는 상태를 말하며, 대체로 50~52세 사이에 나타납니다.', '질병관리청 국가건강정보포털 · 폐경기(2026년 5월)', 'meno'),
               ('25', '회', '난임부부 시술비 지원은 2024년부터 소득 기준 없이, 출산당 총 25회(체외수정 20회·인공수정 5회)까지 받을 수 있습니다. 국내 건강보험 가입자 기준입니다.', '정책브리핑(2026년 3월)', 'infert'),
               ('48,981', '명', '2025년 국가와 지방자치단체의 난임 지원으로 태어난 아이 수입니다.', '보건복지부 보도자료(2026년 5월)', 'infert_born')]),
    'men': dict(
        title='공식 자료로 보는 남성건강',
        items=[('1', '위', '2023년 전립선암은 한국 남성에게 가장 많이 발생한 암으로, 22,640건(남성 암의 15.0%)이 새로 진단되었습니다.', '국가암정보센터 · 2023년 국가암등록통계(2026년 1월 발표)', 'cancer_stat'),
               ('96.9', '%', '전립선암의 5년 상대생존율입니다(2019~2023년 진단).', '국가암정보센터 · 암 생존율(2026년 1월)', 'cancer_surv_type'),
               ('PSA', '', '국가암검진 6종에는 전립선암(PSA 검사)이 포함되어 있지 않습니다. 필요하면 개인 정밀검진에서 선택해 받습니다.', '국가암정보센터 · 국가암검진 사업(2026년 8월 기준)', 'cancer_screen')]),
    'korean-medicine': dict(
        title='공식 자료로 보는 한방',
        items=[('2019', '.4.8', '추나요법은 이날부터 근골격계 질환에 건강보험이 적용되어, 연간 20회 이내로 받을 수 있습니다(국내 건강보험 가입자 기준).', '정책브리핑 · 보건복지부(2019년 3월)', 'chuna'),
               ('6', '개 질환', '첩약(한약) 건강보험 시범사업은 2024년 4월부터 2단계로 월경통, 안면신경마비, 뇌혈관질환 후유증, 알레르기 비염, 기능성 소화불량, 요추추간판탈출증에 적용되고 있습니다(2026년 12월까지).', '정책브리핑 · 한국한의약진흥원', 'cheop'),
               ('2015', '년', '의약품용 한약재는 2015년 1월부터 제조·품질관리기준(GMP)이 전면 의무화되었습니다.', '식품의약품안전처(2015년 1월)', 'gmp'),
               ('620', '곳', '2026년 6월 말 기준 전국 한방병원은 620곳, 한의원은 14,848곳입니다.', '국민건강보험공단 · 요양기관 현황', 'nhis'),
               ('면허', '', '한의사는 한의과대학이나 한의학전문대학원을 졸업하고 국가시험에 합격한 뒤 보건복지부장관의 면허를 받습니다.', '의료법 제5조', 'medlaw5')]),
    'global': dict(
        title='숫자로 보는 한국 의료',
        items=[('201', '만 명', '2025년 한 해 한국 의료를 이용한 외국인 환자 수입니다. 2009년 집계 이후 처음으로 200만 명을 넘었습니다.', '보건복지부·한국보건산업진흥원 · 2025년 외국인환자 유치 실적(2026년 4월)', 'khidi'),
               ('30.8', '%', '국적별로는 중국이 30.8%로 가장 많았고, 일본·대만·미국·태국이 뒤를 이었습니다.', '보건복지부 2025년 외국인환자 유치 실적 · 코리아넷(2026년 4월)', 'koreanet'),
               ('등록제', '', '외국인환자 유치는 법에 따라 시·도지사에게 등록한 의료기관과 유치업자만 할 수 있으며, 등록 유효기간은 3년입니다. atinc 등록번호: 제 A-2026-08-01-07161 호', '국가법령정보센터 · 의료 해외진출 및 외국인환자 유치 지원에 관한 법률 제6조', 'law_attract')]),
}


LEADS = {'checkup': '검진을 계획하기 전에 알아두면 좋은 국가 기준과 숫자입니다.', 'regenerative': '재생의료는 제도를 먼저 아는 것이 중요합니다. 한국에서 무엇이, 어디까지 허용되는지 담았습니다.', 'aesthetic': '해외 고객이 한국에서 가장 많이 찾는 분야입니다. 병원을 고르기 전에 확인할 기준도 함께 담았습니다.', 'women': '생애주기마다 챙겨야 할 국가 검진과 예방접종, 난임 지원 기준입니다.', 'men': '남성에게 가장 많이 발생하는 암과, 국가검진만으로는 놓치기 쉬운 부분입니다.', 'korean-medicine': '한국의 한방 진료는 국가 면허와 품질 기준, 건강보험 제도 안에서 이루어집니다.', 'global': '한국 의료를 찾는 해외 고객은 해마다 늘고 있습니다. 공식 통계로 본 지금의 한국 의료입니다.'}


def _src(label, key):
    if key and key in U:
        return f'<a class="fact__src" href="{U[key]}" target="_blank" rel="noopener">{E(label)}{ic("out")}</a>'
    return f'<p class="fact__src">{E(label)}</p>'


def fact_cards(items):
    out = ''
    for fig, unit, txt, src, key in items:
        word = not any(ch.isdigit() for ch in fig)
        out += (f'<article class="fact"><p class="fact__fig{" fact__fig--word" if word else ""}">{E(fig)}<small>{E(unit)}</small></p>'
                f'<p class="fact__txt">{E(txt)}</p>{_src(src, key)}</article>')
    return f'<div class="fgrid fgrid--{len(items)}">{out}</div>'


def facts_section(cid, sid='facts', cls='sec'):
    F = FACTS[cid]
    body = fact_cards(F['items'])
    if F.get('table'):
        t = F['table']
        th = ''.join(f'<th scope="col">{E(h)}</th>' for h in t['headers'])
        tr = ''.join('<tr>' + ''.join((f'<td data-label="{E(t["headers"][j])}">' if j else '<td>') + f'{E(c)}</td>' for j, c in enumerate(r)) + '</tr>' for r in t['rows'])
        body += (f'<details class="more"><summary>{E(t["title"])}</summary><div class="ftable"><div class="tbl-wrap"><table class="tbl">'
                 f'<thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
                 f'<p class="small">{E(t["note"])}</p>{_src(*t["src"])}</div></details>')
    if F.get('rules'):
        rl = ''.join(f'<li><b>{E(a)}</b><p class="body">{E(b)}</p>' + (_src('출처 보기', k) if k else '') + '</li>' for a, b, k in F['rules'])
        body += f'<details class="more"><summary>관련 제도와 기준</summary><ul class="frules">{rl}</ul></details>'
    return (f'<section class="{cls}" id="{sid}"><div class="wrap"><div class="idx__head"><h2 class="disp-2">{E(F["title"])}</h2>'
            f'<p class="lead">{E(LEADS[cid])}</p></div>'
            f'{body}</div></section>')
