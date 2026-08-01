# LostDock

**LostDock** est un outil de bureau multiplateforme de niveau industriel pour le Google dorking,
écrit en Python. Il fournit un constructeur visuel de requêtes avec tous les opérateurs de moteur de
recherche, une exécution multi-moteur avec limitation de débit et rotation de proxies, un stockage
persistant des résultats, une revérification d'URL en direct, des dorks planifiés, un surlignage regex
et un système de plugins — le tout dans une interface native PySide6 (Qt) fonctionnant sur
**Windows, macOS et Linux**.

> Documentation complète dans [README.md](README.md)

---

## Fonctionnalités

- **Constructeur visuel de dorks** — combinez mots-clés, phrases exactes, logique booléenne
  (`AND`/`OR`/`NOT`), exclusions, termes requis, sites, types de fichiers et tous les opérateurs Google,
  avec aperçu de la requête en direct.
- **Multi-moteur** — adaptateurs Google, DuckDuckGo et Bing derrière une interface unique.
- **Limitation et anti-blocage** — limiteur token-bucket avec jitter, User-Agents rotatifs,
  relances avec backoff et détection de CAPTCHA/bot.
- **Rotation de proxies** — pool de proxies avec rotation round-robin, refroidissement et validation.
- **Stockage persistant** — chaque tâche et résultat dans SQLite, dédupliqué entre moteurs.
- **Revérification d'URL** — re-télécharge les URL et annote code de statut / type de contenu / titre.
- **Dorks planifiés** — exécute des dorks enregistrés à intervalle récurrent en arrière-plan.
- **Surlignage regex** — surligne instantanément les lignes correspondantes.
- **Filtres** — liste blanche/noire de domaines et filtres de conservation par regex d'URL (à l'export).
- **Export** — JSON, CSV, Markdown et un rapport HTML autonome et stylisé.
- **Bibliothèque de dorks** — nommez, enregistrez, chargez et supprimez des dorks.
- **Système de plugins** — modules Python dans `~/.lostdock/plugins/` avec hooks `setup`, `on_result`, `on_export`.
- **Multiplateforme** — un seul code empaqueté pour Windows (`.exe`), macOS (`.app`) et Linux.

## Utilisation rapide

1. Construisez la requête : mots-clés, phrase exacte, exclusions, termes `AND`/`OR`, sites (`site:`),
   types de fichiers et opérateurs en ligne.
2. Choisissez le moteur et le nombre de pages.
3. Cliquez sur **Run Search** : les résultats affluent dans le tableau et sont persistés dans SQLite.
4. Utilisez **Re-check URLs** pour vérifier l'état en direct de chaque résultat.
5. Définissez un **Highlight** regex pour repérer les lignes intéressantes.
6. Cliquez sur **Export...** pour enregistrer en JSON, CSV, Markdown ou HTML.

## Opérateurs pris en charge

`site:` · `inurl:` · `allinurl:` · `intitle:` · `allintitle:` · `intext:` · `allintext:` · `inanchor:` ·
`filetype:` · `ext:` · `cache:` · `link:` · `related:` · `info:` · `define:` · `author:` · `daterange:` ·
`numrange:` · `loc:` · `after:` · `before:` · `lang:` · phrase exacte `"..."` · exclusion `-term` ·
synonyme `~term` · joker `*` · `term1 OR term2`.

## Proxies

Configurez-les dans **Tools → Settings**, un par ligne :

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

## Dorks planifiés

1. Enregistrez un dork (nommez-le dans le champ « Dork name »).
2. Dans **Tools → Settings**, sélectionnez-le et fixez l'intervalle en minutes.
3. Le planificateur l'exécute en arrière-plan et stocke les résultats comme nouvelles tâches.

## Plugins

Placez des fichiers `*.py` dans `~/.lostdock/plugins/`. Un module peut exporter tout sous-ensemble :

```python
NAME = "my_plugin"
def setup(app): ...
def on_result(result): return result   # renvoyer None pour écarter
def on_export(results, fmt, path): ...
```

## Stockage

- **Base de données :** `~/.lostdock/lostdock.db` (SQLite)
- **Plugins :** `~/.lostdock/plugins/`

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

LostDock est un **outil de recherche en sécurité et d'OSINT**. Utilisez-le uniquement contre des
systèmes que vous possédez ou êtes explicitement autorisé à tester. Respectez les Conditions d'Utilisation
des moteurs de recherche, restez modéré, utilisez les proxies de façon responsable et ne l'utilisez jamais
pour un accès non autorisé, le scraping de données personnelles ou toute activité illicite.

## License

MIT — voir [LICENSE](LICENSE).
