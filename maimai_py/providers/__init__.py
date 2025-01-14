from .base import IAliasProvider, IPlayerProvider, ISongProvider, IScoreProvider, ICurveProvider, IRegionProvider, IItemListProvider
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
    "IRegionProvider",
    "LocalProvider",
    "DivingFishProvider",
    "LXNSProvider",
    "YuzuProvider",
    "WechatProvider",
    "ArcadeProvider",
]
