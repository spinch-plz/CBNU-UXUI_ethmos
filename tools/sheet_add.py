"""Figma 'glyphs Bd 10' 시트에 새로 붙인 글자(인덱스 125~)만 골라 격동고딕 10 Bd(700) 글리프에 합칩니다.
사용: python3 tools/sheet_add.py Bd.svg      (Bd 프레임을 SVG로 내보낸 파일 1개. Lt·Sb는 다시 안 내보내도 돼요)
- 칸 위치(열/행) → 글자 순서는 sheet2glyphs.py와 같고, 맨 뒤에 EXTRA 글자가 이어져요."""
import sys, json
sys.path.insert(0, 'tools')
from sheet2glyphs import ASCII, BASE, COLS, PW, PH, parse, bbox, conv
EXTRA = '나낮맑매쁨우절좋통환높'
def run(fn):
    cells, paths = parse(open(fn, encoding='utf8').read())
    cl = list(dict.fromkeys(BASE[700] + ASCII))
    EXTRA_AT = 125   # Figma 시트에서 추가 글자를 놓은 첫 칸(인덱스). 기존 글자는 0~123
    owned = {i: [] for i in range(len(cells))}
    for d in paths:
        x0, y0, x1, y1 = bbox(d); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for i, (rx, ry, rw, rh) in enumerate(cells):
            if rx - 1 <= cx <= rx + rw + 1 and ry - 1 <= cy <= ry + rh + 1: owned[i].append(d); break
    by_idx = {}
    for i, (rx, ry, rw, rh) in enumerate(cells):
        by_idx[round((ry - 20) / PH) * COLS + round((rx - 20) / PW)] = i
    bl = []
    for ch in 'HIEZ':
        k = cl.index(ch)
        if k in by_idx and owned[by_idx[k]]:
            i = by_idx[k]; bl.append(max(bbox(d)[3] for d in owned[i]) - cells[i][1])
    if not bl: raise SystemExit('H I E Z 기준 글자를 못 찾았어요')
    base = sorted(bl)[len(bl) // 2]
    got = {}
    for j, ch in enumerate(EXTRA):
        k = EXTRA_AT + j
        if k not in by_idx: print('칸 없음', ch); continue
        i = by_idx[k]; rx, ry, rw, rh = cells[i]
        dd = ''.join(conv(d, rx, ry + base)[0] for d in owned[i])
        if not dd: print('윤곽 없음(글꼴이 10 Bd로 바뀌었는지 확인)', ch); continue
        got[ch] = [round(rw * 10), dd]
    return got
if __name__ == '__main__':
    got = run(sys.argv[1])
    for path, pick in (('data/glyphs.json', lambda d: d['serif']['w']), ('data/glyphs_gyeokdong.json', lambda d: d['w'])):
        try: d = json.load(open(path, encoding='utf8'))
        except FileNotFoundError: continue
        w = pick(d); key = '700' if '700' in w else 700
        w[key].update(got)
        json.dump(d, open(path, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    print('합친 글자:', ''.join(got), '(', len(got), '/', len(EXTRA), ')')
