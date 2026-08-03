# LostDock

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#instalação)

**LostDock** é uma ferramenta de desktop para Google dorking e pesquisa OSINT. Ela combina
um construtor visual de consultas com busca multi-motor, limitação de taxa, rotação de
proxies e armazenamento persistente de resultados — tudo em uma interface nativa PySide6
(Qt) que roda em **Windows, macOS e Linux**.

> **Leia este README em:** [English](../README.md) · [中文](../README.zh-CN.md) · [Español](../i18n/README.es.md) · [Français](../i18n/README.fr.md) · [Deutsch](../i18n/README.de.md) · [हिन्दी](../i18n/README.hi.md) · [Русский](../i18n/README.ru.md) · [日本語](../README.ja.md) · [한국어](../i18n/README.ko.md) · [Italiano](../i18n/README.it.md) · [العربية](../i18n/README.ar.md)

---

## Sumário

- [Recursos](#recursos)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Uso](#uso)
- [Operadores suportados](#operadores-suportados)
- [Motores de busca](#motores-de-busca)
- [Proxies](#proxies)
- [Dorks agendados](#dorks-agendados)
- [Reverificação de URLs](#reverificação-de-urls)
- [Plugins](#plugins)
- [Exportação](#exportação)
- [Armazenamento de dados](#armazenamento-de-dados)
- [Empacotamento](#empacotamento)
- [Versões](#versões)
- [Desenvolvimento](#desenvolvimento)
- [Aviso legal](#aviso-legal)
- [Licença](#licença)

---

## Recursos

- **Construtor visual de dorks** — combine palavras-chave, frases exatas, lógica booleana
  (`AND`/`OR`/`NOT`), exclusões, termos obrigatórios, sites, tipos de arquivo e todos os
  operadores do Google, com pré-visualização ao vivo.
- **Busca multi-motor** — Google, DuckDuckGo e Bing atrás de uma única interface, além de
  um modo Chrome "pipe" que executa a busca no seu próprio navegador. Ou execute os três de
  uma vez e combine os resultados.
- **Limitação e anti-bloqueio** — limitador token-bucket com jitter, User-Agents rotativos,
  novas tentativas com backoff e detecção de CAPTCHA/bot. O Google recorre a um Chromium
  headless quando o HTTP simples é bloqueado.
- **Rotação de proxies** — pool de proxies com rotação round-robin, cooldown por falha e
  validação.
- **Armazenamento persistente** — cada tarefa e resultado em SQLite, deduplicado entre
  motores.
- **Reverificação de URLs ao vivo** — recarrega as URLs armazenadas e anota código de
  status, tipo de conteúdo e título.
- **Dorks agendados** — executa dorks salvos em intervalos recorrentes em segundo plano.
- **Destaque por regex** — destaca instantaneamente linhas que correspondem a um padrão.
- **Filtros** — whitelist/blacklist de domínios e filtros de retenção por regex de URL
  aplicados na exportação.
- **Exportação** — JSON, CSV, Markdown e um relatório HTML autônomo e estilizado.
- **Biblioteca de dorks** — salve, carregue e gerencie dorks por nome.
- **Sistema de plugins** — adicione módulos Python com hooks `setup`, `on_result` e
  `on_export`.
- **Temas** — estilos escuro, claro e Win98 GDI clássico.
- **Multiplataforma** — um único código empacotado para Windows, macOS e Linux, com um
  instalador/atualizador para Windows.

## Arquitetura

```
┌─ Camada de UI (PySide6/Qt) ────────────────────────────┐
│  Dork Builder │ Results Grid │ Scheduler │ Settings      │
│  Temas (dark / light / win98)                           │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  Camada de serviços                                       │
│  Repository │ Query │ Filter │ Crawler │ Scheduler │      │
│  Exporter │ Plugins                                       │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  Mecanismo principal                                     │
│  Adapters (Google / DuckDuckGo / Bing / Chrome)          │
│  Multi-Engine (all) │ Rate Limiter │ Proxy Pool          │
│  Compiler │ Operators                                    │
└───────────────┬──────────────────────────────────────────┘
┌───────────────▼──────────────────────────────────────────┐
│  SQLite (jobs, results, dorks, schedules, config)        │
└───────────────────────────────────────────────────────────┘
```

## Instalação

> As instruções de instalação são fornecidas intencionalmente apenas em inglês.

### Pré-requisitos

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **uv** (gerenciador de pacotes rápido) — [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/dummy3ye/lostdock.git
cd lostdock

# 2. Crie um ambiente virtual e instale
uv venv
uv pip install -e ".[dev]"

# 3. Instale o Chromium headless usado pelo fallback anti-bloqueio do Google
uv run python -m playwright install chromium

# 4. Execute
uv run lostdock
```

Se você não tiver o `uv`, pode usar `pip` diretamente:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install chromium
lostdock
```

### Alternativa: executar da raiz do repositório sem instalar

```bash
cd src
QT_QPA_PLATFORM=offscreen python -m lostdock.main   # offscreen para testes headless
```

## Uso

1. **Construa uma consulta** — digite palavras-chave, adicione uma frase exata, exclusões,
   termos `AND`/`OR`, sites (`site:`), tipos de arquivo e operadores inline. A consulta
   compilada é atualizada ao vivo.
2. **Escolha um motor** — Google, DuckDuckGo, Bing, Chrome ou "all" — e o número de páginas.
3. Clique em **Run Search**. Os resultados fluem para a tabela; cada resultado é persistido
   no SQLite.
4. Use **Re-check URLs** para buscar cada resultado e anotar seu status ao vivo.
5. Defina um **Highlight** regex para destacar linhas interessantes.
6. Clique em **Export...** para salvar como JSON, CSV, Markdown ou relatório HTML.

## Operadores suportados

O construtor suporta o conjunto completo de operadores do Google:

| Operador | Significado |
|----------|-------------|
| `site:` | Restringe os resultados a um domínio |
| `inurl:` / `allinurl:` | Palavras na URL |
| `intitle:` / `allintitle:` | Palavras no título |
| `intext:` / `allintext:` | Palavras no corpo do texto |
| `inanchor:` | Palavras no texto âncora dos links |
| `filetype:` / `ext:` | Restringe a um tipo de arquivo |
| `cache:` | Versão em cache do Google |
| `link:` | Páginas que apontam para uma URL |
| `related:` | Páginas semelhantes |
| `info:` | Visão geral da página |
| `define:` | Definição de um termo |
| `author:` | Autor de um resultado |
| `daterange:` / `numrange:` | Intervalos numéricos |
| `loc:` | Localização |
| `after:` / `before:` | Filtros de data (`YYYY-MM-DD`) |
| `lang:` | Restrição de idioma |
| `"phrase"` | Frase exata |
| `-term` | Excluir um termo |
| `~term` | Incluir sinônimos |
| `*` | Curinga |
| `term1 OR term2` | Qualquer um dos termos |

## Motores de busca

Todos os motores compartilham a mesma interface (`SearchEngine` em `adapters/base.py`) e
têm limitação de taxa por padrão. Adicione um motor subclassificando `SearchEngine` e
registrando-o em `adapters/__init__.py`.

- **Google** — primeiro obtém a SERP via HTTP. Se o Google responder com CAPTCHA ou bloqueio
  de taxa, re-renderiza a página em um Chromium headless real (via Playwright), o que
  contorna a detecção comportamental de bots na maioria das redes residenciais. Em IPs de
  datacenter o Google pode bloquear no nível de IP de qualquer forma — adicione proxies em
  Tools → Settings ou use outro motor. Requer o binário do Chromium uma vez
  (`python -m playwright install chromium`). Para uso de produção totalmente compatível,
  integre a API JSON Google Custom Search (100 consultas gratuitas/dia).
- **DuckDuckGo** — endpoint HTML leve, geralmente tolerante a acesso automatizado em ritmos
  moderados.
- **Bing** — scraping da SERP; com limitação e sujeito a verificações anti-bot em escala.
- **Chrome (pipe)** — abre a busca diretamente no seu próprio navegador Chrome/Chromium para
  você revisá-la lá. Nenhum resultado é capturado de volta no LostDock; é a forma mais
  simples de buscar quando o Google bloqueia todo o resto. Defina `LOSTDOCK_CHROME` para
  apontar para um binário específico, se necessário.
- **All** — executa Google, DuckDuckGo e Bing para a mesma consulta e combina os resultados.
  Um motor bloqueado nunca aborta a busca; os resultados são deduplicados por URL.

## Proxies

Configure em **Tools → Settings**. Um por linha:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

Os proxies rotacionam por requisição; proxies que falham entram em período de cooldown. Use
o caminho "validate" (no código, `ProxyPool.validate()`) para remover proxies mortos.

## Dorks agendados

1. Salve um dork (dê um nome no campo "Dork name").
2. Em **Tools → Settings**, selecione o dork, defina um intervalo em minutos e salve.
3. Um agendador em segundo plano executa dorks pendentes, armazena resultados como novas
   tarefas e agenda a próxima execução.

## Reverificação de URLs

O botão **Re-check URLs** busca cada URL dos resultados atuais fora da thread da UI, com
atrasos de cortesia, anota cada linha com `código de status`, `tipo de conteúdo` e um
`<title>` ao vivo, e persiste os resultados no banco de dados. Falhas são anotadas inline e
nunca derrubam a UI.

## Plugins

Coloque arquivos `*.py` em `~/.lostdock/plugins/` (ou no diretório `plugins/` incluído). Um
módulo de plugin pode exportar qualquer subconjunto:

```python
NAME = "my_plugin"

def setup(app): ...                    # uma vez na inicialização
def on_result(result): return result   # retorne None para descartar o resultado
def on_export(results, fmt, path): ... # antes da exportação
```

Veja `plugins/example_skip_tracking.py` para um exemplo funcional.

## Exportação

| Formato | Extensão | Notas |
|---------|----------|-------|
| JSON | `.json` | Resultados estruturados completos |
| CSV | `.csv` | Pronto para planilha (UTF-8 BOM) |
| Markdown | `.md` | Legível para humanos |
| HTML | `.html` | Relatório autônomo, links clicáveis |

## Armazenamento de dados

- **Banco de dados:** `~/.lostdock/lostdock.db` (SQLite)
- **Plugins:** `~/.lostdock/plugins/`
- Tabelas: `jobs`, `results`, `saved_dorks`, `schedules`, `settings`. Bancos de dados
  antigos migram automaticamente.

## Empacotamento

O projeto inclui um `lostdock.spec` para PyInstaller. Compile por plataforma:

```bash
uv pip install pyinstaller
pyinstaller lostdock.spec          # cria dist/lostdock
```

- **Windows:** `dist/lostdock.exe`, além de um `lostdock-installer.exe` de arquivo único que
  atua como instalador, atualizador e desinstalador sem direitos de administrador
  (`src/installer/windows/main.py`).
- **macOS:** empacote em `dist/LostDock.app` (assine com `codesign` para distribuição).
- **Linux:** binário `dist/lostdock`, ou envolva em um AppImage/Flatpak. Um `PKGBUILD` do
  Arch Linux está em `packaging/aur/`.

## Versões

As versões são orientadas por tags e automatizadas. Para cortar uma nova versão, é preciso
`git-cliff` (`cargo install git-cliff`):

```bash
make release                # aumenta a versão, regenera CHANGELOG.md, commita e cria tag
```

`make release` lê os conventional commits desde a última tag para escolher a próxima versão
semver (ou passe uma explícita: `./scripts/release.sh 0.2.0`). Em seguida, aumenta a versão
em `pyproject.toml` e `src/lostdock/__init__.py`, executa a suíte de testes, regenera
`CHANGELOG.md` e cria uma tag anotada `vX.Y.Z`.

Enviar a tag aciona o CI, que compila os binários Windows e Linux e o instalador Windows
auto-assinado, e publica um GitHub Release com notas geradas automaticamente (features e
fixes agrupados, referências a issues e contribuidores) via
[git-cliff](https://git-cliff.org).

## Desenvolvimento

```bash
uv run pytest                     # executa a suíte de testes
uv run python -m compileall -q src  # sanity-check dos imports
uv run ruff check src tests       # lint
```

Estrutura do projeto:

```
src/lostdock/
├── core/         modelo Dork, operadores, compilador de consultas, rate limiter, proxy pool
├── adapters/     adaptadores Google / DuckDuckGo / Bing / Chrome, renderizador de navegador
├── services/     repository, query, filter, crawler, scheduler, exporter, plugins
├── ui/           widgets PySide6: dork builder, results grid, worker, settings, theme, main window
└── main.py       ponto de entrada
src/installer/    instalador/atualizador/desinstalador do Windows
tests/            suíte pytest (compiler, engines, services, proxy, scheduler, plugins)
```

## Aviso legal

LostDock é uma ferramenta de **pesquisa em segurança e OSINT**. Use-a somente contra
sistemas que você possui ou sobre os quais tem autorização explícita para testar. Respeite
os Termos de Serviço dos mecanismos de busca: mantenha taxas baixas, use proxies com
responsabilidade e nunca use esta ferramenta para acesso não autorizado, raspagem de dados
pessoais ou qualquer atividade ilegal. Os autores não são responsáveis pelo mau uso.

## Licença

MIT — veja [LICENSE](../LICENSE).
