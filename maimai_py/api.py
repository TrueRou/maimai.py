from contextlib import asynccontextmanager
from dataclasses import dataclass
from importlib.util import find_spec
from typing import Annotated, Literal

from maimai_py.models import *
from maimai_py.enums import ScoreKind
from maimai_py.exceptions import MaimaiPyError
from maimai_py import MaimaiClient, MaimaiSongs, LXNSProvider, DivingFishProvider, ArcadeProvider


router = None
asgi_app = None
maimai_client = MaimaiClient()


def pagination(page_size, page, data):
    total_pages = (len(data) + page_size - 1) // page_size
    if page < 1 or page > total_pages:
        return []

    start = (page - 1) * page_size
    end = page * page_size
    return data[start:end]


@dataclass
class PlayerBests:
    rating: int
    rating_b35: int
    rating_b15: int
    scores_b35: list[Score]
    scores_b15: list[Score]


@dataclass
class PlateStats:
    remained_num: int
    cleared_num: int
    played_num: int
    all_num: int


@dataclass
class SongSimple:
    id: int
    title: str
    artist: str


@dataclass
class PlateObjectSimple:
    song: SongSimple
    levels: list[LevelIndex]
    scores: list[Score] | None


@dataclass
class PlateSimple:
    stats: PlateStats
    data: list[PlateObjectSimple]


if find_spec("fastapi"):
    from fastapi import APIRouter, FastAPI, Query, Request, Header, Depends
    from fastapi.responses import JSONResponse

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await MaimaiSongs._get_or_fetch()
        yield

    asgi_app = FastAPI()
    router = APIRouter(lifespan=lifespan)

    def dep_lxns(token_lxns: Annotated[str | None, Header()] = None):
        return LXNSProvider(token_lxns)

    def dep_diving(token_divingfish: Annotated[str | None, Header()] = None):
        return DivingFishProvider(token_divingfish)

    def dep_arcade():
        return ArcadeProvider()

    def dep_lxns_player(qq: str | None = None, friend_code: int | None = None):
        return PlayerIdentifier(qq=qq, friend_code=friend_code)

    def dep_diving_player(qq: str | None = None, username: str | None = None, credentials: str | None = None):
        return PlayerIdentifier(qq=qq, username=username, credentials=credentials)

    def dep_arcade_player(credentials: str):
        return PlayerIdentifier(credentials=credentials)

    @asgi_app.exception_handler(MaimaiPyError)
    async def exception_handler(request: Request, exc: MaimaiPyError):
        return JSONResponse(
            status_code=400,
            content={"message": f"Oops! There goes a maimai.py error {exc}.", "details": repr(exc)},
        )

    # "icons", "nameplates", "frames", "trophies", "charas", "partners"
    @router.get("/songs", response_model=list[Song], tags=["base"])
    async def get_songs(
        id: int | None = None,
        title: str | None = None,
        artist: str | None = None,
        genre: str | None = None,
        bpm: int | None = None,
        map: str | None = None,
        version: int | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=10000),
    ):
        maimai_songs: MaimaiSongs = await maimai_client.songs()
        if id is not None:
            return [maimai_songs.by_id(id)]
        songs = maimai_songs.filter(title=title, artist=artist, genre=genre, bpm=bpm, map=map, version=version)
        return pagination(page_size, page, songs)

    @router.get("/icons", response_model=list[PlayerIcon], tags=["base"])
    async def get_icons(
        id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        genre: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=10000),
    ):
        items = await maimai_client.items(PlayerIcon)
        if id is not None:
            return [items.by_id(id)]
        filtered_items = items.filter(name=name, description=description, genre=genre)
        return pagination(page_size, page, filtered_items)

    @router.get("/nameplates", response_model=list[PlayerNamePlate], tags=["base"])
    async def get_nameplates(
        id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        genre: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=10000),
    ):
        items = await maimai_client.items(PlayerNamePlate)
        if id is not None:
            return [items.by_id(id)]
        filtered_items = items.filter(name=name, description=description, genre=genre)
        return pagination(page_size, page, filtered_items)

    @router.get("/frames", response_model=list[PlayerFrame], tags=["base"])
    async def get_frames(
        id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        genre: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=10000),
    ):
        items = await maimai_client.items(PlayerFrame)
        if id is not None:
            return [items.by_id(id)]
        filtered_items = items.filter(name=name, description=description, genre=genre)
        return pagination(page_size, page, filtered_items)

    @router.get("/trophies", response_model=list[PlayerTrophy], tags=["base"])
    async def get_trophies(
        id: int | None = None,
        name: str | None = None,
        color: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=10000),
    ):
        items = await maimai_client.items(PlayerTrophy)
        if id is not None:
            return [items.by_id(id)]
        filtered_items = items.filter(name=name, color=color)
        return pagination(page_size, page, filtered_items)

    @router.get("/charas", response_model=list[PlayerChara], tags=["base"])
    async def get_charas(
        id: int | None = None,
        name: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=10000),
    ):
        items = await maimai_client.items(PlayerChara)
        if id is not None:
            return [items.by_id(id)]
        filtered_items = items.filter(name=name)
        return pagination(page_size, page, filtered_items)

    @router.get("/partners", response_model=list[PlayerPartner], tags=["base"])
    async def get_partners(
        id: int | None = None,
        name: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=10000),
    ):
        items = await maimai_client.items(PlayerIcon)
        if id is not None:
            return [items.by_id(id)]
        filtered_items = items.filter(name=name)
        return pagination(page_size, page, filtered_items)

    @router.get("/lxns/players", response_model=LXNSPlayer, tags=["lxns"])
    async def get_player_lxns(
        player: PlayerIdentifier = Depends(dep_lxns_player),
        provider: LXNSProvider = Depends(dep_lxns),
    ):
        return await maimai_client.players(player, provider)

    @router.get("/divingfish/players", response_model=DivingFishPlayer, tags=["divingfish"])
    async def get_player_diving(
        player: PlayerIdentifier = Depends(dep_diving_player),
        provider: DivingFishProvider = Depends(dep_diving),
    ):
        return await maimai_client.players(player, provider)

    @router.get("/arcade/players", response_model=ArcadePlayer, tags=["arcade"])
    async def get_player_arcade(
        player: PlayerIdentifier = Depends(dep_arcade_player),
        provider: ArcadeProvider = Depends(dep_arcade),
    ):
        return await maimai_client.players(player, provider)

    @router.get("/lxns/scores", response_model=list[Score], tags=["lxns"])
    async def get_scores_lxns(
        player: PlayerIdentifier = Depends(dep_lxns_player),
        provider: LXNSProvider = Depends(dep_lxns),
    ):
        scores = await maimai_client.scores(player, kind=ScoreKind.ALL, provider=provider)
        return scores.scores  # no pagination because it costs more

    @router.get("/divingfish/scores", response_model=list[Score], tags=["divingfish"])
    async def get_scores_diving(
        player: PlayerIdentifier = Depends(dep_diving_player),
        provider: DivingFishProvider = Depends(dep_diving),
    ):
        scores = await maimai_client.scores(player, kind=ScoreKind.ALL, provider=provider)
        return scores.scores  # no pagination because it costs more

    @router.get("/arcade/scores", response_model=list[Score], tags=["arcade"])
    async def get_scores_arcade(
        player: PlayerIdentifier = Depends(dep_arcade_player),
        provider: ArcadeProvider = Depends(dep_arcade),
    ):
        scores = await maimai_client.scores(player, kind=ScoreKind.ALL, provider=provider)
        return scores.scores  # no pagination because it costs more

    @router.post("/lxns/scores", tags=["lxns"])
    async def update_scores_lxns(
        scores: list[Score],
        player: PlayerIdentifier = Depends(dep_lxns_player),
        provider: LXNSProvider = Depends(dep_lxns),
    ):
        scores = await maimai_client.updates(player, scores, provider=provider)

    @router.post("/divingfish/scores", tags=["divingfish"])
    async def update_scores_diving(
        scores: list[Score],
        player: PlayerIdentifier = Depends(dep_diving_player),
        provider: DivingFishProvider = Depends(dep_diving),
    ):
        scores = await maimai_client.updates(player, scores, provider=provider)

    @router.get("/lxns/bests", response_model=PlayerBests, tags=["lxns"])
    async def get_bests_lxns(
        player: PlayerIdentifier = Depends(dep_lxns_player),
        provider: LXNSProvider = Depends(dep_lxns),
    ):
        scores = await maimai_client.scores(player, kind=ScoreKind.BEST, provider=provider)
        return PlayerBests(
            rating=scores.rating,
            rating_b35=scores.rating_b35,
            rating_b15=scores.rating_b15,
            scores_b35=scores.scores_b35,
            scores_b15=scores.scores_b15,
        )

    @router.get("/divingfish/bests", response_model=PlayerBests, tags=["divingfish"])
    async def get_bests_diving(
        player: PlayerIdentifier = Depends(dep_diving_player),
        provider: DivingFishProvider = Depends(dep_diving),
    ):
        scores = await maimai_client.scores(player, kind=ScoreKind.BEST, provider=provider)
        return PlayerBests(
            rating=scores.rating,
            rating_b35=scores.rating_b35,
            rating_b15=scores.rating_b15,
            scores_b35=scores.scores_b35,
            scores_b15=scores.scores_b15,
        )

    @router.get("/arcade/bests", response_model=PlayerBests, tags=["arcade"])
    async def get_bests_arcade(
        player: PlayerIdentifier = Depends(dep_arcade_player),
        provider: ArcadeProvider = Depends(dep_arcade),
    ):
        scores = await maimai_client.scores(player, kind=ScoreKind.BEST, provider=provider)
        return PlayerBests(
            rating=scores.rating,
            rating_b35=scores.rating_b35,
            rating_b15=scores.rating_b15,
            scores_b35=scores.scores_b35,
            scores_b15=scores.scores_b15,
        )

    @router.get("/lxns/plates", response_model=PlateSimple, tags=["lxns"])
    async def get_plate_lxns(
        plate: str,
        attr: Literal["remained", "cleared", "played", "all"] = "remained",
        player: PlayerIdentifier = Depends(dep_lxns_player),
        provider: LXNSProvider = Depends(dep_lxns),
    ):
        plates: MaimaiPlates = await maimai_client.plates(player, plate, provider=provider)
        data: list[PlateObject] = getattr(plates, attr)
        return PlateSimple(
            stats=PlateStats(remained_num=plates.remained_num, cleared_num=plates.cleared_num, played_num=plates.played_num, all_num=plates.all_num),
            data=[PlateObjectSimple(song=SongSimple(p.song.id, p.song.title, p.song.artist), levels=p.levels, scores=p.scores) for p in data],
        )

    @router.get("/divingfish/plates", response_model=list[PlateObject], tags=["divingfish"])
    async def get_plate_diving(
        plate: str,
        attr: Literal["remained", "cleared", "played", "all"] = "remained",
        player: PlayerIdentifier = Depends(dep_diving_player),
        provider: DivingFishProvider = Depends(dep_diving),
    ):
        plates: MaimaiPlates = await maimai_client.plates(player, plate, provider=provider)
        data: list[PlateObject] = getattr(plates, attr)
        return PlateSimple(
            stats=PlateStats(remained_num=plates.remained_num, cleared_num=plates.cleared_num, played_num=plates.played_num, all_num=plates.all_num),
            data=[PlateObjectSimple(song=SongSimple(p.song.id, p.song.title, p.song.artist), levels=p.levels, scores=p.scores) for p in data],
        )

    @router.get("/arcade/plates", response_model=list[PlateObject], tags=["arcade"])
    async def get_plate_arcade(
        plate: str,
        attr: Literal["remained", "cleared", "played", "all"] = "remained",
        player: PlayerIdentifier = Depends(dep_arcade_player),
        provider: ArcadeProvider = Depends(dep_arcade),
    ):
        plates: MaimaiPlates = await maimai_client.plates(player, plate, provider=provider)
        data: list[PlateObject] = getattr(plates, attr)
        return PlateSimple(
            stats=PlateStats(remained_num=plates.remained_num, cleared_num=plates.cleared_num, played_num=plates.played_num, all_num=plates.all_num),
            data=[PlateObjectSimple(song=SongSimple(p.song.id, p.song.title, p.song.artist), levels=p.levels, scores=p.scores) for p in data],
        )

    @router.get("/arcade/regions", response_model=PlayerRegion, tags=["arcade"])
    async def get_region(
        player: PlayerIdentifier = Depends(dep_arcade_player),
        provider: ArcadeProvider = Depends(dep_arcade),
    ):
        return await maimai_client.regions(player, provider=provider)

    @router.get("/arcade/qrcode", tags=["arcade"])
    async def parse_qrcode(qrcode: str):
        identifier = await maimai_client.qrcode(qrcode)
        return {"credentials": identifier.credentials}

    asgi_app.include_router(router)


if find_spec("uvicorn") and __name__ == "__main__":
    import uvicorn

    uvicorn.run("maimai_py.api:asgi_app", host="127.0.0.1", port=8000)
