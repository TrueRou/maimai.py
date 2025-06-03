import hashlib
from typing import TYPE_CHECKING

from maimai_py.models import SongAlias
from maimai_py.providers.base import IAliasProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient


class YuzuProvider(IAliasProvider):
    """The provider that fetches song aliases from the Yuzu.

    Yuzu is a bot API that provides song aliases for maimai DX.

    Yuzu: https://bot.yuzuchan.moe/
    """

    base_url = "https://api.yuzuchan.moe/"
    """The base URL for the Yuzu API."""

    def _hash(self) -> str:
        return hashlib.md5(b"yuzu").hexdigest()

    async def get_aliases(self, client: "MaimaiClient") -> list[SongAlias]:
        resp = await client._client.get(self.base_url + "maimaidx/maimaidxalias")
        resp.raise_for_status()
        return [SongAlias(song_id=item["SongID"] % 10000, aliases=item["Alias"]) for item in resp.json()["content"]]
