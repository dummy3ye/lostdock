# Usage Guide

This walks through the LostDock interface from the first query to the exported report.

## The main window

LostDock is a two-panel window: the **dork builder** on the left, the **results table**
on the right, with a toolbar and menus on top.

- **Engine** dropdown — Google, DuckDuckGo, Bing, Chrome (pipe), or "all". The default is
  Chrome (pipe). See [Search engines](engines.md).
- **Pages** spin box — how many result pages to fetch (1–20).
- **Run Search / Cancel** — start or abort a search.
- **Saved** dropdown with **Save / Load / Delete** — manage your saved dork library.
- **Re-check URLs** — re-fetch the current results and annotate live status.
- **Export...** — save the current results to a file.

Menus: **File** (save/load/delete dork, export, quit), **Edit** (undo/redo/cut/copy/paste,
find in results), **View** (toggle status bar, pick a theme), **Tools** (Settings, Re-check
URLs), **Help** (dorking reference, about, report issue, check for updates).

## Building a dork

The builder turns form fields into a Google-compatible query. The compiled query is
previewed live as you type.

| Field | What it does | Example |
|-------|--------------|---------|
| Keywords | plain search terms | `login password` |
| Dork name | optional name used to save the dork | `default creds` |
| Exact phrase | wrapped in quotes | `"admin login"` |
| Exclude (-) | comma-separated, each becomes `-term` | `wiki, stackoverflow` |
| Must have (AND) | comma-separated, all must appear | `admin, password` |
| Any of (OR) | comma-separated, wrapped in `(a OR b)` | `php, asp` |
| Sites (site:) | comma-separated domains | `example.com, *.org` |
| inurl: | text that must appear in the URL | `inurl:admin` |
| intitle: | text in the page `<title>` | `intitle:login` |
| intext: | text in the page body | `intext:password` |
| after: / before: | date filters (`YYYY-MM-DD`) | `after:2024-01-01` |
| File types | checkboxes emitting `filetype:` filters, grouped by category | `pdf`, `docx`, `xls` |

File types are grouped into **Documents**, **Media**, **Spreadsheets & Data**, and
**Code & Web**, each with a "Select All" toggle. Only types Google actually indexes are
included.

### Example query

With keywords `admin`, exact phrase `"default password"`, exclude `example.com`,
site `example.org`, and file type `pdf`, the compiled query is:

```
"default password" admin -example.com site:example.org filetype:pdf
```

## Running a search

1. Build the dork.
2. Choose an engine and page count.
3. Click **Run Search**.

Results stream into the table as they arrive (each row: position, title, URL, snippet,
engine, status). Every result is persisted to SQLite immediately, and results are
deduplicated across engines when using the "all" engine. Click **Cancel** to stop early.

## Saving and loading dorks

- **Save** stores the current builder state under the "Dork name" value.
- **Load** fills the builder from the selected saved dork.
- **Delete** removes the selected dork.

Saved dorks are the same ones the scheduler runs; see [Scheduled dorks](scheduler.md).

## Re-checking URLs

**Re-check URLs** fetches each URL in the current results sequentially off the UI thread,
so the interface stays responsive. Each row is annotated with:

- **status** — HTTP status code and content type (e.g. `200 text/html`); failed fetches
  show `ERR <reason>`
- **content type** — e.g. `text/html`
- **title** — the live `<title>` of the page

Results are written back to the database, so the annotations survive restart. Failures
are annotated inline and never crash the UI.

## Highlighting

- **Highlight** (regex field in the builder) — rows whose URL, title, or snippet match
  the pattern are highlighted. Invalid regexes are ignored silently.
- **Edit → Find in Results (Ctrl+F)** — prompts for a regex and applies it as the row
  highlight.

## Filters (applied on export)

At the bottom of the dork builder, before exporting, you can set:

- **Allow only** — keep only these domains (comma-separated; matches the domain and its
  subdomains).
- **Block** — drop these domains.
- **URL pattern** — keep only URLs matching this regex.
- **Highlight** — highlight rows matching a regex (see above).

The whitelist/blacklist/pattern filter is applied when exporting, so the saved file
contains exactly what you want.

## Export

**Export...** writes the current (filtered) results. See [Packaging: exports](../README.md#export)
for the four formats: JSON, CSV, Markdown, and a self-contained HTML report.

## Themes

**View → Theme** toggles between the built-in themes:

- **Dark** / **Light** — modern flat palettes.
- **Win98**, **Win98 Dark**, **Win98 Pink** — a Windows 9x GDI recreation with hard
  orthogonal edges and 1px bevels.

The status bar (toggle via **View → Toggle Status Bar**) shows progress messages and the
last scheduler run.
