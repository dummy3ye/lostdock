# LostDock

**LostDock** ist ein industrietaugliches, plattformübergreifendes Desktop-Tool für Google Dorking,
geschrieben in Python. Es bietet einen visuellen Query-Builder mit allen Suchmaschinen-Operatoren,
Multi-Engine-Ausführung mit Ratenbegrenzung und Proxy-Rotation, persistente Ergebnisspeicherung,
Live-URL-Überprüfung, geplante Dorks, Regex-Hervorhebung und ein Plugin-System — alles in einer
nativen PySide6- (Qt-) Oberfläche für **Windows, macOS und Linux**.

> Vollständige Dokumentation: [README.md](README.md)

---

## Funktionen

- **Visueller Dork-Builder** — kombinieren Sie Schlüsselwörter, exakte Phrasen, boolesche Logik
  (`AND`/`OR`/`NOT`), Ausschlüsse, Pflichtbegriffe, Seiten, Dateitypen und alle Google-Operatoren
  mit Live-Vorschau.
- **Multi-Engine** — Google-, DuckDuckGo- und Bing-Adapter hinter einer gemeinsamen Schnittstelle.
- **Ratenbegrenzung & Anti-Block** — Token-Bucket-Limiter mit Jitter, rotierende User-Agents,
  Retries mit Backoff und CAPTCHA/Bot-Erkennung.
- **Proxy-Rotation** — Proxy-Pool mit Round-Robin, Fehler-Cooldown und Validierung.
- **Persistente Speicherung** — jede Aufgabe und jedes Ergebnis in SQLite, engineübergreifend dedupliziert.
- **Live-URL-Überprüfung** — ruft URLs erneut ab und annotiert Statuscode / Inhaltstyp / Titel.
- **Geplante Dorks** — führt gespeicherte Dorks in regelmäßigen Abständen im Hintergrund aus.
- **Regex-Hervorhebung** — hebt passende Zeilen sofort hervor.
- **Filter** — Domain-Whitelist/Blacklist und URL-Regex-Filter (beim Export).
- **Export** — JSON, CSV, Markdown und ein gestylter, eigenständiger HTML-Bericht.
- **Dork-Bibliothek** — Dorks benennen, speichern, laden und löschen.
- **Plugin-System** — Python-Module in `~/.lostdock/plugins/` mit Hooks `setup`, `on_result`, `on_export`.
- **Plattformübergreifend** — ein Code, verpackt für Windows (`.exe`), macOS (`.app`) und Linux.

## Kurzanleitung

1. Query aufbauen: Schlüsselwörter, exakte Phrase, Ausschlüsse, `AND`/`OR`-Begriffe, Seiten (`site:`),
   Dateitypen und Inline-Operatoren.
2. Engine und Seitenzahl wählen.
3. **Run Search** klicken — Ergebnisse fließen in die Tabelle und werden in SQLite gespeichert.
4. Mit **Re-check URLs** den Live-Status jedes Ergebnisses prüfen.
5. Ein **Highlight**-Regex setzen, um interessante Zeilen hervorzuheben.
6. **Export...** klicken, um als JSON, CSV, Markdown oder HTML zu speichern.

## Unterstützte Operatoren

`site:` · `inurl:` · `allinurl:` · `intitle:` · `allintitle:` · `intext:` · `allintext:` · `inanchor:` ·
`filetype:` · `ext:` · `cache:` · `link:` · `related:` · `info:` · `define:` · `author:` · `daterange:` ·
`numrange:` · `loc:` · `after:` · `before:` · `lang:` · exakte Phrase `"..."` · Ausschluss `-term` ·
Synonym `~term` · Platzhalter `*` · `term1 OR term2`.

## Proxies

Konfigurieren unter **Tools → Settings**, eine pro Zeile:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

## Geplante Dorks

1. Einen Dork speichern (im Feld „Dork name" benennen).
2. Unter **Tools → Settings** auswählen und Intervall in Minuten festlegen.
3. Der Scheduler führt ihn im Hintergrund aus und speichert Ergebnisse als neue Aufgaben.

## Plugins

Legen Sie `*.py`-Dateien in `~/.lostdock/plugins/` ab. Ein Modul kann jede Teilmenge exportieren:

```python
NAME = "my_plugin"
def setup(app): ...
def on_result(result): return result   # None zurückgeben, um zu verwerfen
def on_export(results, fmt, path): ...
```

## Datenspeicherung

- **Datenbank:** `~/.lostdock/lostdock.db` (SQLite)
- **Plugins:** `~/.lostdock/plugins/`

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

LostDock ist ein **Werkzeug für Sicherheitsforschung und OSINT**. Verwenden Sie es nur gegen Systeme,
die Ihnen gehören oder für die Sie ausdrücklich autorisiert sind. Respektieren Sie die Nutzungsbedingungen
der Suchmaschinen, halten Sie die Raten niedrig, nutzen Sie Proxies verantwortungsvoll und verwenden Sie
das Tool niemals für unbefugten Zugriff, Scraping personenbezogener Daten oder illegale Aktivitäten.

## License

MIT — siehe [LICENSE](LICENSE).
