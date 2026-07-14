"""HTTP client for the Pichau "monte-*" product search endpoints.

Pichau sits behind Cloudflare bot management, which fingerprints the TLS
handshake (JA3) and blocks plain curl/httpx clients even with a convincing
User-Agent header -- that's why a plain requests-style client gets a 403
"Site em Manutenção" page while a browser or Postman gets through. We use
curl_cffi to impersonate a real Chrome TLS fingerprint instead.
"""

from curl_cffi.requests import AsyncSession
from curl_cffi.requests.exceptions import RequestException

BASE_URL = "https://www.pichau.com.br/api/request"
IMPERSONATE = "chrome124"


class PichauAPIError(Exception):
    """Raised when the Pichau API can't be reached or returns something unexpected."""


async def fetch_products(endpoint: str, params: dict[str, str | int | None]) -> dict:
    """Fetch a page of products from a Pichau "monte-*" search endpoint.

    `endpoint` is the path segment after /api/request/, e.g. "monte-processador".
    Each "monte-*" endpoint has its own filter parameter names (plataforma/q
    for processors, socket/marcas for coolers, ...), so callers build their
    own `params` dict; entries with a `None` value are dropped.
    """
    query_params = {k: v for k, v in params.items() if v is not None}

    url = f"{BASE_URL}/{endpoint}"
    try:
        async with AsyncSession() as session:
            response = await session.get(
                url, params=query_params, impersonate=IMPERSONATE, timeout=15
            )
    except RequestException as exc:
        raise PichauAPIError(f"Falha ao conectar com a Pichau: {exc}") from exc

    if response.status_code != 200:
        raise PichauAPIError(
            f"Pichau retornou status {response.status_code} "
            f"(o site pode estar em manutenção ou bloqueando a requisição)."
        )

    try:
        return response.json()
    except ValueError as exc:
        raise PichauAPIError(
            "Resposta da Pichau não é um JSON válido (o site pode estar em manutenção)."
        ) from exc
