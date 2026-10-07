# atInc 홈페이지

atInc(주식회사 애트) 프라이빗 헬스케어 컨시어지 홈페이지입니다.
**내용은 편집기에서, 디자인은 코드에서** 고치는 구조입니다.

| 무엇을 | 어디서 | 누가 |
| --- | --- | --- |
| 문구, 사진, 섹션·카드 순서와 숨기기·복제·삭제, 진료 분야·케어 프로그램 추가, 지역, 연락처 | 편집기 `site/admin/` (= `content/` 폴더) | 관리자 |
| 색·글꼴·여백, 섹션 모양, 새 종류의 섹션, 화면 효과 | `templates/`, `static/assets/site.css`, `static/assets/site.js` | 개발자 |

## 관리자: 편집기로 고치기

편집기 주소: `https://atinc629-baaaam.github.io/atInc.co.kr2/site/admin/`
(도메인을 연결한 뒤에는 `https://atinc.co.kr/admin/`)

1. 처음 한 번, 편집기 첫 화면의 안내대로 GitHub 토큰을 만들어 붙여 넣고 로그인합니다.
2. 위 목록에서 고칠 페이지를 고르면, 실제 홈페이지 화면이 그대로 열립니다.
3. **글자를 누르면** 오른쪽 칸에서 고치고, 화면에 바로 보입니다.
4. **사진을 누르면** 내 컴퓨터에서 새 사진을 고를 수 있습니다. 큰 사진은 자동으로 줄여서 올리고, 잘릴 때 남길 곳(위·가운데·아래 등)도 고릅니다.
5. **섹션·카드 위에 마우스를 올리면** ▲▼(순서), 숨기기, 복제, 삭제 단추가 나옵니다. 새 섹션·카드는 비슷한 것을 복제한 뒤 고칩니다.
6. 위 막대: **사이트 설정**(연락처·회사 정보·메뉴 이름·바닥글), **협력 지역**(지도와 지역 카드), **페이지 정보**(검색 결과에 나오는 제목·설명), **더보기**(진료 분야·케어 프로그램 새로 만들기·숨기기, 로그아웃).
7. **저장**을 누르면 바뀐 내용과 사진이 한 번에 GitHub에 올라가고, 1~2분 뒤 홈페이지에 반영됩니다. 저장 전에는 **모두 취소**로 되돌릴 수 있습니다.

### 저장해도 반영되지 않을 때
공개 전에 자동 검사를 합니다. 아래가 있으면 공개를 멈추고 편집기에 알려 줍니다.
- 협력 병원·재단 이름 (비공개 단어 목록에 있는 말)
- 가격 표기 (숫자 + 원/만원/USD)
- “최고”, “완벽”, “보장” 같은 과장·효과 단정 표현

검사 결과는 GitHub 저장소의 **Actions** 탭에서도 볼 수 있습니다.

## 지킬 것

- 병원명·로고·정확한 주소, 가격, 허락받지 않은 사진·전후 사진은 사이트에 넣지 않습니다.
- 임시 사진(Unsplash)을 협력 병원 실제 시설처럼 소개하지 않습니다. 실제 시설 사진은 병원 허락을 받은 뒤 교체합니다.
- 사진에는 의료진·환자·모델의 얼굴을 넣지 않습니다. 사람은 손이나 뒷모습만 씁니다.
- 효과·결과를 약속하는 문장은 쓰지 않습니다. 협력 기관의 안내는 “협력 기관이 안내하는 일반적인 일정이며, 실제 일정은 의료진이 정합니다”처럼 정보로 소개하고, atInc가 그 일정을 어떻게 챙기는지를 함께 씁니다.
- 협력 병원 자료에서 가져온 진료 항목·순서·준비·회복 정보는 지우지 말고 표현만 고칩니다.
- 지역 설명에는 받으실 수 있는 것만 적고, 장비·규모·인증·재단처럼 병원을 알아볼 수 있는 내용은 적지 않습니다.

## 개발자: 구조

```
content/              편집기가 고치는 내용 (JSON)
  settings.json       연락처·회사 정보·메뉴·바닥글·상담 카드
  pages/*.json        페이지별 섹션 목록
  fields/*.json       진료 분야 (파일 하나 = 페이지 하나, medical-<id>.html)
  programs/*.json     케어 프로그램 (care-<id>.html)
  regions.json        협력 지역 (지도·지역 카드)
templates/            디자인 틀 (Jinja)
  base.html           머리글·메뉴·바닥글
  macros.html         공통 조각 (버튼, 섹션 머리, 상담 카드)
  sections/*.html     섹션 종류마다 한 파일
static/               그대로 복사되는 파일
  assets/             site.css, site.js, map.js, map-base.js, 아이콘, og.png
  admin/              편집기 (index.html, editor.js/css, 페이지 안 도구 inject.js/css)
  uploads/            편집기로 올린 사진 (빌드 때 화면 크기별로 줄인 사본을 만듭니다)
tools/
  build.py            content + templates + static → site/ (공개 페이지 + 편집용 사본 site/admin/edit/)
  qa/                 점검 (site_scan: 문구 검사, edit_marks: 편집 표시 검사, site_qa·ecc_qa)
  map/                지도 바탕(map-base.js) 만들기
site/                 만들어진 사이트 (직접 고치지 않습니다)
docs/manuscripts/     처음 원고 (보관용)
```

### 편집기가 움직이는 방식

- 빌드는 같은 템플릿으로 공개 페이지와 **편집용 사본**(`site/admin/edit/*.html`)을 함께 만듭니다. 편집용 사본에는 글·사진·항목마다 내용 파일의 위치가 표시됩니다 (`data-e="pages/home#sections.3.title"`, `data-img`, `data-item`).
- 편집기는 그 사본을 화면에 띄우고, 누른 곳의 값을 GitHub의 `content/*.json` 에서 읽어 고칩니다.
- 저장은 GitHub API로 한 번의 커밋을 만듭니다 (바뀐 JSON + 올린 사진). 그 사이 다른 곳에서 같은 파일이 바뀌었으면 덮어쓰지 않고 멈춥니다.
- 커밋이 올라가면 GitHub Actions(`.github/workflows/site.yml`)가 사이트를 다시 만들고 검사한 뒤 `site/` 를 저장하고 GitHub Pages에 올립니다.

### 만들기와 검사

```bash
pip install -r requirements.txt
python3 tools/build.py            # site/ 만들기
python3 tools/build.py --check    # 만들고 공개 전 검사 + 편집 표시 검사 (문제 있으면 실패)
```

비공개 단어(병원·재단 이름)는 저장소에 넣지 않습니다. 로컬에서는 `tools/qa/private-words.txt`(저장소에서 빠짐), GitHub Actions·Cloudflare에서는 비밀값 `ATINC_PRIVATE_WORDS`(쉼표 구분)에 둡니다.

### 새 섹션 종류 만들기

1. `templates/sections/<이름>.html` 을 만듭니다. 섹션 값은 `s`, 섹션 위치는 `P`(예: `pages/home#sections.3`), 사이트 설정은 `S` 입니다.
2. 편집할 수 있게 표시를 답니다: 글 하나만 든 태그에는 `{{ A(P ~ '.title') }}`, 글이 섞인 곳에는 `{{ W(P ~ '.title', s.title) }}`, 사진은 `pic(..., path=P ~ '.photo')`, 목록 한 칸에는 `{{ IT(P ~ '.items.' ~ loop.index0) }}`.
3. `static/admin/editor.js` 의 `SECTION_LABELS` 에 한글 이름을 넣습니다.
4. `python3 tools/build.py --check` 로 확인합니다 (`edit_marks` 가 모든 표시가 내용과 맞는지 봅니다).

색·글꼴·여백 같은 디자인 값은 `static/assets/site.css` 맨 위 `:root` 변수에 모여 있습니다.

### 공개 방식

- 지금: **GitHub Pages** (`https://atinc629-baaaam.github.io/atInc.co.kr2/site/`). main에 저장될 때마다 Actions가 `site/` 를 다시 만듭니다.
- 도메인 연결 때 권장: **Cloudflare Pages** — 빌드 명령 `pip install -r requirements.txt && python3 tools/build.py --check`, 출력 폴더 `site`, 환경변수 `ATINC_PRIVATE_WORDS`. 이때는 Actions의 `site/` 저장 단계를 지우고, 저장소를 비공개로 돌립니다.

## 작업 기록

- 1차 2026-10-05 · 2차 2026-10-06 사진 중심 재구성 · 3차 2026-10-06 화면 전면 교체
- 4차 2026-10-07 ECC 검토 반영, 서비스 중심 문구
- 5차 2026-10-07 참고 사이트 구성 반영 ('하는 일 / 하지 않는 일', 자주 묻는 질문)
- 6차 2026-10-07 모바일 점검 반영, 사진 스크롤 효과 정리
- 7차 2026-10-07 내용을 `content/` 로 분리, 템플릿 빌드, 공개 전 자동 검사
- 8차 2026-10-07 자체 편집기: 실제 화면에서 글·사진·섹션을 고치고 저장하면 GitHub에 커밋

## 글꼴·지도

본문은 Pretendard(SIL OFL 1.1, jsDelivr CDN), 로고 글자만 Cormorant Garamond(Google Fonts)입니다.
`tools/map/mapdata/`의 행정구역 경계는 [southkorea-maps](https://github.com/southkorea/southkorea-maps)(통계청 2013, POPONG CC BY 4.0)에서 가져왔습니다.
