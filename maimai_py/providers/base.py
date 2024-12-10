from abc import abstractmethod
from typing import TYPE_CHECKING

from maimai_py.models import Player, PlayerIdentifier, Score, Song, SongAlias

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient


class ISongProvider:
    """The provider that fetches songs from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`
    """

    @abstractmethod
    async def get_songs(self, client: "MaimaiClient") -> list[Song]:
        """@private"""
        raise NotImplementedError()


class IAliasProvider:
    """The provider that fetches song aliases from a specific source.

    Available providers: `YuzuProvider`, `LXNSProvider`
    """

    @abstractmethod
    async def get_aliases(self, client: "MaimaiClient") -> list[SongAlias]:
        """@private"""
        raise NotImplementedError()


class IPlayerProvider:
    """The provider that fetches players from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`
    """

    @abstractmethod
    async def get_player(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> Player:
        """@private"""
        raise NotImplementedError()


class IScoreProvider:
    """The provider that fetches scores from a specific source.

    Available providers: `DivingFishProvider`, `LXNSProvider`, `WechatProvider`
    """

    @abstractmethod
    async def get_scores_best(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> tuple[list[Score], list[Score]]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        """@private"""
        raise NotImplementedError()

    @abstractmethod
    async def update_scores(self, identifier: PlayerIdentifier, scores: list[Score], client: "MaimaiClient") -> None:
        """@private"""
        raise NotImplementedError()
