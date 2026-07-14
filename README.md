# pichau-mcp

MCP server que expõe ferramentas para o Claude Code buscar peças de
computador na Pichau (loja de hardware).

## Tools disponíveis

* `search_processors` — busca processadores via
  `api/request/monte-processador`, com filtros de texto (`query`),
  plataforma (`AMD`/`Intel`), marca(s), socket, vídeo integrado,
  overclock e ordenação. Cada resultado traz `socket` (código bruto,
  para encadear em `search_coolers`/`search_motherboards`) e
  `socket_name` (texto legível, ex: "AMD AM5").
* `search_coolers` — busca coolers (air/water) via
  `api/request/monte-processador-cooler`, filtrando por `socket`
  (código bruto vindo do campo `socket` — não `socket_name` — de um
  processador retornado por `search_processors`), marca(s) e ordenação.
* `search_motherboards` — busca placas-mãe via
  `api/request/monte-placa-mae`, filtrando por `socket` (mesma origem
  acima), marca(s), tipo de memória, formato da placa, características
  e ordenação. Cada resultado traz `socket`/`socket_name` e
  `form_factor`/`form_factor_name` (código bruto e texto legível).
* `search_memory` — busca memórias RAM via `api/request/monte-memoria`,
  filtrando por `memory_type` (DDR3/DDR4/DDR5, deve casar com o
  `memory_type` de uma placa-mãe retornada por `search_motherboards`),
  marca(s), frequência, capacidade e ordenação.
* `search_gpus` — busca placas de vídeo via
  `api/request/monte-placa-de-video`. Sem dependência de socket;
  filtra por marca(s), fabricante do chip (AMD/ATI, NVIDIA, INTEL) e
  modelo específico (ex: "RTX 4070 12GB").
* `search_storage` — busca HDs e SSDs (mesmo catálogo) via
  `api/request/monte-ssd`. Sem dependência de socket; filtra por
  interface (NVME/SATA), formato físico (2.5"/M.2/Placa PCIe) e
  capacidade.
* `search_cases` — busca gabinetes via `api/request/monte-gabinete`,
  filtrando por `form_factor` (obrigatório — aceita um nome como
  `"ATX"`/`"Micro ATX"`/`"E-ATX"` **ou** o código bruto do campo
  `form_factor` de uma placa-mãe retornada por `search_motherboards`,
  ambos funcionam), tipo de gabinete (Full/Mid/Mini Tower) e marca(s).
* `search_power_supplies` — busca fontes via `api/request/monte-fonte`.
  Sem dependência de socket; filtra por potência, modularidade,
  eficiência (80 Plus) e marca(s).
* `search_monitors` — busca monitores via `api/request/monte-monitor`.
  Sem dependência de socket; filtra apenas por `query` e marca(s) —
  os demais atributos da categoria (frequência, resolução, painel,
  tamanho, tempo de resposta, conexões) existem em `aggregations` mas
  foram testados e não são aplicados pelo backend da Pichau, então
  não foram expostos como filtros.
* `search_keyboards` — busca teclados via `api/request/monte-keyboard`.
  Sem dependência de socket; filtra por `mechanical` (mecânico
  sim/não), `interface` (USB/wireless/bluetooth/etc.) e marca(s) —
  `layout`, `iluminacao` e `macro` existem em `aggregations` mas foram
  testados e não são aplicados pelo backend, então não foram expostos.
* `search_cables` — busca cabos, adaptadores, hubs e switches via
  `api/request/monte-cabos`. Sem dependência de socket; filtra apenas
  por `query` e marca(s) — `cor_padrao` e `iluminacao` existem em
  `aggregations` mas foram testados e não são aplicados pelo backend.
* `search_mice` — busca mouses via `api/request/monte-mouse`. Sem
  dependência de socket; filtra por `query`, `interface`
  (USB/wireless/bluetooth/etc.) e marca(s) — `cor_padrao` e
  `iluminacao` existem em `aggregations` mas não são aplicados pelo
  backend.
* `search_speakers` — busca caixas de som via `api/request/monte-sound`.
  Sem dependência de socket; filtra apenas por `query` e marca(s) —
  `cor_padrao`, `iluminacao` e `conectividade` existem em
  `aggregations` mas não são aplicados pelo backend.
* `search_webcams` — busca webcams via `api/request/monte-webcam`.
  Sem dependência de socket; filtra por `query` e marca(s) (únicos
  filtros de categoria disponíveis nesse endpoint).

Todas as tools aceitam `query` (busca textual livre, mapeada para o
parâmetro `q` da Pichau) além dos filtros específicos de cada
categoria.

**Nota:** os filtros de faixa de preço (`price`) e núcleos (`nucleo`,
em processadores) foram testados e removidos por não serem aplicados
de forma confiável pelo backend da Pichau — a requisição ia correta,
mas o resultado não era restringido. Para ordenar por preço, use
`sort="price-asc"`/`"price-desc"`. Também testamos parâmetros comuns
de tamanho de página (`pageSize`, `limit`, `per_page`, etc.) e nenhum
é respeitado — a Pichau sempre retorna 36 itens por página, então
`max_results` corta o excesso no cliente mesmo (`items[:max_results]`).

## Encadeamento entre tools

O fluxo típico de montar um PC encadeia o resultado de uma tool como
entrada de outra:

```text
search_processors → socket ──┬─→ search_coolers (socket)
                              └─→ search_motherboards (socket)
                                        │
                                        └─→ form_factor ─→ search_cases (form_factor)
```

Sempre use o campo **sem** sufixo `_name`/`text` (`socket`,
`form_factor`) para encadear — os campos com sufixo são só para
exibição legível. Isso é coberto por um teste de fumaça em
`tests/test_chaining.py` (ver abaixo).

## Cache e retry

`pichau_mcp/client.py` mantém um cache em memória (45s de TTL) por
combinação exata de `(endpoint, params)`, e tenta cada requisição até
3 vezes com backoff curto antes de desistir — cobre tanto buscas
repetidas dentro de uma sessão (ex: montando várias variações de PC)
quanto bloqueios momentâneos da Cloudflare.

## Catálogos de filtro (marcas, sockets, modelos, etc.)

Os dicionários de código (`PROCESSOR_SOCKETS`, `GPU_MODELS`, `*_BRANDS`
etc., em `pichau_mcp/tools.py`) são mantidos à mão a partir dos
`aggregations` que a própria Pichau retorna em cada endpoint. Eles vão
ficar desatualizados conforme a Pichau adicionar marcas/modelos novos.

Rode `uv run scripts/check_catalogs.py` para comparar os catálogos
locais contra as `aggregations` atuais da API e ver exatamente o que
mudou (saída vazia = tudo em dia; código de saída 1 = há drift). Não
automatizamos a geração desses catálogos em tempo de execução de
propósito: isso acoplaria toda chamada de tool à disponibilidade da
Pichau/Cloudflare no momento, trocando uma manutenção manual ocasional
por uma nova causa de falha no startup do server.

## Estrutura

```text
pichau-mcp/
  server.py               # entrypoint (stdio transport)
  pichau_mcp/
    client.py             # HTTP client genérico p/ endpoints monte-* (cache + retry)
    tools.py               # definição das tools, parsing e handlers
  scripts/
    check_catalogs.py     # diff dos catálogos hardcoded vs aggregations ao vivo
  tests/
    test_chaining.py      # smoke test do encadeamento entre tools (rede real)
    test_client.py        # testes de cache/retry do client (mockado)
  .mcp.json                # registro do server no Claude Code
  pyproject.toml
```

## Rodando localmente

```bash
uv run server.py
```

## Testes

```bash
uv run pytest tests/ -v
```

`tests/test_client.py` mocka o transporte e não depende de rede.
`tests/test_chaining.py` bate na API real da Pichau — existe pra pegar
exatamente a classe de regressão do encadeamento quebrado (campo de
texto no lugar do código bruto), então precisa de rede pra rodar.

## Registrando no Claude Code

O arquivo `.mcp.json` já aponta para este projeto. Reinicie o Claude Code
para que as tools apareçam, ou rode `claude mcp list` para conferir.

Este server também está registrado globalmente (`claude mcp add --scope
user`), disponível em qualquer projeto sob o usuário atual.
