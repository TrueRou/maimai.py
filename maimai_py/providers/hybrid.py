import hashlib
from typing import TYPE_CHECKING

from maimai_py.models import *
from maimai_py.providers.local import LocalProvider

from .base import IAreaProvider, IItemListProvider, ISongProvider
from .divingfish import DivingFishProvider
from .lxns import LXNSProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient


class HybridProvider(ISongProvider, IItemListProvider, IAreaProvider):
    """The provider that fetches data from the LXNS and local, and hybrids them together.

    This provider is used to api endpoints creation, which are not normally used by the client.
    """

    base_url_lxns = LXNSProvider.base_url
    base_url_divingfish = DivingFishProvider.base_url
    provider_local = LocalProvider()
    provider_lxns = LXNSProvider()

    def _hash(self) -> str:
        return hashlib.md5(b"hybrid").hexdigest()

    async def get_songs(self, client: "MaimaiClient") -> list[Song]:
        return await self.provider_lxns.get_songs(client)

    async def get_icons(self, client: "MaimaiClient") -> dict[int, PlayerIcon]:
        return await self.provider_lxns.get_icons(client)

    async def get_nameplates(self, client: "MaimaiClient") -> dict[int, PlayerNamePlate]:
        return await self.provider_lxns.get_nameplates(client)

    async def get_frames(self, client: "MaimaiClient") -> dict[int, PlayerFrame]:
        return await self.provider_lxns.get_frames(client)

    async def get_partners(self, client: "MaimaiClient") -> dict[int, PlayerPartner]:
        return await self.provider_local.get_partners(client)

    async def get_charas(self, client: "MaimaiClient") -> dict[int, PlayerChara]:
        return await self.provider_local.get_charas(client)

    async def get_trophies(self, client: "MaimaiClient") -> dict[int, PlayerTrophy]:
        return await self.provider_local.get_trophies(client)

    async def get_areas(self, lang: str, client: "MaimaiClient") -> dict[str, Area]:
        return await self.provider_local.get_areas(lang, client)
