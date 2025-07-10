from abc import abstractmethod
from typing import TYPE_CHECKING, Iterable

from maimai_py.models import *

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient


class IProvider:
    @abstractmethod
    def _hash(self) -> str: ...


class ISongProvider(IProvider):
    """The provider that fetches songs from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`
    """

    @abstractmethod
    async def get_songs(self, client: "MaimaiClient") -> list[Song]:
        """@private"""
        raise NotImplementedError()


class IAliasProvider(IProvider):
    """The provider that fetches song aliases from a specific source.

    Available providers: `YuzuProvider`, `LXNSProvider`
    """

    @abstractmethod
    async def get_aliases(self, client: "MaimaiClient") -> dict[int, list[str]]:
        """@private"""
        raise NotImplementedError()


class IPlayerProvider(IProvider):
    """The provider that fetches players from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`
    """

    @abstractmethod
    async def get_player(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> Player:
        """@private"""
        raise NotImplementedError()


class IScoreProvider(IProvider):
    """The provider that fetches scores from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`, `WechatProvider`
    """

    async def get_scores_one(self, identifier: PlayerIdentifier, song: Song, client: "MaimaiClient") -> list[Score]:
        """@private"""
        scores = await self.get_scores_all(identifier, client)
        return [score for score in scores if score.id == song.id]

    async def get_scores_best(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        """@private"""
        return await self.get_scores_all(identifier, client)

    @abstractmethod
    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        """@private"""
        raise NotImplementedError()


class IScoreUpdateProvider(IProvider):
    """The provider that updates scores to a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`
    """

    @abstractmethod
    async def update_scores(self, identifier: PlayerIdentifier, scores: Iterable[Score], client: "MaimaiClient") -> None:
        """@private"""
        raise NotImplementedError()


class ICurveProvider(IProvider):
    """The provider that fetches statistics curves from a specific source.

    Available providers: `DivingFishProvider`
    """

    @abstractmethod
    async def get_curves(self, client: "MaimaiClient") -> dict[tuple[int, SongType], list[CurveObject]]:
        """@private"""
        raise NotImplementedError()


class IRegionProvider(IProvider):
    """The provider that fetches player regions from a specific source.

    Available providers: `ArcadeProvider`
    """

    @abstractmethod
    async def get_regions(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[PlayerRegion]:
        """@private"""
        raise NotImplementedError()


class IItemListProvider(IProvider):
    """The provider that fetches player item list data from a specific source.

    Available providers: `LXNSProvider`, `LocalProvider`
    """

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


class IAreaProvider(IProvider):
    """The provider that fetches area data from a specific source.

    Available providers: `LocalProvider`
    """

    @abstractmethod
    async def get_areas(self, lang: str, client: "MaimaiClient") -> dict[str, Area]:
        """@private"""
        raise NotImplementedError()


class IPlayerIdentifierProvider(IProvider):
    """The provider that fetches player identifiers from a specific source.

    Available providers: `ArcadeProvider`
    """

    @abstractmethod
    async def get_identifier(self, code: Union[str, dict[str, str]], client: "MaimaiClient") -> PlayerIdentifier:
        """@private"""
        raise NotImplementedError()
