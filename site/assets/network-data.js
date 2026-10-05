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
  5) note  : 네트워크 페이지 카드에 들어갈 한 줄 설명

  같은 지역에 병원이 여러 곳이면 한 줄씩 따로 적으면 됩니다. 지도에서는 한 점으로 묶이고 '외 n곳'으로 표시됩니다.
*/
window.ATINC_NETWORK = [
  { area: '서울 강남구', name: '서울 강남·압구정', short: '강남·압구정', en: 'Seoul · Gangnam, Apgujeong',
    cats: ['checkup', 'women', 'aesthetic', 'korean-medicine'],
    note: '정밀검진 센터와 여성 클리닉, 피부 클리닉, 한방병원이 한 지역에 있습니다.' },
  { area: '인천 연수구', name: '인천 송도', short: '송도', en: 'Incheon · Songdo',
    cats: ['aesthetic'],
    note: '인천국제공항과 가까운 송도에서 성형외과·피부과 협진 클리닉과 함께합니다.' },
  { area: '인천 서구', name: '인천 검단', short: '검단', en: 'Incheon · Geomdan',
    cats: ['korean-medicine'],
    note: '한·양방 협진 진료와 입원 회복을 함께 받으실 수 있습니다.' },
  { area: '경기 성남시 분당구', name: '경기 분당', short: '분당', en: 'Gyeonggi · Bundang',
    cats: ['regenerative'],
    note: '첨단재생의료 실시기관으로 지정된 병원에서 재생의료 상담을 받으실 수 있습니다.' },
  { area: '경기 군포시', name: '경기 군포', short: '군포', en: 'Gyeonggi · Gunpo',
    cats: ['regenerative'],
    note: 'GMP 기준 세포처리시설에서 본인 세포를 배양하고 초저온으로 보관합니다.' },
  { area: '경기 용인시', name: '경기 용인', short: '용인', en: 'Gyeonggi · Yongin',
    cats: ['checkup'],
    note: '여성 전용 검진 공간과 국제진료센터를 갖춘 정밀검진 센터입니다.' },
  { area: '대구', name: '대구', short: '대구', en: 'Daegu',
    cats: [],
    note: '대구·경북에 계신 분은 가까운 협력 병원에서 상담과 검사를 받으실 수 있습니다.' },
  { area: '부산 남구', name: '부산', short: '부산', en: 'Busan',
    cats: ['checkup'],
    note: 'VIP와 남녀 동선을 나눈 정밀검진 센터와 국제진료센터가 있습니다.' }
];
