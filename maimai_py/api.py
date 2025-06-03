import asyncio
from dataclasses import dataclass
from importlib.util import find_spec
from typing import Annotated, Callable, Literal
from urllib.parse import unquote, urlparse

from aiocache import RedisCache
from aiocache.serializers import PickleSerializer

from maimai_py import ArcadeProvider, DivingFishProvider, LXNSProvider, MaimaiClient, MaimaiSongs
from maimai_py.exceptions import MaimaiPyError
from maimai_py.maimai import MaimaiPlates, MaimaiScores
from maimai_py.models import *

PlateAttrs = Literal["remained", "cleared", "played", "all"]


@dataclass(slots=True)
class ScorePublic(Score):
    song_name: str
    level_value: float


@dataclass(slots=True)
class PlayerBests:
    rating: int
    rating_b35: int
    rating_b15: int
    scores_b35: list[ScorePublic]
    scores_b15: list[ScorePublic]


@dataclass(slots=True)
class ParsedQRCode:
    credentials: str


def pagination(page_size, page, data):
    total_pages = (len(data) + page_size - 1) // page_size
    if page < 1 or page > total_pages:
        return []

    start = (page - 1) * page_size
    end = page * page_size
    return data[start:end]


def xstr(s: str | None) -> str:
    return "" if s is None else str(s).lower()


def istr(i: list | None) -> str:
    return "" if i is None else "".join(i).lower()


def get_filters(functions: dict[Any, Callable[..., bool]]):
    union = [flag for cond, flag in functions.items() if cond is not None]
    filter = lambda obj: all([flag(obj) for flag in union])
    return filter


async def ser_score(score: Score, songs: dict[int, Song]) -> ScorePublic | None:
    if (song := songs.get(score.id)) and (diff := song.get_difficulty(score.type, score.level_index)):
        return ScorePublic(
            id=score.id,
            song_name=song.title,
            level=score.level,
            level_index=score.level_index,
            level_value=diff.level_value,
            achievements=score.achievements,
            fc=score.fc,
            fs=score.fs,
            dx_score=score.dx_score,
            dx_rating=score.dx_rating,
            rate=score.rate,
            type=score.type,
        )


async def ser_bests(maimai_scores: MaimaiScores, maimai_songs: MaimaiSongs) -> PlayerBests:
    song_ids = [score.id for score in maimai_scores.scores_b35 + maimai_scores.scores_b15]
    songs: list[Song] = await maimai_songs.get_batch(song_ids) if len(song_ids) > 0 else []
    required_songs: dict[int, Song] = {song.id: song for song in songs}
    async with asyncio.TaskGroup() as tg:
        b35_tasks = [tg.create_task(ser_score(score, required_songs)) for score in maimai_scores.scores_b35]
        b15_tasks = [tg.create_task(ser_score(score, required_songs)) for score in maimai_scores.scores_b15]
    scores_b35, scores_b15 = [v for task in b35_tasks if (v := task.result())], [v for task in b15_tasks if (v := task.result())]
    return PlayerBests(
        rating=maimai_scores.rating,
        rating_b35=maimai_scores.rating_b35,
        rating_b15=maimai_scores.rating_b15,
        scores_b35=scores_b35,
        scores_b15=scores_b15,
    )


if find_spec("fastapi"):
    from fastapi import APIRouter, Depends, FastAPI, Header, Query, Request
    from fastapi.openapi.utils import get_openapi
    from fastapi.responses import JSONResponse

    def dep_lxns_player(friend_code: int | None = None, qq: int | None = None):
        return PlayerIdentifier(qq=qq, friend_code=friend_code)

    def dep_diving_player_auth(username: str | None = None, credentials: str | None = None):
        return PlayerIdentifier(username=username, credentials=credentials)

    def dep_diving_player(username: str | None = None, qq: int | None = None):
        return PlayerIdentifier(qq=qq, username=username)

    def dep_arcade_player(credentials: str):
        return PlayerIdentifier(credentials=credentials)

    class MaimaiRoutes:
        _client: MaimaiClient

        _lxns_token: str | None = None
        _divingfish_token: str | None = None
        _arcade_proxy: str | None = None

        def __init__(
            self,
            client: MaimaiClient,
            lxns_token: str | None = None,
            divingfish_token: str | None = None,
            arcade_proxy: str | None = None,
        ):
            self._client = client
            self._lxns_token = lxns_token
            self._divingfish_token = divingfish_token
            self._arcade_proxy = arcade_proxy

        async def _get_songs(
            self,
            id: int | None = None,
            title: str | None = None,
            artist: str | None = None,
            genre: Genre | None = None,
            bpm: int | None = None,
            map: str | None = None,
            version: int | None = None,
            type: SongType | None = None,
            level: str | None = None,
            versions: Version | None = None,
            keywords: str | None = None,
            page: int = Query(1, ge=1),
            page_size: int = Query(100, ge=1, le=1000),
        ):
            songs: MaimaiSongs = await self._client.songs()
            type_func: Callable[[Song], bool] = lambda song: song.difficulties._get_children(type) != []  # type: ignore
            level_func: Callable[[Song], bool] = lambda song: any([diff.level == level for diff in song.difficulties._get_children()])
            versions_func: Callable[[Song], bool] = lambda song: versions.value <= song.version < all_versions[all_versions.index(versions) + 1].value  # type: ignore
            keywords_func: Callable[[Song], bool] = lambda song: xstr(keywords) in xstr(song.title) + xstr(song.artist) + istr(song.aliases)
            filters = get_filters({type: type_func, level: level_func, versions: versions_func, keywords: keywords_func})
            results = [x async for x in songs.filter(id=id, title=title, artist=artist, genre=genre, bpm=bpm, map=map, version=version) if filters(x)]
            return pagination(page_size, page, results)

        async def _get_icons(
            self,
            id: int | None = None,
            name: str | None = None,
            description: str | None = None,
            genre: str | None = None,
            keywords: str | None = None,
            page: int = Query(1, ge=1),
            page_size: int = Query(100, ge=1, le=1000),
        ):
            items = await self._client.items(PlayerIcon)
            if id is not None:
                return [item] if (item := items.by_id(id)) else []
            keyword_func: Callable[[PlayerIcon], bool] = lambda icon: xstr(keywords) in (xstr(icon.name) + xstr(icon.description) + xstr(icon.genre))
            filters = get_filters({keywords: keyword_func})
            results = [x async for x in items.filter(name=name, description=description, genre=genre) if filters(x)]
            return pagination(page_size, page, results)

        async def _get_nameplates(
            self,
            id: int | None = None,
            name: str | None = None,
            description: str | None = None,
            genre: str | None = None,
            keywords: str | None = None,
            page: int = Query(1, ge=1),
            page_size: int = Query(100, ge=1, le=1000),
        ):
            items = await self._client.items(PlayerNamePlate)
            if id is not None:
                return [item] if (item := items.by_id(id)) else []
            keyword_func: Callable[[PlayerNamePlate], bool] = lambda icon: xstr(keywords) in (
                xstr(icon.name) + xstr(icon.description) + xstr(icon.genre)
            )
            filters = get_filters({keywords: keyword_func})
            results = [x async for x in items.filter(name=name, description=description, genre=genre) if filters(x)]
            return pagination(page_size, page, results)

        async def _get_frames(
            self,
            id: int | None = None,
            name: str | None = None,
            description: str | None = None,
            genre: str | None = None,
            keywords: str | None = None,
            page: int = Query(1, ge=1),
            page_size: int = Query(100, ge=1, le=1000),
        ):
            items = await self._client.items(PlayerFrame)
            if id is not None:
                return [item] if (item := items.by_id(id)) else []
            keyword_func: Callable[[PlayerFrame], bool] = lambda icon: xstr(keywords) in (xstr(icon.name) + xstr(icon.description) + xstr(icon.genre))
            filters = get_filters({keywords: keyword_func})
            results = [x async for x in items.filter(name=name, description=description, genre=genre) if filters(x)]
            return pagination(page_size, page, results)

        async def _get_trophies(
            self,
            id: int | None = None,
            name: str | None = None,
            color: str | None = None,
            keywords: str | None = None,
            page: int = Query(1, ge=1),
            page_size: int = Query(100, ge=1, le=1000),
        ):
            items = await self._client.items(PlayerTrophy)
            if id is not None:
                return [item] if (item := items.by_id(id)) else []
            keyword_func: Callable[[PlayerTrophy], bool] = lambda icon: xstr(keywords) in (xstr(icon.name) + xstr(icon.color))
            filters = get_filters({keywords: keyword_func})
            results = [x async for x in items.filter(name=name, color=color) if filters(x)]
            return pagination(page_size, page, results)

        async def _get_charas(
            self,
            id: int | None = None,
            name: str | None = None,
            keywords: str | None = None,
            page: int = Query(1, ge=1),
            page_size: int = Query(100, ge=1, le=1000),
        ):
            items = await self._client.items(PlayerChara)
            if id is not None:
                return [item] if (item := items.by_id(id)) else []
            results = items.filter(name=name or keywords)
            return pagination(page_size, page, results)

        async def _get_partners(
            self,
            id: int | None = None,
            name: str | None = None,
            keywords: str | None = None,
            page: int = Query(1, ge=1),
            page_size: int = Query(100, ge=1, le=1000),
        ):
            items = await self._client.items(PlayerPartner)
            if id is not None:
                return [item] if (item := items.by_id(id)) else []
            results = items.filter(name=name or keywords)
            return pagination(page_size, page, results)

        async def _get_areas(
            self,
            lang: Literal["ja", "zh"] = "ja",
            id: str | None = None,
            name: str | None = None,
            page: int = Query(1, ge=1),
            page_size: int = Query(100, ge=1, le=1000),
        ):
            areas = await self._client.areas(lang)
            if id is not None:
                return [area] if (area := await areas.by_id(id)) else []
            if name is not None:
                return [area] if (area := await areas.by_name(name)) else []
            return pagination(page_size, page, await areas.get_all())

        async def _get_player_lxns(self, player: PlayerIdentifier = Depends(dep_lxns_player)):
            provider = LXNSProvider(self._lxns_token)
            return await self._client.players(player, provider)

        async def _get_player_diving(self, player: PlayerIdentifier = Depends(dep_diving_player)):
            provider = DivingFishProvider(self._divingfish_token)
            return await self._client.players(player, provider)

        async def _get_player_arcade(self, player: PlayerIdentifier = Depends(dep_arcade_player)):
            provider = ArcadeProvider(self._arcade_proxy)
            return await self._client.players(player, provider)

        async def _get_scores_lxns(self, player: PlayerIdentifier = Depends(dep_lxns_player)):
            provider = LXNSProvider(self._lxns_token)
            scores = await self._client.scores(player, provider=provider)
            return scores.scores  # no pagination because it costs more

        async def _get_scores_diving(self, player: PlayerIdentifier = Depends(dep_diving_player)):
            provider = DivingFishProvider(self._divingfish_token)
            scores = await self._client.scores(player, provider=provider)
            return scores.scores  # no pagination because it costs more

        async def _get_scores_arcade(self, player: PlayerIdentifier = Depends(dep_arcade_player)):
            provider = ArcadeProvider(self._arcade_proxy)
            scores = await self._client.scores(player, provider=provider)
            return scores.scores  # no pagination because it costs more

        async def _update_scores_lxns(self, scores: list[Score], player: PlayerIdentifier = Depends(dep_lxns_player)):
            provider = LXNSProvider(self._lxns_token)
            await self._client.updates(player, scores, provider=provider)

        async def _update_scores_diving(self, scores: list[Score], player: PlayerIdentifier = Depends(dep_diving_player_auth)):
            provider = DivingFishProvider(self._divingfish_token)
            await self._client.updates(player, scores, provider=provider)

        async def _get_bests_lxns(self, player: PlayerIdentifier = Depends(dep_lxns_player)):
            provider = LXNSProvider(self._lxns_token)
            songs, scores = await asyncio.gather(
                asyncio.create_task(self._client.songs()),
                asyncio.create_task(self._client.scores(player, provider=provider)),
            )
            return await ser_bests(scores, songs)

        async def _get_bests_diving(self, player: PlayerIdentifier = Depends(dep_diving_player)):
            provider = DivingFishProvider(self._divingfish_token)
            songs, scores = await asyncio.gather(
                asyncio.create_task(self._client.songs()),
                asyncio.create_task(self._client.scores(player, provider=provider)),
            )
            return await ser_bests(scores, songs)

        async def _get_bests_arcade(self, player: PlayerIdentifier = Depends(dep_arcade_player)):
            provider = ArcadeProvider(self._arcade_proxy)
            songs, scores = await asyncio.gather(
                asyncio.create_task(self._client.songs()),
                asyncio.create_task(self._client.scores(player, provider=provider)),
            )
            return await ser_bests(scores, songs)

        async def _get_plate_lxns(
            self, plate: str, attr: Literal["remained", "cleared", "played", "all"] = "remained", player: PlayerIdentifier = Depends(dep_lxns_player)
        ):
            provider = LXNSProvider(self._lxns_token)
            plates: MaimaiPlates = await self._client.plates(player, plate, provider=provider)
            return await getattr(plates, f"get_{attr}")()

        async def _get_plate_diving(self, plate: str, attr: PlateAttrs = "remained", player: PlayerIdentifier = Depends(dep_diving_player)):
            provider = DivingFishProvider(self._divingfish_token)
            plates: MaimaiPlates = await self._client.plates(player, plate, provider=provider)
            return await getattr(plates, f"get_{attr}")()

        async def _get_plate_arcade(self, plate: str, attr: PlateAttrs = "remained", player: PlayerIdentifier = Depends(dep_arcade_player)):
            provider = ArcadeProvider(self._arcade_proxy)
            plates: MaimaiPlates = await self._client.plates(player, plate, provider=provider)
            return await getattr(plates, f"get_{attr}")()

        async def _get_region_arcade(self, player: PlayerIdentifier = Depends(dep_arcade_player)):
            provider = ArcadeProvider(self._arcade_proxy)
            return await self._client.regions(player, provider=provider)

        async def _get_qrcode_arcade(self, qrcode: str):
            identifier = await self._client.qrcode(qrcode, http_proxy=self._arcade_proxy)
            return ParsedQRCode(credentials=str(identifier.credentials))

        def get_base(self, tags: list[str | Enum] | None = None) -> APIRouter:
            router = APIRouter(tags=tags)
            router.add_api_route(
                "/songs",
                self._get_songs,
                name="get_songs",
                methods=["GET"],
                response_model=list[Song],
                description="Get songs by various filters, filters are combined by AND",
            )
            router.add_api_route(
                "/icons",
                self._get_icons,
                name="get_icons",
                methods=["GET"],
                response_model=list[PlayerIcon],
                description="Get player icons by various filters, filters are combined by AND",
            )
            router.add_api_route(
                "/nameplates",
                self._get_nameplates,
                name="get_nameplates",
                methods=["GET"],
                response_model=list[PlayerNamePlate],
                description="Get player nameplates by various filters, filters are combined by AND",
            )
            router.add_api_route(
                "/frames",
                self._get_frames,
                name="get_frames",
                methods=["GET"],
                response_model=list[PlayerFrame],
                description="Get player frames by various filters, filters are combined by AND",
            )
            router.add_api_route(
                "/trophies",
                self._get_trophies,
                name="get_trophies",
                methods=["GET"],
                response_model=list[PlayerTrophy],
                description="Get player trophies by various filters, filters are combined by AND",
            )
            router.add_api_route(
                "/charas",
                self._get_charas,
                name="get_charas",
                methods=["GET"],
                response_model=list[PlayerChara],
                description="Get player charas by various filters, filters are combined by AND",
            )
            router.add_api_route(
                "/partners",
                self._get_partners,
                name="get_partners",
                methods=["GET"],
                response_model=list[PlayerPartner],
                description="Get player partners by various filters, filters are combined by AND",
            )
            router.add_api_route(
                "/areas",
                self._get_areas,
                name="get_areas",
                methods=["GET"],
                response_model=list[Area],
                description="Get areas",
            )
            return router

        def get_divingfish(self, tags: list[str | Enum] | None = None) -> APIRouter:
            router = APIRouter(tags=tags)
            router.add_api_route(
                "/players",
                self._get_player_diving,
                name="get_player_diving",
                methods=["GET"],
                response_model=DivingFishPlayer,
                description="Get player info from Diving Fish",
            )
            router.add_api_route(
                "/scores",
                self._get_scores_diving,
                name="get_scores_diving",
                methods=["GET"],
                response_model=list[Score],
                description="Get player ALL scores from Diving Fish",
            )
            router.add_api_route(
                "/scores",
                self._update_scores_diving,
                name="update_scores_diving",
                methods=["POST"],
                description="Update player scores to Diving Fish, should provide the user's username and password, or import token as credentials.",
            )
            router.add_api_route(
                "/bests",
                self._get_bests_diving,
                name="get_bests_diving",
                methods=["GET"],
                response_model=PlayerBests,
                description="Get player b50 scores from Diving Fish",
            )
            router.add_api_route(
                "/plates",
                self._get_plate_diving,
                name="get_plate_diving",
                methods=["GET"],
                response_model=list[PlateObject],
                description="Get player plates from Diving Fish",
            )
            return router

        def get_lxns(self, tags: list[str | Enum] | None = None) -> APIRouter:
            router = APIRouter(tags=tags)
            router.add_api_route(
                "/players",
                self._get_player_lxns,
                name="get_player_lxns",
                methods=["GET"],
                response_model=LXNSPlayer,
                description="Get player info from LXNS",
            )
            router.add_api_route(
                "/scores",
                self._get_scores_lxns,
                name="get_scores_lxns",
                methods=["GET"],
                response_model=list[Score],
                description="Get player ALL scores from LXNS",
            )
            router.add_api_route(
                "/scores",
                self._update_scores_lxns,
                name="update_scores_lxns",
                methods=["POST"],
                description="Update player scores to LXNS",
            )
            router.add_api_route(
                "/bests",
                self._get_bests_lxns,
                name="get_bests_lxns",
                methods=["GET"],
                response_model=PlayerBests,
                description="Get player b50 scores from LXNS",
            )
            router.add_api_route(
                "/plates",
                self._get_plate_lxns,
                name="get_plate_lxns",
                methods=["GET"],
                response_model=list[PlateObject],
                description="Get player plates from LXNS",
            )
            return router

        def get_arcade(self, tags: list[str | Enum] | None = None) -> APIRouter:
            router = APIRouter(tags=tags)
            router.add_api_route(
                "/players",
                self._get_player_arcade,
                name="get_player_arcade",
                methods=["GET"],
                response_model=ArcadePlayer,
                description="Get player info from Arcade",
            )
            router.add_api_route(
                "/scores",
                self._get_scores_arcade,
                name="get_scores_arcade",
                methods=["GET"],
                response_model=list[Score],
                description="Get player ALL scores from Arcade",
            )
            router.add_api_route(
                "/bests",
                self._get_bests_arcade,
                name="get_bests_arcade",
                methods=["GET"],
                response_model=PlayerBests,
                description="Get player b50 scores from Arcade",
            )
            router.add_api_route(
                "/plates",
                self._get_plate_arcade,
                name="get_plate_arcade",
                methods=["GET"],
                response_model=list[PlateObject],
                description="Get player plates from Arcade",
            )
            router.add_api_route(
                "/regions",
                self._get_region_arcade,
                name="get_region_arcade",
                methods=["GET"],
                response_model=list[PlayerRegion],
                description="Get player regions from Arcade",
            )
            router.add_api_route(
                "/qrcode",
                self._get_qrcode_arcade,
                name="get_qrcode_arcade",
                methods=["GET"],
                response_model=ParsedQRCode,
                description="Get encrypted player credentials from QR code",
            )
            return router


if all([find_spec(p) for p in ["fastapi", "uvicorn", "typer"]]) and __name__ == "__main__":
    import typer
    import uvicorn
    from fastapi import APIRouter, Depends, FastAPI, Query, Request
    from fastapi.openapi.utils import get_openapi
    from fastapi.responses import JSONResponse

    def main(
        host: Annotated[str, typer.Option(help="The host address to bind to.")] = "127.0.0.1",
        port: Annotated[int, typer.Option(help="The port number to bind to.")] = 8000,
        redis: Annotated[str | None, typer.Option(help="Redis server address, for example: redis://localhost:6379/0.")] = None,
        lxns_token: Annotated[str | None, typer.Option(help="LXNS token for LXNS API.")] = None,
        divingfish_token: Annotated[str | None, typer.Option(help="Diving Fish token for Diving Fish API.")] = None,
        arcade_proxy: Annotated[str | None, typer.Option(help="HTTP proxy for Arcade API.")] = None,
    ):
        # prepare for redis cache backend
        redis_backend = UNSET
        if redis:
            redis_url = urlparse(redis)
            redis_backend = RedisCache(
                serializer=PickleSerializer(),
                endpoint=unquote(redis_url.hostname or "localhost"),
                port=redis_url.port or 6379,
                password=redis_url.password,
                db=int(unquote(redis_url.path).replace("/", "")),
            )

        # prepare for ASGI app
        asgi_app = FastAPI(title="maimai.py API", description="The definitive python wrapper for MaimaiCN related development.")
        maimai_client = MaimaiClient(cache=redis_backend)
        maimai_routes = MaimaiRoutes(maimai_client, lxns_token=lxns_token, divingfish_token=divingfish_token, arcade_proxy=arcade_proxy)

        # register routes and middlewares
        asgi_app.include_router(maimai_routes.get_base(tags=["base"]))
        asgi_app.include_router(maimai_routes.get_divingfish(tags=["divingfish"]), prefix="/divingfish")
        asgi_app.include_router(maimai_routes.get_lxns(tags=["lxns"]), prefix="/lxns")
        asgi_app.include_router(maimai_routes.get_arcade(tags=["arcade"]), prefix="/arcade")

        @asgi_app.exception_handler(MaimaiPyError)
        async def exception_handler(request: Request, exc: MaimaiPyError):
            return JSONResponse(
                status_code=400,
                content={"message": f"Oops! There goes a maimai.py error {exc}.", "details": repr(exc)},
            )

        @asgi_app.get("/", include_in_schema=False)
        async def root():
            return {"message": "Hello, maimai.py! Check /docs for more information."}

        # run the ASGI app with uvicorn
        uvicorn.run(asgi_app, host=host, port=port)

        # generate OpenAPI specs and save to file, if needed
        def openapi():
            specs = get_openapi(
                title=asgi_app.title,
                version=asgi_app.version,
                openapi_version=asgi_app.openapi_version,
                description=asgi_app.description,
                routes=asgi_app.routes,
            )
            with open(f"openapi.json", "w") as f:
                json.dump(specs, f)

    typer.run(main)


if find_spec("maimai_ffi") and find_spec("nuitka"):
    import json

    import cryptography
    import cryptography.fernet
    import cryptography.hazmat.backends
    import cryptography.hazmat.primitives.ciphers
    import maimai_ffi
    import maimai_ffi.model
    import maimai_ffi.request
    import redis
