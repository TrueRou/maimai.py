# Core Concepts

In maimai.py, we have defined how methods and interfaces are called in a more standardized way.

Similar to the Restful specification, if you understand our specification, you can develop in an intuitive way without having to read too much documentation and APIs.

## Invoking functions

In maimai.py, all methods and interfaces need to be called **asynchronously** via ``MaimaiClient``, which looks like this.

``python
from maimai_py.maimai import MaimaiClient, MaimaiSongs

client: MaimaiClient = MaimaiClient()
songs: MaimaiSongs = await client.songs()
```

Here `await client.songs()` returns a wrapped `MaimaiSongs`, and the wrapped instance provides you with some convenience methods compared to returning `list[Song]` directly.

For example, you can call methods such as `songs.by_title()` to filter directly, or `songs.songs` to access the original list if desired.

We have wrapped most of the data (`MaimaiSongs`, `MaimaiScores`, `MaimaiPlates`), so you can check out the pre-built methods for yourself.

> You can share `MaimaiClient` instances throughout your application, or create new instances on each request.

## Providing a data provider

Most of the methods in maimai.py can't be separated from the **"get/submit data from somewhere ”** logic, and we refer to the target location as the **Provider**.

> As of now, we have supported data providers such as divingfish, LXNS, WeChat OffiAccount, and Maimai Arcade, which support submitting data to divingfish and LXNS.

You can call the method passing in the ``provider`` parameter to tell the framework where to get the data from, e.g.:

``python
from maimai_py.maimai import MaimaiClient

client = MaimaiClient()
lxns = LXNSProvider(developer_token=“your_lxns_developer_token”)
divingfish = DivingFishProvider()

player_lxns = await maimai.players(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
player_diving = await maimai.players(PlayerIdentifier(username=“turou”), provider=divingfish)
```

We recommend that you use a global variable to store the instance of the provider so that you only need to provide the `developer_token` once.

## Providing a player identifier

When fetching or uploading player information, it is often necessary to identify the player, and we use an instance of ``PlayerIdentifier`` as the identifier.

The `PlayerIdentifier` is a generic concept, you need to pass in the appropriate value depending on the use case, for example:

- LXNS doesn't have the concept of `username`, so passing in `username` will throw an exception when using LXNS as a provider.
- To upload scores to divingfish with username and password: `PlayerIdentitifer(username=“Username”, credentials=“Password”)`.
- Use Import-Token when uploading scores to divingfish: `PlayerIdentitifer(credentials=“Import-Token”)`.
- When using arcade as a provider, `credentials` is the player's encrypted userId.

## Next

At this point, you have learned all the core concepts of maimai.py.

- You are now capable of developing a maimai-related project based on maimai.py and are ready to start the journey.
- If you want to learn more about our features in detail, you can continue reading the documentation.
- For experienced developers, you can also [read the API documentation](https://maimai-py.pages.dev/maimai_py).