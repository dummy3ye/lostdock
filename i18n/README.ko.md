# LostDock

**LostDock** 은 Python으로 작성된 산업급 크로스플랫폼 Google 도킹 데스크톱 도구입니다.
모든 검색 엔진 연산자를 지원하는 시각적 쿼리 빌더, 속도 제한과 프록시 로테이션이 포함된 다중 엔진
실행, 결과 영구 저장, URL 재확인, 정기 도크, 정규식 하이라이트, 플러그인 시스템을 갖추고 있으며
**Windows, macOS, Linux**에서 실행되는 네이티브 PySide6(Qt) UI를 사용합니다.

> 전체 문서: [README.md](../README.md)

---

## 기능

- **시각적 도크 빌더** — 키워드, 정확한 구문, 불리언 논리(`AND`/`OR`/`NOT`), 제외어, 필수어, 사이트,
  파일 형식, 모든 Google 연산자를 실시간 미리보기와 함께 조합합니다.
- **다중 엔진** — Google, DuckDuckGo, Bing 어댑터를 단일 인터페이스로 제공.
- **속도 제한 및 차단 방지** — 지터가 포함된 토큰 버킷 제한, User-Agent 로테이션, 백오프 재시도,
  CAPTCHA/봇 감지.
- **프록시 로테이션** — 라운드로빈 회전, 실패 시 쿨다운, 검증 기능이 있는 프록시 풀.
- **영구 저장** — 모든 작업과 결과를 SQLite에 저장하고 엔진 간 중복 제거.
- **URL 재확인** — 저장된 URL을 다시 가져와 상태 코드/콘텐츠 유형/제목을 주석 처리.
- **정기 도크** — 저장된 도크를 백그라운드에서 주기적으로 실행.
- **정규식 하이라이트** — 패턴과 일치하는 행을 즉시 강조.
- **필터** — 도메인 화이트리스트/블랙리스트 및 URL 정규식 필터(내보내기 시 적용).
- **내보내기** — JSON, CSV, Markdown, 스타일이 적용된 자체 포함 HTML 보고서.
- **도크 라이브러리** — 도크 이름 지정, 저장, 로드, 삭제.
- **플러그인 시스템** — `~/.lostdock/plugins/`의 Python 모듈, 훅: `setup`, `on_result`, `on_export`.
- **크로스플랫폼** — 단일 코드로 Windows(`.exe`), macOS(`.app`), Linux용 패키징.

## 빠른 사용법

1. 쿼리 구성: 키워드, 정확한 구문, 제외어, `AND`/`OR` 용어, 사이트(`site:`), 파일 형식, 인라인 연산자.
2. 엔진과 페이지 수를 선택합니다.
3. **Run Search** 클릭 — 결과가 표로 들어오고 SQLite에 저장됩니다.
4. **Re-check URLs**로 각 결과의 실시간 상태를 확인합니다.
5. **Highlight** 정규식으로 관심 행을 강조합니다.
6. **Export...**로 JSON, CSV, Markdown 또는 HTML로 저장합니다.

## 지원 연산자

`site:` · `inurl:` · `allinurl:` · `intitle:` · `allintitle:` · `intext:` · `allintext:` · `inanchor:` ·
`filetype:` · `ext:` · `cache:` · `link:` · `related:` · `info:` · `define:` · `author:` · `daterange:` ·
`numrange:` · `loc:` · `after:` · `before:` · `lang:` · 정확한 구문 `"..."` · 제외 `-term` ·
동의어 `~term` · 와일드카드 `*` · `term1 OR term2`.

## 프록시

**Tools → Settings**에서 한 줄에 하나씩 설정:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

## 정기 도크

1. 도크를 저장합니다("Dork name" 필드에 이름 입력).
2. **Tools → Settings**에서 선택하고 분 단위로 간격을 설정합니다.
3. 스케줄러가 백그라운드에서 실행하고 결과를 새 작업으로 저장합니다.

## 플러그인

`~/.lostdock/plugins/`에 `*.py` 파일을 넣습니다. 모듈은 원하는 훅의 일부를 내보낼 수 있습니다:

```python
NAME = "my_plugin"
def setup(app): ...
def on_result(result): return result   # None을 반환하면 폐기
def on_export(results, fmt, path): ...
```

## 데이터 저장

- **데이터베이스:** `~/.lostdock/lostdock.db`(SQLite)
- **플러그인:** `~/.lostdock/plugins/`

## Installation

> Installation instructions are intentionally provided in English only.

### Prerequisites

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **uv** (fast package manager) — [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-user/lostdock.git
cd lostdock

# 2. Create a virtual environment and install
uv venv
uv pip install -e ".[dev]"

# 3. Run
uv run lostdock
```

If you do not have `uv`, you can use plain `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
lostdock
```

## 면책 조항

LostDock은 **보안 연구 및 OSINT 도구**입니다. 소유한 시스템 또는 명시적 테스트 승인을 받은 시스템에만
사용하십시오. 검색 엔진 서비스 약관을 준수하고, 속도를 낮게 유지하며, 프록시를 책임감 있게 사용하고,
무단 접근, 개인 데이터 스크래핑 또는 불법 활동에는 절대 사용하지 마십시오.

## License

MIT — [LICENSE](LICENSE) 참조.
