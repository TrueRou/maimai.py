import json
import logging
import os
from contextlib import asynccontextmanager
from dataclasses import asdict
from importlib.util import find_spec
from logging import warning
from typing import Annotated, Any, Callable, Literal, Optional, Union
from urllib.parse import unquote, urlparse

from httpx import Cookies
from pydantic import PydanticUndefinedAnnotation

from maimai_py.maimai import (
    MaimaiClient,
    MaimaiClientMultithreading,
    MaimaiPlates,
    MaimaiScores,
    MaimaiSongs,
    _UnsetSentinel,
)
from maimai_py.models import *
from maimai_py.providers import *
from maimai_py.providers.hybrid import HybridProvider

PlateAttrs = Literal["remained", "cleared", "played", "all"]
Label = str


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

    def filter(obj):
        return all([flag(obj) for flag in union])

    return filter


if find_spec("fastapi"):
    from fastapi import APIRouter, Depends, FastAPI, Query, Request
    from fastapi.openapi.utils import get_openapi
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel

    class UpdatesChainRequest(BaseModel):
        source: dict[Label, PlayerIdentifier]
        target: dict[Label, PlayerIdentifier]

        model_config = {
            "json_schema_extra": {
                "examples": [
                    {
                        "source": {"arcade": {"credentials": "userId"}},
                        "target": {
                            "divingfish": {
                                "username": "username",
                                "credentials": "password",
                            },
                            "lxns": {
                                "friend_code": 114514,
                            },
                        },
                    }
                ]
            }
        }

    class UpdatesChainResponse(BaseModel):
        class ChainResult(BaseModel):
            errors: Optional[str]
            scores_num: int
            scores_rating: int

        source: dict[Label, ChainResult]
        target: dict[Label, ChainResult]

        model_config = {
            "json_schema_extra": {
                "examples": [
                    {
                        "source": {
                            "arcade": {
                                "errors": None,
                                "scores_num": 34,
                                "scores_rating": 5678,
                            }
                        },
                        "target": {
                            "divingfish": {
                                "errors": None,
                                "scores_num": 34,
                                "scores_rating": 5678,
                            },
                            "lxns": {
                                "errors": None,
                                "scores_num": 34,
                                "scores_rating": 5678,
                            },
                        },
                    }
                ]
            }
        }

    class WechatOAuthResponse(BaseModel):
        url: str

    class MaimaiRoutes:
        _client: MaimaiClient
        _with_curves: bool

        _lxns_token: Optional[str] = None
        _divingfish_token: Optional[str] = None
        _arcade_proxy: Optional[str] = None

        def __init__(
            self,
            client: MaimaiClient,
            lxns_token: Optional[str] = None,
            divingfish_token: Optional[str] = None,
            arcade_proxy: Optional[str] = None,
            with_curves: bool = False,
        ):
            self._client = client
            self._lxns_token = lxns_token
            self._divingfish_token = divingfish_token
            self._arcade_proxy = arcade_proxy
            self._with_curves = with_curves

        def _dep_lxns_player(
            self,
            credentials: Optional[str] = None,
            friend_code: Optional[int] = None,
            qq: Optional[int] = None,
        ):
            return PlayerIdentifier(credentials=credentials, qq=qq, friend_code=friend_code)

        def _dep_divingfish_player(
            self,
            username: Optional[str] = None,
            credentials: Optional[str] = None,
            qq: Optional[int] = None,
        ):
            return PlayerIdentifier(qq=qq, credentials=credentials, username=username)

        def _dep_arcade_player(self, credentials: str):
            return PlayerIdentifier(credentials=credentials)

        def _dep_wechat_player(
            self,
            t: str = Query(..., alias="_t", description="_t in returned credentials dict"),
            user_id: str = Query(..., alias="userId", description="userId in returned credentials dict"),
        ):
            return PlayerIdentifier(credentials=Cookies({"_t": t, "userId": user_id}))

        def _dep_divingfish(self) -> IProvider:
            return DivingFishProvider(developer_token=self._divingfish_token)

        def _dep_lxns(self) -> IProvider:
            return LXNSProvider(developer_token=self._lxns_token)

        def _dep_arcade(self) -> IProvider:
            return ArcadeProvider(http_proxy=self._arcade_proxy)

        def _dep_wechat(self) -> IProvider:
            return WechatProvider()

        def _dep_hybrid(self) -> IProvider:
            return HybridProvider()

        def get_router(
            self,
            dep_provider: Callable,
            dep_player: Optional[Callable] = None,
            skip_base: bool = True,
        ) -> APIRouter:
            """Get a FastAPI APIRouter with routes for the specified provider and player dependencies.

            Args:
                dep_provider: A dependency function that returns an IProvider instance.
                dep_player: A dependency function that returns a PlayerIdentifier instance. Defaults to None.
                skip_base: Whether to skip base routes (songs, items, areas). Defaults to True.

            Returns:
                APIRouter: A FastAPI APIRouter with the specified routes.
            """
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
                curve_provider = (
                    DivingFishProvider(developer_token=self._divingfish_token) if self._with_curves else None
                )
                maimai_songs: MaimaiSongs = await self._client.songs(provider=provider, curve_provider=curve_provider)

                def type_func(song: Song) -> bool:
                    return song.get_difficulties(type) != []  # type: ignore

                def level_func(song: Song) -> bool:
                    return any([diff.level == level for diff in song.get_difficulties()])

                def versions_func(song: Song) -> bool:
                    return versions.value <= song.version < all_versions[all_versions.index(versions) + 1].value  # type: ignore

                def keywords_func(song: Song) -> bool:
                    return xstr(keywords) in xstr(song.title) + xstr(song.artist) + istr(song.aliases)

                songs = await maimai_songs.filter(
                    id=id,
                    title=title,
                    artist=artist,
                    genre=genre,
                    bpm=bpm,
                    map=map,
                    version=version,
                )
                filters = get_filters(
                    {
                        type: type_func,
                        level: level_func,
                        versions: versions_func,
                        keywords: keywords_func,
                    }
                )
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

                def keyword_func(icon):
                    return xstr(keywords) in (xstr(icon.name) + xstr(icon.description) + xstr(icon.genre))

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

                def keyword_func(icon):
                    return xstr(keywords) in (xstr(icon.name) + xstr(icon.description) + xstr(icon.genre))

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

                def keyword_func(icon):
                    return xstr(keywords) in (xstr(icon.name) + xstr(icon.description) + xstr(icon.genre))

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

                def keyword_func(icon):
                    return xstr(keywords) in (xstr(icon.name) + xstr(icon.color))

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

                def keyword_func(chara):
                    return xstr(keywords) in xstr(chara.name)

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

                def keyword_func(partner):
                    return xstr(keywords) in xstr(partner.name)

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

                def keyword_func(area):
                    return xstr(keywords) in (xstr(area.name) + xstr(area.comment))

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
            ) -> Union[Player, DivingFishPlayer, LXNSPlayer, ArcadePlayer, WechatPlayer, dict]:
                player_obj = await self._client.players(player, provider=provider)
                return asdict(player_obj)

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
                song_trait = (
                    id if id is not None else title if title is not None else keywords if keywords is not None else None
                )
                identifier = None if player._is_empty() else player
                if song_trait is not None:
                    return await self._client.minfo(song_trait, identifier, provider=provider)

            async def _get_identifiers(
                code: str = Query(..., description="code from wechat callback or SGWCMAID"),
                r: Optional[str] = Query(None, description="r from wechat callback"),
                t: Optional[str] = Query(None, description="t from wechat callback"),
                state: Optional[str] = Query(None, description="state from wechat callback"),
                provider: IPlayerIdentifierProvider = Depends(dep_provider),
            ) -> PlayerIdentifier:
                if code.startswith("SGWCMAID") and isinstance(provider, ArcadeProvider):
                    # direct use of SGWCMAID for ArcadeProvider
                    return await self._client.identifiers(code, provider=provider)
                elif all([r, t, state]) and isinstance(provider, WechatProvider):
                    # use the full set of query parameters for WechatProvider
                    params = {"r": r, "t": t, "code": code, "state": state}
                    return await self._client.identifiers(params, provider=provider)
                else:
                    raise MaimaiPyError("Invalid parameters for the selected provider.")

            bases: list[Callable] = [
                _get_songs,
                _get_icons,
                _get_nameplates,
                _get_frames,
                _get_trophies,
                _get_charas,
                _get_partners,
                _get_areas,
            ]
            players: list[Callable] = [
                _get_scores,
                _get_regions,
                _get_players,
                _get_bests,
                _post_scores,
                _get_plates,
                _get_minfo,
                _get_identifiers,
            ]

            all_routes = players + (bases if not skip_base else [])
            try:
                [try_add_route(func, router, dep_provider) for func in all_routes]
            except PydanticUndefinedAnnotation:
                warning(
                    "Current pydantic version does not support maimai.py API annotations"
                    "MaimaiRoutes may not work properly."
                    "Please upgrade pydantic to 2.7+."
                )

            return router

        def get_updates_chain_route(
            self,
            source_deps: list[tuple[Label, Callable]],
            target_deps: list[tuple[Label, Callable]],
            source_mode: Literal["fallback", "parallel"] = "fallback",
            target_mode: Literal["fallback", "parallel"] = "parallel",
        ) -> APIRouter:
            """Get a FastAPI APIRouter with a route for chaining updates from multiple sources to multiple targets.

            Args:
                source_deps: A list of tuples containing labels and dependency functions for source providers.
                target_deps: A list of tuples containing labels and dependency functions for target providers.
                source_mode: The mode for fetching from sources. Defaults to "fallback".
                target_mode: The mode for updating to targets. Defaults to "parallel".

            Returns:
                APIRouter: A FastAPI APIRouter with the updates_chain route.
            """
            router = APIRouter()

            available_sources_labels: set[Label] = {
                label for label, dep_provider in source_deps if isinstance(dep_provider(), IScoreProvider)
            }
            available_targets_labels: set[Label] = {
                label for label, dep_provider in target_deps if isinstance(dep_provider(), IScoreUpdateProvider)
            }

            async def _post_updates_chain(
                body: UpdatesChainRequest,
            ) -> UpdatesChainResponse:
                available_sources: dict[Label, IScoreProvider] = {
                    label: dep_provider()
                    for label, dep_provider in source_deps
                    if isinstance(dep_provider(), IScoreProvider)
                }
                available_targets: dict[Label, IScoreUpdateProvider] = {
                    label: dep_provider()
                    for label, dep_provider in target_deps
                    if isinstance(dep_provider(), IScoreUpdateProvider)
                }
                source_results, target_results = {}, {}

                def _callback(
                    to: dict,
                    scores: MaimaiScores,
                    err: Union[BaseException, None],
                    kwargs: dict[str, Any],
                ):
                    to[kwargs.get("label")] = UpdatesChainResponse.ChainResult(
                        errors=repr(err) if err is not None else None,
                        scores_num=len(scores.scores),
                        scores_rating=scores.rating,
                    )

                await self._client.updates_chain(
                    [
                        (available_sources[label], identifier, {"label": label})
                        for label, identifier in body.source.items()
                        if label in available_sources
                    ],
                    [
                        (available_targets[label], identifier, {"label": label})
                        for label, identifier in body.target.items()
                        if label in available_targets
                    ],
                    source_mode=source_mode,
                    target_mode=target_mode,
                    source_callback=lambda scores, err, kwargs: _callback(source_results, scores, err, kwargs),
                    target_callback=lambda scores, err, kwargs: _callback(target_results, scores, err, kwargs),
                )

                return UpdatesChainResponse(source=source_results, target=target_results)

            router.add_api_route(
                "/updates_chain",
                _post_updates_chain,
                name="post_updates_chain",
                methods=["POST"],
                response_model=UpdatesChainResponse,
                description=f"Fetch scores from multiple sources and update to multiple targets.\n\nAvailable sources: {', '.join(available_sources_labels)}\n\nAvailable targets: {', '.join(available_targets_labels)}\n\nSource mode: {source_mode}, Target mode: {target_mode}",
            )

            return router

        def get_wechat_oauth_route(self) -> APIRouter:
            """Get a FastAPI APIRouter with route for wechat oauth URL generation.

            Returns:
                APIRouter: A FastAPI APIRouter with the wechat_oauth route.
            """
            router = APIRouter()

            async def _get_wechat_oauth() -> WechatOAuthResponse:
                auth_url = await self._client.wechat()
                assert isinstance(auth_url, str)
                return WechatOAuthResponse(url=auth_url)

            router.add_api_route(
                "/wechat_oauth",
                _get_wechat_oauth,
                name="get_wechat_oauth",
                methods=["GET"],
                response_model=WechatOAuthResponse,
                description="Get wechat offiaccount oauth2 auth url with protocal modified redirect_url (https to http).",
            )

            return router


if all([find_spec(p) for p in ["fastapi", "uvicorn", "typer"]]):
    import typer
    import uvicorn
    from fastapi import APIRouter, Depends, FastAPI, Request
    from fastapi.openapi.utils import get_openapi
    from fastapi.responses import JSONResponse

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if routes._with_curves:
            curve_provider = DivingFishProvider(developer_token=routes._divingfish_token)
            logging.info("with_curves is enabled, pre-fetching curves from DivingFish.")
            await routes._client.songs(provider=HybridProvider(), curve_provider=curve_provider)
        yield

    asgi_app = FastAPI(
        title="maimai.py API",
        description="The definitive python wrapper for MaimaiCN related development.",
        lifespan=lifespan,
    )
    routes = MaimaiRoutes(MaimaiClientMultithreading())  # type: ignore

    # register routes and middlewares
    asgi_app.include_router(routes.get_router(routes._dep_hybrid, skip_base=False), tags=["base"])
    asgi_app.include_router(
        routes.get_router(routes._dep_divingfish, routes._dep_divingfish_player),
        prefix="/divingfish",
        tags=["divingfish"],
    )
    asgi_app.include_router(
        routes.get_router(routes._dep_lxns, routes._dep_lxns_player),
        prefix="/lxns",
        tags=["lxns"],
    )
    asgi_app.include_router(
        routes.get_router(routes._dep_wechat, routes._dep_wechat_player),
        prefix="/wechat",
        tags=["wechat"],
    )
    asgi_app.include_router(
        routes.get_router(routes._dep_arcade, routes._dep_arcade_player),
        prefix="/arcade",
        tags=["arcade"],
    )

    # chain updates route
    asgi_app.include_router(
        routes.get_updates_chain_route(
            source_deps=[
                ("divingfish", routes._dep_divingfish),
                ("lxns", routes._dep_lxns),
                ("wechat", routes._dep_wechat),
                ("arcade", routes._dep_arcade),
            ],
            target_deps=[
                ("divingfish", routes._dep_divingfish),
                ("lxns", routes._dep_lxns),
            ],
            source_mode="fallback",
            target_mode="parallel",
        ),
        prefix="/utils",
        tags=["utils"],
    )

    # other utils routes
    asgi_app.include_router(routes.get_wechat_oauth_route(), prefix="/utils", tags=["utils"])

    def main(
        host: Annotated[str, typer.Option(help="The host address to bind to.")] = "127.0.0.1",
        port: Annotated[int, typer.Option(help="The port number to bind to.")] = 8000,
        redis: Annotated[
            Optional[str],
            typer.Option(help="Redis server address, for example: redis://localhost:6379/0."),
        ] = None,
        lxns_token: Annotated[Optional[str], typer.Option(help="LXNS developer token for LXNS API.")] = None,
        divingfish_token: Annotated[
            Optional[str],
            typer.Option(help="DivingFish developer token for DivingFish API."),
        ] = None,
        arcade_proxy: Annotated[Optional[str], typer.Option(help="HTTP proxy for Arcade API.")] = None,
        with_curves: Annotated[bool, typer.Option(help="Whether to fetch curves from Divingfish.")] = False,
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
        routes._with_curves = with_curves

        @asgi_app.exception_handler(MaimaiPyError)
        async def exception_handler_mpy(request: Request, exc: MaimaiPyError):
            return JSONResponse(
                status_code=400,
                content={
                    "message": f"Oops! There goes a maimai.py error: {exc}.",
                    "details": repr(exc),
                },
            )

        @asgi_app.exception_handler(ArcadeError)
        async def exception_handler_mffi(request: Request, exc: MaimaiPyError):
            return JSONResponse(
                status_code=400,
                content={
                    "message": f"Oops! There goes a maimai.ffi error: {exc}.",
                    "details": repr(exc),
                },
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
        with open("openapi.json", "w") as f:
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
