"""HTTP client for the Pichau "monte-*" product search endpoints.

Pichau sits behind Cloudflare bot management, which fingerprints the TLS
handshake (JA3) and blocks plain curl/httpx clients even with a convincing
User-Agent header -- that's why a plain requests-style client gets a 403
"Site em Manutenção" page while a browser or Postman gets through. We use
curl_cffi to impersonate a real Chrome TLS fingerprint instead.
"""

import asyncio
import time

from curl_cffi.requests import AsyncSession
from curl_cffi.requests.exceptions import RequestException

BASE_URL = "https://www.pichau.com.br/api/request"
IMPERSONATE = "chrome124"

CACHE_TTL_SECONDS = 45
MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 0.5

# In-memory cache for repeated identical lookups within a session (e.g. an
# agent re-checking the same search while building out a PC). Keyed by
# (endpoint, sorted params); only successful responses are cached.
_cache: dict[tuple, tuple[float, dict]] = {}


class PichauAPIError(Exception):
    """Raised when the Pichau API can't be reached or returns something unexpected."""


def _cache_key(endpoint: str, params: dict) -> tuple:
    return (endpoint, tuple(sorted(params.items())))


async def fetch_products(endpoint: str, params: dict[str, str | int | None]) -> dict:
    """Fetch a page of products from a Pichau "monte-*" search endpoint.

    `endpoint` is the path segment after /api/request/, e.g. "monte-processador".
    Each "monte-*" endpoint has its own filter parameter names (plataforma/q
    for processors, socket/marcas for coolers, ...), so callers build their
    own `params` dict; entries with a `None` value are dropped.

    Identical (endpoint, params) lookups are served from an in-memory cache
    for CACHE_TTL_SECONDS. Transient failures (network errors or a non-200
    response, e.g. a momentary Cloudflare block) are retried up to
    MAX_ATTEMPTS times with a short linear backoff before raising.
    """
    query_params = {k: v for k, v in params.items() if v is not None}

    key = _cache_key(endpoint, query_params)
    cached = _cache.get(key)
    if cached is not None:
        cached_at, data = cached
        if time.monotonic() - cached_at < CACHE_TTL_SECONDS:
            return data

    url = f"{BASE_URL}/{endpoint}"
    last_error: PichauAPIError | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            async with AsyncSession() as session:
                response = await session.get(
                    url, params=query_params, impersonate=IMPERSONATE, timeout=15
                )
        except RequestException as exc:
            last_error = PichauAPIError(f"Falha ao conectar com a Pichau: {exc}")
        else:
            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError as exc:
                    raise PichauAPIError(
                        "Resposta da Pichau não é um JSON válido "
                        "(o site pode estar em manutenção)."
                    ) from exc
                _cache[key] = (time.monotonic(), data)
                return data

            last_error = PichauAPIError(
                f"Pichau retornou status {response.status_code} "
                f"(o site pode estar em manutenção ou bloqueando a requisição)."
            )

        if attempt < MAX_ATTEMPTS:
            await asyncio.sleep(RETRY_BACKOFF_SECONDS * attempt)

    raise last_error
