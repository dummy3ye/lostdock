# LostDock

**LostDock** 是一款工业级、跨平台的 Google 搜索语法（Google dorking）桌面工具，使用 Python 编写。
它提供可视化查询构建器，支持全部搜索引擎操作符、多引擎执行（含速率限制与代理轮换）、
持久化结果存储、URL 在线复检、定时搜索、正则高亮，以及插件系统——全部内置在原生 PySide6（Qt）界面中，
支持 **Windows、macOS、Linux**。

> 完整文档见 [README.md](README.md)

---

## 功能

- **可视化查询构建器** — 组合关键词、精确短语、布尔逻辑（`AND`/`OR`/`NOT`）、排除词、必含词、
  站点、文件类型以及全部 Google 操作符，实时预览编译后的查询。
- **多引擎** — Google、DuckDuckGo、Bing 三个适配器共用同一接口，界面中可随时切换。
- **速率限制与反拦截** — 令牌桶限速 + 抖动、随机 User-Agent、指数退避重试、验证码/机器人检测。
- **代理轮换** — 代理池支持轮询、失败冷却、可用性验证。
- **持久化存储** — 每个任务与结果存入 SQLite，跨引擎自动去重。
- **URL 在线复检** — 重新抓取已存 URL，标注状态码 / 内容类型 / 实时标题。
- **定时搜索** — 在后台按设定间隔自动运行已保存的搜索。
- **正则高亮** — 即时高亮匹配的行。
- **结果过滤** — 域名白名单/黑名单与 URL 正则保留过滤，导出时生效。
- **导出** — JSON、CSV、Markdown，以及样式化自包含 HTML 报告。
- **保存的搜索库** — 命名、保存、加载、删除搜索。
- **插件系统** — 将 Python 模块放入 `~/.lostdock/plugins/`，支持 `setup`、`on_result`、`on_export` 钩子。
- **跨平台** — 单一代码库可打包为 Windows（`.exe`）、macOS（`.app`）、Linux。

## 快速使用

1. 构建查询：输入关键词、精确短语、排除词、`AND`/`OR` 词、站点（`site:`）、文件类型与内联操作符。
2. 选择引擎与页数。
3. 点击 **Run Search** 开始搜索，结果实时流入表格并持久化。
4. 使用 **Re-check URLs** 在线复检每个结果。
5. 设置 **Highlight** 正则突出关注行。
6. 点击 **Export...** 导出为 JSON、CSV、Markdown 或 HTML 报告。

## 支持的操作符

`site:`、`inurl:`、`allinurl:`、`intitle:`、`allintitle:`、`intext:`、`allintext:`、`inanchor:`、
`filetype:`、`ext:`、`cache:`、`link:`、`related:`、`info:`、`define:`、`author:`、`daterange:`、
`numrange:`、`loc:`、`after:`、`before:`、`lang:`、精确短语 `"..."`、排除 `-term`、同义词 `~term`、
通配符 `*`、`term1 OR term2`。

## 代理

在 **Tools → Settings** 中配置，每行一个：

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

## 定时搜索

1. 先保存搜索（在 "Dork name" 字段命名）。
2. 在 **Tools → Settings** 中选择该搜索并设置间隔（分钟）。
3. 后台调度器到期自动运行，结果作为新任务存储。

## 插件

将 `*.py` 文件放入 `~/.lostdock/plugins/`。可导出任意子集：

```python
NAME = "my_plugin"
def setup(app): ...
def on_result(result): return result   # 返回 None 则丢弃该结果
def on_export(results, fmt, path): ...
```

## 数据存储

- **数据库：** `~/.lostdock/lostdock.db`（SQLite）
- **插件目录：** `~/.lostdock/plugins/`

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

## Disclaimer

LostDock 是**安全研究与 OSINT 工具**。仅用于你拥有或明确获授权测试的系统。
遵守搜索引擎服务条款，保持低速率，合理使用代理，不得用于未授权访问、抓取个人数据或任何非法活动。

## License

MIT — 见 [LICENSE](LICENSE)。
