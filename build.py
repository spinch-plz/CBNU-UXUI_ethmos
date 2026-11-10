#!/usr/bin/env python3
"""src/ + data/ → dist/index.html (단일 파일, 외부 요청·글꼴 파일 없음).
사용: python3 build.py          (파이썬 3 표준 라이브러리만 사용)
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
rd = lambda p: open(os.path.join(ROOT, p), encoding='utf8').read()

t = rd('src/template.html')
t = t.replace('{{OTX_CSS}}', rd('src/ot.css'))
t = t.replace('{{OTX_JS}}', rd('src/ot.js').replace('{{GLYPHS_JSON}}', rd('data/glyphs.json')))
t = t.replace('{{ICONS_JSON}}', json.dumps(json.load(open(os.path.join(ROOT, 'data/icons.json'), encoding='utf8')), separators=(',', ':'), ensure_ascii=False))
assert '{{' not in t.split('<style>')[0] and '{{OTX' not in t and '{{ICONS' not in t and '{{GLYPHS' not in t, '치환되지 않은 자리표시자가 남아 있어요'

# 템플릿은 <title> … </style> 까지가 head, 그 뒤가 body인 조각 형태
head, body = t.split('</style>', 1)
head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
shell = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#e8eef0">
<meta name="description" content="한눈에 보는 비염 — 에스모스(Ethmos) 모바일 앱 프로토타입">
<meta name="robots" content="noindex,nofollow">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="에스모스">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
'''
html = shell + head + '</style>\n</head>\n<body>\n' + body.lstrip('\n') + '\n</body>\n</html>\n'

dist = os.path.join(ROOT, 'dist')
shutil.rmtree(dist, ignore_errors=True)
shutil.copytree(os.path.join(ROOT, 'public'), dist)
open(os.path.join(dist, 'index.html'), 'w', encoding='utf8').write(html)
print('dist/index.html', len(html.encode('utf8')) // 1024, 'KB')
