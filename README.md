# atInc 홈페이지

atInc(주식회사 애트) 프라이빗 헬스케어 컨시어지 홈페이지입니다. HTML·CSS·JS로 된 정적 사이트 19페이지이고, 빌드 없이 `site/` 폴더를 그대로 웹서버에 올리면 됩니다.

- 1차 작업물: 2026-10-05
- 첫 화면: `site/index.html`

## 폴더

| 폴더 | 내용 |
| --- | --- |
| `site/` | 배포용 사이트. 이 폴더 안의 파일 전체를 웹 루트에 올립니다. 자세한 수정 방법은 `site/README.md` |
| `site/assets/fx/` | 움직이는 배경(ShaderGradient), 유리 효과(liquid-glass-js 방식), 3D 세포(three.js). 라이선스는 `THIRD_PARTY_NOTICES.txt` |
| `site/assets/network-data.js` | 협력 병원 목록. 이 파일만 고치면 지도와 목록이 함께 바뀝니다 |
| `build/` | 사이트를 다시 만드는 스크립트와 원고(`build/content/`) |
| `build/qa/` | 점검 스크립트(가로 넘침, 접근성·SEO, 병원명·가격 노출 검사) |

## 다시 만들기

원고나 구성을 바꿨을 때만 필요합니다. 협력 병원 추가·변경은 `site/assets/network-data.js`만 고치면 되고 다시 만들 필요가 없습니다.

```bash
python3 build/site_build.py        # site/*.html, sitemap.xml, robots.txt 생성
python3 build/mapbase_build.py     # 지도 바탕(site/assets/map-base.js), 지도 데이터를 바꿀 때만 (numpy, matplotlib 필요)
python3 build/qa/site_scan.py      # 병원명·가격 등 노출 검사
```

## 지킬 것

- 병원명·로고·정확한 주소, 가격, 허락받지 않은 사진·전후 사진은 사이트에 넣지 않습니다.
- 움직이는 효과는 https 웹서버에서 동작합니다. 파일을 직접 열면 정지 배경으로 보입니다.

## 지도 데이터

`build/mapdata/`의 행정구역 경계는 [southkorea-maps](https://github.com/southkorea/southkorea-maps)(통계청 2013, POPONG CC BY 4.0)에서 가져왔습니다.
