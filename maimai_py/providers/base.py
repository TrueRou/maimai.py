from abc import abstractmethod

from httpx import AsyncClient

from maimai_py.enums import RecordKind
from maimai_py.exceptions import ProviderNotApplicableError
from maimai_py.models import Player, PlayerIdentifier, Song, SongAlias


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
    async def get_scores(self, kind: RecordKind, identifier: PlayerIdentifier, client: AsyncClient) -> None:
        raise ProviderNotApplicableError()
