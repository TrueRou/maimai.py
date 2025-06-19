from .arcade import ArcadeProvider
from .base import (
    IAliasProvider,
    IAreaProvider,
    ICurveProvider,
    IIdentifierProvider,
    IItemListProvider,
    IPlayerProvider,
    IProvider,
    IRegionProvider,
    IScoreProvider,
    IScoreUpdateProvider,
    ISongProvider,
)
from .divingfish import DivingFishProvider
from .local import LocalProvider
from .lxns import LXNSProvider
from .wechat import WechatProvider
from .yuzu import YuzuProvider

__all__ = [
    "IProvider",
    "IScoreUpdateProvider",
    "IAliasProvider",
    "IAreaProvider",
    "ICurveProvider",
    "IItemListProvider",
    "IPlayerProvider",
    "IRegionProvider",
    "IScoreProvider",
    "ISongProvider",
    "IIdentifierProvider",
    "ArcadeProvider",
    "DivingFishProvider",
    "LocalProvider",
    "LXNSProvider",
    "WechatProvider",
    "YuzuProvider",
]
