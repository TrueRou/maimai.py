import httpx
import asyncio
from typing import Any


class MaimaiCaches:
    _caches: dict[str, Any] = {}
    _caches_provider: dict[str, object] = {}
    _available_keys = ["songs", "aliases", "curves", "icons", "nameplates", "frames", "trophies", "charas", "partners"]

    def update(self, key: str, new_val: Any) -> Any:
        if isinstance(new_val, dict):
            value_dict: dict = self._caches.setdefault(key, {})
            value_dict.update(new_val)
        elif isinstance(new_val, list):
            value_list: list = self._caches.setdefault(key, [])
            value_list[:] = new_val
        return new_val

    async def get_or_fetch(self, key: str, client: httpx.AsyncClient, flush=False) -> Any:
        item = self._caches.get(key, None)
        need_flush = not item or flush
        if key in self._available_keys and need_flush:
            provider = self._caches_provider[key]
            item = await getattr(provider, f"get_{key}")(client) if provider else None
            self.update(key, item)
        return item

    async def flush(self, client: httpx.AsyncClient) -> None:
        managed_keys = set(self._caches.keys()) & set(self._available_keys)
        tasks = [self.get_or_fetch(key, client, flush=True) for key in managed_keys]
        await asyncio.gather(*tasks)
        unmanaged_keys = set(self._caches.keys()) - set(self._available_keys)
        [getattr(self._caches[key], "_flush") for key in unmanaged_keys if hasattr(self._caches[key], "_flush")]


default_caches = MaimaiCaches()
