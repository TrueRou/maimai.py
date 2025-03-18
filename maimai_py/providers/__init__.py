from .base import IAliasProvider, IPlayerProvider, ISongProvider, IScoreProvider, ICurveProvider, IRegionProvider, IItemListProvider, IAreaProvider
from .divingfish import DivingFishProvider
from .lxns import LXNSProvider
from .yuzu import YuzuProvider
from .wechat import WechatProvider
from .arcade import ArcadeProvider
from .local import LocalProvider

__all__ = [
    "IAliasProvider",
    "IPlayerProvider",
    "ISongProvider",
    "IScoreProvider",
    "ICurveProvider",
    "IItemListProvider",
    "IAreaProvider",
    "IRegionProvider",
    "LocalProvider",
    "DivingFishProvider",
    "LXNSProvider",
    "YuzuProvider",
    "WechatProvider",
    "ArcadeProvider",
]
