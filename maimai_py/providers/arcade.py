import hashlib
from typing import TYPE_CHECKING

from httpcore import NetworkError, TimeoutException
from maimai_ffi import arcade
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from maimai_py.models import *
from maimai_py.utils import ScoreCoefficient

from .base import IPlayerIdentifierProvider, IScoreProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient, MaimaiSongs


class ArcadeProvider(IScoreProvider, IPlayerIdentifierProvider):
    """The provider that fetches data from the wahlap maimai arcade.

    This part of the maimai.py is not open-source, we distribute the compiled version of this part of the code as maimai_ffi.

    Feel free to ask us to solve if your platform or architecture is not supported.

    maimai.ffi: https://pypi.org/project/maimai-ffi
    """

    _http_proxy: Optional[str] = None

    def __init__(self, http_proxy: Optional[str] = None):
        self._http_proxy = http_proxy

    def _hash(self) -> str:
        return hashlib.md5(b"arcade").hexdigest()

    @staticmethod
    async def _deser_score(score: dict, songs: "MaimaiSongs") -> Optional[Score]:
        if song := await songs.by_id(score["musicId"] % 10000):
            song_type = SongType._from_id(score["musicId"])
            level_index = LevelIndex(score["level"]) if song_type != SongType.UTAGE else score["musicId"]
            achievement = float(score["achievement"]) / 10000
            if diff := song.get_difficulty(song_type, level_index):
                return Score(
                    id=score["musicId"] if score["musicId"] > 100000 else score["musicId"] % 10000,
                    level=diff.level,
                    level_index=diff.level_index,
                    achievements=achievement,
                    fc=None,
                    fs=None,
                    dx_score=score["dx_score"],
                    dx_rating=ScoreCoefficient(achievement).ra(diff.level_value),
                    play_count=None,
                    play_time=None,
                    rate=RateType._from_achievement(achievement),
                    type=song_type,
                )

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(TitleServerNetworkError), reraise=True)
    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        maimai_songs = await client.songs()
        if identifier.credentials and isinstance(identifier.credentials, str):
            resp_list = await arcade.get_user_scores(identifier.credentials.encode(), http_proxy=self._http_proxy)
            v = [s for score in resp_list if (s := await ArcadeProvider._deser_score(score, maimai_songs))]
            return v
        raise InvalidPlayerIdentifierError("Player identifier credentials should be provided.")

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type((TimeoutException, NetworkError)), reraise=True)
    async def get_identifier(self, code: Union[str, dict[str, str]], client: "MaimaiClient") -> PlayerIdentifier:
        resp_bytes: bytes = await arcade.get_uid_encrypted(str(code), http_proxy=self._http_proxy)
        return PlayerIdentifier(credentials=resp_bytes.decode())
