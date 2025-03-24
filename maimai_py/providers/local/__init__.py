import json
from pathlib import Path
from httpx import AsyncClient

from maimai_py.models import *
from maimai_py.providers import IItemListProvider, IAreaProvider


class LocalProvider(IItemListProvider, IAreaProvider):
    """The provider that fetches data from the local storage.

    Most of the data are stored in JSON files in the same directory as this file.
    """

    def __eq__(self, value):
        return isinstance(value, LocalProvider)

    def _read_file(self, file_name: str) -> dict[str, dict]:
        current_folder = Path(__file__).resolve().parent
        path = current_folder / f"{file_name}.json"
        if not path.exists():
            raise FileNotFoundError(f"File {path} not found.")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def get_icons(self, client: AsyncClient) -> dict[int, PlayerIcon]:
        return {int(k): PlayerIcon(id=int(k), name=v) for k, v in self._read_file("icons")["data"].items()}

    async def get_nameplates(self, client: AsyncClient) -> dict[int, PlayerNamePlate]:
        return {int(k): PlayerNamePlate(id=int(k), name=v) for k, v in self._read_file("nameplates")["data"].items()}

    async def get_frames(self, client: AsyncClient) -> dict[int, PlayerFrame]:
        return {int(k): PlayerFrame(id=int(k), name=v) for k, v in self._read_file("frames")["data"].items()}

    async def get_partners(self, client: AsyncClient) -> dict[int, PlayerPartner]:
        return {int(k): PlayerPartner(id=int(k), name=v) for k, v in self._read_file("partners")["data"].items()}

    async def get_charas(self, client: AsyncClient) -> dict[int, PlayerChara]:
        return {int(k): PlayerChara(id=int(k), name=v) for k, v in self._read_file("charas")["data"].items()}

    async def get_trophies(self, client: AsyncClient) -> dict[int, PlayerTrophy]:
        return {int(k): PlayerTrophy(id=int(k), name=v["title"], color=v["rareType"]) for k, v in self._read_file("trophies")["data"].items()}

    async def get_areas(self, lang: str, client: AsyncClient) -> dict[str, Area]:
        songs = await MaimaiSongs._get_or_fetch(client)
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
                        id=s.id if (s := songs.by_title(song["title"])) else -1,
                        title=song["title"],
                        artist=song["artist"],
                        description=song["description"],
                        illustrator=song["illustrator"],
                        movie=song["movie"],
                    )
                    for song in item["songs"]
                ],
            )
            for item in self._read_file(f"areas_{lang}")
        }
