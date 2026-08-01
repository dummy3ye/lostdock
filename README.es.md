# LostDock

**LostDock** es una herramienta de escritorio de nivel industrial, multiplataforma, para Google dorking,
escrita en Python. Ofrece un constructor visual de consultas con todos los operadores de búsqueda,
ejecución multi-motor con limitación de velocidad y rotación de proxies, almacenamiento persistente de
resultados, re-verificación de URLs, dorks programados, resaltado regex y un sistema de plugins — todo en
una interfaz nativa PySide6 (Qt) que funciona en **Windows, macOS y Linux**.

> Documentación completa en [README.md](README.md)

---

## Características

- **Constructor visual de dorks** — combina palabras clave, frases exactas, lógica booleana
  (`AND`/`OR`/`NOT`), exclusiones, términos requeridos, sitios, tipos de archivo y todos los operadores
  de Google, con vista previa en vivo.
- **Multi-motor** — adaptadores de Google, DuckDuckGo y Bing tras una misma interfaz.
- **Limitación y anti-bloqueo** — limitador token-bucket con jitter, User-Agents rotativos,
  reintentos con backoff y detección de CAPTCHA/bot.
- **Rotación de proxies** — pool de proxies con rotación round-robin, enfriamiento por fallos y validación.
- **Almacenamiento persistente** — cada tarea y resultado en SQLite, deduplicado entre motores.
- **Re-verificación de URLs** — vuelve a descargar las URLs y anota código de estado / tipo de contenido / título.
- **Dorks programados** — ejecuta dorks guardados en un intervalo recurrente en segundo plano.
- **Resaltado regex** — resalta filas que coinciden con un patrón al instante.
- **Filtros** — lista blanca/negra de dominios y filtros de retención por regex de URL (al exportar).
- **Exportación** — JSON, CSV, Markdown y un informe HTML autocontenido con estilo.
- **Biblioteca de dorks** — nombra, guarda, carga y elimina dorks.
- **Sistema de plugins** — módulos Python en `~/.lostdock/plugins/` con hooks `setup`, `on_result` y `on_export`.
- **Multiplataforma** — un único código empaquetado para Windows (`.exe`), macOS (`.app`) y Linux.

## Uso rápido

1. Construye la consulta: palabras clave, frase exacta, exclusiones, términos `AND`/`OR`, sitios (`site:`),
   tipos de archivo y operadores en línea.
2. Elige el motor y el número de páginas.
3. Pulsa **Run Search**: los resultados fluyen a la tabla y se persisten en SQLite.
4. Usa **Re-check URLs** para verificar el estado en vivo de cada resultado.
5. Define un **Highlight** regex para destacar filas de interés.
6. Pulsa **Export...** para guardar como JSON, CSV, Markdown o HTML.

## Operadores soportados

`site:` · `inurl:` · `allinurl:` · `intitle:` · `allintitle:` · `intext:` · `allintext:` · `inanchor:` ·
`filetype:` · `ext:` · `cache:` · `link:` · `related:` · `info:` · `define:` · `author:` · `daterange:` ·
`numrange:` · `loc:` · `after:` · `before:` · `lang:` · frase exacta `"..."` · exclusión `-term` ·
sinónimo `~term` · comodín `*` · `term1 OR term2`.

## Proxies

Configúralos en **Tools → Settings**, uno por línea:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

## Dorks programados

1. Guarda un dork (nómbralo en el campo "Dork name").
2. En **Tools → Settings**, selecciónalo y fija el intervalo en minutos.
3. El planificador lo ejecuta en segundo plano y guarda los resultados como nuevas tareas.

## Plugins

Coloca archivos `*.py` en `~/.lostdock/plugins/`. Puedes exportar cualquier subconjunto:

```python
NAME = "my_plugin"
def setup(app): ...
def on_result(result): return result   # devuelve None para descartar
def on_export(results, fmt, path): ...
```

## Almacenamiento

- **Base de datos:** `~/.lostdock/lostdock.db` (SQLite)
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

LostDock es una **herramienta de investigación de seguridad y OSINT**. Úsala únicamente contra
sistemas de tu propiedad o sobre los que tengas autorización explícita. Respeta las Condiciones de
Servicio de los buscadores, mantén límites bajos, usa los proxies con responsabilidad y nunca la
utilices para acceso no autorizado, scraping de datos personales o actividades ilícitas.

## License

MIT — ver [LICENSE](LICENSE).
