from httpx import AsyncClient
from maimai_py.enums import ScoreKind
from maimai_py.exceptions import InvalidDeveloperTokenError
from maimai_py.models import DivingFishPlayer, Player, PlayerIdentifier, Song
from maimai_py.providers.base import IPlayerProvider, IScoreProvider, ISongProvider


class DivingFishProvider(ISongProvider, IPlayerProvider, IScoreProvider):
    base_url = "https://www.diving-fish.com/api/maimaidxprober/"

    def headers(self):
        if not self.developer_token:
            raise InvalidDeveloperTokenError()
        return {"developer-token": self.developer_token}

    def __init__(self, developer_token: str | None = None):
        self.developer_token = developer_token

    async def get_songs(self, client: AsyncClient) -> list[Song]:
        raise NotImplementedError

    async def get_player(self, identifier: PlayerIdentifier, client: AsyncClient) -> Player:
        resp = await client.post(self.base_url + "query/player", json=identifier.as_diving_fish())
        resp.raise_for_status()
        resp_json = resp.json()
        return DivingFishPlayer(
            name=resp_json["username"],
            rating=resp_json["rating"],
            nickname=resp_json["nickname"],
            plate=resp_json["plate"],
            additional_rating=resp_json["additional_rating"],
        )

    async def get_scores(self, identifier: PlayerIdentifier, kind: ScoreKind, client: AsyncClient) -> None:
        raise NotImplementedError
