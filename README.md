# 에스모스(Ethmos) 앱 프로토타입

「한눈에 보는 비염」 졸업전시 UXUI 프로토타입입니다. 앱스토어 배포용이 아니라, 브라우저에서 모바일 앱처럼 눌러 볼 수 있는 **웹 프로토타입**이며 GitHub Pages로 배포합니다.

- 단일 HTML(`dist/index.html`) 한 장이 전부입니다. 서버·DB·외부 요청·글꼴 파일이 없고, 글자는 모두 SVG 아웃라인으로 그려서 어떤 기기에서도 같은 서체로 보입니다.
- 데스크톱에서는 393×852 폰 프레임 옆에 시연 패널(상황 선택·화면 이동)이 보이고, 모바일에서는 화면 가득 앱처럼 보입니다. 홈 화면에 추가하면 전체 화면(standalone)으로 열립니다.
- 값은 브라우저 `localStorage`(`ethmos-proto-2`)에만 저장됩니다. 초기화하려면 사이트 데이터를 지우세요.
- 검색엔진에 노출되지 않도록 `noindex`를 넣었습니다.

## 폴더 구조

```
src/template.html   화면·스타일·동작 전부 (자리표시자 {{OTX_CSS}} {{OTX_JS}} {{ICONS_JSON}})
src/ot.js, ot.css   글자→SVG 아웃라인 렌더러
data/glyphs.json    글자 아웃라인(Pretendard 5굵기 + 격동명조 3굵기)
data/icons.json     Material Symbols 아이콘 path
public/             favicon, 홈 화면 아이콘, manifest (dist로 그대로 복사)
build.py            src + data → dist/index.html  (파이썬 표준 라이브러리만 사용)
tools/              글리프 아웃라인을 다시 만들 때만 쓰는 스크립트(아래 참고)
.github/workflows/pages.yml   main에 푸시하면 자동 빌드·배포
```

## 로컬에서 확인

```bash
python3 build.py
python3 -m http.server -d dist 8000   # http://localhost:8000
```

## GitHub Pages로 배포

1. GitHub에서 새 저장소를 만든다. (예: `ethmos-prototype`)
2. 이 폴더를 올린다.
   ```bash
   git init -b main
   git add .
   git commit -m "에스모스 앱 프로토타입"
   git remote add origin https://github.com/<계정>/<저장소>.git
   git push -u origin main
   ```
3. 저장소 **Settings → Pages → Build and deployment → Source** 를 **GitHub Actions** 로 바꾼다. (처음 한 번만)
4. **Actions** 탭에서 `Deploy prototype to GitHub Pages`가 끝나면 `https://<계정>.github.io/<저장소>/` 에서 열린다.

이후에는 `src/` 를 고치고 `main`에 푸시하면 자동으로 다시 배포됩니다. 모든 경로가 상대 경로라서 저장소 이름이 달라도, 커스텀 도메인을 써도 그대로 동작합니다.

## 글리프 아웃라인 다시 만들기 (보통은 필요 없음)

문구가 바뀌어 새 글자가 필요하거나 서체를 바꿀 때만 씁니다. 글꼴 원본은 라이선스 때문에 저장소에 포함하지 않았습니다(`fonts/`는 `.gitignore`).

1. 빌드된 `dist/index.html`에서 `node tools/audit.js` → 쓰이는 글자·굵기 목록(`data/audit.json`)
2. `fonts/pretendard-sub.woff2`(Pretendard 가변), `fonts/kr-*.otf`(대체 서체) 준비 후 `python3 tools/mkglyphs.py` → `data/glyphs.json`
3. 격동명조는 피그마에서 아웃라인을 따서 내보낸 글리프 시트 SVG로 `python3 tools/sheet2glyphs.py <svg…>` → `data/glyphs_gyeokdong.json` (이 파일이 있으면 `mkglyphs.py`가 우선 사용)

## 라이선스 · 주의

- **격동명조(SD 격동명조) 아웃라인이 `data/glyphs.json` 안에 들어 있습니다.** 글꼴 라이선스상 글자 모양을 이미지/벡터로 쓰는 것이 허용되는지, 저장소를 공개해도 되는지 확인한 뒤 공개 저장소로 올리세요. 확인 전에는 비공개 저장소를 권장합니다. (비공개 저장소에서 Pages를 쓰려면 GitHub 유료 플랜이 필요합니다.)
- Pretendard: SIL Open Font License 1.1 · Material Symbols: Apache License 2.0
- 이 저장소의 화면 디자인·브랜드(로고, 색, 문구)는 졸업전시 작품이며 별도 라이선스를 부여하지 않았습니다.
