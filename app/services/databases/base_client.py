import httpx
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class BaseHTTPClient:
    """Base client with retry + logging for external APIs."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"User-Agent": "BioChem-MCP-Gateway/0.1.0"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    async def get(self, path: str, params: dict | None = None) -> httpx.Response:
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with'.")
        logger.debug(f"GET {self.base_url}{path} params={params}")
        response = await self._client.get(path, params=params)
        response.raise_for_status()
        return response