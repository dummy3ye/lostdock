# LostDock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#installation)

**LostDock** est un outil de bureau pour le Google dorking et la recherche OSINT. Il
associe un constructeur visuel de requêtes à une recherche multi-moteurs, une limitation
de débit, une rotation de proxies et un stockage persistant des résultats — le tout dans
une interface native PySide6 (Qt) fonctionnant sur **Windows, macOS et Linux**.

> **Lisez ce README en :** [English](../README.md) · [中文](../README.zh-CN.md) · [Español](../i18n/README.es.md) · [Deutsch](../i18n/README.de.md) · [हिन्दी](../i18n/README.hi.md) · [Português](../i18n/README.pt-BR.md) · [Русский](../i18n/README.ru.md) · [日本語](../README.ja.md) · [한국어](../i18n/README.ko.md) · [Italiano](../i18n/README.it.md) · [العربية](../i18n/README.ar.md)

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Opérateurs pris en charge](#opérateurs-pris-en-charge)
- [Moteurs de recherche](#moteurs-de-recherche)
- [Proxies](#proxies)
- [Dorks planifiés](#dorks-planifiés)
- [Revérification des URL](#revérification-des-url)
- [Plugins](#plugins)
- [Export](#export)
- [Stockage des données](#stockage-des-données)
- [Packaging](#packaging)
- [Versions](#versions)
- [Développement](#développement)
- [Avertissement](#avertissement)
- [Licence](#licence)

---

## Fonctionnalités

- **Constructeur visuel de dorks** — combinez mots-clés, phrases exactes, logique
  booléenne (`AND`/`OR`/`NOT`), exclusions, termes requis, sites, types de fichiers et
  tous les opérateurs Google, avec un aperçu de requête en direct.
- **Recherche multi-moteurs** — Google, DuckDuckGo et Bing derrière une interface unique,
  plus un mode Chrome « pipe » qui exécute la recherche dans votre propre navigateur. Ou
  exécutez les trois à la fois et fusionnez les résultats.
- **Limitation et anti-blocage** — limiteur token-bucket avec jitter, User-Agents
  rotatifs, nouvelles tentatives avec backoff et détection de CAPTCHA/bot. Google bascule
  vers un rendu Chromium headless lorsque le HTTP simple est bloqué.
- **Rotation de proxies** — pool de proxies avec rotation round-robin, refroidissement en
  cas d'échec et validation.
- **Stockage persistant** — chaque tâche et résultat stocké dans SQLite, dédupliqué entre
  les moteurs.
- **Revérification d'URL en direct** — re-télécharge les URL stockées et annote le code de
  statut, le type de contenu et le titre.
- **Dorks planifiés** — exécute les dorks enregistrés à intervalle récurrent en
  arrière-plan.
- **Surlignage regex** — surligne instantanément les lignes correspondant à un motif.
- **Filtres** — liste blanche/noire de domaines et filtres de conservation par regex d'URL
  appliqués à l'export.
- **Export** — JSON, CSV, Markdown et un rapport HTML autonome et stylisé.
- **Bibliothèque de dorks** — enregistrez, chargez et gérez les dorks par nom.
- **Système de plugins** — ajoutez des modules Python avec les hooks `setup`, `on_result`
  et `on_export`.
- **Thèmes** — styles sombre, clair et Win98 GDI classique.
- **Multiplateforme** — un seul code empaqueté pour Windows, macOS et Linux, avec un
  installeur/mise à jour Windows.

## Architecture

```
┌─ Couche UI (PySide6/Qt) ───────────────────────────────┐
│  Dork Builder │ Results Grid │ Scheduler │ Settings     │
│  Thèmes (dark / light / win98)                          │
└───────────────┬─────────────────────────────────────────┘
┌───────────────▼─────────────────────────────────────────┐
│  Couche de services                                      │
│  Repository │ Query │ Filter │ Crawler │ Scheduler │     │
│  Exporter │ Plugins                                      │
└───────────────┬─────────────────────────────────────────┘
┌───────────────▼─────────────────────────────────────────┐
│  Moteur central                                          │
│  Adapters (Google / DuckDuckGo / Bing / Chrome)          │
│  Multi-Engine (all) │ Rate Limiter │ Proxy Pool          │
│  Compiler │ Operators                                    │
└───────────────┬─────────────────────────────────────────┘
┌───────────────▼─────────────────────────────────────────┐
│  SQLite (jobs, results, dorks, schedules, config)        │
└──────────────────────────────────────────────────────────┘
```

## Installation

> Les instructions d'installation sont volontairement fournies en anglais uniquement.

### Prérequis

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **uv** (gestionnaire de paquets rapide) — [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### Étapes

```bash
# 1. Clonez le dépôt
git clone https://github.com/dummy3ye/lostdock.git
cd lostdock

# 2. Créez un environnement virtuel et installez
uv venv
uv pip install -e ".[dev]"

# 3. Installez le Chromium headless utilisé par le repli anti-blocage de Google
uv run python -m playwright install chromium

# 4. Lancez
uv run lostdock
```

Si vous n'avez pas `uv`, vous pouvez utiliser `pip` directement :

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
lostdock
```

### Alternative : exécuter depuis la racine du dépôt sans installer

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main   # offscreen pour les tests headless
```

## Utilisation

1. **Construisez une requête** — saisissez des mots-clés, ajoutez une phrase exacte, des
   exclusions, des termes `AND`/`OR`, des sites (`site:`), des types de fichiers et des
   opérateurs inline. La requête compilée se met à jour en direct.
2. **Choisissez un moteur** — Google, DuckDuckGo, Bing, Chrome ou « all » — et le nombre
   de pages.
3. Cliquez sur **Run Search**. Les résultats arrivent dans le tableau ; chaque résultat
   est persisté dans SQLite.
4. Utilisez **Re-check URLs** pour télécharger chaque résultat et annoter son statut en
   direct.
5. Définissez un **Highlight** regex pour mettre en évidence les lignes intéressantes.
6. Cliquez sur **Export...** pour enregistrer en JSON, CSV, Markdown ou rapport HTML.

## Opérateurs pris en charge

Le constructeur prend en charge l'ensemble complet des opérateurs Google :

| Opérateur | Signification |
|-----------|---------------|
| `site:` | Restreindre les résultats à un domaine |
| `inurl:` / `allinurl:` | Mots dans l'URL |
| `intitle:` / `allintitle:` | Mots dans le titre |
| `intext:` / `allintext:` | Mots dans le corps du texte |
| `inanchor:` | Mots dans le texte d'ancre des liens |
| `filetype:` / `ext:` | Restreindre à un type de fichier |
| `cache:` | Version en cache de Google |
| `link:` | Pages liant vers une URL |
| `related:` | Pages similaires |
| `info:` | Aperçu de la page |
| `define:` | Définition d'un terme |
| `author:` | Auteur d'un résultat |
| `daterange:` / `numrange:` | Plages numériques |
| `loc:` | Localisation |
| `after:` / `before:` | Filtres de date (`YYYY-MM-DD`) |
| `lang:` | Restriction de langue |
| `"phrase"` | Phrase exacte |
| `-term` | Exclure un terme |
| `~term` | Inclure les synonymes |
| `*` | Joker |
| `term1 OR term2` | L'un ou l'autre terme |

## Moteurs de recherche

Tous les moteurs partagent la même interface (`SearchEngine` dans `adapters/base.py`) et
sont limités en débit par défaut. Ajoutez un moteur en sous-classant `SearchEngine` et en
l'enregistrant dans `adapters/__init__.py`.

- **Google** — gratte d'abord la SERP en HTTP. Si Google répond par un CAPTCHA ou un
  blocage de limite de débit, il rend à nouveau la page dans un vrai Chromium headless (via
  Playwright), ce qui neutralise la détection comportementale de bots sur la plupart des
  réseaux résidentiels. Sur les IP de datacenter, Google peut bloquer au niveau IP de toute
  façon — ajoutez des proxies dans Tools → Settings, ou utilisez un autre moteur. Nécessite
  le binaire Chromium une fois (`python -m playwright install chromium`). Pour un usage de
  production pleinement conforme, intégrez l'API JSON Google Custom Search (100 requêtes
  gratuites/jour).
- **DuckDuckGo** — endpoint HTML léger, généralement tolérant à l'accès automatisé à des
  débits modérés.
- **Bing** — scraping de la SERP ; limité en débit et susceptible de blocs anti-bots à
  grande échelle.
- **Chrome (pipe)** — ouvre la recherche directement dans votre propre navigateur
  Chrome/Chromium pour que vous la consultiez là-bas. Aucun résultat n'est capturé dans
  LostDock ; c'est le moyen le plus simple de chercher quand Google bloque tout le reste.
  Définissez `LOSTDOCK_CHROME` pour pointer vers un binaire spécifique si nécessaire.
- **All** — exécute Google, DuckDuckGo et Bing pour la même requête et fusionne les
  résultats. Un moteur bloqué n'interrompt jamais la recherche ; les résultats sont
  dédupliqués par URL.

## Proxies

Configurez-les dans **Tools → Settings**. Un par ligne :

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

Les proxies tournent à chaque requête ; les proxies en échec entrent en période de
refroidissement. Utilisez le chemin « validate » (dans le code, `ProxyPool.validate()`)
pour supprimer les proxies morts.

## Dorks planifiés

1. Enregistrez un dork (nommez-le dans le champ « Dork name »).
2. Dans **Tools → Settings**, sélectionnez le dork, définissez un intervalle en minutes et
   enregistrez.
3. Un planificateur en arrière-plan exécute les dorks dus, stocke les résultats comme
   nouvelles tâches et repousse la prochaine exécution.

## Revérification des URL

Le bouton **Re-check URLs** télécharge chaque URL des résultats actuels hors du fil de
l'interface, avec des délais de courtoisie, annote chaque ligne avec `code de statut`,
`type de contenu` et un `<title>` en direct, et persiste les résultats dans la base de
données. Les échecs sont annotés en ligne et ne font jamais planter l'interface.

## Plugins

Placez les fichiers `*.py` dans `~/.lostdock/plugins/` (ou le répertoire `plugins/`
fourni). Un module de plugin peut exporter n'importe quel sous-ensemble :

```python
NAME = "my_plugin"

def setup(app): ...                    # une fois au démarrage
def on_result(result): return result   # renvoyer None pour écarter le résultat
def on_export(results, fmt, path): ... # avant l'export
```

Consultez `plugins/example_skip_tracking.py` pour un exemple fonctionnel.

## Export

| Format | Extension | Notes |
|--------|-----------|-------|
| JSON | `.json` | Résultats structurés complets |
| CSV | `.csv` | Prêt pour tableur (UTF-8 BOM) |
| Markdown | `.md` | Lisible par l'humain |
| HTML | `.html` | Rapport autonome, liens cliquables |

## Stockage des données

- **Base de données :** `~/.lostdock/lostdock.db` (SQLite)
- **Plugins :** `~/.lostdock/plugins/`
- Tables : `jobs`, `results`, `saved_dorks`, `schedules`, `settings`. Les anciennes bases
  de données migrent automatiquement.

## Packaging

Le projet inclut un `lostdock.spec` pour PyInstaller. Compilez par plateforme :

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec          # crée dist/lostdock
```

- **Windows :** `dist/lostdock.exe`, plus un `lostdock-installer.exe` mono-fichier qui sert
  d'installeur, de mise à jour et de désinstalleur sans droits administrateur
  (`src/installer/windows/main.py`).
- **macOS :** empaquetez dans `dist/LostDock.app` (signez avec `codesign` pour la
  distribution).
- **Linux :** binaire `dist/lostdock`, ou enveloppez-le dans un AppImage/Flatpak. Un
  `PKGBUILD` Arch Linux se trouve dans `packaging/aur/`.

## Versions

Les versions sont pilotées par les tags et automatisées. Pour publier une nouvelle
version, il faut `git-cliff` (`cargo install git-cliff`) :

```bash
make release                # incrémente la version, régénère CHANGELOG.md, commit et tag
```

`make release` lit les conventional commits depuis le dernier tag pour choisir la
prochaine version semver (ou passez-en une explicite : `./scripts/release.sh 0.2.0`). Il
incrémente ensuite la version dans `pyproject.toml` et `src/lostdock/__init__.py`, lance
la suite de tests, régénère `CHANGELOG.md` et crée un tag annoté `vX.Y.Z`.

Pousser le tag déclenche le CI, qui compile les binaires Windows et Linux et l'installeur
Windows auto-signé, puis publie une GitHub Release avec des notes autogénérées (features
et fixes groupés, références aux issues et contributeurs) via
[git-cliff](https://git-cliff.org).

## Développement

```bash
uv run pytest                     # exécute la suite de tests
uv run python -m compileall -q src  # sanity-check des imports
uv run ruff check src tests       # lint
```

Structure du projet :

```
src/lostdock/
├── core/         modèle Dork, opérateurs, compilateur de requêtes, rate limiter, proxy pool
├── adapters/     adaptateurs Google / DuckDuckGo / Bing / Chrome, rendu navigateur
├── services/     repository, query, filter, crawler, scheduler, exporter, plugins
├── ui/           widgets PySide6 : dork builder, results grid, worker, settings, theme, main window
└── main.py       point d'entrée
src/installer/    installeur/mise à jour/désinstalleur Windows
tests/            suite pytest (compiler, engines, services, proxy, scheduler, plugins)
```

## Avertissement

LostDock est un outil de **recherche en sécurité et d'OSINT**. Utilisez-le uniquement
contre des systèmes que vous possédez ou sur lesquels vous êtes explicitement autorisé à
tester. Respectez les conditions d'utilisation des moteurs de recherche : gardez des
débits faibles, utilisez les proxies de façon responsable et n'utilisez jamais cet outil
pour un accès non autorisé, le scraping de données personnelles ou toute activité illégale.
Les auteurs ne sont pas responsables d'un mauvais usage.

## Licence

MIT — voir [LICENSE](../LICENSE).
