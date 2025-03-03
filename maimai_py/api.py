from dataclasses import dataclass
from importlib.util import find_spec
from typing import Annotated, Callable, Literal

from maimai_py.models import *
from maimai_py.enums import ScoreKind
from maimai_py.exceptions import MaimaiPyError
from maimai_py import MaimaiClient, MaimaiSongs, LXNSProvider, DivingFishProvider, ArcadeProvider


router = None
asgi_app = None
local_lxns_token = None
local_divingfish_token = None
local_arcade_proxy = None
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
    from fastapi.openapi.utils import get_openapi

    asgi_app = FastAPI()
    router = APIRouter()

    def dep_lxns(token_lxns: Annotated[str | None, Header()] = None):
        return LXNSProvider(token_lxns or local_lxns_token)

    def dep_diving(token_divingfish: Annotated[str | None, Header()] = None):
        return DivingFishProvider(token_divingfish or local_divingfish_token)

    def dep_arcade():
        return ArcadeProvider(http_proxy=local_arcade_proxy)

    def dep_lxns_player(friend_code: int | None = None, qq: str | None = None):
        return PlayerIdentifier(qq=qq, friend_code=friend_code)

    def dep_diving_player(username: str | None = None, qq: str | None = None):
        return PlayerIdentifier(qq=qq, username=username)

    def dep_arcade_player(credentials: str):
        return PlayerIdentifier(credentials=credentials)

    @asgi_app.exception_handler(MaimaiPyError)
    async def exception_handler(request: Request, exc: MaimaiPyError):
        return JSONResponse(
            status_code=400,
            content={"message": f"Oops! There goes a maimai.py error {exc}.", "details": repr(exc)},
        )

    @router.get(
        "/songs",
        response_model=list[Song],
        tags=["base"],
        description="Get songs by various filters, filters are combined by AND",
    )
    async def get_songs(
        id: int | None = None,
        title: str | None = None,
        artist: str | None = None,
        genre: Genre | None = None,
        bpm: int | None = None,
        map: str | None = None,
        version: int | None = None,
        keywords: str | None = None,
        type: SongType | None = None,
        level: str | None = None,
        versions: Version | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000),
    ):
        maimai_songs: MaimaiSongs = await maimai_client.songs()
        songs = maimai_songs.filter(id=id, title=title, artist=artist, genre=genre, bpm=bpm, map=map, version=version)

        type_func: Callable[[Song], bool] = lambda song: song.difficulties._get_children(type) != []
        level_func: Callable[[Song], bool] = lambda song: any([diff.level == level for diff in song.difficulties._get_children()])
        versions_func: Callable[[Song], bool] = lambda song: versions.value <= song.version < all_versions[all_versions.index(versions) + 1].value
        keywords_func: Callable[[Song], bool] = lambda song: keywords.lower() in song.title.lower() + song.artist.lower() + "".join(
            alias.lower() for alias in (song.aliases or [])
        )
        post_conditions = [
            cond for cond, flag in zip([type_func, level_func, versions_func, keywords_func], [type, level, versions, keywords]) if flag
        ]
        post_filter = lambda song: all([cond(song) for cond in post_conditions])

        songs = list(filter(post_filter, songs))
        return pagination(page_size, page, songs)

    @router.get(
        "/icons",
        response_model=list[PlayerIcon],
        tags=["base"],
        description="Get player icons by various filters, filters are combined by AND",
    )
    async def get_icons(
        id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        genre: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000),
    ):
        items = await maimai_client.items(PlayerIcon)
        if id is not None:
            return [item] if (item := items.by_id(id)) else []
        filtered_items = items.filter(name=name, description=description, genre=genre)
        return pagination(page_size, page, filtered_items)

    @router.get(
        "/nameplates",
        response_model=list[PlayerNamePlate],
        tags=["base"],
        description="Get player nameplates by various filters, filters are combined by AND",
    )
    async def get_nameplates(
        id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        genre: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000),
    ):
        items = await maimai_client.items(PlayerNamePlate)
        if id is not None:
            return [item] if (item := items.by_id(id)) else []
        filtered_items = items.filter(name=name, description=description, genre=genre)
        return pagination(page_size, page, filtered_items)

    @router.get(
        "/frames",
        response_model=list[PlayerFrame],
        tags=["base"],
        description="Get player frames by various filters, filters are combined by AND",
    )
    async def get_frames(
        id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        genre: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000),
    ):
        items = await maimai_client.items(PlayerFrame)
        if id is not None:
            return [item] if (item := items.by_id(id)) else []
        filtered_items = items.filter(name=name, description=description, genre=genre)
        return pagination(page_size, page, filtered_items)

    @router.get(
        "/trophies",
        response_model=list[PlayerTrophy],
        tags=["base"],
        description="Get player trophies by various filters, filters are combined by AND",
    )
    async def get_trophies(
        id: int | None = None,
        name: str | None = None,
        color: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000),
    ):
        items = await maimai_client.items(PlayerTrophy)
        if id is not None:
            return [item] if (item := items.by_id(id)) else []
        filtered_items = items.filter(name=name, color=color)
        return pagination(page_size, page, filtered_items)

    @router.get(
        "/charas",
        response_model=list[PlayerChara],
        tags=["base"],
        description="Get player charas by various filters, filters are combined by AND",
    )
    async def get_charas(
        id: int | None = None,
        name: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000),
    ):
        items = await maimai_client.items(PlayerChara)
        if id is not None:
            return [item] if (item := items.by_id(id)) else []
        filtered_items = items.filter(name=name)
        return pagination(page_size, page, filtered_items)

    @router.get(
        "/partners",
        response_model=list[PlayerPartner],
        tags=["base"],
        description="Get player partners by various filters, filters are combined by AND",
    )
    async def get_partners(
        id: int | None = None,
        name: str | None = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(100, ge=1, le=1000),
    ):
        items = await maimai_client.items(PlayerPartner)
        if id is not None:
            return [item] if (item := items.by_id(id)) else []
        filtered_items = items.filter(name=name)
        return pagination(page_size, page, filtered_items)

    @router.get(
        "/lxns/players",
        response_model=LXNSPlayer,
        tags=["lxns"],
        description="Get player info from LXNS",
    )
    async def get_player_lxns(
        player: PlayerIdentifier = Depends(dep_lxns_player),
        provider: LXNSProvider = Depends(dep_lxns),
    ):
        return await maimai_client.players(player, provider)

    @router.get(
        "/divingfish/players",
        response_model=DivingFishPlayer,
        tags=["divingfish"],
        description="Get player info from Diving Fish",
    )
    async def get_player_diving(
        player: PlayerIdentifier = Depends(dep_diving_player),
        provider: DivingFishProvider = Depends(dep_diving),
    ):
        return await maimai_client.players(player, provider)

    @router.get(
        "/arcade/players",
        response_model=ArcadePlayer,
        tags=["arcade"],
        description="Get player info from Arcade",
    )
    async def get_player_arcade(
        player: PlayerIdentifier = Depends(dep_arcade_player),
        provider: ArcadeProvider = Depends(dep_arcade),
    ):
        return await maimai_client.players(player, provider)

    @router.get(
        "/lxns/scores",
        response_model=list[Score],
        tags=["lxns"],
        description="Get player ALL scores from LXNS",
    )
    async def get_scores_lxns(
        player: PlayerIdentifier = Depends(dep_lxns_player),
        provider: LXNSProvider = Depends(dep_lxns),
    ):
        scores = await maimai_client.scores(player, kind=ScoreKind.ALL, provider=provider)
        return scores.scores  # no pagination because it costs more

    @router.get(
        "/divingfish/scores",
        response_model=list[Score],
        tags=["divingfish"],
        description="Get player ALL scores from Diving Fish",
    )
    async def get_scores_diving(
        player: PlayerIdentifier = Depends(dep_diving_player),
        provider: DivingFishProvider = Depends(dep_diving),
    ):
        scores = await maimai_client.scores(player, kind=ScoreKind.ALL, provider=provider)
        return scores.scores  # no pagination because it costs more

    @router.get(
        "/arcade/scores",
        response_model=list[Score],
        tags=["arcade"],
        description="Get player ALL scores from Arcade",
    )
    async def get_scores_arcade(
        player: PlayerIdentifier = Depends(dep_arcade_player),
        provider: ArcadeProvider = Depends(dep_arcade),
    ):
        scores = await maimai_client.scores(player, kind=ScoreKind.ALL, provider=provider)
        return scores.scores  # no pagination because it costs more

    @router.post(
        "/lxns/scores",
        tags=["lxns"],
        description="Update player scores to LXNS",
    )
    async def update_scores_lxns(
        scores: list[Score],
        player: PlayerIdentifier = Depends(dep_lxns_player),
        provider: LXNSProvider = Depends(dep_lxns),
    ):
        scores = await maimai_client.updates(player, scores, provider=provider)

    @router.post(
        "/divingfish/scores",
        tags=["divingfish"],
        description="Update player scores to Diving Fish, should provide the user's username and password, or import token as credentials.",
    )
    async def update_scores_diving(
        scores: list[Score],
        username: str | None = None,
        credentials: str | None = None,
    ):
        player = PlayerIdentifier(username=username, credentials=credentials)
        scores = await maimai_client.updates(player, scores, provider=DivingFishProvider())

    @router.get(
        "/lxns/bests",
        response_model=PlayerBests,
        tags=["lxns"],
        description="Get player b50 scores from LXNS",
    )
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

    @router.get(
        "/divingfish/bests",
        response_model=PlayerBests,
        tags=["divingfish"],
        description="Get player b50 scores from Diving Fish",
    )
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

    @router.get(
        "/arcade/bests",
        response_model=PlayerBests,
        tags=["arcade"],
        description="Get player b50 scores from Arcade",
    )
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

    @router.get("/lxns/plates", response_model=PlateSimple, tags=["lxns"], description="Get player plates from LXNS")
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

    @router.get("/divingfish/plates", response_model=PlateSimple, tags=["divingfish"], description="Get player plates from Diving Fish")
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

    @router.get("/arcade/plates", response_model=PlateSimple, tags=["arcade"], description="Get player plates from Arcade")
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

    @router.get("/arcade/regions", response_model=list[PlayerRegion], tags=["arcade"], description="Get player regions from Arcade")
    async def get_region(
        player: PlayerIdentifier = Depends(dep_arcade_player),
        provider: ArcadeProvider = Depends(dep_arcade),
    ):
        return await maimai_client.regions(player, provider=provider)

    @router.get("/arcade/qrcode", tags=["arcade"], description="Get encrypted player credentials from QR code")
    async def parse_qrcode(qrcode: str):
        identifier = await maimai_client.qrcode(qrcode, http_proxy=local_arcade_proxy)
        return {"credentials": identifier.credentials}

    @asgi_app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Hello, maimai.py! Check /docs for more information."}

    asgi_app.include_router(router)

    def openapi():
        specs = get_openapi(
            title=asgi_app.title if asgi_app.title else None,
            version=asgi_app.version if asgi_app.version else None,
            openapi_version=asgi_app.openapi_version if asgi_app.openapi_version else None,
            description=asgi_app.description if asgi_app.description else None,
            routes=asgi_app.routes if asgi_app.routes else None,
        )
        with open(f"openapi.json", "w") as f:
            json.dump(specs, f)


if find_spec("uvicorn") and __name__ == "__main__":
    import uvicorn

    uvicorn.run(asgi_app, host="127.0.0.1", port=8000)


if find_spec("maimai_ffi") and find_spec("nuitka"):
    import json
    import cryptography
    import cryptography.fernet
    import cryptography.hazmat.primitives.ciphers
    import cryptography.hazmat.backends
    import maimai_ffi
    import maimai_ffi.model
    import maimai_ffi.request
