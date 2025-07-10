# 单元用例

所有的例子完全摘抄自 [maimai.py 单元测试](https://github.com/TrueRou/maimai.py/tree/main/tests)，仅推荐有经验的开发者阅读。

如果您阅读下面的内容有困难，建议先阅读 [开始](./get-started.md) 章节，然后进入 **功能** 章节阅读。

## conftest.py

```python
@pytest.fixture(scope="session")
def maimai():
    return MaimaiClient()


@pytest.fixture(scope="session")
def lxns():
    token = os.environ.get("LXNS_DEVELOPER_TOKEN")
    return LXNSProvider(developer_token=token)


@pytest.fixture(scope="session")
def divingfish():
    token = os.environ.get("DIVINGFISH_DEVELOPER_TOKEN")
    return DivingFishProvider(developer_token=token)


@pytest.fixture(scope="session")
def arcade():
    return ArcadeProvider()


@pytest.fixture(scope="session")
def lxns_player():
    personal_token = os.environ.get("LXNS_PERSONAL_TOKEN")
    return PlayerIdentifier(credentials=personal_token)


@pytest.fixture(scope="session")
def divingfish_player():
    username = os.environ.get("DIVINGFISH_USERNAME")
    password = os.environ.get("DIVINGFISH_PASSWORD")
    return PlayerIdentifier(username=username, credentials=password)


@pytest.fixture(scope="session")
def arcade_player():
    encrypted_userid = os.environ.get("ARCADE_ENCRYPTED_USERID")
    return PlayerIdentifier(credentials=encrypted_userid)
```

## test_songs.py

```python
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
    assert any([song.id == 1568 for song in await songs.by_keywords("超天酱")])


@pytest.mark.asyncio(scope="session")
async def test_songs_fetching_lxns(maimai: MaimaiClient, lxns: LXNSProvider):
    songs = await maimai.songs(provider=lxns)
    song1 = await songs.by_id(1231)

    assert song1 is not None
    assert song1.difficulties.dx[0].tap_num != 0

    many_songs = await songs.get_batch([1231, 1232, 1233])
    assert len(many_songs) == 3
```

## test_scores.py

```python
@pytest.mark.asyncio(scope="session")
async def test_scores_fetching_lxns(maimai: MaimaiClient, lxns: LXNSProvider, lxns_player: PlayerIdentifier):
    my_scores = await maimai.scores(lxns_player, provider=lxns)
    assert my_scores.rating_b35 > 10000
    score = my_scores.by_song(1231, level_index=LevelIndex.MASTER)[0]
    assert score.dx_rating >= 308 if score.dx_rating else True  # 生命不詳 MASTER SSS+

    bests = await maimai.bests(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
    assert my_scores.rating == bests.rating

    bests_fallback = await maimai.bests(lxns_player, provider=lxns)
    assert my_scores.rating == bests_fallback.rating
    assert len(bests_fallback.scores_b35) <= 35

    preview = await maimai.minfo(1231, PlayerIdentifier(friend_code=664994421382429), provider=lxns)
    assert preview is not None
    assert all(score.id == preview.song.id for score in preview.scores)

    for song, diff, score in await my_scores.get_mapping():
        assert song.id == score.id and diff.type == score.type and diff.level_index == score.level_index


@pytest.mark.asyncio(scope="session")
async def test_scores_fetching_divingfish(maimai: MaimaiClient, divingfish: DivingFishProvider, divingfish_player: PlayerIdentifier):
    my_scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
    assert my_scores.rating_b35 > 10000
    score = my_scores.by_song(1231, level_index=LevelIndex.MASTER)[0]
    assert score.dx_rating >= 308 if score.dx_rating else True  # 生命不詳 MASTER SSS+

    bests = await maimai.bests(divingfish_player, provider=divingfish)
    assert my_scores.rating == bests.rating
    assert len(bests.scores_b15) <= 15

    preview = await maimai.minfo(1231, PlayerIdentifier(username="turou"), provider=divingfish)
    assert preview is not None
    assert all(score.id == preview.song.id for score in preview.scores)


@pytest.mark.asyncio(scope="session")
async def test_scores_fetching_arcade(maimai: MaimaiClient, arcade: ArcadeProvider, arcade_player: PlayerIdentifier):
    try:
        scores = await maimai.scores(arcade_player, provider=arcade)
        assert scores.rating > 2000

        player: Player = await maimai.players(arcade_player, provider=arcade)
        assert player.rating == scores.rating
    except Exception:
        pytest.skip("Connection error, skipping the test.")


@pytest.mark.asyncio(scope="session")
async def test_plate_fetching(maimai: MaimaiClient, lxns: LXNSProvider):
    my_plate = await maimai.plates(PlayerIdentifier(friend_code=664994421382429), "桃将", provider=lxns)
    cleared_obj = [obj for obj in await my_plate.get_cleared() if obj.song.id == 411]
    remained_obj = [obj for obj in await my_plate.get_remained() if obj.song.id == 411]
    assert len(cleared_obj) == 1 and LevelIndex.MASTER in cleared_obj[0].levels
    assert len(remained_obj) == 1 and LevelIndex.MASTER not in remained_obj[0].levels
    assert await my_plate.count_cleared() + await my_plate.count_remained() == await my_plate.count_all()


@pytest.mark.asyncio(scope="session")
async def test_scores_updating_lxns(maimai: MaimaiClient, lxns: LXNSProvider, lxns_player: PlayerIdentifier):
    scores = []
    await maimai.updates(PlayerIdentifier(friend_code=664994421382429), scores, provider=lxns)
    await maimai.updates(lxns_player, scores, provider=lxns)


@pytest.mark.asyncio(scope="session")
async def test_scores_updating_divingfish(maimai: MaimaiClient, divingfish: DivingFishProvider, divingfish_player: PlayerIdentifier):
    scores = []
    await maimai.updates(divingfish_player, scores, provider=divingfish)
```

## test_players.py

```python
@pytest.mark.asyncio(scope="session")
async def test_players_fetching_lxns(maimai: MaimaiClient, lxns: LXNSProvider, lxns_player: PlayerIdentifier):
    player = await maimai.players(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
    assert player.rating > 10000

    player_personal = await maimai.players(lxns_player, provider=lxns)
    assert player.rating == player_personal.rating


@pytest.mark.asyncio(scope="session")
async def test_players_fetching_divingfish(maimai: MaimaiClient, divingfish: DivingFishProvider, divingfish_player: PlayerIdentifier):
    player = await maimai.players(divingfish_player, provider=divingfish)
    assert player.rating > 10000
```

## test_items.py

```python
@pytest.mark.asyncio(scope="session")
async def test_regions(maimai: MaimaiClient, arcade: ArcadeProvider, arcade_player: PlayerIdentifier):
    try:
        regions = await maimai.regions(arcade_player, provider=arcade)
        assert any(region.region_id == 2 for region in regions)
    except Exception:
        pytest.skip("Connection error, skipping the test.")


@pytest.mark.asyncio(scope="session")
async def test_areas(maimai: MaimaiClient):
    areas = await maimai.areas()
    assert len(await areas.get_all()) >= 1
    assert all(len(area.songs) >= 1 for area in await areas.get_all())
```

## test_client.py

```python
@pytest.mark.asyncio(scope="session")
async def test_singleton(maimai: MaimaiClient):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m_client2 = MaimaiClient()
        assert maimai is m_client2
    m_client_mt1 = MaimaiClientMultithreading(cache_ttl=114)
    m_client_mt2 = MaimaiClientMultithreading(cache_ttl=514)
    assert m_client_mt1 is not m_client_mt2
    assert m_client_mt1._cache_ttl == 114
    assert m_client_mt2._cache_ttl == 514
```