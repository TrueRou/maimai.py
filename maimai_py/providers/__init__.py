from .base import IAliasProvider, IPlayerProvider, ISongProvider, IScoreProvider, ICurveProvider, IRegionProvider, LocalProvider
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
    "LocalProvider",
    "DivingFishProvider",
    "LXNSProvider",
    "YuzuProvider",
    "WechatProvider",
    "ArcadeProvider",
]
