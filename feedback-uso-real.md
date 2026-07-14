# Feedback de uso real — pichau-mcp

Baseado numa sessão real montando variações de PC (processador → cooler → placa-mãe → RAM → SSD → GPU → fonte → gabinete). De 10 tools, 7 funcionaram perfeitamente; 3 (`search_coolers`, `search_motherboards`, `search_cases`) falharam 100% das vezes, sempre com `total_pages: 0`. Achei a causa raiz no código — é um bug de um campo trocado, não falta de dado.

## O bug central

**Arquivo:** `pichau_mcp/tools.py`
**Funções:** `_format_processor` (linha ~1198) e `_format_motherboard` (linha ~1223)

O fluxo documentado (no `README.md` e nas próprias `description` das tools) é:

1. `search_processors` retorna um processador com um campo `socket`.
2. Esse valor vai direto pro parâmetro `socket` (obrigatório) de `search_coolers`/`search_motherboards`.
3. `search_motherboards` retorna uma placa com um campo `form_factor` vindo de `formato_placa` (não `formato_placatext`).
4. Esse valor vai pro parâmetro `form_factor` (obrigatório) de `search_cases`.

Só que os formatadores não fazem isso — eles devolvem o campo de **texto legível**, com o **nome do campo bruto**:

```python
# linha ~1204, dentro de _format_processor
"socket": item.get("sockettext"),   # deveria ser item.get("socket")

# linha ~1228-1229, dentro de _format_motherboard
"socket": item.get("sockettext"),         # idem
"form_factor": item.get("formato_placatext"),  # deveria ser item.get("formato_placa")
```

Resultado prático: `search_processors` me devolveu `"socket": "AMD AM5"` (texto humano). Passei esse valor pra `search_coolers`/`search_motherboards` — que retornaram `total_pages: 0` sempre, porque o backend da Pichau espera o **código numérico interno** (que já está hardcoded no próprio arquivo, em `PROCESSOR_SOCKETS`: AM5 = `"6689"`). Só descobri o código certo lendo o dicionário no código-fonte agora — não tinha como um agente (ou eu) chegar nele só usando as tools, apesar da descrição dizer explicitamente pra usar "o campo `socket`, não `sockettext`". O campo que promete o valor certo está, na prática, entregando o errado.

O mesmo bug se repete um nível abaixo: `search_cases` pede o `formato_placa` de uma placa-mãe, mas `_format_motherboard` só expõe `formato_placatext` (ex: `"ATX"`), nunca o código bruto.

**Por que isso é grave:** não é um filtro faltando — é o **encadeamento entre tools quebrado**. `search_coolers`, `search_motherboards` e `search_cases` são inutilizáveis seguindo o fluxo pretendido pelo próprio projeto. Na prática, montar uma placa-mãe ou um gabinete via MCP hoje não funciona; eu só consegui informação real sobre essas três categorias recorrendo a busca na web como alternativa.

### Sugestão de correção

Não precisa remover o campo de texto (é útil pra exibição) — só expor o código bruto também, com nome claro, e apontar as `description` das tools consumidoras pro nome certo:

```python
def _format_processor(item: dict) -> dict:
    return {
        ...
        "socket": item.get("socket"),          # código bruto — o que search_coolers/motherboards esperam
        "socket_name": item.get("sockettext"),  # texto legível, só pra exibição
        ...
    }

def _format_motherboard(item: dict) -> dict:
    return {
        ...
        "socket": item.get("socket"),
        "socket_name": item.get("sockettext"),
        "form_factor": item.get("formato_placa"),          # código bruto — o que search_cases espera
        "form_factor_name": item.get("formato_placatext"),  # texto legível
        ...
    }
```

E depois um teste de fumaça simples (`search_processors` → pega o primeiro resultado → `search_coolers`/`search_motherboards` com esse socket → confirma `total_pages > 0`) pegaria essa classe de regressão automaticamente. Hoje não existe nenhum teste no projeto (só `server.py`, `client.py`, `tools.py` — nenhum diretório `tests/`), então esse bug não tinha como ser pego antes de chegar num uso real.

## O que funciona bem

- **`search_gpus`, `search_storage`, `search_power_supplies`, `search_memory`, `search_monitors`, `search_keyboards`, `search_processors`** — os 7 sem dependência de campo cruzado funcionaram sem nenhum problema, com resultados corretos e atualizados (estoque, preço à vista/cartão, parcelamento).
- **Mensagens de erro de validação são boas.** `_resolve_codes`/`_resolve_code` (linha ~1160) devolvem "Valor inválido para 'X': ... Válidos: ..." listando as opções aceitas — isso é exatamente o tipo de erro que um agente consegue się autocorrigir sem intervenção humana.
- **Transparência sobre limitações reais da API da Pichau.** As descriptions de `search_monitors` e `search_keyboards` já documentam, de forma explícita, quais filtros existem em `aggregations` mas não são de fato aplicados pelo backend (frequência, resolução, layout, etc.) — dá pra ver que isso foi testado de verdade, não assumido. O mesmo aviso existe no README sobre `price` e `nucleo`. Isso evitou eu perder tempo tentando filtros que nunca funcionariam.
- **`client.py` resolve um problema real e documenta por quê.** Usar `curl_cffi` com impersonation Chrome pra passar do fingerprinting de TLS da Cloudflare é a razão de eu não conseguir fazer `WebFetch` direto no pichau.com.br (retorna 403) mas o MCP conseguir — e isso está comentado no topo do arquivo, então quem mexer no código no futuro entende o porquê sem precisar redescobrir.
- **Padrão de código consistente** entre as 10 tools — validar filtros → montar `params` → `fetch_products` → formatar. Fácil de entender e, se o bug acima for corrigido, fácil de replicar o teste de fumaça pras 3 categorias afetadas.

## Outras oportunidades de melhoria (menor prioridade)

1. **Sem cache.** Cada busca bate direto na API da Pichau. Numa sessão como essa (dezenas de buscas pra montar 3 variações de PC), um cache curto (30-60s) pra combinações idênticas de parâmetros reduziria chamadas repetidas e o risco de esbarrar em rate-limit/bloqueio da Cloudflare.
2. **Sem retry.** `client.py` faz uma única tentativa com timeout de 15s. Uma falha transitória de rede ou um bloqueio momentâneo da Cloudflare derruba a busca inteira sem segunda chance.
3. **Catálogos de código hardcoded vão ficar desatualizados.** `PROCESSOR_SOCKETS`, `GPU_MODELS` (a maior, ~140 entradas) e os demais dicionários de marca/modelo são mantidos manualmente. Quando a Pichau lançar um socket ou modelo de GPU novo (como já quase aconteceu — RTX 50-series já está mapeado, mas o próximo lançamento não vai estar até alguém atualizar o dicionário à mão), a busca por esse item vai falhar com "valor inválido" até o código ser atualizado. Vale avaliar se a API da Pichau expõe as opções de filtro atuais em algum endpoint de agregação/facet — se sim, dava pra gerar esses dicionários automaticamente em vez de mantê-los à mão.
4. **`search_cases` força uma dependência de `search_motherboards` que não precisava ser obrigatória.** Diferente de `search_motherboards`, que expõe `form_factor` como enum livre (`Micro ATX`/`ATX`/`Mini ITX`) além de aceitar o socket, `search_cases` só aceita o código bruto vindo de uma placa-mãe. Seria mais ergonômico (e resolveria o bug acima de quebra) expor `form_factor` em `search_cases` como o mesmo enum humano usado em `search_motherboards`, resolvendo o código internamente — assim a tool funciona sozinha, sem precisar do encadeamento.
5. **Truncamento de `max_results` é client-side.** `items = products.get("items", [])[:max_results]` (repetido em cada handler) busca a página inteira da Pichau e corta depois — funciona, mas desperdiça banda/tokens se a página padrão da Pichau for grande. Vale checar se a API aceita um parâmetro de tamanho de página.

## Resumo — prioridade de ação

| Prioridade | Item | Esforço |
| --- | --- | --- |
| 🔴 Alta | Corrigir `_format_processor`/`_format_motherboard` pra expor o código bruto (`socket`, `form_factor`) em vez do texto | Baixo — troca de 3 linhas |
| 🔴 Alta | Adicionar teste de fumaça encadeado (processador → cooler/placa-mãe → gabinete) pra travar essa classe de regressão | Baixo-médio |
| 🟡 Média | Cache curto + retry no `client.py` | Médio |
| 🟢 Baixa | Expor `form_factor` como enum livre em `search_cases` (não depender só do encadeamento) | Baixo |
| 🟢 Baixa | Avaliar geração automática dos dicionários de código a partir de um endpoint de facets, se existir | Alto |
