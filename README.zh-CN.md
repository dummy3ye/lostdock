# LostDock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#installation)

**LostDock** 是一款用于 Google dorking 与 OSINT 研究的桌面工具。它将可视化查询构建器与多引擎
搜索、速率限制、代理轮换和持久化结果存储结合于一身——全部运行在原生 PySide6（Qt）界面中，
支持 **Windows、macOS 和 Linux**。

> **以其他语言阅读：** [English](README.md) · [Español](i18n/README.es.md) · [Français](i18n/README.fr.md) · [Deutsch](i18n/README.de.md) · [हिन्दी](i18n/README.hi.md) · [Português](i18n/README.pt-BR.md) · [Русский](i18n/README.ru.md) · [日本語](README.ja.md) · [한국어](i18n/README.ko.md) · [Italiano](i18n/README.it.md) · [العربية](i18n/README.ar.md)

---

## 目录

- [功能特性](#功能特性)
- [架构](#架构)
- [安装](#安装)
- [使用](#使用)
- [支持的操作符](#支持的操作符)
- [搜索引擎](#搜索引擎)
- [代理](#代理)
- [定时搜索](#定时搜索)
- [URL 在线复检](#url-在线复检)
- [插件](#插件)
- [导出](#导出)
- [数据存储](#数据存储)
- [打包](#打包)
- [发布](#发布)
- [开发](#开发)
- [免责声明](#免责声明)
- [许可证](#许可证)

---

## 功能特性

- **可视化查询构建器** —— 组合关键词、精确短语、布尔逻辑（`AND`/`OR`/`NOT`）、排除词、
  必含词、站点、文件类型以及全部 Google 操作符，支持实时查询预览。
- **多引擎搜索** —— 通过同一界面使用 Google、DuckDuckGo 和 Bing，另提供 Chrome "pipe" 模式，
  可在你自己的浏览器中直接搜索。也可以同时运行三者并合并结果。
- **速率限制与反拦截** —— 带抖动的令牌桶限速器、随机 User-Agent、退避重试、验证码/机器人
  检测。当普通 HTTP 被拦截时，Google 引擎会自动回退到 headless Chromium 渲染。
- **代理轮换** —— 代理池支持轮询轮换、失败冷却与可用性校验。
- **持久化存储** —— 每个任务与结果都存入 SQLite，跨引擎自动去重。
- **URL 在线复检** —— 重新抓取已存 URL，并标注状态码、内容类型与实时标题。
- **定时搜索** —— 在后台按设定间隔自动运行已保存的搜索。
- **正则高亮** —— 即时高亮匹配指定模式的行。
- **过滤器** —— 域名白名单/黑名单与 URL 正则保留过滤，导出时生效。
- **导出** —— JSON、CSV、Markdown，以及样式化自包含 HTML 报告。
- **搜索库** —— 按名称保存、加载与管理搜索。
- **插件系统** —— 可添加带 `setup`、`on_result`、`on_export` 钩子的 Python 模块。
- **主题** —— 深色、浅色与经典 Win98 GDI 样式。
- **跨平台** —— 一套代码打包 Windows、macOS 与 Linux，并提供 Windows 安装器/更新器。

## 架构

```
┌─ UI 层（PySide6/Qt）────────────────────────────────┐
│  Dork Builder │ Results Grid │ Scheduler │ Settings    │
│  主题（dark / light / win98）                          │
└───────────────┬────────────────────────────────────────┘
┌───────────────▼────────────────────────────────────────┐
│  服务层                                                 │
│  Repository │ Query │ Filter │ Crawler │ Scheduler │    │
│  Exporter │ Plugins                                     │
└───────────────┬────────────────────────────────────────┘
┌───────────────▼────────────────────────────────────────┐
│  核心引擎                                               │
│  Adapters（Google / DuckDuckGo / Bing / Chrome）        │
│  Multi-Engine (all) │ Rate Limiter │ Proxy Pool         │
│  Compiler │ Operators                                   │
└───────────────┬────────────────────────────────────────┘
┌───────────────▼────────────────────────────────────────┐
│  SQLite（jobs、results、dorks、schedules、config）       │
└─────────────────────────────────────────────────────────┘
```

## 安装

> 安装说明特意仅以英文提供。

### 前置要求

- **Python 3.10+** —— [python.org](https://www.python.org/downloads/)
- **uv**（快速包管理器）—— [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### 步骤

```bash
# 1. 克隆仓库
git clone https://github.com/dummy3ye/lostdock.git
cd lostdock

# 2. 创建虚拟环境并安装
uv venv
uv pip install -e ".[dev]"

# 3. 安装 Google 引擎反拦截回退所需的 headless Chromium
uv run python -m playwright install chromium

# 4. 运行
uv run lostdock
```

如果没有 `uv`，也可以直接使用 `pip`：

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
lostdock
```

### 备选：无需安装，从仓库根目录直接运行

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main   # offscreen 用于无界面测试
```

## 使用

1. **构建查询** —— 输入关键词，添加精确短语、排除词、`AND`/`OR` 词、站点（`site:`）、
   文件类型与内联操作符。编译后的查询会实时更新。
2. **选择引擎** —— Google、DuckDuckGo、Bing、Chrome 或 "all"，并设置页数。
3. 点击 **Run Search**。结果流入表格；每条结果都会持久化到 SQLite。
4. 使用 **Re-check URLs** 抓取每条结果并标注其实时状态。
5. 设置 **Highlight** 正则来突出关注行。
6. 点击 **Export...** 导出为 JSON、CSV、Markdown 或 HTML 报告。

## 支持的操作符

构建器支持完整的 Google 操作符集：

| 操作符 | 含义 |
|--------|------|
| `site:` | 将结果限制到某个域名 |
| `inurl:` / `allinurl:` | URL 中的词 |
| `intitle:` / `allintitle:` | 标题中的词 |
| `intext:` / `allintext:` | 正文中的词 |
| `inanchor:` | 链接锚文本中的词 |
| `filetype:` / `ext:` | 限制为某种文件类型 |
| `cache:` | Google 缓存版本 |
| `link:` | 链接到某 URL 的页面 |
| `related:` | 相似页面 |
| `info:` | 页面概览 |
| `define:` | 术语定义 |
| `author:` | 结果作者 |
| `daterange:` / `numrange:` | 数值范围 |
| `loc:` | 位置 |
| `after:` / `before:` | 日期过滤（`YYYY-MM-DD`） |
| `lang:` | 语言限制 |
| `"phrase"` | 精确短语 |
| `-term` | 排除某词 |
| `~term` | 包含同义词 |
| `*` | 通配符 |
| `term1 OR term2` | 两个词中的任一个 |

## 搜索引擎

所有引擎共用同一接口（`adapters/base.py` 中的 `SearchEngine`），默认都有限速。要新增引擎，
只需继承 `SearchEngine` 并在 `adapters/__init__.py` 中注册。

- **Google** —— 先通过 HTTP 抓取 SERP。若 Google 返回验证码或限速拦截，则改用真实 headless
  Chromium（经 Playwright）重新渲染页面，可绕过大多数住宅网络上的行为机器人检测。在数据中心
  IP 上，Google 仍可能直接在 IP 层面拦截——请在 Tools → Settings 中添加代理，或改用其他引擎。
  需一次性安装 Chromium 二进制（`python -m playwright install chromium`）。若要完全合规地
  用于生产，请集成 Google Custom Search JSON API（每天 100 次免费查询）。
- **DuckDuckGo** —— 轻量 HTML 端点，在适中频率下通常容忍自动化访问。
- **Bing** —— SERP 抓取；有限速，大规模使用时可能触发机器人检查。
- **Chrome (pipe)** —— 直接在你自己的 Chrome/Chromium 浏览器中打开搜索供查看。结果不会回传
  到 LostDock；当 Google 拦截其他一切方式时，这是最简单的搜索途径。需要时可设置
  `LOSTDOCK_CHROME` 指向特定二进制。
- **All** —— 对同一查询同时运行 Google、DuckDuckGo 与 Bing 并合并结果。单个引擎被拦截不会
  中止搜索；结果按 URL 去重。

## 代理

在 **Tools → Settings** 中配置，每行一个：

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

代理按请求轮换；失败的代理进入冷却期。可使用 "validate" 路径（代码中的
`ProxyPool.validate()`）剔除失效代理。

## 定时搜索

1. 保存一个搜索（在 "Dork name" 字段命名）。
2. 在 **Tools → Settings** 中选择该搜索，设置间隔（分钟）并保存。
3. 后台调度器会运行到期的搜索，将结果存储为新任务，并推迟下次运行。

## URL 在线复检

**Re-check URLs** 按钮会在 UI 线程之外抓取当前结果中的每条 URL（带礼貌性延迟），为每行标注
`状态码`、`内容类型` 与实时 `<title>`，并将结果写回数据库。失败会就地标注，绝不会导致界面崩溃。

## 插件

将 `*.py` 文件放入 `~/.lostdock/plugins/`（或随附的 `plugins/` 目录）。插件模块可导出任意
子集：

```python
NAME = "my_plugin"

def setup(app): ...                    # 启动时执行一次
def on_result(result): return result   # 返回 None 以丢弃该结果
def on_export(results, fmt, path): ... # 导出前执行
```

可参考 `plugins/example_skip_tracking.py` 的完整示例。

## 导出

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| JSON | `.json` | 完整结构化结果 |
| CSV | `.csv` | 表格就绪（UTF-8 BOM） |
| Markdown | `.md` | 便于阅读 |
| HTML | `.html` | 自包含报告，链接可点击 |

## 数据存储

- **数据库：** `~/.lostdock/lostdock.db`（SQLite）
- **插件：** `~/.lostdock/plugins/`
- 数据表：`jobs`、`results`、`saved_dorks`、`schedules`、`settings`。旧数据库会自动迁移。

## 打包

项目包含用于 PyInstaller 的 `lostdock.spec`。按平台构建：

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec          # 生成 dist/lostdock
```

- **Windows：** `dist/lostdock.exe`，外加单文件 `lostdock-installer.exe`，无需管理员权限即可
  充当安装器、更新器与卸载器（`src/installer/windows/main.py`）。
- **macOS：** 打包为 `dist/LostDock.app`（分发前用 `codesign` 签名）。
- **Linux：** `dist/lostdock` 二进制，或封装为 AppImage/Flatpak。Arch Linux 的 `PKGBUILD`
  位于 `packaging/aur/`。

## 发布

发布由标签驱动并实现自动化。发布新版本需要 `git-cliff`（`cargo install git-cliff`）：

```bash
make release                # 提升版本、重新生成 CHANGELOG.md、提交并打标签
```

`make release` 会读取自上次标签以来的 conventional commits 以确定下一个 semver 版本（也可显式
传入：`./scripts/release.sh 0.2.0`）。随后它会提升 `pyproject.toml` 与
`src/lostdock/__init__.py` 中的版本、运行测试套件、重新生成 `CHANGELOG.md` 并创建带注释的
`vX.Y.Z` 标签。

推送标签会触发 CI：构建 Windows 与 Linux 二进制以及自签名 Windows 安装器，然后通过
[git-cliff](https://git-cliff.org) 发布带自动生成说明（分组的功能/修复、issue 引用与贡献者）
的 GitHub Release。

## 开发

```bash
uv run pytest                     # 运行测试套件
uv run python -m compileall -q src  # 导入健全性检查
uv run ruff check src tests       # 代码检查
```

项目结构：

```
src/lostdock/
├── core/         Dork 模型、操作符、查询编译器、限速器、代理池
├── adapters/     Google / DuckDuckGo / Bing / Chrome 适配器、浏览器渲染器
├── services/     repository、query、filter、crawler、scheduler、exporter、plugins
├── ui/           PySide6 组件：dork builder、results grid、worker、settings、theme、main window
└── main.py       入口
src/installer/    Windows 安装器/更新器/卸载器
tests/            pytest 套件（compiler、engines、services、proxy、scheduler、plugins）
```

## 免责声明

LostDock 是一款**安全研究与 OSINT 工具**。请仅针对你拥有或明确获准测试的系统使用。请遵守
搜索引擎的服务条款：保持低速率、负责任地使用代理，切勿将本工具用于未授权访问、抓取个人数据
或任何违法活动。作者不对滥用行为负责。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
