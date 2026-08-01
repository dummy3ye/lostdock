# LostDock

**LostDock** è uno strumento desktop multipiattaforma di livello industriale per il Google dorking,
scritto in Python. Offre un costruttore visivo di query con tutti gli operatori dei motori di ricerca,
esecuzione multi-motore con limitazione di velocità e rotazione dei proxy, archiviazione persistente dei
risultati, riverifica delle URL, dork programmati, evidenziazione regex e un sistema di plugin — il tutto
in un'interfaccia nativa PySide6 (Qt) che funziona su **Windows, macOS e Linux**.

> Documentazione completa: [README.md](../README.md)

---

## Funzionalità

- **Costruttore visivo di dork** — combina parole chiave, frasi esatte, logica booleana
  (`AND`/`OR`/`NOT`), esclusioni, termini obbligatori, siti, tipi di file e tutti gli operatori di Google,
  con anteprima in tempo reale.
- **Multi-motore** — adapter per Google, DuckDuckGo e Bing dietro un'unica interfaccia.
- **Limitazione e anti-blocco** — limitatore token-bucket con jitter, User-Agent rotativi,
  nuovi tentativi con backoff e rilevamento di CAPTCHA/bot.
- **Rotazione dei proxy** — pool di proxy con rotazione round-robin, cooldown sui guasti e validazione.
- **Archiviazione persistente** — ogni attività e risultato in SQLite, deduplicato tra i motori.
- **Riverifica delle URL** — scarica di nuovo le URL salvate e annota codice di stato / tipo di contenuto / titolo.
- **Dork programmati** — esegue i dork salvati a intervalli ricorrenti in background.
- **Evidenziazione regex** — evidenzia all'istante le righe che corrispondono a un pattern.
- **Filtri** — whitelist/blacklist di domini e filtri di conservazione per regex di URL (in fase di esportazione).
- **Esportazione** — JSON, CSV, Markdown e un report HTML autonomo e stilizzato.
- **Libreria di dork** — denomina, salva, carica ed elimina i dork.
- **Sistema di plugin** — moduli Python in `~/.lostdock/plugins/` con hook `setup`, `on_result`, `on_export`.
- **Multipiattaforma** — un unico codice impacchettato per Windows (`.exe`), macOS (`.app`) e Linux.

## Utilizzo rapido

1. Costruisci la query: parole chiave, frase esatta, esclusioni, termini `AND`/`OR`, siti (`site:`),
   tipi di file e operatori inline.
2. Scegli il motore e il numero di pagine.
3. Clicca su **Run Search**: i risultati affluiscono nella tabella e vengono salvati in SQLite.
4. Usa **Re-check URLs** per verificare lo stato in tempo reale di ogni risultato.
5. Imposta un **Highlight** regex per mettere in evidenza le righe interessanti.
6. Clicca su **Export...** per salvare come JSON, CSV, Markdown o HTML.

## Operatori supportati

`site:` · `inurl:` · `allinurl:` · `intitle:` · `allintitle:` · `intext:` · `allintext:` · `inanchor:` ·
`filetype:` · `ext:` · `cache:` · `link:` · `related:` · `info:` · `define:` · `author:` · `daterange:` ·
`numrange:` · `loc:` · `after:` · `before:` · `lang:` · frase esatta `"..."` · esclusione `-term` ·
sinonimo `~term` · jolly `*` · `term1 OR term2`.

## Proxy

Configurali in **Tools → Settings**, uno per riga:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

## Dork programmati

1. Salva un dork (dai un nome nel campo "Dork name").
2. In **Tools → Settings**, selezionalo e imposta l'intervallo in minuti.
3. Lo scheduler lo esegue in background e salva i risultati come nuove attività.

## Plugin

Metti i file `*.py` in `~/.lostdock/plugins/`. Un modulo può esportare qualsiasi sottoinsieme:

```python
NAME = "my_plugin"
def setup(app): ...
def on_result(result): return result   # restituisci None per scartare
def on_export(results, fmt, path): ...
```

## Archiviazione dati

- **Database:** `~/.lostdock/lostdock.db` (SQLite)
- **Plugin:** `~/.lostdock/plugins/`

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

LostDock è uno **strumento di ricerca sulla sicurezza e OSINT**. Usalo solo contro sistemi di tua
proprietà o per i quali hai esplicita autorizzazione. Rispetta i Termini di Servizio dei motori di ricerca,
mantieni basse le velocità, usa i proxy in modo responsabile e non impiegarlo mai per accessi non autorizzati,
scraping di dati personali o attività illecite.

## License

MIT — vedi [LICENSE](LICENSE).
