# maimai.py

maimai.py is a library for MaimaiCN-related development, wrapping commonly used functions and models for developers.

The key features are:

- **Universal**: Provides data models based on MaimaiJP standards, breaking the barrier of terms confusion between different data sources.
- **Functional**: Various functions covering crawling, querying, uploading, etc. Support for songs, player information, scores, ratings, name plates, etc.
- **Easy**: e.g. `maimai.scores(PlayerIdentifier(username=“turou”), provider=divingfish)` can get all scores of turou in divingfish.
- **Documentated**: Provides user-friendly documentation, also provides a complete API documentation. Most of hints can be instantly accessed directly in the IDE.
- **Advanced**: Support fetching player scores with WeChat OpenID, parse scores HTML, and upload to data source.
- **Arcade✨**: Allows to get players' scores from the arcade via players' QR codes. In the progress, userId are powerful encrypted to keep safe.

You can checkout our api docs at https://maimai-py.pages.dev/.

## Installation

```bash
pip install maimai-py
```

To upgrade:

```bash
pip install -U maimai-py
```

## Example

```python
import asyncio
from maimai_py import MaimaiClient, MaimaiPlates, MaimaiScores, MaimaiSongs, PlayerIdentifier, LXNSProvider, DivingFishProvider


async def quick_start():
    maimai = MaimaiClient()
    divingfish = DivingFishProvider(developer_token="")

    # fetch all songs and their metadata
    songs: MaimaiSongs = await maimai.songs()
    # fetch divingfish user turou's scores (b50 scores by default)
    scores: MaimaiScores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
    # fetch divingfish user turou's 舞将 plate information
    plates: MaimaiPlates = await maimai.plates(PlayerIdentifier(username="turou"), "舞将", provider=divingfish)

    song = songs.by_id(1231)  # 生命不詳 by 蜂屋ななし

    print(f"Song 1231: {song.artist} - {song.title}")
    print(f"TuRou's rating: {scores.rating}, b15 top rating: {scores.scores_b15[0].dx_rating}")
    print(f"TuRou's 舞将: {plates.cleared_num}/{plates.all_num} cleared")

asyncio.run(quick_start())
```

## Async

maimai.py is fully asynchronous by default, and there are no plans to provide synchronous methods.

If you don't want to be asynchronous, you can use the `asyncio.run` wrapper to call asynchronous methods synchronously.