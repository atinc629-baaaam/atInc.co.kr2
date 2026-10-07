#!/usr/bin/env python3
"""관리자 화면(/admin) 설정 파일을 만듭니다: static/admin/config.yml

블록(섹션) 종류를 새로 만들면 templates/sections/<이름>.html 을 만들고,
아래 BLOCKS 에 입력 칸을 적은 뒤 이 스크립트를 다시 실행합니다.

    python3 tools/admin_config.py          # config.yml 만들기 + 내용 파일 검사
    python3 tools/admin_config.py --check  # 검사만 (내용의 모든 값에 입력 칸이 있는지)
"""
import glob
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = 'atinc629-baaaam/atInc.co.kr2'


# ------------------------------------------------------------------ small field builders
def S(name, label, hint=None, req=False, **kw):
    f = {'label': label, 'name': name, 'widget': 'string', 'required': req}
    if hint:
        f['hint'] = hint
    f.update(kw)
    return f


def TX(name, label, hint=None, req=False, **kw):
    return S(name, label, hint, req, widget='text', **kw)


def B(name, label, hint=None, default=False):
    f = {'label': label, 'name': name, 'widget': 'boolean', 'required': False, 'default': default}
    if hint:
        f['hint'] = hint
    return f


def N(name, label, hint=None):
    f = {'label': label, 'name': name, 'widget': 'number', 'value_type': 'int', 'required': False}
    if hint:
        f['hint'] = hint
    return f


def SEL(name, label, options, hint=None, default=None):
    f = {'label': label, 'name': name, 'widget': 'select', 'required': False,
         'options': [{'label': l, 'value': v} for v, l in options]}
    if default is not None:
        f['default'] = default
    if hint:
        f['hint'] = hint
    return f


def OBJ(name, label, fields, req=False, collapsed=False, hint=None):
    f = {'label': label, 'name': name, 'widget': 'object', 'required': req, 'collapsed': collapsed, 'fields': fields}
    if hint:
        f['hint'] = hint
    return f


def LIST(name, label, fields=None, field=None, summary=None, hint=None, req=False, collapsed=True):
    f = {'label': label, 'name': name, 'widget': 'list', 'required': req}
    if fields is not None:
        f['fields'] = fields
        f['collapsed'] = collapsed
    if field is not None:
        f['field'] = field
    if summary:
        f['summary'] = summary
    if hint:
        f['hint'] = hint
    return f


def STRS(name, label, hint=None, item='항목', text=False):
    return LIST(name, label, field=(TX if text else S)('item', item), hint=hint)


PHOTO_HINT = '사람 얼굴, 간판·로고, 수술·피 장면은 쓰지 않습니다. 협력 병원 실제 사진은 병원 허락을 받은 것만 씁니다.'


def PHOTO(name='photo', label='사진', req=False):
    return OBJ(name, label, [
        {'label': '사진 파일', 'name': 'src', 'widget': 'image', 'required': req, 'hint': PHOTO_HINT},
        S('alt', '사진 설명', '무엇이 보이는 사진인지 짧게 적습니다. 화면 낭독기와 검색에 쓰입니다.'),
        S('pos', '사진 초점 위치', '사진이 잘릴 때 남길 곳. 가로% 세로% — 가운데 50% 50%, 위쪽 50% 25%, 아래쪽 50% 75%'),
    ], req=req)


def LINK(name, label):
    return OBJ(name, label, [S('label', '글자'), S('href', '연결 주소', '예: medical.html, network.html, #process')])


BUTTON_STYLES = [('btn btn--light', '밝은 버튼 (어두운 사진 위)'), ('btn btn--line', '테두리 버튼 (사진 위)'),
                 ('btn btn--dark', '진한 버튼'), ('btn btn--ghost', '연한 테두리 버튼'), ('link', '밑줄 글자')]


def BUTTON(name='button', label='버튼'):
    return OBJ(name, label, [
        S('label', '버튼 글자'),
        B('form', '상담 신청서로 연결', '켜면 아래 주소 대신 상담 신청서(구글 폼)가 새 창으로 열립니다.'),
        S('form_label', '신청서 관심 분야', '상담 신청서로 연결할 때 함께 넘길 분야 이름 (예: 건강검진)'),
        S('href', '연결 주소', '신청서 연결이 꺼져 있을 때 이동할 주소. 예: medical-checkup.html'),
        SEL('style', '버튼 모양', BUTTON_STYLES),
        SEL('icon', '화살표 아이콘', [('out', '바깥 화살표 표시')]),
    ])


TONE = SEL('tone', '배경', [('light', '밝은 바탕'), ('sand', '연한 갈색 바탕')], default='light')
HIDDEN = B('hidden', '이 섹션 숨기기', '켜면 화면에서 빠집니다. 지우지 않고 잠시 내릴 때 씁니다.')
ANCHOR = S('anchor', '바로가기 이름', '다른 곳에서 #이름 으로 이 섹션에 바로 올 때 씁니다 (영문 소문자). 보통 비워 둡니다.')
MORE = LINK('more', '오른쪽 링크 (전체 보기 등)')
NOTES = STRS('notes', '아래 작은 안내 문장', text=True)
LABEL = S('label', '작은 영문 머리글', '제목 위에 작게 들어가는 영문 (예: Medical)')
TITLE = S('title', '제목', req=True)
LEAD = TX('lead', '제목 아래 설명')
ITEMS_TT = LIST('items', '카드', [S('title', '제목'), TX('text', '설명')], summary='{{fields.title}}')


def block(name, label, fields, hint=None):
    h = dict(HIDDEN)
    if hint:
        h['hint'] = hint + ' / ' + HIDDEN['hint']
    return {'name': name, 'label': label, 'widget': 'object', 'fields': [h] + fields}


# ------------------------------------------------------------------ blocks (= templates/sections/*.html)
BLOCKS = {
    # --- 홈
    'hero_slider': block('hero_slider', '첫 화면 슬라이드', [
        S('sr_title', '화면 낭독용 제목', '화면에는 보이지 않고 검색엔진과 화면 낭독기에 쓰입니다.'),
        LIST('slides', '슬라이드', [PHOTO(req=True), S('label', '작은 영문 머리글'), TX('title', '큰 제목', '줄을 바꾸면 화면에서도 그 자리에서 줄이 바뀝니다.'),
                                 TX('text', '설명'), BUTTON()], summary='{{fields.label}}'),
    ]),
    'quick_menu': block('quick_menu', '바로가기 메뉴', [
        LIST('items', '메뉴', [SEL('icon', '아이콘', [('medical', '진료(십자)'), ('calendar', '달력'), ('pin', '위치'), ('globe', '지구'), ('chat', '말풍선'), ('phone', '전화')]),
                             S('label', '글자'), S('href', '연결 주소')], summary='{{fields.label}}'),
    ]),
    'marquee': block('marquee', '흐르는 글자 띠', [STRS('words', '흐르는 글자')]),
    'do_dont': block('do_dont', '하는 일 / 하지 않는 일', [
        LABEL, TITLE, LEAD,
        S('do_title', '왼쪽 제목'), LIST('do', '하는 일', [S('k', '항목'), TX('d', '설명')], summary='{{fields.k}}'),
        S('dont_title', '오른쪽 제목'), STRS('dont', '하지 않는 일', text=True),
        S('note', '오른쪽 아래 작은 글', '예: 등록번호'),
    ]),
    'field_tiles': block('field_tiles', '진료 분야 카드 (자동)', [
        LABEL, TITLE, MORE,
        OBJ('note', '아래 한 줄 안내', [S('label', '앞 굵은 글'), TX('text', '문장'), S('link_label', '링크 글자'), S('link_href', '링크 주소')]),
    ], hint='카드는 [진료 분야] 메뉴의 내용으로 자동으로 만들어집니다.'),
    'program_tiles': block('program_tiles', '케어 프로그램 카드 (자동)', [LABEL, TITLE, MORE],
                           hint='카드는 [케어 프로그램] 메뉴의 내용으로 자동으로 만들어집니다.'),
    'flow': block('flow', '진행 단계 (홈)', [ANCHOR, LABEL, TITLE, MORE, LIST('steps', '단계', [S('title', '제목'), TX('text', '설명')], summary='{{fields.title}}')]),
    'network_preview': block('network_preview', '전국 협력 의료기관 (지도)', [
        LABEL, TITLE, TX('text', '설명', '{regions} 라고 적은 자리에 지역 이름(서울, 인천 …)이 자동으로 들어갑니다.'),
        TX('empty', '선택한 분야에 지역이 없을 때 문장'), LINK('link', '아래 링크'),
        S('map_note_en', '지도 아래 영문'), S('map_note', '지도 아래 한글'),
    ], hint='지도와 지역 목록은 [협력 지역] 메뉴의 내용으로 자동으로 만들어집니다.'),
    'intl': block('intl', '사진과 글 (좌우)', [
        PHOTO(), LABEL, TITLE, TX('text', '설명'), STRS('list', '목록'),
        S('en_text', '영문 안내 문장', '뒤에 이메일 주소가 자동으로 붙습니다.'), BUTTON(),
    ]),
    'faq_home': block('faq_home', '자주 묻는 질문', [LABEL, TITLE, LIST('items', '질문', [S('q', '질문'), TX('a', '답')], summary='{{fields.q}}')]),
    'contact_home': block('contact_home', '상담 안내 + 예약 카드 (홈)', [
        LABEL, TITLE, TX('text', '설명'), STRS('notes', '목록'), LINK('link', '아래 링크'), S('button', '예약 카드 버튼 글자'),
    ], hint='예약 카드의 내용은 [사이트 설정 > 상담 예약 카드]에서 고칩니다.'),

    # --- 진료 분야 / 케어 프로그램 상세
    'photo_hero': block('photo_hero', '큰 사진 첫 화면', [
        PHOTO('photo', '사진 (비우면 대표 사진)'),
        S('sub', '제목 아래 한 줄'), TX('text', '설명'),
        S('button', '버튼 글자 (진료 분야)', '버튼은 상담 신청서로 연결됩니다.'),
        LIST('meta', '요약 칸 (케어 프로그램)', [S('k', '항목'), S('v', '내용')], summary='{{fields.k}}: {{fields.v}}'),
        S('reg_note', '작은 안내 (케어 프로그램)'),
    ]),
    'ways': block('ways', '번호 카드', [
        SEL('variant', '모양', [('', '제목 + 설명'), ('who', '짧은 카드 (제목만)')]),
        TITLE, LEAD, MORE, TONE, ANCHOR,
        LIST('items', '카드', [S('title', '제목'), TX('text', '설명')], summary='{{fields.title}}'),
    ]),
    'services': block('services', '진료 목록 (휴대폰에서 접힘)', [
        TITLE, LEAD, MORE, TONE, ANCHOR,
        LIST('items', '진료', [S('title', '제목'), TX('text', '한 줄 설명'), STRS('sub', '세부 항목', text=True)], summary='{{fields.title}}'),
        NOTES,
    ], hint='협력 기관에서 받을 수 있는 진료를 적습니다. 병원 이름·장비 모델·병상 수처럼 병원을 알아볼 수 있는 내용은 적지 않습니다.'),
    'photo_band': block('photo_band', '넓은 사진 띠', [PHOTO(req=True), S('word', '사진 위 영문 글자', '비우면 분야 영문 이름이 들어갑니다.')]),
    'cards': block('cards', '제목 + 설명 카드', [
        TITLE, LEAD, MORE, TONE, ANCHOR,
        LIST('items', '카드', [S('title', '제목'), TX('text', '설명'), S('fit', '작은 글 (이런 분께 …)')], summary='{{fields.title}}'),
        NOTES,
    ]),
    'steps': block('steps', '진행 과정', [
        SEL('layout', '제목 모양', [('', '보통 제목'), ('plain', '큰 제목')]),
        TITLE, LEAD, MORE, TONE, ANCHOR,
        LIST('items', '단계', [S('title', '제목'), TX('text', '설명')], summary='{{fields.title}}'),
    ]),
    'guide': block('guide', '준비·회복 안내 (목록 묶음)', [
        TITLE, LEAD, TONE, ANCHOR,
        B('fold', '휴대폰에서 목록 접기', default=True),
        OBJ('timeline', '일정 그래픽 (선택)', [
            S('title', '그래픽 제목'), S('source', '오른쪽 작은 글 (출처)'),
            LIST('steps', '일정', [S('when', '때 (예: 전날)'), S('title', '제목'), TX('text', '설명')], summary='{{fields.when}} · {{fields.title}}'),
            TX('note', '아래 안내'),
        ], collapsed=True),
        LIST('groups', '목록 묶음', [S('title', '묶음 제목'), STRS('items', '항목', text=True)], summary='{{fields.title}}'),
        NOTES,
    ]),
    'faq_more': block('faq_more', '자주 묻는 질문 + 더 알아보기', [
        S('faq_title', '왼쪽 제목'), LIST('faq', '질문', [S('q', '질문'), TX('a', '답')], summary='{{fields.q}}'),
        S('more_title', '오른쪽 제목'),
        OBJ('about', '① 소개', [
            S('title', '제목'),
            LIST('rows', '설명 줄', [S('term', '용어 (선택)'), TX('text', '설명')], summary='{{fields.term}} {{fields.text}}'),
            LIST('tables', '표', [STRS('headers', '머리 칸'), STRS('labels', '휴대폰용 칸 이름 (선택)'),
                                 LIST('rows', '줄', [STRS('cells', '칸', text=True)])], summary='{{fields.headers}}'),
        ], collapsed=True),
        OBJ('how', '② 원리와 방식', [S('title', '제목'),
                                   LIST('cards', '카드', [S('title', '제목'), TX('text', '설명'), STRS('points', '점 목록 (설명 대신)', text=True)], summary='{{fields.title}}')], collapsed=True),
        OBJ('check', '③ 확인할 것', [S('title', '제목'), LIST('items', '항목', [S('k', '항목'), TX('v', '내용')], summary='{{fields.k}}'),
                                    OBJ('principle', '원칙 상자', [S('title', '제목'), TX('text', '내용')])], collapsed=True),
    ]),
    'cband': block('cband', '상담 띠 + 예약 카드', [
        S('label', '작은 영문 머리글', '비우면 Private Consultation'), TITLE, TX('text', '설명'),
        S('reasons_title', '목록 제목 (예: 이럴 때 상담하세요)'),
        STRS('reasons', '목록', '비우면 [사이트 설정]의 기본 안내 세 줄이 들어갑니다.', text=True),
        S('button', '버튼 글자'), S('form_label', '신청서 관심 분야', '비우면 이 페이지의 분야가 들어갑니다.'),
    ]),
    'step_cards': block('step_cards', '진행 단계 카드 (휴대폰에서 접힘)', [
        TITLE, LEAD, TONE, ANCHOR,
        LIST('items', '단계', [S('title', '제목'), S('en', '영문 작은 글'), STRS('sub', '할 일', text=True)], summary='{{fields.title}}'),
        NOTES,
    ]),
    'facts': block('facts', '숫자 카드 (어두운 바탕)', [
        ANCHOR, TITLE, LEAD,
        LIST('items', '카드', [S('figure', '큰 숫자'), S('unit', '단위'), B('word', '숫자 대신 글자'), TX('text', '설명'),
                              S('source', '출처'), S('source_href', '출처 주소')], summary='{{fields.figure}}{{fields.unit}}'),
    ], hint='공식 통계만 쓰고 출처를 꼭 적습니다.'),
    'journey': block('journey', '목적 목록', [TITLE, LEAD, TONE, S('list_title', '목록 제목'), STRS('items', '목적'), NOTES]),
    'program_links': block('program_links', '다른 케어 프로그램 링크 (자동)', [S('title', '제목'), LIST('extra', '더 넣을 링크', [S('label', '글자'), S('href', '주소')], summary='{{fields.label}}')]),

    # --- 그 밖의 페이지
    'page_hero': block('page_hero', '페이지 첫 화면', [
        S('crumb', '현재 위치 이름', '홈 / ○○ 에 들어가는 이름'), TX('title', '제목', '줄을 바꾸면 화면에서도 줄이 바뀝니다.'),
        TX('lead', '설명', '{regions} 라고 적은 자리에 지역 이름이 자동으로 들어갑니다.'), TX('notice', '작은 고지 문장'),
        LIST('buttons', '버튼', [S('label', '버튼 글자'), B('form', '상담 신청서로 연결'), S('form_label', '신청서 관심 분야'), S('href', '연결 주소'),
                               SEL('style', '버튼 모양', BUTTON_STYLES), SEL('icon', '화살표 아이콘', [('out', '바깥 화살표 표시')])], summary='{{fields.label}}'),
        B('contacts', '이메일·전화 표시'), PHOTO('photo', '오른쪽 사진 (선택)'),
    ]),
    'card_grid': block('card_grid', '카드 묶음 (3칸·4칸)', [
        TONE, TITLE, LEAD,
        SEL('columns', '한 줄 칸 수', [(3, '3칸'), (4, '4칸')], default=3),
        SEL('style', '카드 머리 모양', [('title', '제목'), ('label', '작은 갈색 글자'), ('en', '큰 글자')], default='title'),
        LIST('items', '카드', [S('title', '머리'), TX('text', '설명')], summary='{{fields.title}}'),
    ]),
    'company_info': block('company_info', '회사 정보 표 (자동)', [S('title', '제목')], hint='값은 [사이트 설정 > 회사 정보]에서 고칩니다.'),
    'field_cards': block('field_cards', '진료 분야 목록 카드 (자동)', [S('link_label', '카드 아래 링크 글자')]),
    'access': block('access', '그 밖의 전문 진료', [
        ANCHOR, TX('title', '제목', '줄을 바꾸면 화면에서도 줄이 바뀝니다.'), TX('lead', '설명'),
        LIST('items', '진료', [S('en', '영문'), S('title', '이름'), S('summary', '한 줄 요약'), TX('text', '설명'), STRS('points', '살펴보는 것'),
                              S('meta', '아래 작은 글'), S('button', '버튼 글자')], summary='{{fields.title}}'),
    ]),
    'cta_row': block('cta_row', '한 줄 안내 + 버튼', [TITLE, TX('notice', '작은 안내'), LINK('button', '버튼')]),
    'program_list': block('program_list', '케어 프로그램 목록 (자동)', []),
    'network': block('network', '지도 + 지역 카드 (자동)', [
        S('all_label', '전체 버튼 글자'), TX('empty', '선택한 분야에 지역이 없을 때 문장'),
        S('map_note_en', '지도 아래 영문'), S('map_note', '지도 아래 한글'), TX('note', '목록 아래 작은 글'),
    ], hint='지역은 [협력 지역] 메뉴에서 고칩니다.'),
    'partner_types': block('partner_types', '함께 일하는 곳', [TITLE, LEAD, TONE,
                                                           LIST('items', '종류', [S('title', '이름'), TX('text', '설명'), STRS('examples', '예')], summary='{{fields.title}}')]),
    'two_lists': block('two_lists', '두 칸 목록', [
        TONE,
        OBJ('left', '왼쪽', [TITLE, LEAD, LIST('items', '항목', [S('title', '제목'), TX('text', '설명')], summary='{{fields.title}}')]),
        OBJ('right', '오른쪽', [TITLE, LEAD, STRS('items', '항목')]),
    ]),
    'partner_contact': block('partner_contact', '제휴 문의 띠', [TITLE, TX('text', '설명'), S('mail_button', '메일 버튼 글자'),
                                                             S('form_button', '신청서 버튼 글자'), S('form_label', '신청서 관심 분야')]),
    'form_fields': block('form_fields', '신청서 항목 안내', [TITLE, LEAD, TONE,
                                                       LIST('items', '항목', [S('name', '항목 이름'), B('required', '필수'), S('help', '작은 설명')], summary='{{fields.name}}'),
                                                       S('button', '버튼 글자')]),
    'doc': block('doc', '긴 문서 (방침·고지)', [
        TX('body', '본문', '“## 제목” 줄은 소제목, “- ”로 시작하는 줄은 목록, 빈 줄은 문단 나눔입니다. 링크는 [글자](주소)로 적습니다.'),
        B('company', '아래에 회사 정보 표 넣기'), S('company_title', '회사 정보 제목'),
    ]),
    'text_block': block('text_block', '글 섹션', [TITLE, LEAD, MORE, TONE, ANCHOR,
                                                  TX('text', '본문', '빈 줄로 문단을 나눕니다. 링크는 [글자](주소), 굵게는 **글자**'), BUTTON()]),
}

GENERIC = ['text_block', 'cards', 'steps', 'card_grid', 'photo_band', 'intl', 'faq_home', 'cta_row', 'cband']
PAGE_TYPES = {
    'home': ['hero_slider', 'quick_menu', 'marquee', 'do_dont', 'field_tiles', 'program_tiles', 'flow', 'network_preview', 'intl', 'faq_home', 'contact_home'],
    'about': ['page_hero', 'card_grid', 'company_info', 'cband'],
    'medical': ['page_hero', 'field_cards', 'access', 'cta_row', 'cband'],
    'care': ['page_hero', 'program_list', 'cband'],
    'network': ['page_hero', 'network', 'cband'],
    'partners': ['page_hero', 'partner_types', 'steps', 'two_lists', 'partner_contact'],
    'consultation': ['page_hero', 'steps', 'form_fields', 'cband'],
    'privacy': ['page_hero', 'doc'],
    'notice': ['page_hero', 'doc'],
    'field': ['photo_hero', 'ways', 'services', 'photo_band', 'cards', 'steps', 'guide', 'faq_more', 'cband'],
    'program': ['photo_hero', 'ways', 'guide', 'step_cards', 'cards', 'facts', 'journey', 'program_links', 'cband'],
}
PAGES = [('home', '홈', 'index.html'), ('about', '회사소개', 'about.html'), ('medical', '진료 분야 목록', 'medical.html'),
         ('care', '케어 프로그램 목록', 'care.html'), ('network', '협력 네트워크', 'network.html'), ('partners', '제휴 안내', 'partners.html'),
         ('consultation', '상담 안내', 'consultation.html'), ('privacy', '개인정보처리방침', 'privacy.html'), ('notice', '의료서비스 관련 고지', 'medical-notice.html')]


def types_for(kind):
    names = list(dict.fromkeys(PAGE_TYPES[kind] + GENERIC))
    return [BLOCKS[n] for n in names]


def SECTIONS(kind):
    return {'label': '섹션 (위에서부터 화면 순서)', 'name': 'sections', 'widget': 'list', 'types': types_for(kind), 'collapsed': True,
            'hint': '끌어서 순서를 바꾸고, [추가]로 새 섹션을 넣습니다. 잠시 내릴 때는 섹션 안의 "이 섹션 숨기기"를 켭니다.'}


SEO = OBJ('seo', '검색 결과에 보이는 글', [S('title', '페이지 제목 (브라우저 탭)'), TX('description', '페이지 설명 (검색 결과 아래 글)')], collapsed=True)


def config():
    field_fields = [
        S('id', '영문 이름 (주소)', '영문 소문자와 - 만. 페이지 주소가 medical-<이름>.html 이 됩니다. 만든 뒤에는 바꾸지 마세요.', req=True,
          pattern=['^[a-z0-9-]+$', '영문 소문자, 숫자, - 만 쓸 수 있습니다']),
        N('order', '순서', '메뉴와 카드에 나오는 순서 (작은 숫자가 먼저)'),
        B('hidden', '사이트에서 숨기기'),
        S('ko', '이름', req=True), S('en', '영문 이름', req=True),
        PHOTO('photo', '대표 사진 (첫 화면·홈 카드·목록 카드)', req=True),
        S('form_label', '신청서 관심 분야', '상담 버튼을 누를 때 신청서에 넘길 분야 이름'),
        S('tile_line', '홈 카드 한 줄'), TX('index_text', '진료 분야 목록 카드 설명'),
        SEO, SECTIONS('field'),
    ]
    program_fields = [
        S('id', '영문 이름 (주소)', '영문 소문자와 - 만. 페이지 주소가 care-<이름>.html 이 됩니다. 만든 뒤에는 바꾸지 마세요.', req=True,
          pattern=['^[a-z0-9-]+$', '영문 소문자, 숫자, - 만 쓸 수 있습니다']),
        N('order', '순서'), B('hidden', '사이트에서 숨기기'),
        S('ko', '이름', req=True), S('en', '영문 이름', req=True),
        PHOTO('photo', '대표 사진', req=True),
        S('form_label', '신청서 관심 분야'),
        S('tile_tag', '홈 카드 사진 위 작은 글 (기간 등)'), S('tile_line', '홈 카드 한 줄'),
        S('index_line', '케어 프로그램 목록 한 줄'), S('index_meta', '케어 프로그램 목록 오른쪽 작은 글'),
        SEO, SECTIONS('program'),
    ]
    settings_fields = [
        OBJ('site', '사이트', [S('name', '브랜드 표기'), S('url', '사이트 주소'), S('theme_color', '휴대폰 주소창 색'),
                              TX('org_description', '검색엔진용 회사 소개 한 줄'),
                              STRS('keep_together', '휴대폰에서 줄이 바뀌면 안 되는 말', '띄어쓰기 그대로 적습니다. 예: 한 곳만')], collapsed=True),
        OBJ('contact', '연락처', [S('email', '이메일'), S('phone', '전화 (화면 표기)'), S('phone_tel', '전화 (+82로 시작, 띄어쓰기 없이)'),
                                S('phone_intl', '전화 (해외 표기)'), S('phone_schema', '전화 (검색엔진용)'),
                                S('form_url', '상담 신청서 주소 (구글 폼)'), S('partner_mail', '제휴 문의 메일 주소 (mailto:)')], collapsed=True),
        OBJ('company', '회사 정보', [S('legal_name', '법인명'), S('ceo', '대표'), S('biz_no', '사업자등록번호'), S('tourism_no', '외국인환자 유치업 등록번호'),
                                   S('address', '주소', '정해지면 적습니다. 바닥글·회사소개·고지에 나옵니다.')], collapsed=True),
        OBJ('nav', '메뉴 이름', [S(k, l) for k, l in [('skip', '본문 바로가기'), ('about', '회사소개'), ('medical', '진료 분야'), ('care', '케어 프로그램'),
                                                    ('network', '협력 네트워크'), ('partners', '제휴 안내'), ('consultation', '상담 안내'), ('privacy', '개인정보처리방침'),
                                                    ('notice', '의료서비스 관련 고지'), ('cta', '상담 예약 버튼'), ('fab_call', '오른쪽 떠 있는 전화 버튼'),
                                                    ('fab_top', '맨 위로 버튼'), ('mbar_call', '휴대폰 아래 전화 버튼')]], collapsed=True),
        OBJ('footer', '바닥글', [S('tagline', '한 줄'), S('sub', '영문 한 줄'), TX('notice', '고지 문장'), S('copyright', '저작권 표기')], collapsed=True),
        OBJ('appt', '상담 예약 카드', [S('title', '카드 제목'), LIST('rows', '안내 줄', [S('k', '항목'), TX('v', '내용')], summary='{{fields.k}}'),
                                     S('form_note', '버튼 아래 작은 글'), S('line_label', '전화 앞 글자'), S('intl_en', '해외 안내 (영문)'), S('intl_zh', '해외 안내 (중문)')], collapsed=True),
        OBJ('cband', '상담 띠 기본값', [S('label', '작은 영문 머리글'), STRS('promises', '기본 안내 줄', text=True)], collapsed=True),
    ]
    region_fields = [LIST('regions', '지역', [
        S('area', '지도 위치 (행정구역)', '지도에 점을 찍을 곳. 예: 서울 강남구, 경기 성남시 분당구. 화면에는 나오지 않습니다.'),
        S('name', '화면에 보이는 시·도', '시·도까지만. 구·동 이름과 병원 이름은 적지 않습니다.'),
        S('en', '영문 시·도'),
        {'label': '받을 수 있는 분야', 'name': 'fields', 'widget': 'relation', 'collection': 'fields', 'value_field': 'id',
         'search_fields': ['ko'], 'display_fields': ['ko'], 'multiple': True, 'required': False},
        TX('note', '지역 카드 한 줄', '받으실 수 있는 것만 적습니다. 장비·규모·인증·재단처럼 병원을 알아볼 수 있는 내용은 적지 않습니다.'),
        B('hidden', '숨기기'),
    ], summary='{{fields.name}} · {{fields.area}}', hint='같은 시·도의 설명은 한 카드에 모여서 보입니다.')]

    pages = {'name': 'pages', 'label': '페이지', 'label_singular': '페이지', 'editor': {'preview': False}, 'files': []}
    for key, label, url in PAGES:
        pages['files'].append({'name': key, 'label': label, 'file': f'content/pages/{key}.yml', 'preview_path': '' if url == 'index.html' else url,
                               'fields': [SEO, SECTIONS(key)]})
    return {
        'app_title': 'atInc 홈페이지 관리',
        'backend': {'name': 'github', 'repo': REPO, 'branch': 'main', 'cms_label_prefix': 'cms/',
                    'commit_messages': {'create': '관리자: {{collection}} 「{{slug}}」 추가', 'update': '관리자: {{collection}} 「{{slug}}」 수정',
                                        'delete': '관리자: {{collection}} 「{{slug}}」 삭제', 'uploadMedia': '관리자: 사진 올림 {{path}}',
                                        'deleteMedia': '관리자: 사진 지움 {{path}}'}},
        'publish_mode': 'simple',  # 저장하면 바로 GitHub에 반영 (승인 단계를 쓰려면 'editorial_workflow')
        'media_folder': 'static/uploads',
        'public_folder': '/uploads',
        'site_url': 'https://atinc.co.kr',
        'output': {'omit_empty_optional_fields': True},
        'slug': {'encoding': 'ascii', 'clean_accents': True},
        'collections': [
            {'name': 'settings', 'label': '사이트 설정', 'editor': {'preview': False},
             'files': [{'name': 'settings', 'label': '사이트 설정 (연락처·회사 정보·메뉴·바닥글·상담 카드)', 'file': 'content/settings.yml', 'fields': settings_fields}]},
            pages,
            {'name': 'fields', 'label': '진료 분야', 'label_singular': '진료 분야', 'folder': 'content/fields', 'format': 'yml', 'extension': 'yml',
             'create': True, 'delete': True, 'identifier_field': 'ko', 'slug': '{{id}}', 'summary': '{{order}}. {{ko}} ({{en}})',
             'sortable_fields': ['order', 'ko'], 'preview_path': 'medical-{{id}}.html', 'editor': {'preview': False}, 'fields': field_fields},
            {'name': 'programs', 'label': '케어 프로그램', 'label_singular': '케어 프로그램', 'folder': 'content/programs', 'format': 'yml', 'extension': 'yml',
             'create': True, 'delete': True, 'identifier_field': 'ko', 'slug': '{{id}}', 'summary': '{{order}}. {{ko}} ({{en}})',
             'sortable_fields': ['order', 'ko'], 'preview_path': 'care-{{id}}.html', 'editor': {'preview': False}, 'fields': program_fields},
            {'name': 'regions', 'label': '협력 지역', 'editor': {'preview': False},
             'files': [{'name': 'regions', 'label': '협력 지역 (지도·지역 카드)', 'file': 'content/regions.yml', 'fields': region_fields}]},
        ],
    }


# ------------------------------------------------------------------ check: every value in content has an input
def check(cfg):
    problems = []

    def walk(val, fields, path):
        if isinstance(val, dict):
            names = {f['name']: f for f in fields}
            for k, v in val.items():
                if k == 'type':
                    continue
                if k not in names:
                    problems.append(f'{path}.{k}: 입력 칸 없음')
                    continue
                walk_field(v, names[k], f'{path}.{k}')

    def walk_field(v, f, path):
        w = f.get('widget')
        if w == 'object':
            if not isinstance(v, dict):
                problems.append(f'{path}: 묶음이어야 함'); return
            walk(v, f['fields'], path)
        elif w == 'list':
            if not isinstance(v, list):
                problems.append(f'{path}: 목록이어야 함'); return
            for i, item in enumerate(v):
                if 'types' in f:
                    t = {x['name']: x for x in f['types']}.get(item.get('type'))
                    if not t:
                        problems.append(f'{path}[{i}]: 이 페이지에서 쓸 수 없는 섹션 {item.get("type")}'); continue
                    walk(item, t['fields'], f'{path}[{i}:{item["type"]}]')
                elif 'fields' in f:
                    walk(item, f['fields'], f'{path}[{i}]')
                elif 'field' in f:
                    walk_field(item, f['field'], f'{path}[{i}]')
                elif isinstance(item, (dict, list)):
                    problems.append(f'{path}[{i}]: 단순 목록인데 묶음 값')
        elif w == 'relation':
            pass
        elif isinstance(v, (dict, list)) and w not in ('relation',):
            problems.append(f'{path}: {w} 칸인데 묶음/목록 값')

    cols = {c['name']: c for c in cfg['collections']}
    for c in cfg['collections']:
        if 'files' in c:
            for fdef in c['files']:
                p = os.path.join(ROOT, fdef['file'])
                walk(yaml.safe_load(open(p, encoding='utf-8')), fdef['fields'], fdef['file'])
        else:
            for p in sorted(glob.glob(os.path.join(ROOT, c['folder'], '*.yml'))):
                walk(yaml.safe_load(open(p, encoding='utf-8')), c['fields'], os.path.relpath(p, ROOT))
    # every block has a template, every template has a block
    tpl = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(ROOT, 'templates', 'sections', '*.html'))}
    for n in BLOCKS:
        if n not in tpl:
            problems.append(f'블록 {n}: templates/sections/{n}.html 없음')
    for n in tpl - set(BLOCKS):
        problems.append(f'템플릿 {n}: 관리자 입력 칸 정의 없음')
    return problems


def main():
    cfg = config()
    probs = check(cfg)
    for p in probs:
        print('✗', p)
    if '--check' not in sys.argv:
        os.makedirs(os.path.join(ROOT, 'static', 'admin'), exist_ok=True)
        with open(os.path.join(ROOT, 'static', 'admin', 'config.yml'), 'w', encoding='utf-8') as f:
            f.write('# 자동으로 만들어지는 파일입니다. tools/admin_config.py 를 고친 뒤 다시 실행하세요.\n')
            class NoAlias(yaml.SafeDumper):
                def ignore_aliases(self, data):
                    return True
            yaml.dump(cfg, f, Dumper=NoAlias, allow_unicode=True, sort_keys=False, width=200)
        print('static/admin/config.yml 저장')
    print('검사:', '문제 없음' if not probs else f'{len(probs)}건')
    sys.exit(1 if probs else 0)


if __name__ == '__main__':
    main()
