# LostDock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#instalación)

**LostDock** es una herramienta de escritorio para Google dorking e investigación OSINT.
Combina un constructor visual de consultas con búsqueda multi-motor, limitación de
velocidad, rotación de proxies y almacenamiento persistente de resultados — todo en una
interfaz nativa PySide6 (Qt) que funciona en **Windows, macOS y Linux**.

> **Lee este README en:** [English](../README.md) · [中文](../README.zh-CN.md) · [Français](../i18n/README.fr.md) · [Deutsch](../i18n/README.de.md) · [हिन्दी](../i18n/README.hi.md) · [Português](../i18n/README.pt-BR.md) · [Русский](../i18n/README.ru.md) · [日本語](../README.ja.md) · [한국어](../i18n/README.ko.md) · [Italiano](../i18n/README.it.md) · [العربية](../i18n/README.ar.md)

---

## Tabla de contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Uso](#uso)
- [Operadores compatibles](#operadores-compatibles)
- [Motores de búsqueda](#motores-de-búsqueda)
- [Proxies](#proxies)
- [Dorks programados](#dorks-programados)
- [Re-verificación de URLs](#re-verificación-de-urls)
- [Plugins](#plugins)
- [Exportación](#exportación)
- [Almacenamiento de datos](#almacenamiento-de-datos)
- [Empaquetado](#empaquetado)
- [Lanzamientos](#lanzamientos)
- [Desarrollo](#desarrollo)
- [Aviso legal](#aviso-legal)
- [Licencia](#licencia)

---

## Características

- **Constructor visual de dorks** — combina palabras clave, frases exactas, lógica
  booleana (`AND`/`OR`/`NOT`), exclusiones, términos requeridos, sitios, tipos de archivo
  y todos los operadores de Google, con vista previa en vivo.
- **Búsqueda multi-motor** — Google, DuckDuckGo y Bing tras una sola interfaz, además de
  un modo Chrome "pipe" que ejecuta la búsqueda en tu propio navegador. O ejecuta los tres
  a la vez y combina los resultados.
- **Limitación y anti-bloqueo** — limitador token-bucket con jitter, User-Agents rotativos,
  reintentos con backoff y detección de CAPTCHA/bot. Google recurre a un Chromium headless
  cuando el HTTP plano es bloqueado.
- **Rotación de proxies** — pool de proxies con rotación round-robin, enfriamiento ante
  fallos y validación.
- **Almacenamiento persistente** — cada tarea y resultado en SQLite, deduplicado entre
  motores.
- **Re-verificación de URLs en vivo** — vuelve a descargar las URLs almacenadas y anota el
  código de estado, el tipo de contenido y el título.
- **Dorks programados** — ejecuta dorks guardados a intervalos recurrentes en segundo plano.
- **Resaltado regex** — resalta al instante las filas que coinciden con un patrón.
- **Filtros** — lista blanca/negra de dominios y filtros de retención por regex de URL al
  exportar.
- **Exportación** — JSON, CSV, Markdown y un informe HTML autocontenido con estilo.
- **Biblioteca de dorks** — guarda, carga y administra dorks por nombre.
- **Sistema de plugins** — añade módulos Python con hooks `setup`, `on_result` y `on_export`.
- **Temas** — estilos oscuro, claro y Win98 GDI clásico.
- **Multiplataforma** — un solo código empaquetado para Windows, macOS y Linux, con un
  instalador/actualizador para Windows.

## Arquitectura

```
┌─ Capa de UI (PySide6/Qt) ──────────────────────────────┐
│  Dork Builder │ Results Grid │ Scheduler │ Settings     │
│  Themes (dark / light / win98)                         │
└───────────────┬─────────────────────────────────────────┘
┌───────────────▼─────────────────────────────────────────┐
│  Capa de servicios                                       │
│  Repository │ Query │ Filter │ Crawler │ Scheduler │     │
│  Exporter │ Plugins                                      │
└───────────────┬─────────────────────────────────────────┘
┌───────────────▼─────────────────────────────────────────┐
│  Motor principal                                         │
│  Adapters (Google / DuckDuckGo / Bing / Chrome)          │
│  Multi-Engine (all) │ Rate Limiter │ Proxy Pool          │
│  Compiler │ Operators                                    │
└───────────────┬─────────────────────────────────────────┘
┌───────────────▼─────────────────────────────────────────┐
│  SQLite (jobs, results, dorks, schedules, config)        │
└──────────────────────────────────────────────────────────┘
```

## Instalación

> Las instrucciones de instalación se proporcionan intencionalmente solo en inglés.

### Requisitos

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **uv** (gestor de paquetes rápido) — [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### Pasos

```bash
# 1. Clona el repositorio
git clone https://github.com/dummy3ye/lostdock.git
cd lostdock

# 2. Crea un entorno virtual e instala
uv venv
uv pip install -e ".[dev]"

# 3. Instala el Chromium headless usado por el fallback anti-bloqueo de Google
uv run python -m playwright install chromium

# 4. Ejecuta
uv run lostdock
```

Si no tienes `uv`, puedes usar `pip` directamente:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
lostdock
```

### Alternativa: ejecutar desde la raíz del repositorio sin instalar

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main   # offscreen para pruebas headless
```

## Uso

1. **Construye una consulta** — escribe palabras clave, añade una frase exacta,
   exclusiones, términos `AND`/`OR`, sitios (`site:`), tipos de archivo y operadores
   inline. La consulta compilada se actualiza en vivo.
2. **Elige un motor** — Google, DuckDuckGo, Bing, Chrome o "all" — y el número de páginas.
3. Haz clic en **Run Search**. Los resultados fluyen a la tabla; cada resultado se
   persiste en SQLite.
4. Usa **Re-check URLs** para descargar cada resultado y anotar su estado en vivo.
5. Define un **Highlight** regex para resaltar filas interesantes.
6. Haz clic en **Export...** para guardar como JSON, CSV, Markdown o informe HTML.

## Operadores compatibles

El constructor admite el conjunto completo de operadores de Google:

| Operador | Significado |
|----------|-------------|
| `site:` | Restringe resultados a un dominio |
| `inurl:` / `allinurl:` | Palabras en la URL |
| `intitle:` / `allintitle:` | Palabras en el título |
| `intext:` / `allintext:` | Palabras en el cuerpo del texto |
| `inanchor:` | Palabras en el texto del enlace |
| `filetype:` / `ext:` | Restringe a un tipo de archivo |
| `cache:` | Versión en caché de Google |
| `link:` | Páginas que enlazan a una URL |
| `related:` | Páginas similares |
| `info:` | Resumen de la página |
| `define:` | Definición de un término |
| `author:` | Autor de un resultado |
| `daterange:` / `numrange:` | Rangos numéricos |
| `loc:` | Ubicación |
| `after:` / `before:` | Filtros de fecha (`YYYY-MM-DD`) |
| `lang:` | Restricción de idioma |
| `"phrase"` | Frase exacta |
| `-term` | Excluir un término |
| `~term` | Incluir sinónimos |
| `*` | Comodín |
| `term1 OR term2` | Cualquiera de los términos |

## Motores de búsqueda

Todos los motores comparten la misma interfaz (`SearchEngine` en `adapters/base.py`) y
tienen limitación de velocidad por defecto. Añade un motor nuevo subclasificando
`SearchEngine` y registrándolo en `adapters/__init__.py`.

- **Google** — primero obtiene la SERP por HTTP. Si Google responde con un CAPTCHA o un
  bloqueo por límite de velocidad, vuelve a renderizar la página en un Chromium headless
  real (vía Playwright), lo que elude la detección de bots en la mayoría de redes
  residenciales. En IPs de datacenter Google puede bloquear a nivel de IP de todos modos —
  añade proxies en Tools → Settings, o usa otro motor. Requiere el binario de Chromium una
  vez (`python -m playwright install chromium`). Para un uso de producción totalmente
  conforme, integra la API Google Custom Search JSON (100 consultas gratuitas al día).
- **DuckDuckGo** — endpoint HTML ligero, generalmente tolerante al acceso automatizado a
  ritmos moderados.
- **Bing** — scraping de la SERP; con limitación y posible bloqueo por bots a escala.
- **Chrome (pipe)** — abre la búsqueda directamente en tu propio navegador
  Chrome/Chromium para que la revises allí. No se capturan resultados de vuelta a
  LostDock; es la forma más simple de buscar cuando Google bloquea todo lo demás. Define
  `LOSTDOCK_CHROME` para apuntar a un binario concreto si es necesario.
- **All** — ejecuta Google, DuckDuckGo y Bing para la misma consulta y combina los
  resultados. Un motor bloqueado nunca aborta la búsqueda; los resultados se deduplican
  por URL.

## Proxies

Configúralos en **Tools → Settings**. Uno por línea:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

Los proxies rotan por petición; los que fallan entran en un período de enfriamiento. Usa
la ruta "validate" (en código, `ProxyPool.validate()`) para descartar proxies muertos.

## Dorks programados

1. Guarda un dork (ponle nombre en el campo "Dork name").
2. En **Tools → Settings**, selecciona el dork, define un intervalo en minutos y guarda.
3. Un planificador en segundo plano ejecuta los dorks pendientes, almacena los resultados
   como nuevas tareas y adelanta la siguiente ejecución.

## Re-verificación de URLs

El botón **Re-check URLs** descarga cada URL de los resultados actuales fuera del hilo de
la UI, con retardos de cortesía, anota cada fila con `código de estado`, `tipo de
contenido` y un `<title>` en vivo, y persiste los resultados en la base de datos. Los
fallos se anotan en línea y nunca rompen la UI.

## Plugins

Coloca archivos `*.py` en `~/.lostdock/plugins/` (o en el directorio `plugins/`
incluido). Un módulo de plugin puede exportar cualquier subconjunto:

```python
NAME = "my_plugin"

def setup(app): ...                    # una vez al inicio
def on_result(result): return result   # devuelve None para descartar el resultado
def on_export(results, fmt, path): ... # antes de exportar
```

Consulta `plugins/example_skip_tracking.py` para un ejemplo funcional.

## Exportación

| Formato | Extensión | Notas |
|---------|-----------|-------|
| JSON | `.json` | Resultados estructurados completos |
| CSV | `.csv` | Listo para hoja de cálculo (UTF-8 BOM) |
| Markdown | `.md` | Legible para humanos |
| HTML | `.html` | Informe autocontenido, enlaces clicables |

## Almacenamiento de datos

- **Base de datos:** `~/.lostdock/lostdock.db` (SQLite)
- **Plugins:** `~/.lostdock/plugins/`
- Tablas: `jobs`, `results`, `saved_dorks`, `schedules`, `settings`. Las bases de datos
  antiguas migran automáticamente.

## Empaquetado

El proyecto incluye un `lostdock.spec` para PyInstaller. Compila por plataforma:

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec          # crea dist/lostdock
```

- **Windows:** `dist/lostdock.exe`, más un `lostdock-installer.exe` de un solo archivo
  que actúa como instalador, actualizador y desinstalador sin derechos de administrador
  (`src/installer/windows/main.py`).
- **macOS:** empaquétalo en `dist/LostDock.app` (firma con `codesign` para distribuir).
- **Linux:** binario `dist/lostdock`, o envuélvelo en un AppImage/Flatpak. Un `PKGBUILD`
  de Arch Linux vive en `packaging/aur/`.

## Lanzamientos

Los lanzamientos se gestionan por tags y están automatizados. Para cortar un nuevo
lanzamiento necesitas `git-cliff` (`cargo install git-cliff`):

```bash
make release                # sube la versión, regenera CHANGELOG.md, hace commit y tag
```

`make release` lee los conventional commits desde el último tag para elegir la siguiente
versión semver (o pásale una explícita: `./scripts/release.sh 0.2.0`). Luego sube la
versión en `pyproject.toml` y `src/lostdock/__init__.py`, ejecuta la suite de tests,
regenera `CHANGELOG.md` y crea un tag anotado `vX.Y.Z`.

Empujar el tag dispara el CI, que compila los binarios de Windows y Linux y el instalador
de Windows auto-firmado, y publica un GitHub Release con notas autogeneradas (features y
fixes agrupados, referencias a issues y contribuyentes) vía
[git-cliff](https://git-cliff.org).

## Desarrollo

```bash
uv run pytest                     # ejecuta la suite de tests
uv run python -m compileall -q src  # sanity-check de imports
uv run ruff check src tests       # lint
```

Estructura del proyecto:

```
src/lostdock/
├── core/         modelo de Dork, operadores, compilador de consultas, rate limiter, proxy pool
├── adapters/     adaptadores Google / DuckDuckGo / Bing / Chrome, renderizador de navegador
├── services/     repository, query, filter, crawler, scheduler, exporter, plugins
├── ui/           widgets PySide6: dork builder, results grid, worker, settings, theme, main window
└── main.py       punto de entrada
src/installer/    instalador/actualizador/desinstalador de Windows
tests/            suite pytest (compiler, engines, services, proxy, scheduler, plugins)
```

## Aviso legal

LostDock es una herramienta de **investigación de seguridad y OSINT**. Úsala solo contra
sistemas que sean tuyos o sobre los que tengas autorización explícita. Respeta los
términos de servicio de los buscadores: mantén límites de velocidad bajos, usa los proxies
con responsabilidad y nunca utilices esta herramienta para accesos no autorizados, scraping
de datos personales o cualquier actividad ilegal. Los autores no son responsables del mal
uso.

## Licencia

MIT — consulta [LICENSE](../LICENSE).
