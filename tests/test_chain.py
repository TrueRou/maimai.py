from typing import Iterable

import pytest

from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerIdentifier, Score
from maimai_py.providers.base import IScoreProvider, IScoreUpdateProvider

source_counter, target_counter, callback_counter = 0, 0, 0


@pytest.mark.asyncio(scope="session")
async def test_update_chain(maimai: MaimaiClient):
    class MockProvider(IScoreProvider, IScoreUpdateProvider):
        async def get_scores_all(self, identifier: PlayerIdentifier, client: MaimaiClient) -> list[Score]:
            global source_counter
            source_counter += 1
            return []

        async def update_scores(self, identifier: PlayerIdentifier, scores: Iterable[Score], client: MaimaiClient) -> None:
            global target_counter
            target_counter += 1

    await maimai.updates_chain(
        source=[
            (MockProvider(), PlayerIdentifier(username="source1"), {}),
            (MockProvider(), PlayerIdentifier(username="source2"), {}),
            (MockProvider(), None, {}),
        ],
        target=[
            (MockProvider(), PlayerIdentifier(username="target1"), {}),
            (MockProvider(), PlayerIdentifier(username="target2"), {}),
            (MockProvider(), None, {}),
        ],
        source_callback=lambda ms, err, kwargs: globals().update(callback_counter=callback_counter + 1),
        target_callback=lambda ls, err, kwargs: globals().update(callback_counter=callback_counter + 2),
    )

    assert source_counter == 1 and target_counter == 2 and callback_counter == 5

    await maimai.updates_chain(
        source=[
            (MockProvider(), PlayerIdentifier(username="source1"), {}),
            (MockProvider(), PlayerIdentifier(username="source2"), {}),
            (MockProvider(), None, {}),
        ],
        target=[
            (MockProvider(), PlayerIdentifier(username="target1"), {}),
            (MockProvider(), PlayerIdentifier(username="target2"), {}),
            (MockProvider(), None, {}),
        ],
        source_callback=lambda sp, ms, err: globals().update(callback_counter=callback_counter + 1),
        target_callback=lambda tp, ls, err: globals().update(callback_counter=callback_counter + 2),
        source_mode="parallel",
        target_mode="fallback",
    )

    assert source_counter == 3 and target_counter == 3 and callback_counter == 9


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
