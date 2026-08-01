# LostDock

**LostDock** é uma ferramenta de desktop multiplataforma de nível industrial para Google dorking,
escrita em Python. Ela oferece um construtor visual de consultas com todos os operadores de busca,
execução multi-motor com limitação de taxa e rotação de proxies, armazenamento persistente de resultados,
reverificação de URLs, dorks agendados, destaque por regex e um sistema de plugins — tudo em uma interface
nativa PySide6 (Qt) que roda em **Windows, macOS e Linux**.

> Documentação completa: [README.md](../README.md)

---

## Recursos

- **Construtor visual de dorks** — combine palavras-chave, frases exatas, lógica booleana
  (`AND`/`OR`/`NOT`), exclusões, termos obrigatórios, sites, tipos de arquivo e todos os operadores do
  Google, com pré-visualização ao vivo.
- **Multi-motor** — adaptadores para Google, DuckDuckGo e Bing atrás de uma única interface.
- **Limitação e anti-bloqueio** — limitador token-bucket com jitter, User-Agents rotativos,
  novas tentativas com backoff e detecção de CAPTCHA/bot.
- **Rotação de proxies** — pool de proxies com rotação round-robin, cooldown por falha e validação.
- **Armazenamento persistente** — cada tarefa e resultado em SQLite, deduplicado entre motores.
- **Reverificação de URLs** — recarrega as URLs armazenadas e anota código de status / tipo de conteúdo / título.
- **Dorks agendados** — executa dorks salvos em intervalos recorrentes em segundo plano.
- **Destaque por regex** — destaca linhas que correspondem a um padrão instantaneamente.
- **Filtros** — whitelist/blacklist de domínios e filtros de retenção por regex de URL (na exportação).
- **Exportação** — JSON, CSV, Markdown e um relatório HTML autônomo e estilizado.
- **Biblioteca de dorks** — nomeie, salve, carregue e exclua dorks.
- **Sistema de plugins** — módulos Python em `~/.lostdock/plugins/` com hooks `setup`, `on_result`, `on_export`.
- **Multiplataforma** — um único código empacotado para Windows (`.exe`), macOS (`.app`) e Linux.

## Uso rápido

1. Monte a consulta: palavras-chave, frase exata, exclusões, termos `AND`/`OR`, sites (`site:`),
   tipos de arquivo e operadores inline.
2. Escolha o motor e o número de páginas.
3. Clique em **Run Search**: os resultados fluem para a tabela e são persistidos no SQLite.
4. Use **Re-check URLs** para verificar o status ao vivo de cada resultado.
5. Defina um **Highlight** regex para realçar linhas interessantes.
6. Clique em **Export...** para salvar como JSON, CSV, Markdown ou HTML.

## Operadores suportados

`site:` · `inurl:` · `allinurl:` · `intitle:` · `allintitle:` · `intext:` · `allintext:` · `inanchor:` ·
`filetype:` · `ext:` · `cache:` · `link:` · `related:` · `info:` · `define:` · `author:` · `daterange:` ·
`numrange:` · `loc:` · `after:` · `before:` · `lang:` · frase exata `"..."` · exclusão `-term` ·
sinônimo `~term` · curinga `*` · `term1 OR term2`.

## Proxies

Configure em **Tools → Settings**, um por linha:

```
http://127.0.0.1:8080
socks5://127.0.0.1:1080
```

## Dorks agendados

1. Salve um dork (nomeie-o no campo "Dork name").
2. Em **Tools → Settings**, selecione-o e defina o intervalo em minutos.
3. O agendador o executa em segundo plano e salva os resultados como novas tarefas.

## Plugins

Coloque arquivos `*.py` em `~/.lostdock/plugins/`. Um módulo pode exportar qualquer subconjunto:

```python
NAME = "my_plugin"
def setup(app): ...
def on_result(result): return result   # retorne None para descartar
def on_export(results, fmt, path): ...
```

## Armazenamento

- **Banco de dados:** `~/.lostdock/lostdock.db` (SQLite)
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

LostDock é uma **ferramenta de pesquisa em segurança e OSINT**. Use-a somente contra sistemas que você
possui ou sobre os quais está explicitamente autorizado a testar. Respeite os Termos de Serviço dos
mecanismos de busca, mantenha taxas baixas, use proxies com responsabilidade e nunca a utilize para
acesso não autorizado, raspagem de dados pessoais ou atividades ilícitas.

## License

MIT — veja [LICENSE](LICENSE).
