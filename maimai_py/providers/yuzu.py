from httpx import AsyncClient
from maimai_py.models import SongAlias
from maimai_py.providers.base import IAliasProvider


class YuzuProvider(IAliasProvider):
    base_url = "https://api.yuzuchan.moe/"

    async def get_aliases(self, client: AsyncClient) -> list[SongAlias]:
        resp = await client.get(self.base_url + "maimaidx/maimaidxalias")
        resp.raise_for_status()
        return [SongAlias(song_id=item["SongID"] % 10000, aliases=item["Alias"]) for item in resp.json()["content"]]
