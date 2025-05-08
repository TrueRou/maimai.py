import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING

from maimai_py.models import *
from maimai_py.providers import IAreaProvider, IItemListProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient


class LocalProvider(IItemListProvider, IAreaProvider):
    """The provider that fetches data from the local storage.

    Most of the data are stored in JSON files in the same directory as this file.
    """

    def _hash(self) -> str:
        current_folder = Path(__file__).resolve().parent
        json_files = sorted(current_folder.glob("*.json"))

        if not json_files:
            return hashlib.md5(b"local").hexdigest()

        combined_content = b""
        for file_path in json_files:
            with open(file_path, "rb") as f:
                combined_content += f.read()

        return hashlib.md5(combined_content).hexdigest()

    def _read_file(self, file_name: str) -> Any:
        current_folder = Path(__file__).resolve().parent
        path = current_folder / f"{file_name}.json"
        if not path.exists():
            raise FileNotFoundError(f"File {path} not found.")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _read_file_dict(self, file_name: str) -> dict:
        obj = self._read_file(file_name)
        if isinstance(obj, dict):
            return obj["data"]
        else:
            raise ValueError(f"File {file_name} is not a dictionary.")

    def _read_file_list(self, file_name: str) -> list:
        obj = self._read_file(file_name)
        if isinstance(obj, list):
            return obj
        else:
            raise ValueError(f"File {file_name} is not a list.")

    async def get_icons(self, client: "MaimaiClient") -> dict[int, PlayerIcon]:
        return {int(k): PlayerIcon(id=int(k), name=v) for k, v in self._read_file_dict("icons").items()}

    async def get_nameplates(self, client: "MaimaiClient") -> dict[int, PlayerNamePlate]:
        return {int(k): PlayerNamePlate(id=int(k), name=v) for k, v in self._read_file_dict("nameplates").items()}

    async def get_frames(self, client: "MaimaiClient") -> dict[int, PlayerFrame]:
        return {int(k): PlayerFrame(id=int(k), name=v) for k, v in self._read_file_dict("frames").items()}

    async def get_partners(self, client: "MaimaiClient") -> dict[int, PlayerPartner]:
        return {int(k): PlayerPartner(id=int(k), name=v) for k, v in self._read_file_dict("partners").items()}

    async def get_charas(self, client: "MaimaiClient") -> dict[int, PlayerChara]:
        return {int(k): PlayerChara(id=int(k), name=v) for k, v in self._read_file_dict("charas").items()}

    async def get_trophies(self, client: "MaimaiClient") -> dict[int, PlayerTrophy]:
        return {int(k): PlayerTrophy(id=int(k), name=v["title"], color=v["rareType"]) for k, v in self._read_file_dict("trophies").items()}

    async def get_areas(self, lang: str, client: "MaimaiClient") -> dict[str, Area]:
        maimai_songs = await client.songs()
        return {
            item["id"]: Area(
                id=item["id"],
                name=item["name"],
                comment=item["comment"],
                description=item["description"],
                video_id=item["video_id"],
                characters=[
                    AreaCharacter(
                        name=char["name"],
                        illustrator=char["illustrator"],
                        description1=char["description1"],
                        description2=char["description2"],
                        team=char["team"],
                        props=char["props"],
                    )
                    for char in item["characters"]
                ],
                songs=[
                    AreaSong(
                        id=s.id if (s := await maimai_songs.by_title(song["title"])) else None,
                        title=song["title"],
                        artist=song["artist"],
                        description=song["description"],
                        illustrator=song["illustrator"],
                        movie=song["movie"],
                    )
                    for song in item["songs"]
                ],
            )
            for item in self._read_file_list(f"areas_{lang}")
        }
