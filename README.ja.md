# LostDock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#installation)

**LostDock** は Google ドーキングと OSINT 調査のためのデスクトップツールです。ビジュアル
ドークビルダーとマルチエンジン検索、レート制限、プロキシローテーション、結果の永続保存を
組み合わせており、ネイティブな PySide6（Qt）インターフェースで **Windows・macOS・Linux**
で動作します。

> **この README を読む:** [English](README.md) · [Español](i18n/README.es.md) · [Français](i18n/README.fr.md) · [Deutsch](i18n/README.de.md) · [हिन्दी](i18n/README.hi.md) · [Português](i18n/README.pt-BR.md) · [Русский](i18n/README.ru.md) · [한국어](i18n/README.ko.md) · [Italiano](i18n/README.it.md) · [العربية](i18n/README.ar.md)

---

## 目次

- [機能](#機能)
- [アーキテクチャ](#アーキテクチャ)
- [インストール](#インストール)
- [使い方](#使い方)
- [対応オペレーター](#対応オペレーター)
- [検索エンジン](#検索エンジン)
- [プロキシ](#プロキシ)
- [定期ドーク](#定期ドーク)
- [URL の再チェック](#url-の再チェック)
- [プラグイン](#プラグイン)
- [エクスポート](#エクスポート)
- [データ保存](#データ保存)
- [パッケージング](#パッケージング)
- [リリース](#リリース)
- [開発](#開発)
- [免責事項](#免責事項)
- [ライセンス](#ライセンス)

---

## 機能

- **ビジュアルドークビルダー** — キーワード、完全一致フレーズ、ブール論理（`AND`/`OR`/`NOT`）、
  除外語、必須語、サイト、ファイルタイプ、すべての Google オペレーターを、ライブプレビュー付きで
  組み合わせられます。
- **マルチエンジン検索** — Google・DuckDuckGo・Bing を単一インターフェースで利用でき、さらに
  自分のブラウザで検索を開く Chrome "pipe" モードもあります。3 つを同時に実行して結果を結合も
  可能です。
- **レート制限とアンチブロック** — ジッター付きトークンバケット制限、User-Agent ローテーション、
  バックオフ付きリトライ、CAPTCHA/ボット検知。通常の HTTP がブロックされた場合、Google エンジンは
  headless Chromium でのレンダリングにフォールバックします。
- **プロキシローテーション** — ラウンドロビン回転、失敗時クールダウン、検証機能付きプロキシプール。
- **永続ストレージ** — すべてのジョブと結果を SQLite に保存し、エンジン間で重複排除します。
- **ライブ URL 再チェック** — 保存済み URL を再取得し、ステータスコード、コンテンツタイプ、タイトル
  を注記します。
- **定期ドーク** — 保存したドークをバックグラウンドで一定間隔で実行します。
- **正規表現ハイライト** — パターンに一致する行を即座にハイライトします。
- **フィルター** — ドメインのホワイトリスト/ブラックリストと、エクスポート時に適用される URL 正規
  表現の保持フィルター。
- **エクスポート** — JSON、CSV、Markdown、スタイル付きの自己完結型 HTML レポート。
- **ドークライブラリ** — ドークを名前で保存・読み込み・管理できます。
- **プラグインシステム** — `setup`、`on_result`、`on_export` フックを持つ Python モジュールを追加。
- **テーマ** — ダーク、ライト、クラシック Win98 GDI スタイル。
- **クロスプラットフォーム** — Windows・macOS・Linux 向けの単一コードベースと、Windows 用インストー
  ラー/アップデーター。

## アーキテクチャ

```
┌─ UI レイヤー（PySide6/Qt）─────────────────────────────┐
│  Dork Builder │ Results Grid │ Scheduler │ Settings      │
│  テーマ（dark / light / win98）                          │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  サービスレイヤー                                          │
│  Repository │ Query │ Filter │ Crawler │ Scheduler │      │
│  Exporter │ Plugins                                       │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  コアエンジン                                              │
│  Adapters（Google / DuckDuckGo / Bing / Chrome）          │
│  Multi-Engine (all) │ Rate Limiter │ Proxy Pool           │
│  Compiler │ Operators                                     │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  SQLite（jobs、results、dorks、schedules、config）        │
└───────────────────────────────────────────────────────────┘
```

## インストール

> インストール手順は意図的に英語のみで提供しています。

### 前提条件

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **uv**（高速パッケージマネージャー）— [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### 手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/dummy3ye/lostdock.git
cd lostdock

# 2. 仮想環境を作成してインストール
uv venv
uv pip install -e ".[dev]"

# 3. Google エンジンのアンチブロックフォールバックが使う headless Chromium をインストール
uv run python -m playwright install chromium

# 4. 実行
uv run lostdock
```

`uv` がない場合は、通常の `pip` でも構いません:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
lostdock
```

### 別法：インストールせずにリポジトリ直下から実行

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main   # ヘッドレステスト用の offscreen
```

## 使い方

1. **クエリを組み立てる** — キーワードを入力し、完全一致フレーズ、除外語、`AND`/`OR` 語、
   サイト（`site:`）、ファイルタイプ、インラインオペレーターを追加します。コンパイルされたクエリは
   ライブで更新されます。
2. **エンジンを選ぶ** — Google、DuckDuckGo、Bing、Chrome、または "all" — とページ数を指定。
3. **Run Search** をクリック。結果がテーブルに流れ込み、各結果は SQLite に保存されます。
4. **Re-check URLs** で各結果を取得し、ライブステータスを注記します。
5. 注目行を強調する **Highlight** 正規表現を設定します。
6. **Export...** をクリックして JSON、CSV、Markdown、HTML レポートとして保存します。

## 対応オペレーター

ビルダーは Google オペレーターの全セットに対応しています:

| オペレーター | 意味 |
|--------------|------|
| `site:` | 結果をドメインに制限 |
| `inurl:` / `allinurl:` | URL 内の語 |
| `intitle:` / `allintitle:` | タイトル内の語 |
| `intext:` / `allintext:` | 本文内の語 |
| `inanchor:` | リンクのアンカーテキスト内の語 |
| `filetype:` / `ext:` | ファイルタイプに制限 |
| `cache:` | Google のキャッシュ版 |
| `link:` | その URL へリンクするページ |
| `related:` | 類似ページ |
| `info:` | ページ概要 |
| `define:` | 用語の定義 |
| `author:` | 結果の著者 |
| `daterange:` / `numrange:` | 数値範囲 |
| `loc:` | 場所 |
| `after:` / `before:` | 日付フィルター（`YYYY-MM-DD`） |
| `lang:` | 言語の制限 |
| `"phrase"` | 完全一致フレーズ |
| `-term` | 用語を除外 |
| `~term` | 同義語を含める |
| `*` | ワイルドカード |
| `term1 OR term2` | いずれかの用語 |

## 検索エンジン

すべてのエンジンは共通のインターフェース（`adapters/base.py` の `SearchEngine`）を共有し、
デフォルトでレート制限されます。`SearchEngine` をサブクラス化し、`adapters/__init__.py` に
登録することで新しいエンジンを追加できます。

- **Google** — まず HTTP で SERP をスクレイピングします。Google が CAPTCHA やレート制限ブロックで
  応答した場合は、実際の headless Chromium（Playwright 経由）でページを再レンダリングし、ほとんどの
  住宅ネットワークで行動ベースのボット検知を回避します。データセンター IP では IP レベルでブロック
  されることがあります — Tools → Settings でプロキシを追加するか、別のエンジンを使ってください。
  Chromium バイナリが一度必要です（`python -m playwright install chromium`）。完全に準拠した本番
  利用には、Google Custom Search JSON API（1 日 100 件の無料クエリ）の統合を検討してください。
- **DuckDuckGo** — 軽量な HTML エンドポイントで、適度な頻度の自動アクセスには概ね寛容です。
- **Bing** — SERP スクレイピング。レート制限あり、大規模になるとボットチェックを受ける可能性あり。
- **Chrome (pipe)** — 検索を自分の Chrome/Chromium ブラウザで直接開き、そこで確認します。結果は
  LostDock に取り込まれません。Google が他をすべてブロックした場合の最も簡単な検索方法です。必要に
  応じて `LOSTDOCK_CHROME` で特定のバイナリを指定できます。
- **All** — 同じクエリで Google・DuckDuckGo・Bing を実行し、結果を結合します。1 つのエンジンが
  ブロックされても検索は中断されず、結果は URL で重複排除されます。

## プロキシ

**Tools → Settings** で設定します。1 行に 1 つ:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

プロキシはリクエストごとにローテーションされ、失敗したプロキシはクールダウンに入ります。
"validate" パス（コード内の `ProxyPool.validate()`）で死んだプロキシを除去できます。

## 定期ドーク

1. ドークを保存します（「Dork name」欄に名前を入力）。
2. **Tools → Settings** でドークを選択し、分単位の間隔を設定して保存します。
3. バックグラウンドのスケジューラーが期限の来たドークを実行し、結果を新しいジョブとして保存し、
   次の実行を繰り延べます。

## URL の再チェック

**Re-check URLs** ボタンは、現在の結果の各 URL を UI スレッドの外で丁寧な遅延付きで取得し、
各行に `ステータスコード`、`コンテンツタイプ`、ライブの `<title>` を注記して、結果をデータベースに
保存します。失敗はインラインで注記され、UI がクラッシュすることはありません。

## プラグイン

`*.py` ファイルを `~/.lostdock/plugins/`（または同梱の `plugins/` ディレクトリ）に置きます。
プラグインモジュールは任意のサブセットをエクスポートできます:

```python
NAME = "my_plugin"

def setup(app): ...                    # 起動時に一度だけ
def on_result(result): return result   # None を返すとその結果を破棄
def on_export(results, fmt, path): ... # エクスポート前
```

動作例は `plugins/example_skip_tracking.py` を参照してください。

## エクスポート

| 形式 | 拡張子 | 備考 |
|------|--------|------|
| JSON | `.json` | 完全な構造化結果 |
| CSV | `.csv` | スプレッドシート対応（UTF-8 BOM） |
| Markdown | `.md` | 人が読みやすい |
| HTML | `.html` | 自己完結型レポート、クリック可能なリンク |

## データ保存

- **データベース:** `~/.lostdock/lostdock.db`（SQLite）
- **プラグイン:** `~/.lostdock/plugins/`
- テーブル: `jobs`、`results`、`saved_dorks`、`schedules`、`settings`。古いデータベースは自動的に
  マイグレーションされます。

## パッケージング

プロジェクトには PyInstaller 用の `lostdock.spec` が含まれています。プラットフォーム別にビルド:

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec          # dist/lostdock を作成
```

- **Windows:** `dist/lostdock.exe` に加え、管理者権限なしでインストーラー・アップデーター・
  アンインストーラーとして機能する単一ファイルの `lostdock-installer.exe`
  （`src/installer/windows/main.py`）。
- **macOS:** `dist/LostDock.app` にバンドル（配布時は `codesign` で署名）。
- **Linux:** `dist/lostdock` バイナリ、または AppImage/Flatpak にラップ。Arch Linux の
  `PKGBUILD` は `packaging/aur/` にあります。

## リリース

リリースはタグ駆動で自動化されています。新しいリリースを切るには `git-cliff`
（`cargo install git-cliff`）が必要です:

```bash
make release                # バージョンを上げ、CHANGELOG.md を再生成し、コミットしてタグ付け
```

`make release` は直前のタグ以降の conventional commits を読み、次の semver バージョンを決めます
（または明示的に指定: `./scripts/release.sh 0.2.0`）。その後 `pyproject.toml` と
`src/lostdock/__init__.py` のバージョンを上げ、テストスイートを実行し、`CHANGELOG.md` を再生成して、
アノテーション付きの `vX.Y.Z` タグを作成します。

タグをプッシュすると CI が実行され、Windows と Linux のバイナリと自己署名された Windows
インストーラーをビルドし、[git-cliff](https://git-cliff.org) による自動生成ノート（グループ化された
機能/修正、issue 参照、コントリビューター）付きの GitHub Release を公開します。

## 開発

```bash
uv run pytest                     # テストスイートを実行
uv run python -m compileall -q src  # import の健全性チェック
uv run ruff check src tests       # lint
```

プロジェクト構成:

```
src/lostdock/
├── core/         Dork モデル、オペレーター、クエリコンパイラ、レートリミッター、プロキシプール
├── adapters/     Google / DuckDuckGo / Bing / Chrome アダプター、ブラウザレンダラー
├── services/     repository、query、filter、crawler、scheduler、exporter、plugins
├── ui/           PySide6 ウィジェット: dork builder、results grid、worker、settings、theme、main window
└── main.py       エントリーポイント
src/installer/    Windows インストーラー/アップデーター/アンインストーラー
tests/            pytest スイート（compiler、engines、services、proxy、scheduler、plugins）
```

## 免責事項

LostDock は**セキュリティ研究と OSINT のためのツール**です。所有しているシステム、または明示的に
テスト許可を得たシステムにのみ使用してください。検索エンジンの利用規約を尊重し、レートを低く保ち、
プロキシを責任を持って使い、不正アクセス、個人データのスクレイピング、違法行為にこのツールを決して
使わないでください。著者は誤用について責任を負いません。

## ライセンス

MIT — [LICENSE](LICENSE) を参照。
