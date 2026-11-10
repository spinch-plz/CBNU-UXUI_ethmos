"""글리프 아웃라인 생성: 글꼴 파일 → 문자별 SVG path (1000 em 단위, 베이스라인 y=0, 아래가 +).
사용: python3 mkglyphs.py  → glyphs.json
Pretendard(가변)는 굵기별로 인스턴스를 만들어 쓰고, 격동명조는 glyphs_gyeokdong.json(피그마 아웃라인)이 있으면 그것을, 없으면 대체 서체(Noto Serif CJK)를 쓴다."""
import json, os, re
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen

aud = json.load(open('data/audit.json'))
ASCII = ''.join(chr(i) for i in range(32, 127))
EXTRA = '°·×—→㎍㎥²³³…‘’“”ㆍ'
VOCAB = '좋음보통나쁨매우나쁨낮음높음없음약함심함'
tmpl = open('src/template.html', encoding='utf8').read()
TM = set(c for c in tmpl if 0xAC00 <= ord(c) <= 0xD7A3 or c in EXTRA)

def num(v):
    r = round(v)
    return str(r)

def path_of(gs, name, upm):
    sp = SVGPathPen(gs, ntos=num)
    k = 1000.0 / upm
    gs[name].draw(TransformPen(sp, (k, 0, 0, -k, 0, 0)))
    return sp.getCommands()

def compact(d):
    d = re.sub(r'([MLQCHVZ])\s*', r'\1', d)
    d = re.sub(r' (?=-)', '', d)
    return d

def rel(d):
    """절대좌표 path → 상대좌표(작은 숫자)로 바꿔 용량을 줄인다"""
    t = re.findall(r'[MLHVQCZ]|-?\d+(?:\.\d+)?', d); i = 0; cmd = None; cx = cy = sx = sy = 0; out = []
    n = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'Q': 4, 'C': 6, 'Z': 0}
    fmt = lambda v: str(int(round(v)))
    def join(c, vals):
        r = c
        for k, v in enumerate(vals):
            x = fmt(v)
            r += (' ' if k and not x.startswith('-') else '') + x
        return r
    while i < len(t):
        if t[i] in n: cmd = t[i]; i += 1
        if cmd == 'Z': out.append('z'); cx, cy = sx, sy; continue
        v = [float(x) for x in t[i:i + n[cmd]]]; i += n[cmd]
        if cmd == 'M': out.append(join('m', [v[0] - cx, v[1] - cy])); cx, cy = v; sx, sy = v; cmd = 'L'
        elif cmd == 'L': out.append(join('l', [v[0] - cx, v[1] - cy])); cx, cy = v
        elif cmd == 'H': out.append(join('h', [v[0] - cx])); cx = v[0]
        elif cmd == 'V': out.append(join('v', [v[0] - cy])); cy = v[0]
        elif cmd == 'Q': out.append(join('q', [v[0] - cx, v[1] - cy, v[2] - cx, v[3] - cy])); cx, cy = v[2], v[3]
        elif cmd == 'C': out.append(join('c', [v[0] - cx, v[1] - cy, v[2] - cx, v[3] - cy, v[4] - cx, v[5] - cy])); cx, cy = v[4], v[5]
    r = ''.join(out)
    return re.sub(r'(?<=[a-z])\s+', '', r)

def build(font, chars, upm):
    gs = font.getGlyphSet(); cm = font.getBestCmap(); hm = font['hmtx']
    out = {}
    for c in sorted(chars):
        if ord(c) not in cm: continue
        n = cm[ord(c)]
        out[c] = [round(hm[n][0] * 1000.0 / upm), rel(path_of(gs, n, upm))]
    return out

res = {}
# --- Pretendard (가변) ---
pf = TTFont('fonts/pretendard-sub.woff2'); upm = pf['head'].unitsPerEm
res['pret'] = {'m': [round(pf['hhea'].ascent * 1000 / upm), round(-pf['hhea'].descent * 1000 / upm)], 'w': {}}
want = {}
for k, v in aud.items():
    f, w = k.split(':')
    if f == 'pret': want[int(w)] = set(v)
for w in (300, 400, 500, 600, 700): want.setdefault(w, set())
CRAWL = [l.strip() for l in open('data/crawl_missed.txt', encoding='utf8') if l.strip()] if os.path.exists('data/crawl_missed.txt') else []
for x in CRAWL:
    m = re.match(r'(pret|serif)(\d{3})(.)$', x)
    if m and m.group(1) == 'pret': want.setdefault(int(m.group(2)), set()).add(m.group(3))
for w in want:
    s = set(want[w]) | set(ASCII) | set(VOCAB) | set(EXTRA)
    if w == 300: s = set(want[w]) | set(ASCII) | set(EXTRA)
    if w != 300: s |= TM
    inst = instancer.instantiateVariableFont(TTFont('fonts/pretendard-sub.woff2'), {'wght': w}, inplace=False)
    res['pret']['w'][w] = build(inst, s, upm)
    print('pret', w, len(res['pret']['w'][w]))
# --- 격동명조 ---
SER = {400: 'fonts/kr-Regular.otf', 600: 'fonts/kr-SemiBold.otf', 700: 'fonts/kr-Bold.otf'}
sets = json.load(open('data/sheet_sets.json'))
extra_ser = set(ASCII) | set(VOCAB) | set('°·×')
gk = json.load(open('data/glyphs_gyeokdong.json')) if os.path.exists('data/glyphs_gyeokdong.json') else None
res['serif'] = {'m': None, 'w': {}, 'src': 'figma' if gk else 'stand-in'}
if gk: res['serif']['raw'] = 1
for w, fn in SER.items():
    k = TTFont(fn); u = k['head'].unitsPerEm
    if res['serif']['m'] is None: res['serif']['m'] = gk['m'] if gk else [round(k['hhea'].ascent * 1000 / u), round(-k['hhea'].descent * 1000 / u)]
    s = set(sets[str(w)]) | (extra_ser if w != 700 else set(ASCII) | set('°·×'))
    if w == 400: s |= set(aud.get('serif:500', ''))
    s |= set(aud.get('serif:%d' % w, ''))
    s |= {x[8:] for x in CRAWL if x.startswith('serif%d' % w)}
    g = build(k, s, u)
    if gk:  # 피그마에서 뽑은 격동명조 아웃라인이 있으면 대체 서체 글리프 위에 덮어쓴다
        g.update({c: [v[0], rel(v[1]) if v[1] else ''] for c, v in gk['w'][str(w)].items()})
    res['serif']['w'][w] = g
    print('serif', w, len(g))
json.dump(res, open('data/glyphs.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('data/glyphs.json', os.path.getsize('data/glyphs.json') // 1024, 'KB')
