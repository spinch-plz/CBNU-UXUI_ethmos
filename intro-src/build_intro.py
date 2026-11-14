#!/usr/bin/env python3
"""intro-src/index.template.html → public/intro/index.html (단일 파일, 외부 요청 없음)

사용:  pip install segno fonttools brotli
       python3 intro-src/build_intro.py [QR이 가리킬 주소]
- Pretendard 서브셋은 npm 패키지(pretendard@1.3.9)에서 받아 씁니다 (node/npm 필요, 첫 실행 때만 다운로드).
- QR 주소 기본값은 앱 프로토타입 주소입니다.
"""
import re, base64, subprocess, sys, os, glob, tempfile

URL = sys.argv[1] if len(sys.argv) > 1 else "https://spinch-plz.github.io/CBNU-UXUI_ethmos/"
URL_TEXT = URL.replace("https://", "").rstrip("/")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
tpl = open(f"{HERE}/index.template.html", encoding="utf-8").read()
svg = open(f"{HERE}/logo.svg", encoding="utf-8").read()
L1, L2 = re.findall(r' d="([^"]+)"', svg)

# ---- QR (오류정정 H, 가운데 로고 자리 비움)
import segno
m = [list(r) for r in segno.make(URL, error="h", micro=False).matrix]; n = len(m)
k = int(round(n * 0.26)); k += (n - k) % 2
a = (n - k) // 2; b = a + k
d = []
for y, row in enumerate(m):
    x = 0
    while x < n:
        if row[x] and not (a <= x < b and a <= y < b):
            s = x
            while x < n and row[x] and not (a <= x < b and a <= y < b): x += 1
            d.append(f"M{s} {y}h{x-s}v1h-{x-s}z")
        else: x += 1
sc = k * 0.80 / 199; lw = 124 * sc; lh = 199 * sc
tx = a + k / 2 - lw / 2; ty = a + k / 2 - lh / 2; pad = k * 0.06
qr = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 {n+2} {n+2}" shape-rendering="crispEdges" role="img" aria-label="앱 연결 QR코드">'
      f'<rect x="-1" y="-1" width="{n+2}" height="{n+2}" fill="#fff"/><path d="{"".join(d)}" fill="#0b4a50"/>'
      f'<rect x="{a+pad*.4}" y="{a+pad*.4}" width="{k-pad*.8}" height="{k-pad*.8}" rx="{k*.2}" fill="#fff"/>'
      f'<g transform="translate({tx} {ty}) scale({sc})" fill="#0b4a50"><path d="{L1}"/><path d="{L2}"/></g></svg>')

# ---- 글꼴: 화면에 쓰인 글자만 남긴 Pretendard 서브셋 (woff2 → base64)
tmp = tempfile.mkdtemp()
pkg = glob.glob(f"{ROOT}/intro-src/.pretendard/package/dist/public/static/Pretendard-Regular.otf")
if not pkg:
    os.makedirs(f"{ROOT}/intro-src/.pretendard", exist_ok=True)
    subprocess.check_call(["npm", "pack", "pretendard@1.3.9", "--silent"], cwd=f"{ROOT}/intro-src/.pretendard")
    subprocess.check_call("tar xzf pretendard-*.tgz", shell=True, cwd=f"{ROOT}/intro-src/.pretendard")
fdir = f"{ROOT}/intro-src/.pretendard/package/dist/public/static"
chars = set(tpl) | set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,:/-_·…→↺×") | set(URL_TEXT)
open(f"{tmp}/chars.txt", "w", encoding="utf-8").write("".join(sorted(c for c in chars if ord(c) > 31 and c not in "{}")))
def sub(name):
    out = f"{tmp}/{name}.woff2"
    subprocess.check_call(["pyftsubset", f"{fdir}/Pretendard-{name}.otf", f"--text-file={tmp}/chars.txt", "--flavor=woff2",
                           f"--output-file={out}", "--layout-features=kern,liga", "--no-hinting"])
    return base64.b64encode(open(out, "rb").read()).decode()

shape = lambda n: base64.b64encode(open(f"{HERE}/shapes/{n}.png", "rb").read()).decode()
html = (tpl.replace("{{LOGO1}}", L1).replace("{{LOGO2}}", L2).replace("<!--QR_SVG-->", qr)
        .replace("{{URL_TEXT}}", URL_TEXT).replace("{{URL}}", URL)
        .replace("{{MASK_PNG}}", shape("mask")).replace("{{PILL_PNG}}", shape("pill")).replace("{{FONT_REG}}", sub("Regular")).replace("{{FONT_SEMI}}", sub("SemiBold")))
assert "{{" not in html.split("<script>")[0], "치환되지 않은 자리표시자가 남아 있어요"
os.makedirs(f"{ROOT}/public/intro", exist_ok=True)
open(f"{ROOT}/public/intro/index.html", "w", encoding="utf-8").write(html)
print("완료: public/intro/index.html", len(html) // 1024, "KB")
