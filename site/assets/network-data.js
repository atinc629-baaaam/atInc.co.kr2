/*
  atInc 협력 네트워크 데이터 — 이 파일 하나만 고치면 지도와 목록이 함께 바뀝니다.

  병원을 추가하는 방법
  1) 아래 목록에 { ... }, 한 덩어리를 복사해 붙입니다.
  2) area  : 행정구역 이름. '시도 시군구'로 적습니다. 예) '서울 강남구', '경기 성남시 분당구', '대전 유성구'
             시까지만 적어도 됩니다(예: '경기 용인시'). 시도만 적으면 시도 중심에 표시됩니다(예: '대구').
  3) name  : 사이트에 보이는 지역 표기. 병원 이름은 적지 않습니다.
     short : 수도권 확대 지도에 들어갈 짧은 이름(예: '분당')
     en    : 영문 지역 표기
  4) cats  : 분야. checkup(건강검진) regenerative(재생의료·줄기세포) aesthetic(성형·피부)
             women(여성건강) men(남성건강) korean-medicine(한방·웰니스) 가운데 해당하는 것
  5) note  : 네트워크 페이지 카드에 들어갈 한 줄 설명. 그 지역에서 '받으실 수 있는 것'만 적고,
             장비 사양·규모·인증·운영 재단처럼 병원을 알아볼 수 있는 내용은 적지 않습니다.

  같은 지역에 병원이 여러 곳이면 한 줄씩 따로 적으면 됩니다. 지도에서는 한 점으로 묶이고 '외 n곳'으로 표시됩니다.
*/
window.ATINC_NETWORK = [
  { area: '서울 강남구', name: '서울 강남·압구정', short: '강남·압구정', en: 'Seoul · Gangnam, Apgujeong',
    cats: ['checkup', 'women', 'korean-medicine'],
    note: '정밀 건강검진과 여성 진료, 한방 미용 진료를 받으실 수 있습니다.' },
  { area: '인천 연수구', name: '인천 송도', short: '송도', en: 'Incheon · Songdo',
    cats: ['aesthetic'],
    note: '공항에서 가까운 곳에서 성형·피부 상담과 시술을 받으실 수 있습니다.' },
  { area: '인천 서구', name: '인천 검단', short: '검단', en: 'Incheon · Geomdan',
    cats: ['korean-medicine', 'aesthetic'],
    note: '한·양방 협진 진료와 입원 회복, 성형·피부 진료를 받으실 수 있습니다.' },
  { area: '인천 부평구', name: '인천 부평', short: '부평', en: 'Incheon · Bupyeong',
    cats: ['korean-medicine'],
    note: '한방 진료와 재활, 입원 치료를 받으실 수 있습니다.' },
  { area: '인천 남동구', name: '인천 남동', short: '남동', en: 'Incheon · Namdong',
    cats: ['korean-medicine'],
    note: '뇌졸중 재활과 오랜 회복이 필요한 분의 입원 치료를 받으실 수 있습니다.' },
  { area: '경기 성남시 분당구', name: '경기 분당', short: '분당', en: 'Gyeonggi · Bundang',
    cats: ['regenerative'],
    note: '재생의료 진료 상담과 세포 보관 상담을 받으실 수 있습니다.' },
  { area: '경기 군포시', name: '경기 군포', short: '군포', en: 'Gyeonggi · Gunpo',
    cats: ['regenerative'],
    note: '본인 세포의 배양과 보관 상담을 받으실 수 있습니다.' },
  { area: '경기 용인시', name: '경기 용인', short: '용인', en: 'Gyeonggi · Yongin',
    cats: ['checkup'],
    note: '정밀 건강검진을 받으실 수 있습니다.' },
  { area: '대구', name: '대구', short: '대구', en: 'Daegu',
    cats: ['women', 'men'],
    note: '난임 검사와 시험관아기, 가임력 보존, 남성 난임 진료를 받으실 수 있습니다.' },
  { area: '부산 남구', name: '부산', short: '부산', en: 'Busan',
    cats: ['checkup'],
    note: '정밀 건강검진과 외국어 안내를 받으실 수 있습니다.' }
];
