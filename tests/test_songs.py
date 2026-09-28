import pytest

from maimai_py.enums import FCType, RateType, SongType
from maimai_py.maimai import MaimaiClient
from maimai_py.providers import DivingFishProvider, LXNSProvider


@pytest.mark.asyncio(scope="session")
async def test_songs_fetching_divingfish(maimai: MaimaiClient, divingfish: DivingFishProvider):
    songs = await maimai.songs(provider=divingfish, curve_provider=divingfish)
    song1 = await songs.by_id(1231)  # 生命不詳
    song2 = await songs.by_alias("不知死活")

    assert song1 is not None and song2 is not None
    assert song1.title == "生命不詳"
    assert song1.difficulties.dx[3].note_designer == "はっぴー"
    assert song1.difficulties.dx[3].curve is not None
    assert song1.difficulties.dx[3].curve.sample_size > 10000
    assert song2.id == song1.id
    assert any(song.id == 1568 for song in await songs.by_keywords("超天酱"))

    song3 = await songs.by_id(1355)  # [協]ラグトレイン
    assert song3 is not None
    assert song3.difficulties.utage[0].is_buddy
    assert song3.difficulties.utage[0].buddy_notes is not None
    assert song3.difficulties.utage[0].buddy_notes.left_tap_num == 183

    assert await songs.by_id(998) is not None  # Oshama Scramble! (Cranky Remix)


@pytest.mark.asyncio(scope="session")
async def test_songs_fetching_lxns(maimai: MaimaiClient, lxns: LXNSProvider):
    songs = await maimai.songs(provider=lxns)
    song1 = await songs.by_id(1231)

    assert song1 is not None
    assert song1.difficulties.dx[0].tap_num != 0

    song2 = await songs.by_id(111355)  # [協]ラグトレイン
    assert song2 is not None
    assert song2.difficulties.utage[0].is_buddy
    assert song2.difficulties.utage[0].buddy_notes is not None
    assert song2.difficulties.utage[0].buddy_notes.left_tap_num == 183

    many_songs = await songs.get_batch([1231, 1232, 1233])
    assert len(many_songs) == 3


def _chart_entry(**overrides):
    """A chart_stats entry mirroring the real DivingFish response (trimmed)."""
    entry = {
        "cnt": 5262.0,
        "diff": "12",
        "fit_diff": 11.977104339850483,
        "avg": 99.2785099158366,
        "avg_dx": 5007.113162175543,
        "std_dev": 1.7406669216376824,
        "dist": [45, 8, 11, 6, 12, 168, 275, 598, 583, 1019, 880, 1318, 3101, 6115],  # ascending D..SSSP
        "fc_dist": [3797.0, 3156, 5353, 950, 883],  # [not-FC, FC, FCP, AP, APP]
    }
    entry.update(overrides)
    return entry


def test_deser_curve_fc_dist():
    curve = DivingFishProvider._deser_curve(_chart_entry())
    assert curve.sample_size == 5262
    assert curve.fit_level_value == pytest.approx(11.977, abs=1e-3)
    assert curve.avg_dx_score == pytest.approx(5007.11, abs=1e-2)
    # fc_dist is ordered [not-FC, FC, FCP, AP, APP], FCType is ordered APP/AP/FCP/FC.
    assert curve.fc_sample_size == {FCType.APP: 883, FCType.AP: 950, FCType.FCP: 5353, FCType.FC: 3156}
    # dist is ascending D..SSSP while RateType is ordered SSSP..D.
    assert curve.rate_sample_size[RateType.SSSP] == 6115
    assert curve.rate_sample_size[RateType.D] == 45
    assert sum(curve.fc_sample_size.values()) == 3156 + 5353 + 950 + 883  # the not-FC slot is excluded


def test_deser_curve_legacy_dist():
    entry = _chart_entry()
    del entry["fc_dist"]
    curve = DivingFishProvider._deser_curve(entry)
    # Legacy layouts merge the FC distribution into dist[1..4]: APP=dist[4], AP=dist[3], FCP=dist[2], FC=dist[1].
    assert curve.fc_sample_size == {
        FCType.APP: entry["dist"][4],
        FCType.AP: entry["dist"][3],
        FCType.FCP: entry["dist"][2],
        FCType.FC: entry["dist"][1],
    }


async def test_get_curves_maps_ids_and_filters_empty():
    class _FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "charts": {
                    "8": [_chart_entry(), _chart_entry(), _chart_entry(), _chart_entry(), {}],  # a SD song
                    "10999": [_chart_entry(), {}],  # a DX song, mapped to (999, DX)
                }
            }

    class _FakeHttp:
        async def get(self, url):
            assert url.endswith("chart_stats")
            return _FakeResp()

    class _FakeClient:
        _client = _FakeHttp()

    curves = await DivingFishProvider().get_curves(_FakeClient())  # type: ignore[arg-type]
    assert set(curves) == {(8, SongType.STANDARD), (999, SongType.DX)}
    assert len(curves[(8, SongType.STANDARD)]) == 4  # trailing {} placeholders are dropped
    assert len(curves[(999, SongType.DX)]) == 1


async def test_get_curves_uses_overridden_deser():
    class _CustomProvider(DivingFishProvider):
        @staticmethod
        def _deser_curve(chart: dict):
            curve = DivingFishProvider._deser_curve(chart)
            curve.sample_size += 1
            return curve

    class _FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"charts": {"8": [_chart_entry()]}}

    class _FakeHttp:
        async def get(self, url):
            return _FakeResp()

    class _FakeClient:
        _client = _FakeHttp()

    curves = await _CustomProvider().get_curves(_FakeClient())  # type: ignore[arg-type]
    assert curves[(8, SongType.STANDARD)][0].sample_size == 5263  # the override takes effect


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
