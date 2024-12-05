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

plate_aliases: dict[str, str] = {
    "暁": "晓",
    "櫻": "樱",
    "菫": "堇",
    "輝": "辉",
    "華": "华",
    "極": "极",
}

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


class SongType(Enum):
    STANDARD = "standard"
    DX = "dx"
    UTAGE = "utage"
