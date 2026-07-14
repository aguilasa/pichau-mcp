"""Smoke test for cross-tool field chaining.

These tests hit the real Pichau API -- there is no mocking layer in this
project (see pichau_mcp/client.py for why: Cloudflare's TLS fingerprinting
means a mocked transport wouldn't exercise the thing that actually breaks).
They exist to catch the class of regression where a formatter exposes a
human-readable text field under the name a downstream tool expects a raw
code in, e.g. `_format_processor` returning `sockettext` under the `socket`
key instead of the raw `socket` code that `search_coolers`/
`search_motherboards` require.
"""

import json

from pichau_mcp.tools import (
    handle_search_cases,
    handle_search_coolers,
    handle_search_motherboards,
    handle_search_processors,
)


def _first_result(payload: list) -> dict:
    return json.loads(payload[0].text)["results"][0]


async def test_processor_socket_chains_into_coolers_and_motherboards():
    processors = await handle_search_processors({"query": "ryzen 5 7600", "max_results": 1})
    processor = _first_result(processors)
    socket = processor["socket"]
    assert socket and socket.isdigit(), (
        f"search_processors must return a raw numeric socket code in 'socket', got {socket!r}"
    )

    coolers = await handle_search_coolers({"socket": socket, "max_results": 1})
    cooler_payload = json.loads(coolers[0].text)
    assert cooler_payload["total_pages"] > 0, (
        "search_coolers returned no results chaining a valid processor socket"
    )

    motherboards = await handle_search_motherboards({"socket": socket, "max_results": 1})
    mb_payload = json.loads(motherboards[0].text)
    assert mb_payload["total_pages"] > 0, (
        "search_motherboards returned no results chaining a valid processor socket"
    )


async def test_motherboard_form_factor_chains_into_cases():
    motherboards = await handle_search_motherboards({"socket": "6689", "max_results": 1})
    motherboard = _first_result(motherboards)
    form_factor = motherboard["form_factor"]
    assert form_factor and form_factor.isdigit(), (
        f"search_motherboards must return a raw numeric form_factor code, got {form_factor!r}"
    )

    cases = await handle_search_cases({"form_factor": form_factor, "max_results": 1})
    cases_payload = json.loads(cases[0].text)
    assert cases_payload["total_pages"] > 0, (
        "search_cases returned no results chaining a valid motherboard form_factor"
    )
