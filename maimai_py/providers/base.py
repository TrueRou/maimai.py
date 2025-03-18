from abc import abstractmethod
from httpx import AsyncClient

from maimai_py.models import *


class ISongProvider:
    """The provider that fetches songs from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`
    """

    @abstractmethod
    async def get_songs(self, client: AsyncClient) -> list[Song]:
        """@private"""
        raise NotImplementedError()


class IAliasProvider:
    """The provider that fetches song aliases from a specific source.

    Available providers: `YuzuProvider`, `LXNSProvider`
    """

    @abstractmethod
    async def get_aliases(self, client: AsyncClient) -> list[SongAlias]:
        """@private"""
        raise NotImplementedError()


class IPlayerProvider:
    """The provider that fetches players from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`
    """

    @abstractmethod
    async def get_player(self, identifier: PlayerIdentifier, client: AsyncClient) -> Player:
        """@private"""
        raise NotImplementedError()


class IScoreProvider:
    """The provider that fetches scores from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`, `WechatProvider`
    """

    @abstractmethod
    async def get_scores_best(self, identifier: PlayerIdentifier, client: AsyncClient) -> tuple[list[Score], list[Score]]:
        """@private"""
        # Return (None, None) will call the main client to handle this, which will then fetch all scores instead
        return None, None

    @abstractmethod
    async def get_scores_all(self, identifier: PlayerIdentifier, client: AsyncClient) -> list[Score]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def update_scores(self, identifier: PlayerIdentifier, scores: list[Score], client: AsyncClient) -> None:
        """@private"""
        raise NotImplementedError()


class ICurveProvider:
    """The provider that fetches statistics curves from a specific source.

    Available providers: `DivingFishProvider`
    """

    @abstractmethod
    async def get_curves(self, client: AsyncClient) -> dict[str, list[CurveObject | None]]:
        """@private"""
        raise NotImplementedError()


class IRegionProvider:
    """The provider that fetches player regions from a specific source.

    Available providers: `ArcadeProvider`
    """

    @abstractmethod
    async def get_regions(self, identifier: PlayerIdentifier, client: AsyncClient) -> list[PlayerRegion]:
        """@private"""
        raise NotImplementedError()


class IItemListProvider:
    """The provider that fetches player item list data from a specific source.

    Available providers: `LXNSProvider`, `LocalProvider`
    """

    @abstractmethod
    async def get_icons(self, client: AsyncClient) -> dict[int, PlayerIcon]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def get_nameplates(self, client: AsyncClient) -> dict[int, PlayerNamePlate]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def get_frames(self, client: AsyncClient) -> dict[int, PlayerFrame]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def get_partners(self, client: AsyncClient) -> dict[int, PlayerPartner]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def get_charas(self, client: AsyncClient) -> dict[int, PlayerChara]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def get_trophies(self, client: AsyncClient) -> dict[int, PlayerTrophy]:
        """@private"""
        raise NotImplementedError()


class IAreaProvider:
    """The provider that fetches area data from a specific source.

    Available providers: `LocalProvider`
    """

    @abstractmethod
    async def get_areas(self, lang: str, client: AsyncClient) -> list[Area]:
        """@private"""
        raise NotImplementedError()
