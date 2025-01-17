from httpx import AsyncClient

from maimai_py.models import SongAlias
from maimai_py.providers import IAliasProvider


class YuzuProvider(IAliasProvider):
    """The provider that fetches song aliases from the Yuzu.

    Yuzu is a bot API that provides song aliases for maimai DX.

    Yuzu: https://bot.yuzuchan.moe/
    """

    base_url = "https://api.yuzuchan.moe/"
    """The base URL for the Yuzu API."""

    def __eq__(self, value):
        return isinstance(value, YuzuProvider)

    async def get_aliases(self, client: AsyncClient) -> list[SongAlias]:
        resp = await client.get(self.base_url + "maimaidx/maimaidxalias")
        resp.raise_for_status()
        return [SongAlias(song_id=item["SongID"] % 10000, aliases=item["Alias"]) for item in resp.json()["content"]]
