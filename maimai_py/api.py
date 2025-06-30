import os
from importlib.util import find_spec
from typing import Annotated, Any, Callable, Literal, Optional, Union
from urllib.parse import unquote, urlparse

from maimai_py.maimai import MaimaiClient, MaimaiClientMultithreading, MaimaiPlates, MaimaiSongs, _UnsetSentinel
from maimai_py.models import *
from maimai_py.providers import *
from maimai_py.providers.hybrid import HybridProvider

PlateAttrs = Literal["remained", "cleared", "played", "all"]


def xstr(s: Optional[str]) -> str:
    return "" if s is None else str(s).lower()


def istr(i: Optional[list]) -> str:
    return "" if i is None else "".join(i).lower()


def pagination(page_size, page, data):
    total_pages = (len(data) + page_size - 1) // page_size
    if page < 1 or page > total_pages:
        return []

    start = (page - 1) * page_size
    end = page * page_size
    return data[start:end]


def get_filters(functions: dict[Any, Callable[..., bool]]):
    union = [flag for cond, flag in functions.items() if cond is not None]
    filter = lambda obj: all([flag(obj) for flag in union])
    return filter


if find_spec("fastapi"):
    from fastapi import APIRouter, Depends, FastAPI, Query, Request
    from fastapi.openapi.utils import get_openapi
    from fastapi.responses import JSONResponse

    class MaimaiRoutes:
        _client: MaimaiClient

        _lxns_token: Optional[str] = None
        _divingfish_token: Optional[str] = None
        _arcade_proxy: Optional[str] = None

        def __init__(
            self,
            client: MaimaiClient,
            lxns_token: Optional[str] = None,
            divingfish_token: Optional[str] = None,
            arcade_proxy: Optional[str] = None,
        ):
            self._client = client
            self._lxns_token = lxns_token
            self._divingfish_token = divingfish_token
            self._arcade_proxy = arcade_proxy

        def _dep_lxns_player(self, credentials: Optional[str] = None, friend_code: Optional[int] = None, qq: Optional[int] = None):
            return PlayerIdentifier(credentials=credentials, qq=qq, friend_code=friend_code)

        def _dep_divingfish_player(self, username: Optional[str] = None, credentials: Optional[str] = None, qq: Optional[int] = None):
            return PlayerIdentifier(qq=qq, credentials=credentials, username=username)

        def _dep_arcade_player(self, credentials: str):
            return PlayerIdentifier(credentials=credentials)

        def _dep_divingfish(self) -> IProvider:
            return DivingFishProvider(developer_token=self._divingfish_token)

        def _dep_lxns(self) -> IProvider:
            return LXNSProvider(developer_token=self._lxns_token)

        def _dep_arcade(self) -> IProvider:
            return ArcadeProvider(http_proxy=self._arcade_proxy)

        def _dep_hybrid(self) -> IProvider:
            return HybridProvider()

        def get_router(self, dep_provider: Callable, dep_player: Optional[Callable] = None, skip_base: bool = True) -> APIRouter:
            router = APIRouter()

            def try_add_route(func: Callable, router: APIRouter, dep_provider: Callable):
                provider_type = func.__annotations__.get("provider")
                if provider_type and isinstance(dep_provider(), provider_type):
                    method = "GET" if "get_" in func.__name__ else "POST"
                    response_model = func.__annotations__.get("return")
                    router.add_api_route(
                        f"/{func.__name__.split('_')[-1]}",
                        func,
                        name=f"{func.__name__}",
                        methods=[method],
                        response_model=response_model,
                        description=func.__doc__,
                    )

            async def _get_songs(
                id: Optional[int] = None,
                title: Optional[str] = None,
                artist: Optional[str] = None,
                genre: Optional[Genre] = None,
                bpm: Optional[int] = None,
                map: Optional[str] = None,
                version: Optional[int] = None,
                type: Optional[SongType] = None,
                level: Optional[str] = None,
                versions: Optional[Version] = None,
                keywords: Optional[str] = None,
                page: int = Query(1, ge=1),
                page_size: int = Query(100, ge=1),
                provider: ISongProvider = Depends(dep_provider),
            ) -> list[Song]:
                maimai_songs: MaimaiSongs = await self._client.songs(provider=provider)
                type_func: Callable[[Song], bool] = lambda song: song.get_difficulties(type) != []  # type: ignore
                level_func: Callable[[Song], bool] = lambda song: any([diff.level == level for diff in song.get_difficulties()])
                versions_func: Callable[[Song], bool] = lambda song: versions.value <= song.version < all_versions[all_versions.index(versions) + 1].value  # type: ignore
                keywords_func: Callable[[Song], bool] = lambda song: xstr(keywords) in xstr(song.title) + xstr(song.artist) + istr(song.aliases)
                songs = await maimai_songs.filter(id=id, title=title, artist=artist, genre=genre, bpm=bpm, map=map, version=version)
                filters = get_filters({type: type_func, level: level_func, versions: versions_func, keywords: keywords_func})
                result = [song for song in songs if filters(song)]
                return pagination(page_size, page, result)

            async def _get_icons(
                id: Optional[int] = None,
                name: Optional[str] = None,
                description: Optional[str] = None,
                genre: Optional[str] = None,
                keywords: Optional[str] = None,
                page: int = Query(1, ge=1),
                page_size: int = Query(100, ge=1),
                provider: IItemListProvider = Depends(dep_provider),
            ) -> list[PlayerIcon]:
                items = await self._client.items(PlayerIcon, provider=provider)
                if id is not None:
                    return [item] if (item := await items.by_id(id)) else []
                keyword_func = lambda icon: xstr(keywords) in (xstr(icon.name) + xstr(icon.description) + xstr(icon.genre))
                filters = get_filters({keywords: keyword_func})
                result = [x for x in await items.filter(name=name, description=description, genre=genre) if filters(x)]
                return pagination(page_size, page, result)

            async def _get_nameplates(
                id: Optional[int] = None,
                name: Optional[str] = None,
                description: Optional[str] = None,
                genre: Optional[str] = None,
                keywords: Optional[str] = None,
                page: int = Query(1, ge=1),
                page_size: int = Query(100, ge=1),
                provider: IItemListProvider = Depends(dep_provider),
            ) -> list[PlayerNamePlate]:
                items = await self._client.items(PlayerNamePlate, provider=provider)
                if id is not None:
                    return [item] if (item := await items.by_id(id)) else []
                keyword_func = lambda icon: xstr(keywords) in (xstr(icon.name) + xstr(icon.description) + xstr(icon.genre))
                filters = get_filters({keywords: keyword_func})
                result = [x for x in await items.filter(name=name, description=description, genre=genre) if filters(x)]
                return pagination(page_size, page, result)

            async def _get_frames(
                id: Optional[int] = None,
                name: Optional[str] = None,
                description: Optional[str] = None,
                genre: Optional[str] = None,
                keywords: Optional[str] = None,
                page: int = Query(1, ge=1),
                page_size: int = Query(100, ge=1),
                provider: IItemListProvider = Depends(dep_provider),
            ) -> list[PlayerFrame]:
                items = await self._client.items(PlayerFrame, provider=provider)
                if id is not None:
                    return [item] if (item := await items.by_id(id)) else []
                keyword_func = lambda icon: xstr(keywords) in (xstr(icon.name) + xstr(icon.description) + xstr(icon.genre))
                filters = get_filters({keywords: keyword_func})
                result = [x for x in await items.filter(name=name, description=description, genre=genre) if filters(x)]
                return pagination(page_size, page, result)

            async def _get_trophies(
                id: Optional[int] = None,
                name: Optional[str] = None,
                color: Optional[str] = None,
                keywords: Optional[str] = None,
                page: int = Query(1, ge=1),
                page_size: int = Query(100, ge=1),
                provider: IItemListProvider = Depends(dep_provider),
            ) -> list[PlayerTrophy]:
                items = await self._client.items(PlayerTrophy, provider=provider)
                if id is not None:
                    return [item] if (item := await items.by_id(id)) else []
                keyword_func = lambda icon: xstr(keywords) in (xstr(icon.name) + xstr(icon.color))
                filters = get_filters({keywords: keyword_func})
                result = [x for x in await items.filter(name=name, color=color) if filters(x)]
                return pagination(page_size, page, result)

            async def _get_charas(
                id: Optional[int] = None,
                name: Optional[str] = None,
                keywords: Optional[str] = None,
                page: int = Query(1, ge=1),
                page_size: int = Query(100, ge=1),
                provider: IItemListProvider = Depends(dep_provider),
            ) -> list[PlayerChara]:
                items = await self._client.items(PlayerChara, provider=provider)
                if id is not None:
                    return [item] if (item := await items.by_id(id)) else []
                keyword_func = lambda chara: xstr(keywords) in xstr(chara.name)
                filters = get_filters({keywords: keyword_func})
                result = [x for x in await items.filter(name=name) if filters(x)]
                return pagination(page_size, page, result)

            async def _get_partners(
                id: Optional[int] = None,
                name: Optional[str] = None,
                keywords: Optional[str] = None,
                page: int = Query(1, ge=1),
                page_size: int = Query(100, ge=1),
                provider: IItemListProvider = Depends(dep_provider),
            ) -> list[PlayerPartner]:
                items = await self._client.items(PlayerPartner, provider=provider)
                if id is not None:
                    return [item] if (item := await items.by_id(id)) else []
                keyword_func = lambda partner: xstr(keywords) in xstr(partner.name)
                filters = get_filters({keywords: keyword_func})
                result = [x for x in await items.filter(name=name) if filters(x)]
                return pagination(page_size, page, result)

            async def _get_areas(
                lang: Literal["ja", "zh"] = "ja",
                id: Optional[str] = None,
                name: Optional[str] = None,
                keywords: Optional[str] = None,
                page: int = Query(1, ge=1),
                page_size: int = Query(100, ge=1),
                provider: IAreaProvider = Depends(dep_provider),
            ) -> list[Area]:
                areas = await self._client.areas(lang, provider=provider)
                if id is not None:
                    return [area] if (area := await areas.by_id(id)) else []
                if name is not None:
                    return [area] if (area := await areas.by_name(name)) else []
                keyword_func = lambda area: xstr(keywords) in (xstr(area.name) + xstr(area.comment))
                filters = get_filters({keywords: keyword_func})
                result = [x for x in await areas.get_all() if filters(x)]
                return pagination(page_size, page, result)

            async def _get_scores(
                provider: IScoreProvider = Depends(dep_provider),
                player: PlayerIdentifier = Depends(dep_player),
            ) -> list[ScoreExtend]:
                scores = await self._client.scores(player, provider=provider)
                return scores.scores

            async def _get_regions(
                provider: IRegionProvider = Depends(dep_provider),
                player: PlayerIdentifier = Depends(dep_player),
            ) -> list[PlayerRegion]:
                return await self._client.regions(player, provider=provider)

            async def _get_players(
                provider: IPlayerProvider = Depends(dep_provider),
                player: PlayerIdentifier = Depends(dep_player),
            ) -> Union[Player, DivingFishPlayer, LXNSPlayer, ArcadePlayer]:
                return await self._client.players(player, provider=provider)

            async def _get_bests(
                provider: IScoreProvider = Depends(dep_provider),
                player: PlayerIdentifier = Depends(dep_player),
            ) -> PlayerBests:
                maimai_scores = await self._client.bests(player, provider=provider)
                return maimai_scores.get_player_bests()

            async def _post_scores(
                scores: list[Score],
                provider: IScoreUpdateProvider = Depends(dep_provider),
                player: PlayerIdentifier = Depends(dep_player),
            ) -> None:
                await self._client.updates(player, scores, provider=provider)

            async def _get_plates(
                plate: str,
                attr: Literal["remained", "cleared", "played", "all"] = "remained",
                provider: IScoreProvider = Depends(dep_provider),
                player: PlayerIdentifier = Depends(dep_player),
            ) -> list[PlateObject]:
                plates: MaimaiPlates = await self._client.plates(player, plate, provider=provider)
                return await getattr(plates, f"get_{attr}")()

            async def _get_minfo(
                id: Optional[int] = None,
                title: Optional[str] = None,
                keywords: Optional[str] = None,
                provider: IScoreProvider = Depends(dep_provider),
                player: PlayerIdentifier = Depends(dep_player),
            ) -> Optional[PlayerSong]:
                song_trait = id if id is not None else title if title is not None else keywords if keywords is not None else None
                if song_trait is not None:
                    return await self._client.minfo(song_trait, player, provider=provider)

            async def _get_identifiers(
                code: str,
                provider: IPlayerIdentifierProvider = Depends(dep_provider),
            ) -> PlayerIdentifier:
                return await self._client.identifiers(code, provider=provider)

            bases: list[Callable] = [_get_songs, _get_icons, _get_nameplates, _get_frames, _get_trophies, _get_charas, _get_partners, _get_areas]
            players: list[Callable] = [_get_scores, _get_regions, _get_players, _get_bests, _post_scores, _get_plates, _get_minfo, _get_identifiers]

            all = players + (bases if not skip_base else [])
            [try_add_route(func, router, dep_provider) for func in all]

            return router


if all([find_spec(p) for p in ["fastapi", "uvicorn", "typer"]]):
    import typer
    import uvicorn
    from fastapi import APIRouter, Depends, FastAPI, Request
    from fastapi.openapi.utils import get_openapi
    from fastapi.responses import JSONResponse

    # prepare for ASGI app
    asgi_app = FastAPI(title="maimai.py API", description="The definitive python wrapper for MaimaiCN related development.")
    routes = MaimaiRoutes(MaimaiClientMultithreading())  # type: ignore

    # register routes and middlewares
    asgi_app.include_router(routes.get_router(routes._dep_hybrid, skip_base=False), tags=["base"])
    asgi_app.include_router(routes.get_router(routes._dep_divingfish, routes._dep_divingfish_player), prefix="/divingfish", tags=["divingfish"])
    asgi_app.include_router(routes.get_router(routes._dep_lxns, routes._dep_lxns_player), prefix="/lxns", tags=["lxns"])
    asgi_app.include_router(routes.get_router(routes._dep_arcade, routes._dep_arcade_player), prefix="/arcade", tags=["arcade"])

    def main(
        host: Annotated[str, typer.Option(help="The host address to bind to.")] = "127.0.0.1",
        port: Annotated[int, typer.Option(help="The port number to bind to.")] = 8000,
        redis: Annotated[Optional[str], typer.Option(help="Redis server address, for example: redis://localhost:6379/0.")] = None,
        lxns_token: Annotated[Optional[str], typer.Option(help="LXNS token for LXNS API.")] = None,
        divingfish_token: Annotated[Optional[str], typer.Option(help="Diving Fish token for Diving Fish API.")] = None,
        arcade_proxy: Annotated[Optional[str], typer.Option(help="HTTP proxy for Arcade API.")] = None,
    ):
        # prepare for redis cache backend
        redis_backend = UNSET
        if redis and find_spec("redis"):
            from aiocache import RedisCache
            from aiocache.serializers import PickleSerializer

            redis_url = urlparse(redis)
            redis_backend = RedisCache(
                serializer=PickleSerializer(),
                endpoint=unquote(redis_url.hostname or "localhost"),
                port=redis_url.port or 6379,
                password=redis_url.password,
                db=int(unquote(redis_url.path).replace("/", "")),
            )

        # override the default maimai.py client
        routes._client._cache = routes._client._cache if isinstance(redis_backend, _UnsetSentinel) else redis_backend
        routes._lxns_token = lxns_token or os.environ.get("LXNS_DEVELOPER_TOKEN")
        routes._divingfish_token = divingfish_token or os.environ.get("DIVINGFISH_DEVELOPER_TOKEN")
        routes._arcade_proxy = arcade_proxy

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

    if __name__ == "__main__":
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
