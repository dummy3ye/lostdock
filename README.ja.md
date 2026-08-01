# LostDock

**LostDock** は、Python 製の産業グレードでクロスプラットフォームな Google ドーキング・デスクトップツールです。
すべての検索エンジン演算子を使ったビジュアルクエリビルダー、レート制限とプロキシローテーション付きの
マルチエンジン実行、結果の永続ストレージ、URL 再チェック、定期ドーク、正規表現ハイライト、プラグイン
システムを備えており、**Windows・macOS・Linux** で動作するネイティブな PySide6（Qt）UI を採用しています。

> 完全なドキュメント: [README.md](README.md)

---

## 特徴

- **ビジュアルドークビルダー** — キーワード、完全一致フレーズ、ブール論理（`AND`/`OR`/`NOT`）、除外語、
  必須語、サイト、ファイルタイプ、すべての Google 演算子をライブプレビュー付きで組み合わせられます。
- **マルチエンジン** — Google・DuckDuckGo・Bing のアダプタを単一インターフェースで提供。
- **レート制限とアンチブロック** — ジッター付きトークンバケット制限、User-Agent ローテーション、
  バックオフ付きリトライ、CAPTCHA/ボット検知。
- **プロキシローテーション** — ラウンドロビン回転、失敗時クールダウン、検証機能付きプロキシプール。
- **永続ストレージ** — すべてのジョブと結果を SQLite に保存し、エンジン間で重複排除。
- **URL 再チェック** — 保存済み URL を再取得し、ステータスコード / コンテンツタイプ / タイトルを注記。
- **定期ドーク** — 保存したドークをバックグラウンドで一定間隔で実行。
- **正規表現ハイライト** — パターンに一致する行を即座にハイライト。
- **フィルター** — ドメインのホワイト/ブラックリストと URL 正規表現フィルター（エクスポート時に適用）。
- **エクスポート** — JSON、CSV、Markdown、およびスタイル付き自己完結型 HTML レポート。
- **ドークライブラリ** — ドークの名前付け・保存・読み込み・削除。
- **プラグインシステム** — `~/.lostdock/plugins/` 内の Python モジュール、フック: `setup`・`on_result`・`on_export`。
- **クロスプラットフォーム** — 単一コードを Windows（`.exe`）、macOS（`.app`）、Linux 用にパッケージ化。

## クイック利用

1. クエリを組み立てる: キーワード、完全一致フレーズ、除外語、`AND`/`OR` 語、サイト（`site:`）、
   ファイルタイプ、インライン演算子。
2. エンジンとページ数を選択。
3. **Run Search** をクリック — 結果がテーブルに流れ込み、SQLite に保存されます。
4. **Re-check URLs** で各結果のライブステータスを確認。
5. **Highlight** の正規表現で注目行を強調。
6. **Export...** で JSON・CSV・Markdown・HTML として保存。

## 対応演算子

`site:` · `inurl:` · `allinurl:` · `intitle:` · `allintitle:` · `intext:` · `allintext:` · `inanchor:` ·
`filetype:` · `ext:` · `cache:` · `link:` · `related:` · `info:` · `define:` · `author:` · `daterange:` ·
`numrange:` · `loc:` · `after:` · `before:` · `lang:` · 完全一致 `"..."` · 除外 `-term` ·
同義語 `~term` · ワイルドカード `*` · `term1 OR term2`。

## プロキシ

**Tools → Settings** で設定。1 行に 1 つ:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

## 定期ドーク

1. ドークを保存（「Dork name」欄に名前を入力）。
2. **Tools → Settings** で選択し、間隔を分単位で設定。
3. スケジューラーがバックグラウンドで実行し、結果を新しいジョブとして保存。

## プラグイン

`~/.lostdock/plugins/` に `*.py` ファイルを配置します。任意のフックをエクスポートできます:

```python
NAME = "my_plugin"
def setup(app): ...
def on_result(result): return result   # None を返すと破棄
def on_export(results, fmt, path): ...
```

## データ保存

- **データベース:** `~/.lostdock/lostdock.db`（SQLite）
- **プラグイン:** `~/.lostdock/plugins/`

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

## 免責事項

LostDock は**セキュリティ研究・OSINT ツール**です。所有している、または明示的なテスト許可を得た
システムにのみ使用してください。検索エンジンの利用規約を尊重し、レートを低く保ち、プロキシを責任を
持って使い、不正アクセス・個人データのスクレイピング・違法行為には絶対に使用しないでください。

## License

MIT — [LICENSE](LICENSE) を参照。
