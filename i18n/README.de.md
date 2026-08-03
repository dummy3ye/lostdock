# LostDock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#installation)

**LostDock** ist ein Desktop-Werkzeug für Google Dorking und OSINT-Recherche. Es verbindet
einen visuellen Dork-Builder mit einer Multi-Engine-Suche, Ratenbegrenzung,
Proxy-Rotation und persistenter Ergebnisspeicherung — alles in einer nativen PySide6
(Qt)-Oberfläche, die auf **Windows, macOS und Linux** läuft.

> **Lesen Sie dieses README in:** [English](../README.md) · [中文](../README.zh-CN.md) · [Español](../i18n/README.es.md) · [Français](../i18n/README.fr.md) · [हिन्दी](../i18n/README.hi.md) · [Português](../i18n/README.pt-BR.md) · [Русский](../i18n/README.ru.md) · [日本語](../README.ja.md) · [한국어](../i18n/README.ko.md) · [Italiano](../i18n/README.it.md) · [العربية](../i18n/README.ar.md)

---

## Inhaltsverzeichnis

- [Funktionen](#funktionen)
- [Architektur](#architektur)
- [Installation](#installation)
- [Verwendung](#verwendung)
- [Unterstützte Operatoren](#unterstützte-operatoren)
- [Suchmaschinen](#suchmaschinen)
- [Proxies](#proxies)
- [Geplante Dorks](#geplante-dorks)
- [URL-Neuprüfung](#url-neuprüfung)
- [Plugins](#plugins)
- [Export](#export)
- [Datenspeicherung](#datenspeicherung)
- [Packaging](#packaging)
- [Releases](#releases)
- [Entwicklung](#entwicklung)
- [Haftungsausschluss](#haftungsausschluss)
- [Lizenz](#lizenz)

---

## Funktionen

- **Visueller Dork-Builder** — kombinieren Sie Suchbegriffe, exakte Phrasen, boolesche
  Logik (`AND`/`OR`/`NOT`), Ausschlüsse, Pflichtbegriffe, Seiten, Dateitypen und alle
  Google-Operatoren mit Live-Vorschau.
- **Multi-Engine-Suche** — Google, DuckDuckGo und Bing hinter einer Oberfläche, plus ein
  Chrome-„Pipe“-Modus, der die Suche in Ihrem eigenen Browser ausführt. Oder führen Sie
  alle drei gleichzeitig aus und fassen Sie die Ergebnisse zusammen.
- **Ratenbegrenzung & Anti-Block** — Token-Bucket-Limiter mit Jitter, rotierende
  User-Agents, Backoff-Wiederholungen und CAPTCHA/Bot-Erkennung. Google weicht auf einen
  Headless-Chromium-Renderer aus, wenn einfaches HTTP blockiert wird.
- **Proxy-Rotation** — Proxy-Pool mit Round-Robin-Rotation, Fehler-Cooldown und
  Validierung.
- **Persistente Speicherung** — jeder Job und jedes Ergebnis in SQLite, engineübergreifend
  dedupliziert.
- **Live-URL-Neuprüfung** — gespeicherte URLs neu abrufen und Statuscode, Content-Type und
  Titel annotieren.
- **Geplante Dorks** — gespeicherte Dorks in regelmäßigen Abständen im Hintergrund
  ausführen.
- **Regex-Hervorhebung** — Zeilen, die einem Muster entsprechen, sofort hervorheben.
- **Filter** — Domain-Whitelist/Blacklist und URL-Regex-Keep-Filter beim Export.
- **Export** — JSON, CSV, Markdown und ein gestylter, eigenständiger HTML-Bericht.
- **Dork-Bibliothek** — Dorks nach Namen speichern, laden und verwalten.
- **Plugin-System** — Python-Module mit `setup`-, `on_result`- und `on_export`-Hooks
  einbinden.
- **Themes** — dunkle, helle und klassische Win98-GDI-Stile.
- **Plattformübergreifend** — eine Codebasis für Windows, macOS und Linux, mit einem
  Windows-Installer/Updater.

## Architektur

```
┌─ UI-Ebene (PySide6/Qt) ────────────────────────────────┐
│  Dork Builder │ Results Grid │ Scheduler │ Settings      │
│  Themes (dark / light / win98)                          │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  Service-Ebene                                            │
│  Repository │ Query │ Filter │ Crawler │ Scheduler │      │
│  Exporter │ Plugins                                       │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  Kern-Engine                                               │
│  Adapters (Google / DuckDuckGo / Bing / Chrome)           │
│  Multi-Engine (all) │ Rate Limiter │ Proxy Pool           │
│  Compiler │ Operators                                     │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  SQLite (jobs, results, dorks, schedules, config)         │
└───────────────────────────────────────────────────────────┘
```

## Installation

> Die Installationsanleitung ist bewusst nur auf Englisch verfügbar.

### Voraussetzungen

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **uv** (schneller Paketmanager) — [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### Schritte

```bash
# 1. Repository klonen
git clone https://github.com/dummy3ye/lostdock.git
cd lostdock

# 2. Virtuelle Umgebung erstellen und installieren
uv venv
uv pip install -e ".[dev]"

# 3. Das Headless-Chromium installieren, das der Anti-Block-Fallback von Google nutzt
uv run python -m playwright install chromium

# 4. Ausführen
uv run lostdock
```

Falls Sie kein `uv` haben, geht es auch mit einfachem `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
lostdock
```

### Alternative: Aus der Repo-Wurzel ohne Installation ausführen

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main   # offscreen für Headless-Tests
```

## Verwendung

1. **Abfrage erstellen** — Suchbegriffe eingeben, exakte Phrase, Ausschlüsse, `AND`/`OR`-
   Begriffe, Seiten (`site:`), Dateitypen und Inline-Operatoren hinzufügen. Die kompilierte
   Abfrage aktualisiert sich live.
2. **Engine wählen** — Google, DuckDuckGo, Bing, Chrome oder „all“ — und die Seitenzahl.
3. **Run Search** klicken. Die Ergebnisse fließen in die Tabelle; jedes Ergebnis wird in
   SQLite gespeichert.
4. **Re-check URLs** verwenden, um jedes Ergebnis abzurufen und seinen Live-Status zu
   annotieren.
5. Ein **Highlight**-Regex setzen, um interessante Zeilen hervorzuheben.
6. **Export...** klicken, um als JSON, CSV, Markdown oder HTML-Bericht zu speichern.

## Unterstützte Operatoren

Der Builder unterstützt den vollständigen Google-Operatorensatz:

| Operator | Bedeutung |
|----------|-----------|
| `site:` | Ergebnisse auf eine Domain beschränken |
| `inurl:` / `allinurl:` | Wörter in der URL |
| `intitle:` / `allintitle:` | Wörter im Titel |
| `intext:` / `allintext:` | Wörter im Fließtext |
| `inanchor:` | Wörter im Ankertext von Links |
| `filetype:` / `ext:` | Auf einen Dateityp beschränken |
| `cache:` | Googles gecachte Version |
| `link:` | Seiten, die auf eine URL verlinken |
| `related:` | Ähnliche Seiten |
| `info:` | Seitenübersicht |
| `define:` | Definition eines Begriffs |
| `author:` | Autor eines Ergebnisses |
| `daterange:` / `numrange:` | Zahlenbereiche |
| `loc:` | Ort |
| `after:` / `before:` | Datumsfilter (`YYYY-MM-DD`) |
| `lang:` | Spracheinschränkung |
| `"phrase"` | Exakte Phrase |
| `-term` | Begriff ausschließen |
| `~term` | Synonyme einbeziehen |
| `*` | Platzhalter |
| `term1 OR term2` | Einer der beiden Begriffe |

## Suchmaschinen

Alle Engines teilen sich dieselbe Schnittstelle (`SearchEngine` in `adapters/base.py`) und
sind standardmäßig ratenbegrenzt. Fügen Sie eine Engine hinzu, indem Sie `SearchEngine`
ableiten und sie in `adapters/__init__.py` registrieren.

- **Google** — scrapet zuerst die SERP per HTTP. Antwortet Google mit CAPTCHA oder
  Ratenlimit-Block, wird die Seite in einem echten Headless-Chromium (via Playwright) neu
  gerendert, was die verhaltensbasierte Bot-Erkennung auf den meisten Heimnetzen umgeht.
  Auf Rechenzentrum-IPs blockt Google möglicherweise ohnehin auf IP-Ebene — fügen Sie
  Proxies unter Tools → Settings hinzu oder verwenden Sie eine andere Engine. Erfordert
  das Chromium-Binary einmalig (`python -m playwright install chromium`). Für vollständig
  konforme Produktion integrieren Sie die Google Custom Search JSON API (100 kostenlose
  Abfragen/Tag).
- **DuckDuckGo** — schlanker HTML-Endpunkt, bei moderater Nutzung meist tolerant gegenüber
  automatisiertem Zugriff.
- **Bing** — SERP-Scraping; ratenbegrenzt und bei großem Umfang anfällig für Bot-Checks.
- **Chrome (pipe)** — öffnet die Suche direkt in Ihrem eigenen Chrome/Chromium-Browser zur
  Ansicht dort. Es werden keine Ergebnisse zurück in LostDock übernommen; es ist der
  einfachste Weg zu suchen, wenn Google alles andere blockt. Setzen Sie `LOSTDOCK_CHROME`,
  um bei Bedarf auf ein bestimmtes Binary zu zeigen.
- **All** — führt Google, DuckDuckGo und Bing für dieselbe Abfrage aus und fasst die
  Ergebnisse zusammen. Eine blockierte Engine bricht die Suche nie ab; Ergebnisse werden
  per URL dedupliziert.

## Proxies

Legen Sie Proxies unter **Tools → Settings** fest. Einer pro Zeile:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

Proxies rotieren pro Anfrage; fehlgeschlagene Proxies gehen in eine Cooldown-Phase.
Nutzen Sie den „validate“-Pfad (im Code `ProxyPool.validate()`), um tote Proxies zu
entfernen.

## Geplante Dorks

1. Einen Dork speichern (im Feld „Dork name“ benennen).
2. Unter **Tools → Settings** den Dork auswählen, ein Intervall in Minuten festlegen und
   speichern.
3. Ein Hintergrund-Scheduler führt fällige Dorks aus, speichert Ergebnisse als neue Jobs
   und setzt die nächste Ausführung herauf.

## URL-Neuprüfung

Der **Re-check URLs**-Button ruft jede URL der aktuellen Ergebnisse außerhalb des UI-Threads
mit Höflichkeitsverzögerungen ab, annotiert jede Zeile mit `Statuscode`, `Content-Type` und
einem Live-`<title>` und persistiert die Ergebnisse in der Datenbank. Fehler werden inline
annotiert und bringen die UI nie zum Absturz.

## Plugins

Legen Sie `*.py`-Dateien in `~/.lostdock/plugins/` ab (oder im mitgelieferten Verzeichnis
`plugins/`). Ein Plugin-Modul kann jede Teilmenge exportieren:

```python
NAME = "my_plugin"

def setup(app): ...                    # einmalig beim Start
def on_result(result): return result   # None zurückgeben, um das Ergebnis zu verwerfen
def on_export(results, fmt, path): ... # vor dem Export
```

Siehe `plugins/example_skip_tracking.py` für ein funktionierendes Beispiel.

## Export

| Format | Erweiterung | Hinweise |
|--------|-------------|----------|
| JSON | `.json` | Vollständige strukturierte Ergebnisse |
| CSV | `.csv` | Tabellenkalkulationsbereit (UTF-8 BOM) |
| Markdown | `.md` | Menschenlesbar |
| HTML | `.html` | Eigenständiger Bericht, klickbare Links |

## Datenspeicherung

- **Datenbank:** `~/.lostdock/lostdock.db` (SQLite)
- **Plugins:** `~/.lostdock/plugins/`
- Tabellen: `jobs`, `results`, `saved_dorks`, `schedules`, `settings`. Alte Datenbanken
  migrieren automatisch.

## Packaging

Das Projekt enthält eine `lostdock.spec` für PyInstaller. Plattformspezifisch bauen:

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec          # erstellt dist/lostdock
```

- **Windows:** `dist/lostdock.exe`, plus eine eindateiige `lostdock-installer.exe`, die als
  Installer, Updater und Deinstaller ohne Admin-Rechte fungiert
  (`src/installer/windows/main.py`).
- **macOS:** als `dist/lostdock.app` bündeln (mit `codesign` für die Verteilung
  signieren).
- **Linux:** `dist/lostdock`-Binary oder in ein AppImage/Flatpak verpacken. Ein Arch-Linux-
  `PKGBUILD` liegt unter `packaging/aur/`.

## Releases

Releases sind tag-getrieben und automatisiert. Für ein neues Release wird `git-cliff`
benötigt (`cargo install git-cliff`):

```bash
make release                # Version erhöhen, CHANGELOG.md regenerieren, committen und tagen
```

`make release` liest die Conventional Commits seit dem letzten Tag, um die nächste SemVer-
Version zu ermitteln (oder eine explizite übergeben: `./scripts/release.sh 0.2.0`). Danach
erhöht es die Version in `pyproject.toml` und `src/lostdock/__init__.py`, führt die
Test-Suite aus, regeneriert `CHANGELOG.md` und erstellt einen annotierten `vX.Y.Z`-Tag.

Das Pushen des Tags löst das CI aus, das die Windows- und Linux-Binaries und den
selbstsignierten Windows-Installer baut und dann eine GitHub-Release mit automatisch
generierten Notizen (gruppierte Features/Fixes, Issue-Referenzen und Mitwirkende) via
[git-cliff](https://git-cliff.org) veröffentlicht.

## Entwicklung

```bash
uv run pytest                     # Test-Suite ausführen
uv run python -m compileall -q src  # Imports prüfen (Sanity-Check)
uv run ruff check src tests       # Lint
```

Projektstruktur:

```
src/lostdock/
├── core/         Dork-Modell, Operatoren, Query-Compiler, Rate Limiter, Proxy Pool
├── adapters/     Google / DuckDuckGo / Bing / Chrome Adapter, Browser-Renderer
├── services/     repository, query, filter, crawler, scheduler, exporter, plugins
├── ui/           PySide6-Widgets: dork builder, results grid, worker, settings, theme, main window
└── main.py       Einstiegspunkt
src/installer/    Windows-Installer/Updater/Deinstaller
tests/            pytest-Suite (compiler, engines, services, proxy, scheduler, plugins)
```

## Haftungsausschluss

LostDock ist ein **Sicherheitsforschungs- und OSINT-Werkzeug**. Verwenden Sie es nur gegen
Systeme, die Ihnen gehören oder für die Sie ausdrücklich autorisiert sind. Respektieren Sie
die Nutzungsbedingungen der Suchmaschinen: halten Sie Raten niedrig, nutzen Sie Proxies
verantwortungsvoll und verwenden Sie dieses Werkzeug niemals für unbefugten Zugriff, das
Scraping persönlicher Daten oder illegale Aktivitäten. Die Autoren sind nicht für
Fehlgebrauch verantwortlich.

## Lizenz

MIT — siehe [LICENSE](../LICENSE).
