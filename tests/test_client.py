"""Unit tests for the caching and retry behavior in pichau_mcp/client.py.

Unlike tests/test_chaining.py, these mock the transport so they don't hit
the real Pichau API -- they're testing our own retry/cache logic, not
Pichau's backend.
"""

from unittest.mock import patch

import pytest

from pichau_mcp.client import PichauAPIError, _cache, fetch_products
from curl_cffi.requests.exceptions import RequestException


class _FakeResponse:
    def __init__(self, status_code: int, json_data: dict | None = None):
        self.status_code = status_code
        self._json_data = json_data

    def json(self) -> dict:
        return self._json_data


def _patch_session(get_fn):
    patcher = patch("pichau_mcp.client.AsyncSession")
    mock_session_cls = patcher.start()
    instance = mock_session_cls.return_value
    instance.__aenter__.return_value = instance
    instance.__aexit__.return_value = None
    instance.get = get_fn
    return patcher


@pytest.fixture(autouse=True)
def clear_cache():
    _cache.clear()
    yield
    _cache.clear()


async def test_identical_calls_are_served_from_cache():
    call_count = 0

    async def get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return _FakeResponse(200, {"products": {"items": [], "page_info": {}}})

    patcher = _patch_session(get)
    try:
        first = await fetch_products("monte-processador", {"page": 1, "q": "x"})
        second = await fetch_products("monte-processador", {"page": 1, "q": "x"})
    finally:
        patcher.stop()

    assert first is second
    assert call_count == 1


async def test_retries_transient_network_errors_then_succeeds():
    call_count = 0

    async def get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RequestException("simulated transient network error")
        return _FakeResponse(200, {"products": {"items": [], "page_info": {}}})

    patcher = _patch_session(get)
    try:
        data = await fetch_products("monte-processador", {"page": 1, "q": "retry"})
    finally:
        patcher.stop()

    assert call_count == 3
    assert data == {"products": {"items": [], "page_info": {}}}


async def test_gives_up_after_max_attempts():
    call_count = 0

    async def get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise RequestException("always fails")

    patcher = _patch_session(get)
    try:
        with pytest.raises(PichauAPIError):
            await fetch_products("monte-processador", {"page": 1, "q": "fail"})
    finally:
        patcher.stop()

    assert call_count == 3


async def test_non_200_response_is_not_cached():
    call_count = 0

    async def get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return _FakeResponse(403)

    patcher = _patch_session(get)
    try:
        with pytest.raises(PichauAPIError):
            await fetch_products("monte-processador", {"page": 1, "q": "blocked"})
    finally:
        patcher.stop()

    assert call_count == 3
