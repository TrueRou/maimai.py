# Core Concepts

In maimai.py, we have defined how functions and methods are called in a more common way.

Similar to the `RESTful` specification, if you understand our specification, you can develop in an intuitive way without having to read too much documentation and APIs.

## Asynchronous

In maimai.py, all methods and interfaces need to be called **asynchronously** through `MaimaiClient`, as shown below.

```python
from maimai_py.maimai import MaimaiClient, MaimaiSongs

client: MaimaiClient = MaimaiClient()
songs: MaimaiSongs = await client.songs()
```

For IO-intensive applications, asynchronous calls can provide significant development advantages by avoiding blocking without affecting readability. **maimai.py only supports asynchronous calls**.

We do not currently have plans to provide synchronous calls. If you encounter any difficulties, please contact us, and we will do our best to assist you.

::: tip
You can share a `MaimaiClient` instance throughout the application or create a new instance for each request.
:::

## Encapsulate

The previously mentioned `MaimaiSongs` is an encapsulated object. Compared to directly returning `list[Song]`, encapsulated objects provide some convenient methods.

For example, you can directly call methods like `songs.by_title()` for filtering. If needed, you can access the original list through `songs.songs`.

We have encapsulated most data (`MaimaiSongs`, `MaimaiScores`, `MaimaiPlates`), and readers can explore the predefined methods.

Due to the flexibility of encapsulated objects, we have designed a caching mechanism based on them to avoid multiple requests for chart information and other data. For details on the caching mechanism and cache refresh, please refer to the caching strategy section.

## Data Provider

In maimai.py, we introduced the concept of data provider, which enables a common way of fetching or uploading data from multiple sources.

::: info
As of now, we have supported data providers such as divingfish, LXNS, WeChat OffiAccount, and Maimai Arcade, which support submitting data to divingfish and LXNS.
:::

You can use the `provider` parameter when calling a method to indicate where to get the data from, for example:

```python
from maimai_py.maimai import MaimaiClient

client = MaimaiClient()
lxns = LXNSProvider(developer_token="your_lxns_developer_token")
divingfish = DivingFishProvider()

player_lxns = await maimai.players(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
player_diving = await maimai.players(PlayerIdentifier(username=“turou”), provider=divingfish)
```

We recommend that you use a global variable to store the instance of the provider so that you only need to provide the `developer_token` once.

## Player Identifier

When fetching or uploading player information, it is often necessary to identify the player. We use an instance of ``PlayerIdentifier`` as the identifier.

The `PlayerIdentifier` is a generic concept, you need to pass in the appropriate value depending on the use case, for example:

- LXNS doesn't have the concept of `username`, so passing in `username` will throw an exception when using LXNS as a provider.
- To upload scores to divingfish with username and password: `PlayerIdentitifer(username=“Username”, credentials=“Password”)`.
- Use Import-Token when uploading scores to divingfish: `PlayerIdentitifer(credentials=“Import-Token”)`.
- When using arcade as a provider, `credentials` is the player's encrypted userId.

## Next

At this point, you have learned all the core concepts of maimai.py.

- You are now capable of developing a maimai-related project based on maimai.py and are ready to start the journey.
- If you want to learn more about our features in detail, you can continue reading the documentation.
- For experienced developers, you can also [read the API documentation](https://api.maimai.turou.fun/maimai_py).