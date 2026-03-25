from typing import Iterable

import pytest

from maimai_py import MaimaiClientMultithreading
from maimai_py.enums import LevelIndex, RateType, SongType
from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerIdentifier, Score
from maimai_py.providers.base import IScoreProvider, IScoreUpdateProvider
from maimai_py.providers.divingfish import DivingFishProvider
from maimai_py.providers.lxns import LXNSProvider


class MockArcadeProvider(IScoreProvider):
    def _hash(self) -> str:
        return "mock-arcade-provider"

    async def get_scores_all(self, identifier: PlayerIdentifier, client: MaimaiClient) -> list[Score]:
        return [
            Score(
                id=100998,
                level="14",
                level_index=LevelIndex.BASIC,
                achievements=100.0,
                fc=None,
                fs=None,
                dx_score=1234,
                dx_rating=100.0,
                play_count=1,
                play_time=None,
                rate=RateType.SSS,
                type=SongType.UTAGE,
            )
        ]


class MockDivingFishUpdateProvider(IScoreUpdateProvider):
    def __init__(self):
        self.uploaded: list[dict] = []

    def _hash(self) -> str:
        return "mock-divingfish-provider"

    async def update_scores(self, identifier: PlayerIdentifier, scores: Iterable[Score], client: MaimaiClient) -> None:
        songs = await client.songs()
        for score in scores:
            if payload := await DivingFishProvider._ser_score(score, songs):
                self.uploaded.append(payload)


@pytest.mark.asyncio(scope="session")
async def test_utage_only_song_can_be_uploaded_from_arcade_to_divingfish():
    client = MaimaiClientMultithreading()
    source = MockArcadeProvider()
    target = MockDivingFishUpdateProvider()

    # 模拟 Arcade 拉取成绩，再上传到。
    fetched_scores = await client.scores(PlayerIdentifier(username="source"), provider=source)
    await client.updates(PlayerIdentifier(username="target", credentials="password"), fetched_scores.scores, target)

    # 断言上传载荷中确实包含该宴谱条目。
    assert any(payload["title"].startswith("[宴]") for payload in target.uploaded)


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
