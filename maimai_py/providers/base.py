from abc import abstractmethod
from typing import TYPE_CHECKING

from maimai_py.models import *

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient


class ISongProvider:
    """The provider that fetches songs from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`
    """

    @abstractmethod
    def _hash(self) -> str: ...

    @abstractmethod
    async def get_songs(self, client: "MaimaiClient") -> list[Song]:
        """@private"""
        raise NotImplementedError()


class IAliasProvider:
    """The provider that fetches song aliases from a specific source.

    Available providers: `YuzuProvider`, `LXNSProvider`
    """

    @abstractmethod
    def _hash(self) -> str: ...

    @abstractmethod
    async def get_aliases(self, client: "MaimaiClient") -> list[SongAlias]:
        """@private"""
        raise NotImplementedError()


class IPlayerProvider:
    """The provider that fetches players from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`
    """

    @abstractmethod
    def _hash(self) -> str: ...

    @abstractmethod
    async def get_player(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> Player:
        """@private"""
        raise NotImplementedError()


class IScoreProvider:
    """The provider that fetches scores from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`, `WechatProvider`
    """

    @abstractmethod
    def _hash(self) -> str: ...

    @abstractmethod
    async def get_scores_best(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> tuple[list[Score] | None, list[Score] | None]:
        """@private"""
        # Return (None, None) will call the main client to handle this, which will then fetch all scores instead
        return None, None

    @abstractmethod
    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def update_scores(self, identifier: PlayerIdentifier, scores: list[Score], client: "MaimaiClient") -> None:
        """@private"""
        raise NotImplementedError()


class ICurveProvider:
    """The provider that fetches statistics curves from a specific source.

    Available providers: `DivingFishProvider`
    """

    @abstractmethod
    def _hash(self) -> str: ...

    @abstractmethod
    async def get_curves(self, client: "MaimaiClient") -> dict[tuple[int, SongType], list[CurveObject | None]]:
        """@private"""
        raise NotImplementedError()


class IRegionProvider:
    """The provider that fetches player regions from a specific source.

    Available providers: `ArcadeProvider`
    """

    @abstractmethod
    def _hash(self) -> str: ...

    @abstractmethod
    async def get_regions(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[PlayerRegion]:
        """@private"""
        raise NotImplementedError()


class IItemListProvider:
    """The provider that fetches player item list data from a specific source.

    Available providers: `LXNSProvider`, `LocalProvider`
    """

    @abstractmethod
    def _hash(self) -> str: ...

    @abstractmethod
    async def get_icons(self, client: "MaimaiClient") -> dict[int, PlayerIcon]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def get_nameplates(self, client: "MaimaiClient") -> dict[int, PlayerNamePlate]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def get_frames(self, client: "MaimaiClient") -> dict[int, PlayerFrame]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def get_partners(self, client: "MaimaiClient") -> dict[int, PlayerPartner]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def get_charas(self, client: "MaimaiClient") -> dict[int, PlayerChara]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def get_trophies(self, client: "MaimaiClient") -> dict[int, PlayerTrophy]:
        """@private"""
        raise NotImplementedError()


class IAreaProvider:
    """The provider that fetches area data from a specific source.

    Available providers: `LocalProvider`
    """

    @abstractmethod
    def _hash(self) -> str: ...

    @abstractmethod
    async def get_areas(self, lang: str, client: "MaimaiClient") -> dict[str, Area]:
        """@private"""
        raise NotImplementedError()
