"""Diff the hardcoded filter catalogs in pichau_mcp/tools.py against Pichau's
live `aggregations` for each endpoint.

The tools' brand/socket/model/etc. dictionaries are maintained by hand (see
README "Catálogos hardcoded" note) rather than fetched at request time --
building a dynamic-catalog system would couple every tool call's JSON
schema to Pichau/Cloudflare being reachable, trading a maintenance chore
for a new startup failure mode. This script is the lower-risk middle
ground: a manual, read-only check a maintainer can run periodically (or
when a "valor inválido" report comes in) to see exactly what changed
upstream, without touching the request path at all.

Usage:
    uv run scripts/check_catalogs.py

Exits 0 if every catalog matches Pichau's current aggregations, 1 if any
drift was found (new options, removed options, or a value that moved).
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pichau_mcp import tools as t  # noqa: E402
from pichau_mcp.client import PichauAPIError, fetch_products  # noqa: E402

# (endpoint, attribute_code, catalog_dict, catalog_name)
CATALOGS = [
    ("monte-processador", "socket", t.PROCESSOR_SOCKETS, "PROCESSOR_SOCKETS"),
    ("monte-processador", "marcas", t.PROCESSOR_BRANDS, "PROCESSOR_BRANDS"),
    ("monte-processador", "vgaintegrado", t.PROCESSOR_INTEGRATED_GRAPHICS, "PROCESSOR_INTEGRATED_GRAPHICS"),
    ("monte-processador", "overclock", t.PROCESSOR_OVERCLOCK, "PROCESSOR_OVERCLOCK"),
    ("monte-processador-cooler", "marcas", t.COOLER_BRANDS, "COOLER_BRANDS"),
    ("monte-placa-mae", "marcas", t.MOTHERBOARD_BRANDS, "MOTHERBOARD_BRANDS"),
    ("monte-placa-mae", "tipo_de_memoria", t.MOTHERBOARD_MEMORY_TYPES, "MOTHERBOARD_MEMORY_TYPES"),
    ("monte-placa-mae", "formato_placa", t.MOTHERBOARD_FORM_FACTORS, "MOTHERBOARD_FORM_FACTORS"),
    ("monte-placa-mae", "caracteristicas", t.MOTHERBOARD_FEATURES, "MOTHERBOARD_FEATURES"),
    ("monte-memoria", "marcas", t.MEMORY_BRANDS, "MEMORY_BRANDS"),
    ("monte-memoria", "frequencia", t.MEMORY_FREQUENCIES, "MEMORY_FREQUENCIES"),
    ("monte-memoria", "capacidadememoria", t.MEMORY_CAPACITIES, "MEMORY_CAPACITIES"),
    ("monte-placa-de-video", "marcas", t.GPU_BRANDS, "GPU_BRANDS"),
    ("monte-placa-de-video", "placadevideo", t.GPU_VENDORS, "GPU_VENDORS"),
    ("monte-placa-de-video", "rgpu", t.GPU_MODELS, "GPU_MODELS"),
    ("monte-ssd", "barramento_ssd", t.STORAGE_INTERFACES, "STORAGE_INTERFACES"),
    ("monte-ssd", "formato_ssd", t.STORAGE_FORM_FACTORS, "STORAGE_FORM_FACTORS"),
    ("monte-ssd", "rarmazenamento", t.STORAGE_CAPACITIES, "STORAGE_CAPACITIES"),
    ("monte-gabinete", "formato_placa", t.CASE_FORM_FACTORS, "CASE_FORM_FACTORS"),
    ("monte-gabinete", "tipo_gabinete", t.CASE_TYPES, "CASE_TYPES"),
    ("monte-gabinete", "marcas", t.CASE_BRANDS, "CASE_BRANDS"),
    ("monte-fonte", "potencia_fonte", t.PSU_WATTAGE, "PSU_WATTAGE"),
    ("monte-fonte", "modular_fonte", t.PSU_MODULAR, "PSU_MODULAR"),
    ("monte-fonte", "eficiencia_fonte", t.PSU_EFFICIENCY, "PSU_EFFICIENCY"),
    ("monte-fonte", "marcas", t.PSU_BRANDS, "PSU_BRANDS"),
    ("monte-monitor", "marcas", t.MONITOR_BRANDS, "MONITOR_BRANDS"),
    ("monte-keyboard", "mecanico", t.KEYBOARD_MECHANICAL, "KEYBOARD_MECHANICAL"),
    ("monte-keyboard", "interface", t.KEYBOARD_INTERFACES, "KEYBOARD_INTERFACES"),
    ("monte-keyboard", "marcas", t.KEYBOARD_BRANDS, "KEYBOARD_BRANDS"),
]


async def _fetch_aggregations(endpoint: str) -> dict[str, dict[str, str]]:
    """Return {attribute_code: {label: value}} for one endpoint's aggregations."""
    data = await fetch_products(endpoint, {"page": 1})
    result = {}
    for agg in data.get("products", {}).get("aggregations", []):
        result[agg["attribute_code"]] = {
            # Pichau sometimes has trailing whitespace on labels (e.g. "Vinik ")
            # that our catalogs normalize away -- strip here too, or every run
            # reports the same non-issue as drift.
            opt["label"].strip(): opt["value"]
            for opt in agg.get("options", [])
        }
    return result


async def main() -> int:
    endpoints = sorted({endpoint for endpoint, *_ in CATALOGS})
    aggregations_by_endpoint = {}
    for endpoint in endpoints:
        try:
            aggregations_by_endpoint[endpoint] = await _fetch_aggregations(endpoint)
        except PichauAPIError as exc:
            print(f"⚠️  Falha ao buscar {endpoint}: {exc}")
            aggregations_by_endpoint[endpoint] = {}

    any_drift = False
    for endpoint, attribute_code, local_catalog, name in CATALOGS:
        live = aggregations_by_endpoint.get(endpoint, {}).get(attribute_code)
        if live is None:
            print(f"⚠️  {name}: attribute_code '{attribute_code}' não encontrado em {endpoint}")
            any_drift = True
            continue

        added = {label: value for label, value in live.items() if label not in local_catalog}
        removed = {label: value for label, value in local_catalog.items() if label not in live}
        changed = {
            label: (local_catalog[label], live[label])
            for label in local_catalog
            if label in live and local_catalog[label] != live[label]
        }

        if not added and not removed and not changed:
            continue

        any_drift = True
        print(f"\n{name} ({endpoint}?{attribute_code}):")
        for label, value in added.items():
            print(f"  + novo: {label!r}: {value!r}")
        for label, value in removed.items():
            print(f"  - sumiu: {label!r}: {value!r} (pode ter saído de linha, não necessariamente remover)")
        for label, (old, new) in changed.items():
            print(f"  ~ mudou: {label!r}: {old!r} -> {new!r}")

    if not any_drift:
        print("Todos os catálogos batem com as aggregations atuais da Pichau. ✅")
        return 0

    print("\nCatálogos desatualizados. Atualize os dicionários em pichau_mcp/tools.py.")
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
