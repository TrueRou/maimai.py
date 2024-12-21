# LXNSProvider

Implementations: ISongProvider, IPlayerProvider, IScoreProvider, IAliasProvider

Source: https://maimai.lxns.net/

Apply for Developer Token: https://maimai.lxns.net/developer

Developer QQ Group: 991669419

## About Developer Token

LXNS's Developer Token is necessary only in the following scenarios:

- Getting player information
- Get player's B50 score (ScoreKind.BEST)
- Get the player's all scores (ScoreKind.ALL)
- Update player scores

It is recommended to always provide a developer token for LXNS, which is required for most of LXNS's actions.

## About alias providers

LXNS has its own alias provider (IAliasProvider), but the data may not be as full as Yuzu's, so it is recommended to use Yuzu.

## About privacy settings

When getting or uploading information through LXNS, you need to agree to LXNS's privacy settings, otherwise a privacy exception will be thrown.

! [Snipaste_2024-12-21_12-52-35.png](https://s2.loli.net/2024/12/21/EcjIO8eDuWvQotB.png)