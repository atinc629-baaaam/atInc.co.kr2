# atInc 홈페이지

atInc(주식회사 애트) 프라이빗 헬스케어 컨시어지 홈페이지입니다. HTML·CSS·JS로 된 정적 사이트 19페이지이고, 빌드 없이 `site/` 폴더를 그대로 웹서버에 올리면 됩니다.

- 1차 작업물: 2026-10-05
- 2차 작업물: 2026-10-06, 사진 중심으로 다시 구성
- 3차 작업물: 2026-10-06, 화면 전면 교체(산세리프·밝은 바탕), 얼굴 없는 사진, 바로가기·슬라이드 표시·상담 버튼
- 4차 작업물: 2026-10-07, ECC 검토 반영. 의료 효과가 아니라 서비스(어떤 기관과 어떻게 연결하고 무엇을 챙기는지) 중심으로 문구 정리, 협력 병원 자료는 유지
- 첫 화면: `site/index.html`

## 폴더

| 폴더 | 내용 |
| --- | --- |
| `site/` | 배포용 사이트. 이 폴더 안의 파일 전체를 웹 루트에 올립니다. 자세한 수정 방법은 `site/README.md` |
| `build/photos.json` | 사이트에 쓰는 사진 목록. 지금은 Unsplash 임시 사진이고, 실제 사진은 `site/assets/img/`에 넣은 뒤 `src`를 `assets/img/파일명.jpg`로 바꾸고 다시 만들면 됩니다 |
| `site/assets/fx/` | 1차 작업물의 움직이는 배경·유리 효과·3D 세포(three.js). 2차에서는 쓰지 않고 남겨 둠. 라이선스는 `THIRD_PARTY_NOTICES.txt` |
| `site/assets/network-data.js` | 협력 병원 목록. 이 파일만 고치면 지도와 목록이 함께 바뀝니다 |
| `build/` | 사이트를 다시 만드는 스크립트와 원고(`build/content/`) |
| `build/site_revise.py` | 마지막 문구 손질 목록(페이지, 바꿀 문장, 새 문장). 빌드 때 맞는 문장이 없으면 `REVISE unmatched`로 알려 줍니다 |
| `build/qa/` | 점검 스크립트(가로 넘침, 접근성·SEO, 병원명·가격 노출 검사) |

## 다시 만들기

원고나 구성을 바꿨을 때만 필요합니다. 협력 병원 추가·변경은 `site/assets/network-data.js`만 고치면 되고 다시 만들 필요가 없습니다.

```bash
python3 build/site_build.py        # site/*.html, sitemap.xml, robots.txt 생성
python3 build/mapbase_build.py     # 지도 바탕(site/assets/map-base.js), 지도 데이터를 바꿀 때만 (numpy, matplotlib 필요)
python3 build/qa/site_scan.py      # 병원명·가격 등 노출 검사
```

## 글꼴

본문은 Pretendard(SIL OFL 1.1, jsDelivr CDN), 로고 글자만 Cormorant Garamond(Google Fonts)입니다.

## 지킬 것

- 병원명·로고·정확한 주소, 가격, 허락받지 않은 사진·전후 사진은 사이트에 넣지 않습니다.
- 임시 사진(Unsplash)을 협력 병원 실제 시설처럼 소개하지 않습니다. 실제 시설 사진은 병원 허락을 받은 뒤 교체합니다.
- 사진에는 의료진·환자·모델의 얼굴을 넣지 않습니다. 사람은 손이나 뒷모습만 씁니다.
- 효과·결과를 약속하는 문장(“좋아집니다”, “다음 날 출근할 수 있습니다”)은 쓰지 않습니다. 협력 기관의 안내는 “협력 기관이 안내하는 일반적인 일정이며, 실제 일정은 의료진이 정합니다”처럼 정보로 소개하고, atInc가 그 일정을 어떻게 챙기는지를 함께 씁니다.
- 협력 병원 자료에서 가져온 진료 항목·순서·준비·회복 정보는 지우지 말고 표현만 고칩니다.

## 지도 데이터

`build/mapdata/`의 행정구역 경계는 [southkorea-maps](https://github.com/southkorea/southkorea-maps)(통계청 2013, POPONG CC BY 4.0)에서 가져왔습니다.
