# DivingFishProvider

Implementations: ISongProvider, IPlayerProvider, IScoreProvider

Source: https://www.diving-fish.com/maimaidx/prober/

Apply for Developer Token: Login - Edit Profile - Click “Here” button - Apply for new Token

Developer QQ Group: 605800479

## About Developer Token

The Developer Token for divingfish is only necessary in the following cases:

- Get all scores of a player (ScoreKind.ALL)

## About uploading scores

There are two ways for a divingfish to upload scores.

- Using divingfish username and password: `PlayerIdentitifer(username=“Username”, credentials=“Password”)`
- Using an Import-Token: `PlayerIdentitifer(credentials=“Import-Token”)`