from enum import Enum, IntEnum


class Version(IntEnum):
    MAIMAI = 10000
    MAIMAI_PLUS = 11000
    MAIMAI_GREEN = 12000
    MAIMAI_GREEN_PLUS = 13000
    MAIMAI_ORANGE = 14000
    MAIMAI_ORANGE_PLUS = 15000
    MAIMAI_PINK = 16000
    MAIMAI_PINK_PLUS = 17000
    MAIMAI_MURASAKI = 18000
    MAIMAI_MURASAKI_PLUS = 18500
    MAIMAI_MILK = 19000
    MAIMAI_MILK_PLUS = 19500
    MAIMAI_FINALE = 19900
    MAIMAI_DX = 20000
    MAIMAI_DX_PLUS = 20000
    MAIMAI_DX_SPLASH = 21000  # 舞萌DX 2021
    MAIMAI_DX_UNIVERSE = 22000  # 舞萌DX 2022
    MAIMAI_DX_FESTIVAL = 23000  # 舞萌DX 2023
    MAIMAI_DX_BUDDIES = 24000  # 舞萌DX 2024
    MAIMAI_DX_FUTURE = 30000  # 舞萌DX 2077


class Genre(Enum):
    POPSアニメ = "POPSアニメ"
    niconicoボーカロイド = "niconicoボーカロイド"
    東方Project = "東方Project"
    ゲームバラエティ = "ゲームバラエティ"
    maimai = "maimai"
    オンゲキCHUNITHM = "オンゲキCHUNITHM"
    宴会場 = "宴会場"


all_versions = list(Version.__members__.values())
"""@private"""

current_version = all_versions[-2]
"""@private"""

plate_to_version: dict[str, Version] = {
    "初": Version.MAIMAI,
    "真": Version.MAIMAI_PLUS,
    "超": Version.MAIMAI_GREEN,
    "檄": Version.MAIMAI_GREEN_PLUS,
    "橙": Version.MAIMAI_ORANGE,
    "晓": Version.MAIMAI_ORANGE_PLUS,
    "桃": Version.MAIMAI_PINK,
    "樱": Version.MAIMAI_PINK_PLUS,
    "紫": Version.MAIMAI_MURASAKI,
    "堇": Version.MAIMAI_MURASAKI_PLUS,
    "白": Version.MAIMAI_MILK,
    "雪": Version.MAIMAI_MILK_PLUS,
    "辉": Version.MAIMAI_FINALE,
    "熊": Version.MAIMAI_DX,
    "华": Version.MAIMAI_DX,
    "爽": Version.MAIMAI_DX_SPLASH,
    "煌": Version.MAIMAI_DX_SPLASH,
    "星": Version.MAIMAI_DX_UNIVERSE,
    "宙": Version.MAIMAI_DX_UNIVERSE,
    "祭": Version.MAIMAI_DX_FESTIVAL,
    "祝": Version.MAIMAI_DX_FESTIVAL,
    "双": Version.MAIMAI_DX_BUDDIES,
    "宴": Version.MAIMAI_DX_BUDDIES,
    "未": Version.MAIMAI_DX_FUTURE,
}
"""@private"""


divingfish_to_version: dict[str, Version] = {
    "maimai": Version.MAIMAI,
    "maimai PLUS": Version.MAIMAI_PLUS,
    "maimai GreeN": Version.MAIMAI_GREEN,
    "maimai GreeN PLUS": Version.MAIMAI_GREEN_PLUS,
    "maimai ORANGE": Version.MAIMAI_ORANGE,
    "maimai ORANGE PLUS": Version.MAIMAI_ORANGE_PLUS,
    "maimai PiNK": Version.MAIMAI_PINK,
    "maimai PiNK PLUS": Version.MAIMAI_PINK_PLUS,
    "maimai MURASAKi": Version.MAIMAI_MURASAKI,
    "maimai MURASAKi PLUS": Version.MAIMAI_MURASAKI_PLUS,
    "maimai MiLK": Version.MAIMAI_MILK,
    "MiLK PLUS": Version.MAIMAI_MILK_PLUS,
    "maimai FiNALE": Version.MAIMAI_FINALE,
    "maimai でらっくす": Version.MAIMAI_DX,
    "maimai でらっくす PLUS": Version.MAIMAI_DX_PLUS,
    "maimai でらっくす Splash": Version.MAIMAI_DX_SPLASH,
    "maimai でらっくす Splash PLUS": Version.MAIMAI_DX_SPLASH,
    "maimai でらっくす UNiVERSE": Version.MAIMAI_DX_UNIVERSE,
    "maimai でらっくす UNiVERSE PLUS": Version.MAIMAI_DX_UNIVERSE,
    "maimai でらっくす FESTiVAL": Version.MAIMAI_DX_FESTIVAL,
    "maimai でらっくす FESTiVAL PLUS": Version.MAIMAI_DX_FESTIVAL,
    "maimai でらっくす BUDDiES": Version.MAIMAI_DX_BUDDIES,
    "maimai でらっくす BUDDiES PLUS": Version.MAIMAI_DX_BUDDIES,
}
"""@private"""

name_to_genre: dict[str, Genre] = {
    "POPSアニメ": Genre.POPSアニメ,
    "流行&动漫": Genre.POPSアニメ,
    "niconicoボーカロイド": Genre.niconicoボーカロイド,
    "niconico & VOCALOID": Genre.niconicoボーカロイド,
    "東方Project": Genre.東方Project,
    "东方Project": Genre.東方Project,
    "ゲームバラエティ": Genre.ゲームバラエティ,
    "其他游戏": Genre.ゲームバラエティ,
    "maimai": Genre.maimai,
    "舞萌": Genre.maimai,
    "オンゲキCHUNITHM": Genre.オンゲキCHUNITHM,
    "音击&中二节奏": Genre.オンゲキCHUNITHM,
    "宴会場": Genre.宴会場,
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

    @staticmethod
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

    @staticmethod
    def _from_id(id: int | str) -> "SongType":
        id = int(id)
        return SongType.UTAGE if id > 100000 else SongType.DX if id > 10000 else SongType.STANDARD

    def _to_id(self, id: int | str) -> int:
        id = int(id)
        return id if self == SongType.STANDARD else id + 10000 if self == SongType.DX else id + 100000

    def _to_abbr(self) -> str:
        return "SD" if self == SongType.STANDARD else "DX" if self else "UTAGE"
