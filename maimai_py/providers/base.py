from abc import abstractmethod

from httpx import AsyncClient

from maimai_py.exceptions import ProviderNotApplicableError
from maimai_py.models import Player, PlayerIdentifier, Score, Song, SongAlias


class ISongProvider:
    @abstractmethod
    async def get_songs(self, client: AsyncClient) -> list[Song]:
        raise ProviderNotApplicableError()


class IAliasProvider:
    @abstractmethod
    async def get_aliases(self, client: AsyncClient) -> list[SongAlias]:
        raise ProviderNotApplicableError()


class IPlayerProvider:
    @abstractmethod
    async def get_player(self, identifier: PlayerIdentifier, client: AsyncClient) -> Player:
        raise ProviderNotApplicableError()


class IScoreProvider:
    @abstractmethod
    async def get_scores_best(self, identifier: PlayerIdentifier, ap_only: bool, client: AsyncClient) -> tuple[list[Score], list[Score]]:
        raise ProviderNotApplicableError()

    @abstractmethod
    async def get_scores_all(self, identifier: PlayerIdentifier, client: AsyncClient) -> list[Score]:
        raise ProviderNotApplicableError()
