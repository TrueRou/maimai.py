import contextlib

import httpx


@contextlib.asynccontextmanager
async def async_httpx_ctx():
    async with httpx.AsyncClient(transport=httpx.HTTPTransport(retries=3), timeout=20) as session:
        yield session
