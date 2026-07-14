# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An MCP (Model Context Protocol) server, in Python, exposing 10 tools that search hardware categories on Pichau (a Brazilian PC parts retailer): processors, coolers, motherboards, memory, GPUs, storage, cases, power supplies, monitors, and keyboards. It talks to Pichau's internal `api/request/monte-*` JSON endpoints — the same ones that back Pichau's "build your PC" tool — not a public/documented API.

## Commands

```bash
uv run server.py              # run the MCP server locally (stdio transport)
uv run pytest tests/ -v       # full test suite
uv run pytest tests/test_client.py -v      # cache/retry tests only (mocked, no network)
uv run pytest tests/test_chaining.py -v    # cross-tool chaining smoke test (hits real API)
uv run scripts/check_catalogs.py           # diff hardcoded filter catalogs against live Pichau aggregations
```

No lint/format tooling is configured. Dependencies are managed with `uv` (`uv add <pkg>` / `uv add --dev <pkg>`); don't edit `pyproject.toml` dependencies by hand.

## Architecture

### The Cloudflare problem (read this before touching HTTP)

Pichau sits behind Cloudflare bot management, which fingerprints the TLS handshake (JA3). A plain `curl`/`httpx`/`requests`-style client gets a 403 "Site em Manutenção" page even with a convincing `User-Agent` header, while a real browser or Postman gets through — the giveaway is the TLS fingerprint, not headers. `pichau_mcp/client.py` uses `curl_cffi` with `impersonate="chrome124"` to work around this. Do not swap in a different HTTP library without confirming it survives this fingerprinting (test with `uv run python3 -c "from curl_cffi.requests import Session; ..."` against a live `monte-*` endpoint).

### Request flow

`server.py` (stdio MCP entrypoint) → `pichau_mcp/tools.py` (`TOOLS` list + `HANDLERS` dict, keyed by tool name) → each `handle_search_*` validates/resolves filter arguments, builds a `params` dict, and calls `pichau_mcp/client.py::fetch_products(endpoint, params)` → response items are passed through a `_format_*` function before being returned as JSON text.

`fetch_products` caches successful responses in-memory for 45s keyed by `(endpoint, sorted params)`, and retries transient failures (network errors, non-200 status) up to 3 times with linear backoff. Cache/retry live entirely in `client.py`; tool handlers never see failures that were successfully retried.

### Filter catalogs are hand-maintained, not dynamic

Each `monte-*` endpoint has its own filter parameter names (e.g. processors use `plataforma`/`marcas`/`socket`; coolers use `socket`/`marcas`; PSUs use `potencia_fonte`/`modular_fonte`/`eficiencia_fonte`). The valid values for name-based filters (brands, sockets, GPU models, etc.) are hardcoded as `{"Human Name": "pichau_code", ...}` dicts in `pichau_mcp/tools.py`, built from that endpoint's `aggregations` response. This is a deliberate tradeoff: building these dynamically at request time would couple every tool call to Pichau/Cloudflare being reachable. Instead, run `uv run scripts/check_catalogs.py` periodically (or when a "valor inválido" report comes in) to see what drifted upstream and update the dicts by hand.

**Not every filter Pichau exposes in `aggregations` is actually honored by its backend.** Several were tested and found to be silently ignored (the request succeeds but doesn't narrow results): `price` (all categories), `nucleo`/core-count (processors), and `layout`/`iluminacao`/`macro` (keyboards), `frequencia_monitor`/`resolucao_monitor`/`tipo_de_painel`/`tamanho_da_tela`/`tempo_de_resposta`/`conexoes_monitor` (monitors). These were deliberately left out of the corresponding tool's `inputSchema` rather than shipped as filters that silently no-op. Before adding a new filter for any category, verify it actually narrows results (compare `total_pages` with and without the filter against the live API) rather than trusting that an `aggregations` entry implies a working filter.

Also confirmed *not* to exist: any server-side page-size parameter (`pageSize`, `limit`, `per_page`, etc. were all tried) — Pichau always returns a fixed page size, so `max_results` is enforced client-side by slicing (`items[:max_results]`) after fetching a full page.

### Cross-tool chaining and the raw-code-vs-text-label trap

Several tools are meant to be chained: a `search_processors` result's `socket` field feeds into `search_coolers`/`search_motherboards`'s `socket` parameter; a `search_motherboards` result's `form_factor` field feeds into `search_cases`'s `form_factor` parameter. Pichau's filter parameters take raw internal codes (e.g. `"6689"`), not human-readable text (e.g. `"AMD AM5"`).

Every formatter that returns a chainable field exposes **both** the raw code (unsuffixed, e.g. `socket`, `form_factor` — this is what downstream tools require) and a human-readable counterpart (suffixed `_name`, e.g. `socket_name`, `form_factor_name` — for display only). A prior regression swapped these (the raw-code field returned the text label instead), which silently broke the three chained tools with `total_pages: 0` and was invisible without live end-to-end testing. `tests/test_chaining.py` exists specifically to catch this class of bug — it asserts the chained fields are numeric codes and that chaining them actually returns non-empty results against the live API. Run it after touching any `_format_*` function.

`search_cases`'s `form_factor` is the one exception: it accepts either the raw code or a human name (e.g. `"ATX"`), resolved internally, so it also works standalone without going through `search_motherboards` first.

### Adding a new tool for a category

Follow the existing pattern in `pichau_mcp/tools.py`: a `Tool(...)` definition (JSON Schema `inputSchema`), a catalog dict per name-based filter (built from that endpoint's live `aggregations`, verified filter-by-filter as above), a `_format_<category>` function, and a `handle_search_<category>` async function that resolves filter args to Pichau codes via `_resolve_codes`/`_resolve_code`, builds the `params` dict, calls `fetch_products`, and formats results. Register the tool in both the `TOOLS` list and `HANDLERS` dict at the bottom of the file.
