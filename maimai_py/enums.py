from enum import Enum

"""
Prebuilt Dicts
"""

plate_to_version: dict[str, int] = {
    "初": 10000,  # maimai
    "真": 11000,  # maimai PLUS
    "超": 12000,  # GreeN
    "檄": 13000,  # GreeN PLUS
    "橙": 14000,  # ORANGE
    "晓": 15000,  # ORANGE PLUS
    "桃": 16000,  # PiNK
    "樱": 17000,  # PiNK PLUS
    "紫": 18000,  # MURASAKi
    "堇": 18500,  # MURASAKi PLUS
    "白": 19000,  # MiLK
    "雪": 19500,  # MiLK PLUS
    "辉": 19900,  # FiNALE
    "熊": 20000,  # 舞萌DX
    "华": 20000,  # 舞萌DX
    "爽": 21000,  # 舞萌DX 2021
    "煌": 21000,  # 舞萌DX 2021
    "星": 22000,  # 舞萌DX 2022
    "宙": 22000,  # 舞萌DX 2022
    "祭": 23000,  # 舞萌DX 2023
    "祝": 23000,  # 舞萌DX 2023
    "双": 24000,  # 舞萌DX 2024
    "宴": 24000,  # 舞萌DX 2024
}
"""@private"""

current_version = list(plate_to_version.values())[-1]
"""@private

We consider the latest version to be the highest version in the plate_to_version dict.
"""

divingfish_to_version = {
    "maimai": 10000,
    "maimai PLUS": 11000,
    "maimai GreeN": 12000,
    "maimai GreeN PLUS": 13000,
    "maimai ORANGE": 14000,
    "maimai ORANGE PLUS": 15000,
    "maimai PiNK": 16000,
    "maimai PiNK PLUS": 17000,
    "maimai MURASAKi": 18000,
    "maimai MURASAKi PLUS": 18500,
    "maimai MiLK": 19000,
    "MiLK PLUS": 19500,
    "maimai FiNALE": 19900,
    "maimai でらっくす": 20000,
    "maimai でらっくす PLUS": 20000,
    "maimai でらっくす Splash": 21000,
    "maimai でらっくす Splash PLUS": 21000,
    "maimai でらっくす UNiVERSE": 22000,
    "maimai でらっくす UNiVERSE PLUS": 22000,
    "maimai でらっくす FESTiVAL": 23000,
    "maimai でらっくす FESTiVAL PLUS": 23000,
    "maimai でらっくす BUDDiES": 24000,
}
"""@private"""

plate_aliases: dict[str, str] = {
    "暁": "晓",
    "櫻": "樱",
    "菫": "堇",
    "輝": "辉",
    "華": "华",
    "極": "极",
}
"""@private"""


class ScoreKind(Enum):
    BEST = 0
    ALL = 1


class LevelIndex(Enum):
    BASIC = 0
    ADVANCED = 1
    EXPERT = 2
    MASTER = 3
    ReMASTER = 4


class FCType(Enum):
    APP = 0
    AP = 1
    FCP = 2
    FC = 3


class FSType(Enum):
    SYNC = 0
    FS = 1
    FSP = 2
    FSD = 3
    FSDP = 4


class RateType(Enum):
    SSSP = 0
    SSS = 1
    SSP = 2
    SS = 3
    SP = 4
    S = 5
    AAA = 6
    AA = 7
    A = 8
    BBB = 9
    BB = 10
    B = 11
    C = 12
    D = 13

    def _from_achievement(achievement: float) -> "RateType":
        if achievement >= 100.5:
            return RateType.SSSP
        if achievement >= 100:
            return RateType.SSS
        if achievement >= 99.5:
            return RateType.SSP
        if achievement >= 99:
            return RateType.SS
        if achievement >= 98:
            return RateType.SP
        if achievement >= 97:
            return RateType.S
        if achievement >= 94:
            return RateType.AAA
        if achievement >= 90:
            return RateType.AA
        if achievement >= 80:
            return RateType.A
        if achievement >= 75:
            return RateType.BBB
        if achievement >= 70:
            return RateType.BB
        if achievement >= 60:
            return RateType.B
        if achievement >= 50:
            return RateType.C
        return RateType.D


class SongType(Enum):
    STANDARD = "standard"
    DX = "dx"
    UTAGE = "utage"

    def _from_id(id: int | str) -> "SongType":
        id = int(id)
        return SongType.UTAGE if id > 100000 else SongType.DX if id > 10000 else SongType.STANDARD

    def _to_id(self, id: int | str) -> int:
        return id if self == SongType.STANDARD else id + 10000 if self == SongType.DX else id + 100000

    def _to_abbr(self) -> str:
        return "SD" if self == SongType.STANDARD else "DX" if self else "UTAGE"
