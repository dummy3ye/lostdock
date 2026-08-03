# LostDock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#설치)

**LostDock**은 Google 도킹과 OSINT 조사를 위한 데스크톱 도구입니다. 시각적 도크 빌더와
멀티 엔진 검색, 속도 제한, 프록시 로테이션, 영구 결과 저장을 결합한 네이티브 PySide6(Qt)
인터페이스로 **Windows, macOS, Linux**에서 실행됩니다.

> **이 README 읽기:** [English](../README.md) · [中文](../README.zh-CN.md) · [Español](../i18n/README.es.md) · [Français](../i18n/README.fr.md) · [Deutsch](../i18n/README.de.md) · [हिन्दी](../i18n/README.hi.md) · [Português](../i18n/README.pt-BR.md) · [Русский](../i18n/README.ru.md) · [日本語](../README.ja.md) · [Italiano](../i18n/README.it.md) · [العربية](../i18n/README.ar.md)

---

## 목차

- [기능](#기능)
- [아키텍처](#아키텍처)
- [설치](#설치)
- [사용법](#사용법)
- [지원 연산자](#지원-연산자)
- [검색 엔진](#검색-엔진)
- [프록시](#프록시)
- [정기 도크](#정기-도크)
- [URL 재확인](#url-재확인)
- [플러그인](#플러그인)
- [내보내기](#내보내기)
- [데이터 저장](#데이터-저장)
- [패키징](#패키징)
- [릴리스](#릴리스)
- [개발](#개발)
- [면책 조항](#면책-조항)
- [라이선스](#라이선스)

---

## 기능

- **시각적 도크 빌더** — 키워드, 정확한 구문, 불리언 논리(`AND`/`OR`/`NOT`), 제외어,
  필수어, 사이트, 파일 형식, 모든 Google 연산자를 실시간 미리보기와 함께 조합합니다.
- **멀티 엔진 검색** — 단일 인터페이스로 Google, DuckDuckGo, Bing을 지원하며, 브라우저에서
  직접 검색하는 Chrome "pipe" 모드도 제공합니다. 또는 세 개를 모두 실행해 결과를 합칩니다.
- **속도 제한 및 차단 방지** — 지터가 포함된 토큰 버킷 제한, User-Agent 로테이션,
  백오프 재시도, CAPTCHA/봇 감지. 일반 HTTP가 차단되면 Google은 headless Chromium
  렌더링으로 전환합니다.
- **프록시 로테이션** — 라운드로빈 회전, 실패 시 쿨다운, 검증 기능이 있는 프록시 풀.
- **영구 저장** — 모든 작업과 결과를 SQLite에 저장하고 엔진 간 중복을 제거합니다.
- **실시간 URL 재확인** — 저장된 URL을 다시 가져와 상태 코드, 콘텐츠 유형, 제목을
  주석 처리합니다.
- **정기 도크** — 저장된 도크를 백그라운드에서 일정 간격으로 실행합니다.
- **정규식 하이라이트** — 패턴과 일치하는 행을 즉시 강조합니다.
- **필터** — 도메인 화이트리스트/블랙리스트와 내보내기 시 적용되는 URL 정규식 유지 필터.
- **내보내기** — JSON, CSV, Markdown, 스타일이 적용된 독립형 HTML 보고서.
- **도크 라이브러리** — 도크를 이름으로 저장, 로드, 관리합니다.
- **플러그인 시스템** — `setup`, `on_result`, `on_export` 훅을 가진 Python 모듈 추가.
- **테마** — 다크, 라이트, 클래식 Win98 GDI 스타일.
- **크로스플랫폼** — Windows, macOS, Linux용 단일 코드베이스와 Windows
  설치 프로그램/업데이터.

## 아키텍처

```
┌─ UI 레이어 (PySide6/Qt) ──────────────────────────────┐
│  Dork Builder │ Results Grid │ Scheduler │ Settings      │
│  테마 (dark / light / win98)                            │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  서비스 레이어                                             │
│  Repository │ Query │ Filter │ Crawler │ Scheduler │      │
│  Exporter │ Plugins                                       │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  코어 엔진                                                │
│  Adapters (Google / DuckDuckGo / Bing / Chrome)           │
│  Multi-Engine (all) │ Rate Limiter │ Proxy Pool           │
│  Compiler │ Operators                                     │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  SQLite (jobs, results, dorks, schedules, config)         │
└───────────────────────────────────────────────────────────┘
```

## 설치

> 설치 지침은 의도적으로 영어로만 제공됩니다.

### 사전 요구 사항

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **uv** (빠른 패키지 매니저) — [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### 단계

```bash
# 1. 저장소 복제
git clone https://github.com/dummy3ye/lostdock.git
cd lostdock

# 2. 가상 환경 생성 및 설치
uv venv
uv pip install -e ".[dev]"

# 3. Google 엔진의 차단 방지 폴백에 사용되는 headless Chromium 설치
uv run python -m playwright install chromium

# 4. 실행
uv run lostdock
```

`uv`가 없다면 일반 `pip`을 사용할 수 있습니다:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
lostdock
```

### 대안: 설치 없이 저장소 루트에서 실행

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main   # 헤드리스 테스트용 offscreen
```

## 사용법

1. **쿼리 작성** — 키워드를 입력하고 정확한 구문, 제외어, `AND`/`OR` 용어, 사이트
   (`site:`), 파일 형식, 인라인 연산자를 추가합니다. 컴파일된 쿼리는 실시간으로
   업데이트됩니다.
2. **엔진 선택** — Google, DuckDuckGo, Bing, Chrome 또는 "all" — 및 페이지 수.
3. **Run Search**를 클릭합니다. 결과가 테이블로 들어오고 각 결과는 SQLite에 저장됩니다.
4. **Re-check URLs**로 각 결과를 가져와 실시간 상태를 주석 처리합니다.
5. 관심 있는 행을 강조할 **Highlight** 정규식을 설정합니다.
6. **Export...**를 클릭해 JSON, CSV, Markdown 또는 HTML 보고서로 저장합니다.

## 지원 연산자

빌더는 전체 Google 연산자 집합을 지원합니다:

| 연산자 | 의미 |
|--------|------|
| `site:` | 결과를 도메인으로 제한 |
| `inurl:` / `allinurl:` | URL 안의 단어 |
| `intitle:` / `allintitle:` | 제목 안의 단어 |
| `intext:` / `allintext:` | 본문 안의 단어 |
| `inanchor:` | 링크 앵커 텍스트의 단어 |
| `filetype:` / `ext:` | 파일 형식으로 제한 |
| `cache:` | Google 캐시 버전 |
| `link:` | URL을 가리키는 페이지 |
| `related:` | 유사한 페이지 |
| `info:` | 페이지 개요 |
| `define:` | 용어 정의 |
| `author:` | 결과 작성자 |
| `daterange:` / `numrange:` | 숫자 범위 |
| `loc:` | 위치 |
| `after:` / `before:` | 날짜 필터 (`YYYY-MM-DD`) |
| `lang:` | 언어 제한 |
| `"phrase"` | 정확한 구문 |
| `-term` | 용어 제외 |
| `~term` | 동의어 포함 |
| `*` | 와일드카드 |
| `term1 OR term2` | 둘 중 하나의 용어 |

## 검색 엔진

모든 엔진은 동일한 인터페이스(`adapters/base.py`의 `SearchEngine`)를 공유하며 기본적으로
속도가 제한됩니다. `SearchEngine`을 상속하고 `adapters/__init__.py`에 등록하여 새 엔진을
추가할 수 있습니다.

- **Google** — 먼저 HTTP로 SERP를 스크레이핑합니다. Google이 CAPTCHA 또는 속도 제한
  차단으로 응답하면 Playwright를 통해 실제 headless Chromium에서 페이지를 다시 렌더링하여
  대부분의 가정용 네트워크에서 동작 기반 봇 탐지를 우회합니다. 데이터센터 IP에서는 Google이
  IP 수준에서 차단할 수 있으므로 Tools → Settings에서 프록시를 추가하거나 다른 엔진을
  사용하세요. Chromium 바이너리가 한 번 필요합니다
  (`python -m playwright install chromium`). 완전히 규정을 준수하는 프로덕션 사용을
  위해서는 Google Custom Search JSON API(하루 100회 무료 쿼리)를 통합하세요.
- **DuckDuckGo** — 가벼운 HTML 엔드포인트로, 적절한 속도에서 자동화 액세스에 일반적으로
  관대합니다.
- **Bing** — SERP 스크레이핑. 속도가 제한되고 대규모 사용 시 봇 검사에 걸릴 수 있습니다.
- **Chrome (pipe)** — 검색을 사용자 브라우저에서 바로 열어 확인합니다. 결과는 LostDock으로
  캡처되지 않습니다. Google이 다른 모든 것을 차단할 때 가장 간단한 검색 방법입니다. 필요한
  경우 `LOSTDOCK_CHROME`으로 특정 바이너리를 지정할 수 있습니다.
- **All** — 같은 쿼리로 Google, DuckDuckGo, Bing을 실행하고 결과를 합칩니다. 하나의 엔진이
  차단되어도 검색이 중단되지 않으며 결과는 URL 기준으로 중복 제거됩니다.

## 프록시

**Tools → Settings**에서 한 줄에 하나씩 설정:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

프록시는 요청마다 로테이션되고 실패한 프록시는 쿨다운에 들어갑니다. "validate" 경로(코드의
`ProxyPool.validate()`)를 사용해 죽은 프록시를 제거하세요.

## 정기 도크

1. 도크를 저장합니다("Dork name" 필드에 이름 입력).
2. **Tools → Settings**에서 도크를 선택하고 분 단위 간격을 설정한 후 저장합니다.
3. 백그라운드 스케줄러가 예정된 도크를 실행하고 결과를 새 작업으로 저장하며 다음 실행을
   늦춥니다.

## URL 재확인

**Re-check URLs** 버튼은 현재 결과의 각 URL을 UI 스레드 밖에서 정중한 지연으로 가져오고
각 행에 `상태 코드`, `콘텐츠 유형`, 실시간 `<title>`을 주석 처리한 뒤 데이터베이스에
저장합니다. 실패는 인라인으로 주석 처리되며 UI가 멈추지 않습니다.

## 플러그인

`*.py` 파일을 `~/.lostdock/plugins/`(또는 포함된 `plugins/` 디렉터리)에 넣습니다. 플러그인
모듈은 원하는 하위 집합을 내보낼 수 있습니다:

```python
NAME = "my_plugin"

def setup(app): ...                    # 시작 시 한 번
def on_result(result): return result   # 결과를 버리려면 None 반환
def on_export(results, fmt, path): ... # 내보내기 전
```

작동 예시는 `plugins/example_skip_tracking.py`를 참조하세요.

## 내보내기

| 형식 | 확장자 | 참고 |
|------|--------|------|
| JSON | `.json` | 완전한 구조화 결과 |
| CSV | `.csv` | 스프레드시트 준비됨 (UTF-8 BOM) |
| Markdown | `.md` | 사람이 읽기 쉬움 |
| HTML | `.html` | 독립형 보고서, 클릭 가능한 링크 |

## 데이터 저장

- **데이터베이스:** `~/.lostdock/lostdock.db` (SQLite)
- **플러그인:** `~/.lostdock/plugins/`
- 테이블: `jobs`, `results`, `saved_dorks`, `schedules`, `settings`. 기존 데이터베이스는
  자동으로 마이그레이션됩니다.

## 패키징

프로젝트에는 PyInstaller용 `lostdock.spec`이 포함되어 있습니다. 플랫폼별 빌드:

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec          # dist/lostdock 생성
```

- **Windows:** `dist/lostdock.exe` 및 관리자 권한 없이 설치 프로그램, 업데이터,
  제거 프로그램 역할을 하는 단일 파일 `lostdock-installer.exe`
  (`src/installer/windows/main.py`).
- **macOS:** `dist/LostDock.app`으로 번들링(배포 시 `codesign`으로 서명).
- **Linux:** `dist/lostdock` 바이너리 또는 AppImage/Flatpak으로 패키징. Arch Linux용
  `PKGBUILD`는 `packaging/aur/`에 있습니다.

## 릴리스

릴리스는 태그 기반으로 자동화되어 있습니다. 새 릴리스를 만들려면 `git-cliff`가 필요합니다
(`cargo install git-cliff`):

```bash
make release                # 버전 올리고, CHANGELOG.md 재생성, 커밋 및 태그
```

`make release`는 마지막 태그 이후의 conventional commits를 읽어 다음 semver 버전을
선택합니다(또는 명시적으로 지정: `./scripts/release.sh 0.2.0`). 그런 다음
`pyproject.toml`과 `src/lostdock/__init__.py`의 버전을 올리고 테스트 스위트를 실행한 후
`CHANGELOG.md`를 재생성하고 주석 달린 `vX.Y.Z` 태그를 만듭니다.

태그를 푸시하면 CI가 실행되어 Windows와 Linux 바이너리 및 자체 서명된 Windows 설치
프로그램을 빌드하고 [git-cliff](https://git-cliff.org)를 통해 자동 생성된 노트(그룹화된
기능/수정, issue 참조, 기여자)와 함께 GitHub Release를 게시합니다.

## 개발

```bash
uv run pytest                     # 테스트 스위트 실행
uv run python -m compileall -q src  # import sanity-check
uv run ruff check src tests       # 린트
```

프로젝트 구조:

```
src/lostdock/
├── core/         Dork 모델, 연산자, 쿼리 컴파일러, rate limiter, proxy pool
├── adapters/     Google / DuckDuckGo / Bing / Chrome 어댑터, 브라우저 렌더러
├── services/     repository, query, filter, crawler, scheduler, exporter, plugins
├── ui/           PySide6 위젯: dork builder, results grid, worker, settings, theme, main window
└── main.py       진입점
src/installer/    Windows 설치 프로그램/업데이터/제거 프로그램
tests/            pytest 스위트 (compiler, engines, services, proxy, scheduler, plugins)
```

## 면책 조항

LostDock은 **보안 연구 및 OSINT 도구**입니다. 소유한 시스템이나 명시적으로 테스트 승인을
받은 시스템에만 사용하세요. 검색 엔진 서비스 약관을 준수하고 속도를 낮게 유지하며 프록시를
책임감 있게 사용하고, 무단 액세스, 개인 데이터 스크래핑 또는 불법 활동에 이 도구를 절대
사용하지 마세요. 저자는 오용에 대해 책임지지 않습니다.

## 라이선스

MIT — [LICENSE](../LICENSE) 참조.
