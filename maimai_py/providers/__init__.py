from .arcade import ArcadeProvider
from .base import IAliasProvider, IAreaProvider, ICurveProvider, IItemListProvider, IPlayerProvider, IRegionProvider, IScoreProvider, ISongProvider
from .divingfish import DivingFishProvider
from .hybrid import HybridProvider
from .local import LocalProvider
from .lxns import LXNSProvider
from .wechat import WechatProvider
from .yuzu import YuzuProvider

__all__ = [
    "IAliasProvider",
    "IPlayerProvider",
    "ISongProvider",
    "IScoreProvider",
    "ICurveProvider",
    "IItemListProvider",
    "IAreaProvider",
    "IRegionProvider",
    "HybridProvider",
    "LocalProvider",
    "DivingFishProvider",
    "LXNSProvider",
    "YuzuProvider",
    "WechatProvider",
    "ArcadeProvider",
]
