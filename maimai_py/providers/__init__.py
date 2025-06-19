from .arcade import ArcadeProvider
from .base import (
    IAimeProvider,
    IAliasProvider,
    IAreaProvider,
    ICurveProvider,
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
    "IAimeProvider",
    "ArcadeProvider",
    "DivingFishProvider",
    "LocalProvider",
    "LXNSProvider",
    "WechatProvider",
    "YuzuProvider",
]
