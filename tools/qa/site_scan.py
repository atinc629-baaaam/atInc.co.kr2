#!/usr/bin/env python3
"""공개 전 문구 검사: 가격 표기, 과장 표현, 병원을 알아볼 수 있는 이름이 화면에 나오는지 확인합니다.

병원·재단 이름 같은 비공개 단어는 이 저장소에 적지 않습니다. 아래 둘 중 한 곳에 둡니다.
  - 환경변수 ATINC_PRIVATE_WORDS (쉼표로 구분) — GitHub Actions 비밀값(Secrets)으로 넣습니다
  - tools/qa/private-words.txt (한 줄에 하나, .gitignore 로 저장소에서 빠집니다)

    python3 tools/qa/site_scan.py [site 폴더]      # 문제가 있으면 종료 코드 1
"""
import glob
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'site')

# 누구나 봐도 되는 규칙: 과장·효과 단정 표현, 작업 흔적
PUBLIC_WORDS = ['최고', '완벽', '보장합', '효과 보장', '안전 보장', '여성 의료진', '[', '**', '관심 분야:', '\\', '(MEDICAL)', '(ABOUT)', 'PRIVÉ']


def private_words():
    words = [w.strip() for w in os.environ.get('ATINC_PRIVATE_WORDS', '').split(',') if w.strip()]
    p = os.path.join(HERE, 'private-words.txt')
    if os.path.exists(p):
        words += [w.strip() for w in open(p, encoding='utf-8') if w.strip() and not w.startswith('#')]
    return words


def main():
    priv = private_words()
    if not priv:
        print('※ 비공개 단어 목록이 없어 병원 이름 검사는 건너뜁니다 (ATINC_PRIVATE_WORDS 또는 tools/qa/private-words.txt)')
    problems = 0
    for f in sorted(glob.glob(os.path.join(SITE, '*.html'))):
        t = open(f, encoding='utf-8').read()
        t = re.sub(r'<script[\s\S]*?</script>', '', t)
        t = re.sub(r'<style[\s\S]*?</style>', '', t)
        t = re.sub(r'<title[\s\S]*?</title>', '', t)
        t = re.sub(r'<svg[\s\S]*?</svg>', '', t)
        txt = html.unescape(re.sub(r'<[^>]+>', '\n', t))
        lines = [x.strip() for x in txt.split('\n') if x.strip()]
        hits = []
        for x in lines:
            if re.search(r'\d[\d,]*\s*(원|만원|USD|\$)', x):
                hits.append(('가격 표기', x[:80]))
            for b in PUBLIC_WORDS:
                if b in x:
                    hits.append((b, x[:90]))
            for b in priv:
                if b in x:
                    hits.append(('비공개 단어', x[:90].replace(b, '■' * len(b))))
        # 예외: 개인정보처리방침의 'Google Forms)' 같은 고정 문구
        hits = [h for h in hits if not (os.path.basename(f) == 'privacy.html' and 'Google Forms' in h[1])]
        problems += len(hits)
        print(os.path.basename(f), len(lines), hits[:12])
    if problems:
        print(f'\n문제 {problems}건')
        sys.exit(1)
    print('\n문제 없음')


if __name__ == '__main__':
    main()
