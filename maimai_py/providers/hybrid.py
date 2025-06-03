import asyncio
import hashlib
from typing import TYPE_CHECKING

from maimai_py.enums import *
from maimai_py.models import *
from maimai_py.providers.base import ISongProvider
from maimai_py.providers.lxns import LXNSProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient


class HybridProvider(ISongProvider):
    """The provider that fetches data from the LXNS and DivingFish, and hybrids them together.

    This provider is used to provide full notes and utage songs data, taking advantage of the LXNS and DivingFish APIs.

    LXNS: https://maimai.lxns.net/

    DivingFish: https://www.diving-fish.com/maimaidx/prober/
    """

    base_url_lxns = "https://maimai.lxns.net/"
    base_url_divingfish = "https://www.diving-fish.com/api/maimaidxprober/"

    def _hash(self) -> str:
        return hashlib.md5(b"hybrid").hexdigest()

    @staticmethod
    def _deser_note(diff: dict, key: str) -> int:
        if "notes" in diff:
            if "is_buddy" in diff and diff["is_buddy"]:
                return diff["notes"]["left"][key] + diff["notes"]["right"][key]
            return diff["notes"][key]
        return 0

    @staticmethod
    def _deser_diff(difficulty: dict, id: int, dv_dict: dict) -> SongDifficulty:
        diff = SongDifficulty(
            type=SongType[difficulty["type"].upper()],
            level=difficulty["level"],
            level_value=difficulty["level_value"],
            level_index=LevelIndex(difficulty["difficulty"]),
            note_designer=difficulty["note_designer"],
            version=difficulty["version"],
            tap_num=HybridProvider._deser_note(difficulty, "tap"),
            hold_num=HybridProvider._deser_note(difficulty, "hold"),
            slide_num=HybridProvider._deser_note(difficulty, "slide"),
            touch_num=HybridProvider._deser_note(difficulty, "touch"),
            break_num=HybridProvider._deser_note(difficulty, "break"),
            curve=None,
        )
        dv_id = diff._get_divingfish_id(id)
        if dv_difficulty := dv_dict.get(dv_id, None):
            if diff.level_index.value < len(dv_difficulty["charts"]):
                notes: list = dv_difficulty["charts"][diff.level_index.value]["notes"]
                diff.tap_num = notes[0] if len(notes) > 0 else 0
                diff.hold_num = notes[1] if len(notes) > 1 else 0
                diff.slide_num = notes[2] if len(notes) > 2 else 0
                diff.touch_num = notes[3] if len(notes) > 3 else 0
                diff.break_num = notes[4] if len(notes) > 4 else 0
        return diff

    async def get_songs(self, client: "MaimaiClient") -> list[Song]:
        lxns, divingfish = await asyncio.gather(
            asyncio.create_task(client._client.get(self.base_url_lxns + "api/v0/maimai/song/list")),
            asyncio.create_task(client._client.get(self.base_url_divingfish + "music_data")),
        )
        lxns.raise_for_status()
        divingfish.raise_for_status()
        resp_lxns, resp_divingfish = lxns.json(), divingfish.json()

        dv_songs = {int(song["id"]): song for song in resp_divingfish}
        unique_songs: dict[int, Song] = {}

        for song in resp_lxns["songs"]:
            id = int(song["id"]) % 10000
            if id not in unique_songs:
                unique_songs[id] = LXNSProvider._deser_song(song)
            difficulties = unique_songs[id].difficulties
            difficulties.standard.extend(HybridProvider._deser_diff(diff, id, dv_songs) for diff in song["difficulties"].get("standard", []))
            difficulties.dx.extend(HybridProvider._deser_diff(diff, id, dv_songs) for diff in song["difficulties"].get("dx", []))
            difficulties.utage.extend(LXNSProvider._deser_diff_utage(diff) for diff in song["difficulties"].get("utage", []))
        return list(unique_songs.values())
