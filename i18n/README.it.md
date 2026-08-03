# LostDock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#installazione)

**LostDock** è uno strumento desktop per il Google dorking e la ricerca OSINT. Abbina un
costruttore visivo di query alla ricerca multi-motore, alla limitazione della velocità, alla
rotazione dei proxy e all'archiviazione persistente dei risultati — il tutto in
un'interfaccia nativa PySide6 (Qt) che funziona su **Windows, macOS e Linux**.

> **Leggi questo README in:** [English](../README.md) · [中文](../README.zh-CN.md) · [Español](../i18n/README.es.md) · [Français](../i18n/README.fr.md) · [Deutsch](../i18n/README.de.md) · [हिन्दी](../i18n/README.hi.md) · [Português](../i18n/README.pt-BR.md) · [Русский](../i18n/README.ru.md) · [日本語](../README.ja.md) · [한국어](../i18n/README.ko.md) · [العربية](../i18n/README.ar.md)

---

## Indice dei contenuti

- [Funzionalità](#funzionalità)
- [Architettura](#architettura)
- [Installazione](#installazione)
- [Utilizzo](#utilizzo)
- [Operatori supportati](#operatori-supportati)
- [Motori di ricerca](#motori-di-ricerca)
- [Proxy](#proxy)
- [Dork programmati](#dork-programmati)
- [Riverifica delle URL](#riverifica-delle-url)
- [Plugin](#plugin)
- [Esportazione](#esportazione)
- [Archiviazione dei dati](#archiviazione-dei-dati)
- [Packaging](#packaging)
- [Release](#release)
- [Sviluppo](#sviluppo)
- [Disclaimer](#disclaimer)
- [Licenza](#licenza)

---

## Funzionalità

- **Costruttore visivo di dork** — combina parole chiave, frasi esatte, logica booleana
  (`AND`/`OR`/`NOT`), esclusioni, termini obbligatori, siti, tipi di file e tutti gli
  operatori Google, con anteprima della query in tempo reale.
- **Ricerca multi-motore** — Google, DuckDuckGo e Bing dietro un'unica interfaccia, più un
  modo Chrome "pipe" che esegue la ricerca nel tuo browser. Oppure esegui tutti e tre
  insieme e combina i risultati.
- **Limitazione e anti-blocco** — limitatore token-bucket con jitter, User-Agent rotativi,
  nuovi tentativi con backoff e rilevamento di CAPTCHA/bot. Google ripiega su un rendering
  Chromium headless quando l'HTTP semplice viene bloccato.
- **Rotazione dei proxy** — pool di proxy con rotazione round-robin, cooldown sugli errori
  e validazione.
- **Archiviazione persistente** — ogni job e risultato in SQLite, deduplicato tra i motori.
- **Riverifica delle URL in tempo reale** — riscarica le URL memorizzate e annota codice di
  stato, tipo di contenuto e titolo.
- **Dork programmati** — esegue i dork salvati a intervalli ricorrenti in background.
- **Evidenziazione regex** — evidenzia istantaneamente le righe che corrispondono a un
  pattern.
- **Filtri** — whitelist/blacklist di domini e filtri di mantenimento per regex di URL
  applicati all'esportazione.
- **Esportazione** — JSON, CSV, Markdown e un report HTML autonomo e stilizzato.
- **Libreria di dork** — salva, carica e gestisci i dork per nome.
- **Sistema di plugin** — aggiungi moduli Python con hook `setup`, `on_result` e
  `on_export`.
- **Temi** — stili scuro, chiaro e Win98 GDI classico.
- **Multipiattaforma** — un solo codice impacchettato per Windows, macOS e Linux, con un
  installer/updater per Windows.

## Architettura

```
┌─ Livello UI (PySide6/Qt) ──────────────────────────────┐
│  Dork Builder │ Results Grid │ Scheduler │ Settings      │
│  Temi (dark / light / win98)                            │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  Livello servizi                                          │
│  Repository │ Query │ Filter │ Crawler │ Scheduler │      │
│  Exporter │ Plugins                                       │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  Motore principale                                        │
│  Adapters (Google / DuckDuckGo / Bing / Chrome)           │
│  Multi-Engine (all) │ Rate Limiter │ Proxy Pool           │
│  Compiler │ Operators                                     │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  SQLite (jobs, results, dorks, schedules, config)         │
└───────────────────────────────────────────────────────────┘
```

## Installazione

> Le istruzioni di installazione sono volutamente fornite solo in inglese.

### Prerequisiti

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **uv** (gestore di pacchetti veloce) — [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### Passaggi

```bash
# 1. Clona il repository
git clone https://github.com/dummy3ye/lostdock.git
cd lostdock

# 2. Crea un ambiente virtuale e installa
uv venv
uv pip install -e ".[dev]"

# 3. Installa il Chromium headless usato dal fallback anti-blocco di Google
uv run python -m playwright install chromium

# 4. Esegui
uv run lostdock
```

Se non hai `uv`, puoi usare direttamente `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
lostdock
```

### Alternativa: eseguire dalla radice del repository senza installare

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main   # offscreen per test headless
```

## Utilizzo

1. **Costruisci una query** — inserisci parole chiave, aggiungi una frase esatta,
   esclusioni, termini `AND`/`OR`, siti (`site:`), tipi di file e operatori inline. La
   query compilata si aggiorna in tempo reale.
2. **Scegli un motore** — Google, DuckDuckGo, Bing, Chrome o "all" — e il numero di pagine.
3. Fai clic su **Run Search**. I risultati confluiscono nella tabella; ogni risultato viene
   salvato in SQLite.
4. Usa **Re-check URLs** per scaricare ogni risultato e annotare il suo stato in tempo
   reale.
5. Imposta un **Highlight** regex per evidenziare le righe interessanti.
6. Fai clic su **Export...** per salvare come JSON, CSV, Markdown o report HTML.

## Operatori supportati

Il builder supporta l'intero set di operatori Google:

| Operatore | Significato |
|-----------|-------------|
| `site:` | Limita i risultati a un dominio |
| `inurl:` / `allinurl:` | Parole nell'URL |
| `intitle:` / `allintitle:` | Parole nel titolo |
| `intext:` / `allintext:` | Parole nel corpo del testo |
| `inanchor:` | Parole nel testo di ancoraggio dei link |
| `filetype:` / `ext:` | Limita a un tipo di file |
| `cache:` | Versione cache di Google |
| `link:` | Pagine che puntano a un URL |
| `related:` | Pagine simili |
| `info:` | Panoramica della pagina |
| `define:` | Definizione di un termine |
| `author:` | Autore di un risultato |
| `daterange:` / `numrange:` | Intervalli numerici |
| `loc:` | Posizione |
| `after:` / `before:` | Filtri data (`YYYY-MM-DD`) |
| `lang:` | Restrizione della lingua |
| `"phrase"` | Frase esatta |
| `-term` | Escludi un termine |
| `~term` | Includi sinonimi |
| `*` | Jolly |
| `term1 OR term2` | Uno o l'altro termine |

## Motori di ricerca

Tutti i motori condividono la stessa interfaccia (`SearchEngine` in `adapters/base.py`) e
sono limitati in velocità per impostazione predefinita. Aggiungi un motore sottoclassando
`SearchEngine` e registrandolo in `adapters/__init__.py`.

- **Google** — scarica prima la SERP via HTTP. Se Google risponde con un CAPTCHA o un
  blocco per limiti di velocità, ri-renderizza la pagina in un vero Chromium headless (via
  Playwright), che aggira il rilevamento comportamentale dei bot sulla maggior parte delle
  reti residenziali. Su IP di datacenter Google può comunque bloccare a livello IP —
  aggiungi proxy in Tools → Settings oppure usa un altro motore. Richiede il binario
  Chromium una volta (`python -m playwright install chromium`). Per un uso di produzione
  pienamente conforme, integra l'API JSON Google Custom Search (100 query gratuite/giorno).
- **DuckDuckGo** — endpoint HTML leggero, generalmente tollerante all'accesso automatizzato
  a ritmi moderati.
- **Bing** — scraping della SERP; limitato in velocità e soggetto a controlli anti-bot su
  larga scala.
- **Chrome (pipe)** — apre la ricerca direttamente nel tuo browser Chrome/Chromium per
  consultarla lì. Nessun risultato viene catturato in LostDock; è il modo più semplice per
  cercare quando Google blocca tutto il resto. Imposta `LOSTDOCK_CHROME` per puntare a un
  binario specifico se necessario.
- **All** — esegue Google, DuckDuckGo e Bing per la stessa query e combina i risultati. Un
  motore bloccato non interrompe mai la ricerca; i risultati sono deduplicati per URL.

## Proxy

Configurali in **Tools → Settings**. Uno per riga:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

I proxy ruotano per richiesta; quelli in errore entrano in un periodo di cooldown. Usa il
percorso "validate" (nel codice, `ProxyPool.validate()`) per rimuovere i proxy morti.

## Dork programmati

1. Salva un dork (dai un nome nel campo "Dork name").
2. In **Tools → Settings**, seleziona il dork, imposta un intervallo in minuti e salva.
3. Uno scheduler in background esegue i dork in scadenza, salva i risultati come nuovi job e
   posticipa la prossima esecuzione.

## Riverifica delle URL

Il pulsante **Re-check URLs** scarica ogni URL dei risultati correnti fuori dal thread
dell'interfaccia, con ritardi di cortesia, annota ogni riga con `codice di stato`, `tipo di
contenuto` e un `<title>` in tempo reale, e salva i risultati nel database. Gli errori
vengono annotati inline e non fanno mai crashare l'interfaccia.

## Plugin

Metti i file `*.py` in `~/.lostdock/plugins/` (o nella directory `plugins/` inclusa). Un
modulo plugin può esportare qualsiasi sottoinsieme:

```python
NAME = "my_plugin"

def setup(app): ...                    # una volta all'avvio
def on_result(result): return result   # restituisci None per scartare il risultato
def on_export(results, fmt, path): ... # prima dell'esportazione
```

Vedi `plugins/example_skip_tracking.py` per un esempio funzionante.

## Esportazione

| Formato | Estensione | Note |
|---------|------------|------|
| JSON | `.json` | Risultati strutturati completi |
| CSV | `.csv` | Pronto per fogli di calcolo (UTF-8 BOM) |
| Markdown | `.md` | Leggibile dall'uomo |
| HTML | `.html` | Report autonomo, link cliccabili |

## Archiviazione dei dati

- **Database:** `~/.lostdock/lostdock.db` (SQLite)
- **Plugin:** `~/.lostdock/plugins/`
- Tabelle: `jobs`, `results`, `saved_dorks`, `schedules`, `settings`. I database vecchi
  migrano automaticamente.

## Packaging

Il progetto include un `lostdock.spec` per PyInstaller. Compila per piattaforma:

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec          # crea dist/lostdock
```

- **Windows:** `dist/lostdock.exe`, più un `lostdock-installer.exe` a file singolo che agisce
  come installer, updater e uninstaller senza privilegi di amministratore
  (`src/installer/windows/main.py`).
- **macOS:** impacchetta in `dist/LostDock.app` (firma con `codesign` per la distribuzione).
- **Linux:** binario `dist/lostdock`, oppure avvolgilo in un AppImage/Flatpak. Un `PKGBUILD`
  per Arch Linux vive in `packaging/aur/`.

## Release

Le release sono guidate dai tag e automatizzate. Per pubblicare una nuova release serve
`git-cliff` (`cargo install git-cliff`):

```bash
make release                # incrementa la versione, rigenera CHANGELOG.md, committa e tagga
```

`make release` legge i conventional commit dall'ultimo tag per scegliere la prossima
versione semver (oppure passane una esplicita: `./scripts/release.sh 0.2.0`). Poi incrementa
la versione in `pyproject.toml` e `src/lostdock/__init__.py`, esegue la suite di test,
rigenera `CHANGELOG.md` e crea un tag annotato `vX.Y.Z`.

Il push del tag attiva il CI, che compila i binari Windows e Linux e l'installer Windows
auto-firmato, quindi pubblica una GitHub Release con note autogenerate (feature e fix
raggruppati, riferimenti alle issue e contributori) via
[git-cliff](https://git-cliff.org).

## Sviluppo

```bash
uv run pytest                     # esegue la suite di test
uv run python -m compileall -q src  # sanity-check degli import
uv run ruff check src tests       # lint
```

Struttura del progetto:

```
src/lostdock/
├── core/         modello Dork, operatori, compilatore di query, rate limiter, proxy pool
├── adapters/     adapter Google / DuckDuckGo / Bing / Chrome, renderer browser
├── services/     repository, query, filter, crawler, scheduler, exporter, plugins
├── ui/           widget PySide6: dork builder, results grid, worker, settings, theme, main window
└── main.py       punto di ingresso
src/installer/    installer/updater/uninstaller per Windows
tests/            suite pytest (compiler, engines, services, proxy, scheduler, plugins)
```

## Disclaimer

LostDock è uno **strumento di ricerca sulla sicurezza e OSINT**. Usalo solo contro sistemi
di tua proprietà o su cui sei esplicitamente autorizzato a testare. Rispetta i Termini di
Servizio dei motori di ricerca: mantieni bassi i ritmi, usa i proxy in modo responsabile e
non usare mai questo strumento per accessi non autorizzati, scraping di dati personali o
attività illegali. Gli autori non sono responsabili di un uso improprio.

## Licenza

MIT — vedi [LICENSE](../LICENSE).
