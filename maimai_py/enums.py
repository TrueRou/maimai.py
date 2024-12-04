from enum import Enum

"""
Prebuilt Enums
"""


class ScoreKind(Enum):
    BEST = 0
    AP = 1
    ALL = 2


"""
Maimai Enums
"""


class LevelIndex(Enum):
    BASIC = 0
    ADVANCED = 1
    EXPERT = 2
    MASTER = 3
    ReMASTER = 4


class FCType(Enum):
    APP = "AP+"
    AP = "AP"
    FCP = "FC+"
    FC = "FC"


class FSType(Enum):
    FDXP = "FDX+"
    FDX = "FDX"
    FSP = "FS+"
    FS = "FS"
    SYNC = "SYNC PLAY"


class RateType(Enum):
    SSSP = "SSS+"
    SSS = "SSS"
    SSP = "SS+"
    SS = "SS"
    SP = "S+"
    S = "S"
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    C = "C"
    D = "D"


class SongType(Enum):
    STANDARD = "standard"
    DX = "dx"
    UTAGE = "utage"
