# atInc 홈페이지

atInc(주식회사 애트) 프라이빗 헬스케어 컨시어지 홈페이지입니다.
**내용은 관리자 화면에서, 디자인은 코드에서** 고치는 구조입니다.

| 무엇을 | 어디서 | 누가 |
| --- | --- | --- |
| 문구, 사진, 진료 분야·케어 프로그램 추가/삭제, 섹션 순서·숨김·추가, 지역, 연락처 | 관리자 화면 `https://atinc.co.kr/admin/` (= `content/` 폴더) | 관리자 |
| 색·글꼴·여백, 섹션 모양, 새 종류의 섹션, 화면 효과 | `templates/`, `static/assets/site.css`, `static/assets/site.js` | 개발자 |

## 관리자: 내용 고치기

1. `https://atinc.co.kr/admin/` 에 들어가 GitHub 계정으로 로그인합니다 (처음 한 번 아래 [로그인 준비]).
2. 왼쪽 메뉴에서 고칠 곳을 고릅니다.
   - **사이트 설정**: 전화·이메일·상담 신청서 주소, 회사 정보, 메뉴 이름, 바닥글, 상담 예약 카드
   - **페이지**: 홈·회사소개·진료 분야 목록·케어 프로그램 목록·협력 네트워크·제휴·상담 안내·개인정보처리방침·고지
   - **진료 분야**: 분야마다 한 페이지. [새로 만들기]로 분야를 추가하면 메뉴·홈 카드·목록·지도 필터가 함께 생깁니다 (기존 분야를 [복제]해서 고치면 빠릅니다)
   - **케어 프로그램**: 프로그램마다 한 페이지. 추가하는 방법은 진료 분야와 같습니다
   - **협력 지역**: 지도와 지역 카드. 시·도와 받을 수 있는 분야, 한 줄 설명
3. 페이지 안의 **섹션**은 끌어서 순서를 바꾸고, [추가]로 새 섹션을 넣고, “이 섹션 숨기기”로 잠시 내립니다.
4. 사진은 사진 칸에서 올리거나 주소를 넣습니다. 올린 사진은 자동으로 화면 크기별로 줄여서 씁니다.
5. **저장**하면 바로 공개되지 않고 “초안”이 됩니다. **[미리 보기 열기]**로 실제 화면을 확인하고, 상태를 [검토 중] → [준비됨]으로 바꾼 뒤 대표님이 **[게시]**를 누르면 사이트에 반영됩니다 (보통 1~2분).

### 저장해도 공개되지 않을 때
공개 전에 자동 검사를 합니다. 아래가 있으면 공개를 멈춥니다.
- 협력 병원·재단 이름 (비공개 단어 목록에 있는 말)
- 가격 표기 (숫자 + 원/만원/USD)
- “최고”, “완벽”, “보장” 같은 과장·효과 단정 표현
- 관리자 화면에서 고칠 수 없는 값

검사 결과는 GitHub 저장소의 **Actions** 탭(또는 Cloudflare Pages 배포 기록)에서 볼 수 있습니다.

### 로그인 준비 (사람마다 한 번)
1. GitHub 계정을 만들고, 대표 계정에서 이 저장소에 **Collaborator**로 초대받습니다 (Settings → Collaborators).
2. 관리자 화면에서 **[액세스 토큰으로 로그인]**을 누르면 GitHub 토큰 만드는 페이지가 열립니다. 권한이 미리 골라져 있으니 저장소만 이 저장소로 고르고 만든 뒤, 토큰을 붙여 넣습니다.
   - 토큰은 그 브라우저에만 저장됩니다. 공용 PC에서는 다 쓴 뒤 로그아웃하세요.
   - 여러 사람이 쓰게 되면 “GitHub로 로그인” 버튼을 쓰도록 바꿀 수 있습니다 (Cloudflare Workers에 Sveltia CMS Authenticator 설치, 아래 [나중에 할 수 있는 것]).

## 지킬 것

- 병원명·로고·정확한 주소, 가격, 허락받지 않은 사진·전후 사진은 사이트에 넣지 않습니다.
- 임시 사진(Unsplash)을 협력 병원 실제 시설처럼 소개하지 않습니다. 실제 시설 사진은 병원 허락을 받은 뒤 교체합니다.
- 사진에는 의료진·환자·모델의 얼굴을 넣지 않습니다. 사람은 손이나 뒷모습만 씁니다.
- 효과·결과를 약속하는 문장은 쓰지 않습니다. 협력 기관의 안내는 “협력 기관이 안내하는 일반적인 일정이며, 실제 일정은 의료진이 정합니다”처럼 정보로 소개하고, atInc가 그 일정을 어떻게 챙기는지를 함께 씁니다.
- 협력 병원 자료에서 가져온 진료 항목·순서·준비·회복 정보는 지우지 말고 표현만 고칩니다.
- 지역 설명에는 받으실 수 있는 것만 적고, 장비·규모·인증·재단처럼 병원을 알아볼 수 있는 내용은 적지 않습니다.

## 개발자: 구조

```
content/              관리자가 고치는 내용 (YAML). 관리자 화면이 이 파일들을 고칩니다
  settings.yml        연락처·회사 정보·메뉴·바닥글·상담 카드
  pages/*.yml         페이지별 섹션 목록
  fields/*.yml        진료 분야 (파일 하나 = 페이지 하나, medical-<id>.html)
  programs/*.yml      케어 프로그램 (care-<id>.html)
  regions.yml         협력 지역 (지도·지역 카드)
templates/            디자인 틀 (Jinja)
  base.html           머리글·메뉴·바닥글
  macros.html         공통 조각 (버튼, 섹션 머리, 상담 카드)
  sections/*.html     섹션 종류마다 한 파일
static/               그대로 복사되는 파일
  assets/             site.css, site.js, map.js, map-base.js, 아이콘, og.png
  admin/              관리자 화면 (index.html, config.yml)
  uploads/            관리자가 올린 사진
tools/
  build.py            content + templates + static → site/
  admin_config.py     관리자 화면 설정(static/admin/config.yml) 만들기 + 입력 칸 검사
  qa/                 점검 (site_scan: 문구 검사, site_qa: 가로 넘침, ecc_qa: 접근성·SEO)
  map/                지도 바탕(map-base.js) 만들기
site/                 만들어진 사이트 (직접 고치지 않습니다)
docs/manuscripts/     처음 원고 (보관용)
```

### 만들기와 검사

```bash
pip install -r requirements.txt
python3 tools/build.py            # site/ 만들기
python3 tools/build.py --check    # 만들고 공개 전 검사 (문제 있으면 실패)
python3 tools/admin_config.py     # 관리자 화면 설정 다시 만들기 (섹션 종류를 바꿨을 때)
```

비공개 단어(병원·재단 이름)는 저장소에 넣지 않습니다. 로컬에서는 `tools/qa/private-words.txt`(저장소에서 빠짐), GitHub Actions·Cloudflare에서는 비밀값 `ATINC_PRIVATE_WORDS`(쉼표 구분)에 둡니다.

### 새 섹션 종류 만들기

1. `templates/sections/<이름>.html` 을 만듭니다. 섹션 값은 `s`, 사이트 설정은 `S`, 진료 분야·프로그램 목록은 `fields`, `programs` 입니다.
2. `tools/admin_config.py` 의 `BLOCKS` 에 관리자 입력 칸을 적고, 쓸 페이지를 `PAGE_TYPES`(또는 어디서나 쓰려면 `GENERIC`)에 넣습니다.
3. `python3 tools/admin_config.py` 로 설정을 다시 만들고 `python3 tools/build.py --check` 로 확인합니다.

색·글꼴·여백 같은 디자인 값은 `static/assets/site.css` 맨 위 `:root` 변수에 모여 있습니다.

### 공개 방식

- **Cloudflare Pages** (권장): 저장소를 연결하고 빌드 명령 `pip install -r requirements.txt && python3 tools/build.py --check`, 출력 폴더 `site`, 환경변수 `ATINC_PRIVATE_WORDS`. main은 atinc.co.kr, 관리자 초안(다른 브랜치)은 미리보기 주소로 자동 공개됩니다. 검사에 실패하면 배포가 멈추고 이전 버전이 그대로 유지됩니다.
- **GitHub Actions** (`.github/workflows/site.yml`): 모든 수정에 검사를 돌리고, main에서는 `site/` 를 다시 만들어 저장합니다 (Cloudflare 연결 전까지 GitHub Pages·미리보기 링크용).

### 나중에 할 수 있는 것
- “GitHub로 로그인” 버튼: GitHub OAuth App을 만들고 Cloudflare Workers에 [Sveltia CMS Authenticator](https://github.com/sveltia/sveltia-cms-auth)를 설치한 뒤 `tools/admin_config.py` 의 `backend` 에 `base_url` 을 넣습니다.

## 작업 기록

- 1차 2026-10-05 · 2차 2026-10-06 사진 중심 재구성 · 3차 2026-10-06 화면 전면 교체
- 4차 2026-10-07 ECC 검토 반영, 서비스 중심 문구
- 5차 2026-10-07 참고 사이트 구성 반영 ('하는 일 / 하지 않는 일', 자주 묻는 질문)
- 6차 2026-10-07 모바일 점검 반영, 사진 스크롤 효과 정리
- 7차 2026-10-07 관리자 시스템: 내용을 `content/` 로 분리, 템플릿 빌드, 관리자 화면(Sveltia CMS), 공개 전 자동 검사

## 글꼴·지도

본문은 Pretendard(SIL OFL 1.1, jsDelivr CDN), 로고 글자만 Cormorant Garamond(Google Fonts)입니다.
`tools/map/mapdata/`의 행정구역 경계는 [southkorea-maps](https://github.com/southkorea/southkorea-maps)(통계청 2013, POPONG CC BY 4.0)에서 가져왔습니다.
