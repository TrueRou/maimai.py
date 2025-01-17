# Caching Strategy

## Caching Strategy

In the current version of maimai.py, there are a total of 9 types of data that are cached, as shown in the table below.

| Parameter Name | Caching Scenario                                             | Default Cache Data Source |
|----------------|--------------------------------------------------------------|---------------------------|
| `songs`        | Fetching songs or depends on songs when fetching scores      | `LXNSProvider`            |
| `aliases`      | Fetching songs or depends on songs when fetching scores      | `YuzuProvider`            |
| `curves`       | Fetching songs or depends on songs when fetching scores      | `DivingFishProvider`      |
| `icons`        | Fetching icons or depends on songs when fetching scores      | `LXNSProvider`            |
| `nameplates`   | Fetching nameplates or depends on songs when fetching scores | `LXNSProvider`            |
| `frames`       | Fetching frames or depends on songs when fetching scores     | `LXNSProvider`            |
| `trophies`     | Fetching trophies or depends on songs when fetching scores   | `LocalProvider`           |
| `charas`       | Fetching characters or depends on songs when fetching scores | `LocalProvider`           |
| `partners`     | Fetching partners or depends on songs when fetching scores   | `LocalProvider`           |

When encountering a caching scenario, it will first check if the cache exists. If it does, it will return the cached data directly; otherwise, it will request data from the data source and cache it.

It should be noted that when overriding the default data source, the cache will be REFRESHED using the data source you specified, replacing the default data source.

Therefore, you can manually specify the data source and cache the data in advance by actively calling methods, for example:

```python
# First time fetching scores, passively caching song information, using the default cache data source (LXNSProvider, YuzuProvider, DivingFishProvider)
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# Fetch scores again, since the song information is already cached, it will not request the song information again
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# Manually fetch song information, since the Provider is overwritten, it will actively refresh the cache, using the data source (DivingFishProvider, YuzuProvider, DivingFishProvider)
songs = await maimai.songs(provider=DivingFishProvider())
# Fetch scores again, since the song information is already cached, it will not request the song information again
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# Of course, you can also force refresh the cache by providing the flush parameter
# Since the default data source has been overwritten, it will use the data source (DivingFishProvider, YuzuProvider, DivingFishProvider)
songs = await maimai.songs(flush=True)
```

## Cache Refresh

maimai.py does not automatically refresh the cache. The first method of refreshing has been mentioned above, which is to force refresh the cache by specifying the flush parameter.

```python
songs = await maimai.songs()
await asyncio.sleep(86400) # Simulate one day later
songs = await maimai.songs(flush=True)
```

For multiple types of data, calling methods one by one is cumbersome, so maimai.py provides the `flush` method to refresh all cached data.

```python
songs = await maimai.songs()
nameplates = await maimai.items(PlayerNameplates)()
await asyncio.sleep(86400) # Simulate one day later
await maimai.flush() # Refresh all cached data
```

## Performance Recommendations

You do not need to frequently refresh the cache. Generally, it is sufficient to refresh the cache at a fixed time each day.

If you are developing a web application, we recommend using maimai.py in a way similar to the following:

```python
from fastapi import FastAPI
import asyncio
from maimai import MaimaiClient, DivingFishProvider

app = FastAPI()
maimai = MaimaiClient()

@app.on_event("startup")
async def startup_event():
    maimai_songs = await maimai.songs()
    my_scheduler = asyncio.create_task(daily_flush()) # Call flush at a fixed time each day

@app.get("/songs/list", response_model=list[Song])
async def get_songs():
    return await maimai.songs() # This will fetch data from the cache, avoiding additional requests
```

::: info
For more information on web applications, please refer to our built-in web implementation [api.py](https://github.com/TrueRou/maimai.py/blob/main/maimai_py/api.py)
:::