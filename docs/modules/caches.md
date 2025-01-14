# Cache Strategy

## Cache Strategy

In the current version of maimai.py, there are a total of 9 types of data that will be cached, as shown in the table below.

| Name         | Active Cache Scenario | Passive Cache Scenario              | Default Data Source  |
|--------------|-----------------------|-------------------------------------|----------------------|
| `songs`      | Fetch songs           | Fetching scores if song is required | `LXNSProvider`       |
| `aliases`    | Fetch songs           | Fetching scores if song is required | `None (not fetched)` |
| `curves`     | Fetch songs           | Fetching scores if song is required | `None (not fetched)` |
| `icons`      | Fetch icons           | Fetching scores if song is required | `LXNSProvider`       |
| `nameplates` | Fetch nameplates      | Fetching scores if song is required | `LXNSProvider`       |
| `frames`     | Fetch frames          | Fetching scores if song is required | `LXNSProvider`       |
| `trophies`   | Fetch trophys         | Fetching scores if song is required | `LocalProvider`      |
| `charas`     | Fetch characters      | Fetching scores if song is required | `LocalProvider`      |
| `partners`   | Fetch partners        | Fetching scores if song is required | `LocalProvider`      |

When encountering a cache scenario, it will first check if the cache exists. If it does, it will return the cached data directly; otherwise, it will request data from the data source and cache it.

It should be noted that when an active cache scenario is triggered, the data source you actively specify will be used for caching, replacing the default data source.

Therefore, you can manually specify the data source by calling the active cache method and cache the data in advance, for example:

```python
# Fetch scores for the first time, passively cache song info, using default cache data source (LXNSProvider, None, None)
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# Fetch scores again, since song info has been cached, it will not request song info again
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# Manually fetch song info, trigger active cache scenario, using data source (DivingFishProvider, YuzuProvider, DivingFishProvider)
songs = await maimai.songs(provider=DivingFishProvider())
# Fetch scores again, since song info has been cached, it will not request song info again, but this time the song info includes song aliases and song curves
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
```

## Cache Refresh

maimai.py does not automatically refresh the cache, but you can manually refresh the cache by calling the `flush` method, for example:

```python
# Manually fetch song info, trigger active cache scenario, using data source (DivingFishProvider, YuzuProvider, DivingFishProvider)
songs = await maimai.songs(provider=DivingFishProvider())

# Assume refreshing the cache once a day
async def daily_flush():
    while True:
        await maimai.flush()
        await asyncio.sleep(86400)

# Start the async scheduler
asyncio.create_task(daily_flush())
```

The `flush` method will check all currently cached data, and if the data source supports the refresh operation, it will call the refresh method of the data source.

## Performance Recommendations

Please try to minimize the number of times the active cache scenario is triggered, as the active cache scenario will cause the data source to request data and cache it, which is a time-consuming operation.

Generally speaking, you only need to manually cache once when the program starts and refresh the cache at a fixed time every day.

If you are developing a web application, we recommend using maimai.py in a way similar to the following:

```python
from fastapi import FastAPI
import asyncio
from maimai import Maimai, DivingFishProvider

app = FastAPI()
maimai = Maimai()
maimai_songs = None # Singleton object, fetch once, use everywhere

@app.on_event("startup")
async def startup_event():
    maimai_songs = await maimai.songs(provider=DivingFishProvider())
    my_scheduler = asyncio.create_task(daily_flush()) # Call flush at a fixed time every day

@app.get("/songs/list", response_model=list[Song])
async def get_songs():
    return maimai_songs.songs # Data model conversion omitted
```

## maimai.flush() Method

Refer to https://api.maimai.turou.fun/maimai_py#MaimaiClient.flush