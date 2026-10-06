# 2026-10 ECC review: final wording pass, applied to every built page after the copy maps.
# Rule: talk about the service (which institutions, how atInc connects and arranges things),
# never about medical effects. Information that came from the contracted hospitals is kept,
# only reworded so it reads as "what the partner institutions offer / tell their patients".
# Each entry: (page file or None for all pages, old text, new text). build prints any entry that matched nothing.
import re

REVISE = [
    # ---------- regenerative medicine: storage and consultation, not a product line
    ('medical-regenerative.html', '내 세포로 준비하는, 프라이빗 셀 케어', '세포 보관과 재생의료 상담, 할 수 있는 것부터 확인합니다'),
    ('medical-regenerative.html', '협력 센터 의료진과의 상담을 잡아 드리고, 채취부터 배양, 보관, 적용까지 일정은 atInc가 맡습니다.',
     '협력 센터 의료진과의 상담을 잡아 드리고, 채취와 배양, 보관 일정은 atInc가 맡습니다. 보관한 세포를 실제로 쓸지는 그때 의료진과 정하시게 됩니다.'),
    ('medical-regenerative.html', '>보관 또는 회차 진행<', '>보관과 회차 일정<'),
    ('medical-regenerative.html', '세포를 초저온으로 보관한 뒤 보관증서를 발급해 드립니다. 회차형 프로그램은 정해진 회차 일정대로 받으시면 됩니다.',
     '세포를 초저온으로 보관하고, 보관 기관이 보관증서를 발급합니다. 의료진이 정한 회차 일정이 있으면 atInc가 체류 일정에 맞춰 예약합니다.'),
    ('medical-regenerative.html', '>경과 관리<', '>경과 확인 일정<'),
    ('medical-regenerative.html', '회차마다 경과를 확인하고, 재평가와 다음 상담 일정은 atInc가 챙깁니다.', '의료진의 경과 확인과 다음 상담 날짜를 atInc가 잡아 둡니다.'),
    ('medical-regenerative.html', '회차형 프로그램은 어떻게 구성되나요?', '회차형 프로그램도 안내받을 수 있나요?'),
    ('medical-regenerative.html', '1회, 3회, 7회 구성이 있습니다. 회차별 날짜는 의료진과 상담한 뒤 체류 일정에 맞춰 잡아 드립니다.',
     '협력 기관에는 1회·3회·7회로 나눠 진행하는 구성이 있습니다. 국내에서는 보건복지부가 지정한 재생의료기관이 승인받은 계획 범위 안에서만 받을 수 있고, 대상이 되는지와 횟수는 의료진이 정합니다. atInc는 그 상담과 날짜를 체류 일정에 맞춰 잡아 드립니다.'),
    ('medical-regenerative.html', '채취와 회차 날짜를 한국에 오시는 일정에 맞춰 잡아 드립니다.', '채취와 상담 날짜를 한국에 오시는 일정에 맞춰 잡아 드립니다.'),
    ('medical-regenerative.html', '라인과 회차 구성에 따라 달라지기 때문에, 상담을 마친 뒤 따로 알려 드립니다.', '보관 기관과 기간, 받으시는 구성에 따라 달라서 상담을 마친 뒤 따로 알려 드립니다.'),
    ('medical-regenerative.html', '성체줄기세포는 지방, 골수 등 몸 곳곳의 조직에 있으며 손상된 조직의 재생에 관여합니다.',
     '성체줄기세포는 지방, 골수 등 몸 곳곳의 조직에 있습니다. 치료에 쓰려면 법이 정한 절차와 의료진 판단을 거쳐야 합니다.'),
    ('medical-regenerative.html', '내 세포로 준비하는 셀 케어, 상담부터 받아 보세요', '세포 보관과 재생의료, 상담부터 받아 보세요'),
    ('medical-regenerative.html', '회차형 셀 케어를 한국 체류 일정에 맞춰 받고 싶을 때', '의료진이 정한 회차 일정을 한국 체류 일정에 맞추고 싶을 때'),
    ('medical-regenerative.html', '웰에이징 관리를 시작하고 싶을 때', '웰에이징 검사와 관리 프로그램이 궁금할 때'),
    ('medical.html', '건강할 때 내 세포를 보관해 두거나, 연구기관과 협력하는 셀 케어 라인을 고르실 수 있습니다.',
     '건강할 때 본인 세포를 보관하는 방법과, 지정 재생의료기관에서 상담받을 수 있는 범위를 안내해 드립니다.'),

    # ---------- women
    ('medical-women.html', '골반저 재건과 여성 성형은 국소마취로 하고, 수술 당일 퇴원합니다. 회복 일정은 진찰 때 따로 설명해 드립니다.',
     '협력 기관에서는 국소마취나 수면마취로 하고 당일 퇴원하는 경우가 많습니다. 다만 수술 종류와 건강 상태에 따라 입원이 필요할 수 있어, 마취와 입원 여부는 진찰 때 설명을 들으십니다.'),
    ('medical-women.html', '인공 메쉬 대신 본인의 조직으로 재건하는 방식을 씁니다.', '협력 기관은 인공 메쉬 대신 본인의 조직으로 재건하는 방식을 씁니다. 수술 방법은 진찰 뒤 의료진이 정합니다.'),
    ('medical-women.html', '갱년기(폐경이행기)는 월경이 불규칙해질 때부터 폐경까지의 시기입니다.', '갱년기는 폐경 전후 몇 년을 함께 이르는 말로, 월경이 불규칙해지는 폐경이행기를 포함합니다.'),
    ('medical-women.html', '월경 주기가 불규칙해지기 시작할 때부터 마지막 월경까지의 시기입니다.', '폐경 전후 몇 년 동안의 시기로, 월경 주기가 불규칙해지는 폐경이행기를 포함합니다.'),
    ('medical-women.html', '>갱년기(폐경이행기)<', '>갱년기<'),
    ('medical-women.html', '상담 내용이 외부에 알려질까 걱정돼요.', '상담 내용이 외부에 알려질까 걱정됩니다.'),

    # ---------- aesthetic
    ('medical-aesthetic.html', '머무시는 기간을 먼저 알려 주세요. 그 기간 안에서 상담과 시술, 경과 확인 날짜를 잡아 드립니다.',
     '머무시는 기간을 먼저 알려 주세요. 그 안에 회복과 경과 확인까지 마치기 어려운 수술은 의료진이 다른 방법을 권하거나 다음 방문으로 미루자고 할 수 있습니다. 수술 뒤 비행기를 타도 되는 시점도 의료진에게 확인한 뒤 귀국 일정을 잡습니다.'),
    ('medical-aesthetic.html', '짧은 일정 안에 상담과 시술, 경과 확인까지 받으셔야 할 때', '체류 기간 안에 상담과 시술, 경과 확인까지 할 수 있는지 먼저 알아보고 싶을 때'),
    ('medical-aesthetic.html', '리프팅을 받은 날에는 가볍게 세안하시고, 화장은 다음 날부터 하세요. 술·담배와 강한 마사지는 1~2주, 사우나와 격한 운동은 3~5일 동안 피하시고, 자외선은 꼭 차단해 주세요.',
     '받으신 시술·수술에 맞는 회복 방법을 의료진에게 듣습니다. atInc는 그 안내에 맞춰 경과 확인 날짜와 귀국 일정을 잡아 둡니다. 협력 클리닉이 안내하는 장비 리프팅의 회복 방법은 아래에 정리해 두었습니다.'),
    ('medical-aesthetic.html', '>프리미엄 리프팅<', '>리프팅<'),

    # ---------- checkup
    ('medical-checkup.html', '순서대로 검사를 받으시면 됩니다. 종합검진은 보통 3~4시간 걸립니다.', '순서대로 검사를 받으시면 됩니다. 종합검진은 구성에 따라 보통 3~4시간 걸립니다.'),
    ('medical-checkup.html', '돌연사 예방 등 분야별 집중 구성', '돌연사 위험 요인 확인 등 분야별 집중 구성'),
    ('medical-checkup.html', '가장 비싼 검진이 아니라, 나에게 맞는 검진', '검진기관과 검사 항목, 비교해 보고 고르세요'),
    ('care-private-checkup.html', '가장 비싼 검진이 아니라, 나에게 맞는 검진.', '검사 항목은 나이와 가족력에 맞춰 함께 정합니다.'),
    ('care.html', '가장 비싼 검진이 아니라, 나에게 맞는 검진.', '검진 당일 동행부터 결과 이후 30일까지.'),

    # ---------- men
    ('medical-men.html', '방문 목적과 이전 검사 결과는 비공개로 받아, 맞는 전문의 상담과 검사를 예약해 드립니다.',
     '첫 통화에서 방문 목적을 들은 뒤 필요한 검사 자료는 그때 따로 받아, 맞는 전문의 상담과 검사를 예약해 드립니다.'),

    # ---------- longevity 90: hospitals examine, atInc arranges
    ('care-longevity-90.html', '<h3>정밀 평가</h3><p class="svcs__en">DIAGNOSE</p>', '<h3>병원 검사</h3><p class="svcs__en">CHECK-UP</p>'),
    ('care-longevity-90.html', '암과 심혈관·뇌혈관 질환 위험을 살펴봅니다', '협력 병원에서 암과 심혈관·뇌혈관 질환 관련 검사를 받으십니다'),
    ('care-longevity-90.html', '대사건강과 비만, 당뇨 관련 검사를 진행합니다', '대사건강과 비만, 당뇨 관련 검사를 받으십니다'),
    ('care-longevity-90.html', '영양 상태와 비타민, 미네랄을 검사합니다', '영양 상태와 비타민, 미네랄 검사를 받으실 수 있습니다'),
    ('care-longevity-90.html', '호르몬과 스트레스 관련 검사도 합니다', '호르몬과 스트레스 관련 검사도 받으실 수 있습니다'),
    ('care-longevity-90.html', '신체 조성과 근육량, 근력을 측정합니다', '신체 조성과 근육량, 근력 측정도 함께 잡아 드립니다'),
    ('care-longevity-90.html', '수면과 피로, 인지 기능을 평가합니다', '수면과 피로, 인지 기능 검사도 받으실 수 있습니다'),
    ('care-longevity-90.html', '필요하면 유전자·면역 관련 검사도 받으실 수 있습니다', '필요하면 유전자·면역 관련 검사도 받으실 수 있으며, 받으실 검사는 의료진이 정합니다'),
    ('care-longevity-90.html', '어떤 정밀평가와 병원 상담이 필요한지 정합니다', '어떤 검사와 병원 상담을 받으실지 의료진과 정하실 수 있게 준비합니다'),
    ('care-longevity-90.html', '검사 결과를 보고 진료와 영양, 운동, 수면, 회복 일정을 짭니다', '의료진의 설명과 권고에 맞춰 진료와 영양, 운동, 수면, 회복 일정을 짭니다'),
    ('care-longevity-90.html', '90일 뒤 재평가를 거쳐 다음 계획을 말씀드립니다', '90일 뒤 병원 재검사 일정을 잡고, 의료진 설명에 맞춰 다음 일정을 정리해 드립니다'),
    ('care-longevity-90.html', '90일이 지나면 다시 평가하고 다음 계획을 제안해 드립니다', '90일이 지나면 재검사 일정을 잡고, 다음 일정을 정리해 드립니다'),
    ('care-longevity-90.html', '전담 헬스 컨시어지 한 사람이 맡습니다', '담당 매니저 한 사람이 맡습니다'),
    ('care-longevity-90.html', '정밀평가 + 30·60·90일', '병원 검사 + 30·60·90일'),
    ('care-longevity-90.html', '>CEO·고자산가<', '>일정이 빠듯한 경영진<'),

    # ---------- executive 365
    ('care-executive-365.html', '기업 CEO·오너·임원과 고자산가를 위한 연간 헬스 오피스입니다.', '경영진과 그 가족처럼 일정이 빠듯한 분들을 위한 연간 헬스 오피스입니다.'),
    ('care-executive-365.html', '>국내외 고자산가<', '>해외와 한국을 오가며 일하시는 분<'),
    (None, '전담 코디네이터', '담당 매니저'),

    # ---------- global medical journey
    ('care-global-medical-journey.html', '입국 전부터 귀국 후까지, 담당 매니저 한 사람이 맡습니다.', '한국에서의 진료 일정, 도착 전에 맞춰 둡니다.'),
    ('care-global-medical-journey.html', '귀국 후 상담까지 담당자가 챙겨 드립니다', '귀국 후 상담까지 담당 매니저가 챙겨 드립니다'),
    ('care-global-medical-journey.html', '영문 결과자료 받아 드리기', '영문 결과지 발급을 도와 드립니다(본인 확인이 필요한 곳이 있습니다)'),
    ('care-global-medical-journey.html', '>보호자 일정 챙기기<', '>보호자분 일정도 함께 챙깁니다<'),
    ('care-global-medical-journey.html', '<li>공항 픽업</li>', '<li>공항으로 마중 나갑니다</li>'),
    ('care-global-medical-journey.html', '<li>의료통역</li>', '<li>진료 때 의료통역사가 함께합니다</li>'),
    ('care-global-medical-journey.html', '<li>온라인 사전상담</li>', '<li>온라인으로 먼저 상담합니다</li>'),

    # ---------- care index
    ('care.html', '검진이 끝난 뒤의 일정까지 챙깁니다', '하루 검진부터 1년 관리까지'),
    ('care.html', 'atInc CARE는 병원 예약은 물론, 미리 준비하실 것과 전체 일정, 결과가 나온 뒤의 관리까지 저희가 맡는 프로그램입니다.',
     '케어 프로그램은 병원 예약에 더해 사전 준비와 전체 일정, 결과가 나온 뒤의 관리까지 atInc가 맡는 서비스입니다.'),

    # ---------- medical index
    ('medical.html', '어디까지 챙겨 드릴지는 atInc CARE에서 고르시면 됩니다', '어디까지 맡기실지는 케어 프로그램에서 고르시면 됩니다'),
    ('medical.html', '아래 네 분야는 정해 둔 협력 병원이 없어서, 상담 후에 알맞은 병원을 찾아 예약해 드립니다.',
     '아래 분야는 지역에 따라 협력 기관이 있기도 하고 없기도 합니다. 상담 내용에 맞는 병원을 그때마다 찾아 예약해 드립니다.'),
    ('medical.html', '영상·병리·진료 자료를 모아 암종에 맞는 전문의에게 추가 의견을 받아 드립니다.', '영상·병리·진료 자료를 모아 암종에 맞는 전문의에게 직접 진료를 받고 추가 의견을 들으실 수 있게 예약해 드립니다.'),

    # ---------- partners: what atInc does, not "sending patients"
    ('partners.html', 'atInc는 환자를 소개하는 데서 그치지 않습니다. 방문 전에 목적과 자료를 미리 받아 두고, 통역과 체류를 챙깁니다. 진료가 끝난 뒤의 다음 일정까지 저희가 맡습니다.',
     'atInc는 고객이 고른 병원에 가시기 전의 준비와 진료 뒤의 일정을 맡습니다. 방문 목적과 자료를 미리 정리하고, 통역과 체류, 다음 진료 날짜까지 챙깁니다.'),
    ('partners.html', '방문 목적과 기존 검사 자료가 정리된 고객을 소개해 드립니다. 통역과 이동, 방문 전후 연락은 저희가 맡으니 병원은 진료에 집중하시면 됩니다.',
     'atInc 고객이 귀 기관을 고르시면, 고객이 동의한 범위에서 방문 목적과 기존 자료를 정리해 미리 전해 드립니다. 통역과 이동, 방문 전후 연락은 저희가 맡으니 병원은 진료에 집중하시면 됩니다.'),
    ('partners.html', '진료 일정이 정해지면 그에 맞춰 예약을 드립니다.', '진료 일정이 정해지면 그에 맞춰 숙소와 차량, 통역을 예약합니다.'),

    # ---------- notice: stock photos are not facilities
    ('medical-notice.html', '소개된 의료기관의 이름은 공개하지 않으며, 시설 사진은 사용 허락을 받은 범위에서만 게시합니다.',
     '소개된 의료기관의 이름은 공개하지 않습니다. 사이트의 사진은 이해를 돕기 위한 참고 이미지이며, atInc나 협력 의료기관의 실제 시설 사진이 아닙니다.'),

    # ---------- about: role, not denial
    ('about.html', 'atInc는 진단이나 치료를 하는 의료기관이 아닙니다. 검사와 진단, 처방, 시술, 치료는 모두 의료기관과 담당 의료진이 판단해 진행합니다.',
     '검사와 진단, 처방, 시술, 치료는 협력 의료기관의 담당 의료진이 판단해 진행하고, atInc는 그 앞뒤의 병원 선택과 예약, 동행, 결과 이후 일정을 맡습니다.'),

    # ---------- network: say "we keep adding" once
    ('network.html', '</span>의 병원과 함께하고, 협력 병원을 지역마다 계속 늘려 가고 있습니다.', '</span>의 병원과 함께합니다.'),

    # ---------- people and wording used everywhere
    (None, '담당자가 연락드립니다', '담당 매니저가 연락드립니다'),
    (None, '담당자가 별도로 안내', '담당 매니저가 별도로 안내'),
    (None, '담당자가 따로', '담당 매니저가 따로'),
    (None, '알려드립니다', '알려 드립니다'),
    # buttons: one verb ("상담 예약") and the programme's Korean name
    (None, 'LONGEVITY 90 상담하기', '90일 롱제비티 상담 예약'),
    (None, 'EXECUTIVE 365 상담하기', '연간 헬스 오피스 상담 예약'),
    (None, '셀 케어 상담하기', '재생의료 상담 예약'),
    (None, '한국 진료 상담하기', '해외 고객 상담 예약'),
    # ---------- 2026-10-07 partner check: results are issued to the patient
    ('about.html', '결과지를 받아 전해 드리고, 결과 상담과 재검, 다음 진료 날짜까지 잡아 둡니다.', '결과지 발급을 도와 드리고, 결과 상담과 재검, 다음 진료 날짜까지 잡아 둡니다.'),
    ('medical-checkup.html', '결과지는 검진하고 약 2주 뒤에 나옵니다.', '간단한 결과는 당일 확인할 수 있고, 결과지는 기관에 따라 당일부터 약 2주 사이에 나옵니다.'),
    ('medical-checkup.html', '결과지는 약 2주 뒤에 나오고, 자세한 설명은', '결과지는 기관에 따라 당일부터 약 2주 사이에 나오고, 자세한 설명은'),
]

BUTTON_RE = re.compile(r'>([^<>]{1,30}?) 상담하기(<svg|</a>)')
USED = set()


def revise(h, fn):
    for i, (page, a, b) in enumerate(REVISE):
        if page and page != fn:
            continue
        if a in h:
            h = h.replace(a, b)
            USED.add(i)
    return BUTTON_RE.sub(lambda m: f'>{m.group(1)} 상담 예약{m.group(2)}', h)


def report():
    miss = [REVISE[i] for i in range(len(REVISE)) if i not in USED]
    for page, a, _ in miss:
        print('  REVISE unmatched:', page or '*', '|', a[:70])
    return miss
