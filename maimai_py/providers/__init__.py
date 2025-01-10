from .base import IAliasProvider, IPlayerProvider, ISongProvider, IScoreProvider, ICurveProvider, IRegionProvider
from .divingfish import DivingFishProvider
from .lxns import LXNSProvider
from .yuzu import YuzuProvider
from .wechat import WechatProvider
from .arcade import ArcadeProvider

__all__ = [
    "IAliasProvider",
    "IPlayerProvider",
    "ISongProvider",
    "IScoreProvider",
    "ICurveProvider",
    "IRegionProvider",
    "DivingFishProvider",
    "LXNSProvider",
    "YuzuProvider",
    "WechatProvider",
    "ArcadeProvider",
]
