#!/usr/bin/env python3
"""편집용 페이지(site/admin/edit/)의 표시가 모두 실제 내용을 가리키는지 확인합니다.

- data-e   (글): 내용 파일의 그 위치에 글자 값이 있고, 화면 글자와 같아야 합니다
- data-img (사진): 그 위치에 사진 묶음(src)이 있어야 합니다
- data-item(항목): 그 위치가 목록의 한 칸이어야 합니다

    python3 tools/qa/edit_marks.py [site 폴더]
"""
import glob
import html
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'site')
CACHE = {}


def content(file_key):
    if file_key not in CACHE:
        CACHE[file_key] = json.load(open(os.path.join(ROOT, 'content', file_key + '.json'), encoding='utf-8'))
    return CACHE[file_key]


def resolve(path):
    fk, _, dotted = path.partition('#')
    cur = content(fk)
    parent, key = None, None
    for part in dotted.split('.') if dotted else []:
        parent, key = cur, part
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            cur = cur[part]
    return cur, parent, key


def norm(t):
    t = html.unescape(t).replace(' ', ' ')
    return re.sub(r'\s+', ' ', t).strip()


def plain(v, kind):
    v = str(v)
    if kind == 'rich':
        v = v.replace('\n', '')
    if kind == 'paras':
        v = re.sub(r'\s*\n\s*\n\s*', '', v)   # 문단 사이 빈 줄은 화면에서 문단 나눔으로만 남습니다
    if kind in ('rich', 'regions', 'paras'):
        v = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'\1', v).replace('**', '')
    return norm(v)


class Collector(HTMLParser):
    VOID = {'img', 'br', 'meta', 'link', 'input', 'hr', 'source', 'wbr', 'area', 'base', 'col', 'embed', 'param', 'track'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.marks = [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'data-img' in a:
            self.marks.append(('img', a['data-img'], None, None))
        if 'data-item' in a:
            self.marks.append(('item', a['data-item'], None, None))
        if tag in self.VOID:
            return
        rec = {'tag': tag, 'e': a.get('data-e'), 'k': a.get('data-k') or 'text', 'text': []}
        self.stack.append(rec)

    def handle_endtag(self, tag):
        while self.stack:
            rec = self.stack.pop()
            txt = ''.join(rec['text'])
            if self.stack:
                self.stack[-1]['text'].append(txt)
            if rec['e']:
                self.marks.append(('e', rec['e'], rec['k'], txt))
            if rec['tag'] == tag:
                break

    def handle_data(self, data):
        if self.stack:
            self.stack[-1]['text'].append(data)


def main():
    problems, counts = [], {'e': 0, 'img': 0, 'item': 0}
    for f in sorted(glob.glob(os.path.join(SITE, 'admin', 'edit', '*.html'))):
        src = open(f, encoding='utf-8').read()
        body = src[src.index('<main'):src.rindex('</footer>')]
        c = Collector()
        c.feed(body)
        name = os.path.basename(f)
        for kind, path, k, txt in c.marks:
            counts[kind] += 1
            try:
                val, parent, key = resolve(path)
            except (KeyError, IndexError, ValueError, FileNotFoundError) as ex:
                # 빈 칸(값이 아직 없는 글자 자리)은 괜찮습니다: 부모 묶음까지는 있어야 합니다
                head, _, last = path.rpartition('.')
                try:
                    par, _, _ = resolve(head) if '#' in head else (None, None, None)
                except Exception:
                    par = None
                if kind == 'e' and isinstance(par, dict) and not norm(txt):
                    counts['e'] += 0
                    continue
                problems.append(f'{name}: {path} → 내용에 없음 ({ex.__class__.__name__})')
                continue
            if kind == 'img':
                if not isinstance(val, dict) or 'src' not in val:
                    problems.append(f'{name}: {path} → 사진 묶음이 아님')
            elif kind == 'item':
                if not isinstance(parent, list):
                    problems.append(f'{name}: {path} → 목록 칸이 아님')
            else:
                if not isinstance(val, (str, int, float)):
                    problems.append(f'{name}: {path} → 글자 값이 아님')
                    continue
                if k == 'lines':
                    want = norm(str(val).replace('\n', ''))
                elif k == 'doc':
                    want = None
                else:
                    want = plain(val, k)
                got = norm(txt)
                if k == 'regions':
                    want = want.split('{regions}')[0]
                    got = got[:len(want)]
                if want is not None and want != got:
                    problems.append(f'{name}: {path} → 화면 "{got[:40]}" ≠ 내용 "{want[:40]}"')
    for p in problems[:40]:
        print('✗', p)
    print(f'표시: 글 {counts["e"]} · 사진 {counts["img"]} · 항목 {counts["item"]} / 문제 {len(problems)}건')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
