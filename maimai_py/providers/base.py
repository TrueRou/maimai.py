from abc import abstractmethod

from httpx import AsyncClient

from maimai_py.models import Player, PlayerIdentifier, Score, Song, SongAlias


class ISongProvider:
    @abstractmethod
    async def get_songs(self, client: AsyncClient) -> list[Song]:
        raise NotImplementedError()


class IAliasProvider:
    @abstractmethod
    async def get_aliases(self, client: AsyncClient) -> list[SongAlias]:
        raise NotImplementedError()


class IPlayerProvider:
    @abstractmethod
    async def get_player(self, identifier: PlayerIdentifier, client: AsyncClient) -> Player:
        raise NotImplementedError()


class IScoreProvider:
    @abstractmethod
    async def get_scores_best(self, identifier: PlayerIdentifier, client: AsyncClient) -> tuple[list[Score], list[Score]]:
        raise NotImplementedError()

    @abstractmethod
    async def get_scores_all(self, identifier: PlayerIdentifier, client: AsyncClient) -> list[Score]:
        raise NotImplementedError()
