# Examples

All functions can provide `provider` parameter, you can pass in different providers according to your needs, you can check which `providers` are supported by the function in IDE or API documentation.

## Get song information

``` Python
## Initialize MaimaiClient and cache all songs.
maimai = MaimaiClient()
songs = await maimai.songs()
# songs = await maimai.songs(provider=DivingFishProvider()) # You can manually specify the divingfish data provider

# Query songs by ID
song1 = songs.by_id(1231) # life unspecified
assert song1.title == “Unknown Life”
assert song1.difficulties.dx[3].note_designer == “はっぴー”

# Query songs from aliases
song2 = songs.by_alias(“unknown”)
assert song2.id == song1.id
```

## Get player information

``` Python
## Initialize MaimaiClient, initialize LXNS API, initialize divingfish API
maimai = MaimaiClient()
lxns = LXNSProvider(developer_token=“your_lxns_developer_token”)
divingfish = DivingFishProvider()

# Get information about player 664994421382429 from LXNS
player1 = await maimai.players(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
assert player1.rating > 10000

# Get turou player information from divingfish
player2 = await maimai.players(PlayerIdentifier(username=“turou”), provider=divingfish)
assert player2.rating > 10000
```

## Getting score information

``` Python
## Initialize MaimaiClient, initialize LXNS API, initialize divingfish API
maimai = MaimaiClient()
lxns = LXNSProvider(developer_token=“your_lxns_developer_token”)
divingfish = DivingFishProvider()

# Get all the scores for player 664994421382429 from LXNS
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# Returns a list of scores that can be calculated like rating, rating_b35, rating_b15, etc.
assert my_scores.rating_b35 > 10000
# You can also get individual ratings for the song 1231 MASTER by_level
assert my_scores.by_level(1231, LevelIndex.MASTER).dx_rating >= 308 # life not detailed MASTER SSS+

# Get the data from the divingfish and do something similar
my_scores = await maimai.scores(PlayerIdentifier(username=“turou”), provider=divingfish)
assert my_scores.rating > 15000
assert my_scores.by_level(1231, LevelIndex.MASTER).dx_rating >= 308 # Life is not long MASTER SSS+
```

## Get information about the plates

```python
# Initialize MaimaiClient, initialize LXNS APIs
maimai = MaimaiClient()
lxns = LXNSProvider(developer_token=“your_lxns_developer_token”)

# Get 664994421382429 player's 舞将 achievements from LXNS
my_plate = await maimai.plates(PlayerIdentifier(friend_code=664994421382429), “舞将”, provider=lxns)
assert my_plate.cleared_num + my_plate.remained_num == my_plate.all_num

# Print out the performance information for those who played, but didn't reach their goals
for plate_object in my_plate.remained.
    message = f “Your goal for the {plate_object.song.title} song on the 舞将 was not met, you played but did not fulfill the condition with the following score:”
    for score in plate_object.scores:
        message += f"{score.level} difficulty: {score.dx_rating} %\n”
```

## Updating scores to a data provider

```python
## Initialize MaimaiClient, initialize divingfish and LXNS APIs
maimai = MaimaiClient()
lxns = LXNSProvider(developer_token=“your_lxns_developer_token”)
divingfish = DivingFishProvider()

# pull scores from divingfish and upload to LXNS (kinda weird, just an example here, normally it should be fetched from wechat or arcade and then uploaded to the prober)
scores = await maimai.scores(PlayerIdentifier(username=“turou”), kind=ScoreKind.ALL, provider=divingfish)
await maimai.updates(PlayerIdentifier(friend_code=664994421382429), scores.scores, provider=lxns)
```

## Get scores from the machine and update the prober

```python
maimai = MaimaiClient()
lxns = LXNSProvider(developer_token=“your_lxns_developer_token”)

# The QRCode here is filled in with the parsed player QR code from WeChat
my_account = await maimai.qrcode(“SGWCMAID241218124023A51D36BFBF65DB955DEB72905905D6A12D8056371E0499C74CD3592FCXXXXXXXXX”)
scores = await maimai.scores(my_account, provider=ArcadeProvider())
await maimai.updates(PlayerIdentifier(friend_code=664994421382429), scores.scores, provider=lxns)
```

## Updating the scores prober by means of a proxy

This is a long section, so you can go to the sample project section to learn more about it.