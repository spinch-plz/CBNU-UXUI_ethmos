"""Figma '글리프 시트'(격동명조로 글꼴을 바꾼 뒤 SVG로 내보낸 3개 프레임) → glyphs_gyeokdong.json
사용: python3 sheet2glyphs.py Lt.svg Sb.svg Bd.svg
- 칸(rect)의 폭 = 글자 advance, 칸 높이 = 자동 줄높이(100px 기준), 'H I E Z' 아래끝 = 베이스라인.
- 칸 위치(열/행)로 글자를 찾으므로 SVG 안의 id·순서는 필요 없음."""
import re, sys, json, math
ASCII = ''.join(chr(33 + i) for i in range(94))
BASE = {int(k): v for k, v in json.load(open('data/sheet_sets.json', encoding='utf8')).items()}
COLS, PW, PH = 20, 190, 190
def chars_of(w): return list(dict.fromkeys(BASE[w] + ASCII))
def attrs(tag): return dict(re.findall(r'([\w:-]+)="([^"]*)"', tag))
def tok(d): return re.findall(r'[MLHVCQSTAZmlhvcqstaz]|-?\d*\.?\d+(?:e-?\d+)?', d)
def conv(d, ox, oy):
    """path d(절대좌표) → 1000em 기준 정수 path, (ox,oy)=글자 원점(SVG 좌표). 반환 (d, ymax_svg)"""
    t = tok(d); i = 0; out = []; cmd = None; x = y = 0; ymax = -1e9; ymin = 1e9
    fx = lambda v: str(round((v - ox) * 10)); fy = lambda v: str(round((v - oy) * 10))
    n = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'Q': 4, 'Z': 0}
    while i < len(t):
        if re.match(r'[A-Za-z]', t[i]): cmd = t[i]; i += 1
        if cmd in ('Z', 'z'): out.append('Z'); continue
        if cmd not in n: raise SystemExit('unsupported path command ' + cmd)
        k = n[cmd]; v = list(map(float, t[i:i + k])); i += k
        if cmd == 'H': v = [v[0], y]; c = 'L'
        elif cmd == 'V': v = [x, v[0]]; c = 'L'
        else: c = cmd
        pts = [(v[j], v[j + 1]) for j in range(0, len(v), 2)]
        for px, py in pts: ymax = max(ymax, py); ymin = min(ymin, py)
        x, y = pts[-1]
        out.append(c + ' '.join(f'{fx(px)} {fy(py)}' for px, py in pts))
        if cmd == 'M': cmd = 'L'
    return re.sub(r' (?=-)', '', ''.join(out)), ymax, ymin
def parse(svg):
    cells = []; paths = []
    for m in re.finditer(r'<(rect|path)\b[^>]*>', svg):
        a = attrs(m.group(0))
        if m.group(1) == 'rect' and a.get('fill-opacity', '').startswith('0.0'):
            mt = re.search(r'translate\(\s*(-?[\d.]+)[ ,]+(-?[\d.]+)', a.get('transform', ''))
            tx, ty = (float(mt.group(1)), float(mt.group(2))) if mt else (float(a.get('x', 0)), float(a.get('y', 0)))
            cells.append((tx, ty, float(a['width']), float(a['height'])))
        elif m.group(1) == 'path' and a.get('fill', '').lower() in ('black', '#000', '#000000'):
            paths.append(a['d'])
    return cells, paths
def bbox(d):
    t = tok(d); xs = []; ys = []; i = 0; cmd = None; x = y = 0
    n = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'Q': 4, 'Z': 0}
    while i < len(t):
        if re.match(r'[A-Za-z]', t[i]): cmd = t[i]; i += 1
        if cmd in ('Z', 'z'): continue
        k = n[cmd]; v = list(map(float, t[i:i + k])); i += k
        if cmd == 'H': v = [v[0], y]
        elif cmd == 'V': v = [x, v[0]]
        for j in range(0, len(v), 2): xs.append(v[j]); ys.append(v[j + 1])
        x, y = xs[-1], ys[-1]
        if cmd == 'M': cmd = 'L'
    return min(xs), min(ys), max(xs), max(ys)
def run(files):
    res = {'w': {}, 'm': None, 'space': None}
    asc = []
    for w, fn in zip((400, 600, 700), files):
        cells, paths = parse(open(fn, encoding='utf8').read())
        cl = chars_of(w); got = {}; heights = []
        owned = {i: [] for i in range(len(cells))}
        for d in paths:
            x0, y0, x1, y1 = bbox(d); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            for i, (rx, ry, rw, rh) in enumerate(cells):
                if rx - 1 <= cx <= rx + rw + 1 and ry - 1 <= cy <= ry + rh + 1: owned[i].append(d); break
        # 칸 → 글자
        by_idx = {}
        for i, (rx, ry, rw, rh) in enumerate(cells):
            col = round((rx - 20) / PW); row = round((ry - 20) / PH); by_idx[row * COLS + col] = i
        # 베이스라인: 아래가 평평한 글자들의 아래끝
        bl = []
        for ch in 'HIEZ':
            if ch in cl and cl.index(ch) in by_idx:
                i = by_idx[cl.index(ch)]; ds = owned[i]
                if ds: bl.append(max(bbox(d)[3] for d in ds) - cells[i][1])
        if not bl: raise SystemExit('baseline reference glyphs (H I E Z) missing in ' + fn)
        base = sorted(bl)[len(bl) // 2]
        H0 = sorted(c[3] for c in cells)[len(cells) // 2]
        asc.append((base, H0))
        for k, ch in enumerate(cl):
            if k not in by_idx: continue
            i = by_idx[k]; rx, ry, rw, rh = cells[i]
            ds = owned[i]; dd = ''
            for d in ds: dd += conv(d, rx, ry + base)[0]
            got[ch] = [round(rw * 10), dd]
        # 공백 advance = ('가 가' 폭) − ('가가' 폭)
        nrow = math.ceil(len(cl) / COLS)
        w0 = by_idx.get(nrow * COLS + 0); w1 = by_idx.get(nrow * COLS + 4)
        if w0 is not None and w1 is not None and res['space'] is None: res['space'] = round((cells[w1][2] - cells[w0][2]) * 10)
        got[' '] = [res['space'] or 250, '']
        res['w'][w] = got
        print(w, 'glyphs', len(got), 'baseline', base, 'cell h', H0, 'missing', [c for c in cl if c not in got][:10])
    base, H0 = asc[0]
    res['m'] = [round(base * 10), round((H0 - base) * 10)]
    return res
if __name__ == '__main__':
    r = run(sys.argv[1:4])
    json.dump(r, open('data/glyphs_gyeokdong.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    print('glyphs_gyeokdong.json  m=', r['m'], 'space=', r['space'])
