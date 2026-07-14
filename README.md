# pichau-mcp

MCP server que expõe ferramentas para o Claude Code buscar peças de
computador na Pichau (loja de hardware).

## Tools disponíveis

* `search_processors` — busca processadores via
  `api/request/monte-processador`, com filtros de texto (`query`),
  plataforma (`AMD`/`Intel`), marca(s), socket, vídeo integrado,
  overclock e ordenação.
* `search_coolers` — busca coolers (air/water) via
  `api/request/monte-processador-cooler`, filtrando por `socket`
  (código vindo do campo `socket` de um processador retornado por
  `search_processors`), marca(s) e ordenação.
* `search_motherboards` — busca placas-mãe via
  `api/request/monte-placa-mae`, filtrando por `socket` (mesma origem
  acima), marca(s), tipo de memória, formato da placa, características
  e ordenação.
* `search_memory` — busca memórias RAM via `api/request/monte-memoria`,
  filtrando por `memory_type` (DDR4/DDR5, deve casar com o `memory_type`
  de uma placa-mãe retornada por `search_motherboards`), marca(s),
  frequência, capacidade e ordenação.
* `search_gpus` — busca placas de vídeo via
  `api/request/monte-placa-de-video`. Sem dependência de socket;
  filtra por marca(s), fabricante do chip (AMD/ATI, NVIDIA, INTEL) e
  modelo específico (ex: "RTX 4070 12GB").
* `search_storage` — busca HDs e SSDs (mesmo catálogo) via
  `api/request/monte-ssd`. Sem dependência de socket; filtra por
  interface (NVME/SATA), formato físico (2.5"/M.2/Placa PCIe) e
  capacidade.
* `search_cases` — busca gabinetes via `api/request/monte-gabinete`,
  filtrando por `form_factor` (código bruto vindo do campo
  `formato_placa` — não `formato_placatext` — de uma placa-mãe
  retornada por `search_motherboards`, obrigatório), tipo de gabinete
  (Full/Mid/Mini Tower) e marca(s).
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

Todas as tools aceitam `query` (busca textual livre, mapeada para o
parâmetro `q` da Pichau) além dos filtros específicos de cada
categoria.

**Nota:** os filtros de faixa de preço (`price`) e núcleos (`nucleo`,
em processadores) foram testados e removidos por não serem aplicados
de forma confiável pelo backend da Pichau — a requisição ia correta,
mas o resultado não era restringido. Para ordenar por preço, use
`sort="price-asc"`/`"price-desc"`.

## Estrutura

```text
pichau-mcp/
  server.py            # entrypoint (stdio transport)
  pichau_mcp/
    client.py          # HTTP client genérico para os endpoints monte-*
    tools.py          # definição das tools, parsing e handlers
  .mcp.json            # registro do server no Claude Code
  pyproject.toml
```

## Rodando localmente

```bash
uv run server.py
```

## Registrando no Claude Code

O arquivo `.mcp.json` já aponta para este projeto. Reinicie o Claude Code
para que as tools apareçam, ou rode `claude mcp list` para conferir.

## Próximos passos

* Adicionar tools para outras categorias (placas-mãe, memória, GPU, etc.)
  reaproveitando `pichau_mcp/client.py::fetch_products`.
