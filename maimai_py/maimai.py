from typing import Literal, Type
import httpx
from httpx import AsyncClient

from maimai_ffi import arcade
from maimai_py.enums import *
from maimai_py.models import *
from maimai_py.providers import *
from maimai_py.caches import default_caches
from maimai_py.exceptions import WechatTokenExpiredError
from maimai_py.utils.sentinel import UNSET


class MaimaiClient:
    """The main client of maimai.py."""

    default_caches._caches_provider["songs"] = LXNSProvider()
    default_caches._caches_provider["aliases"] = YuzuProvider()
    default_caches._caches_provider["curves"] = DivingFishProvider()
    default_caches._caches_provider["icons"] = LXNSProvider()
    default_caches._caches_provider["nameplates"] = LXNSProvider()
    default_caches._caches_provider["frames"] = LXNSProvider()
    default_caches._caches_provider["trophies"] = LocalProvider()
    default_caches._caches_provider["charas"] = LocalProvider()
    default_caches._caches_provider["partners"] = LocalProvider()

    _client: AsyncClient

    def __init__(self, timeout: float = 20.0, **kwargs) -> None:
        """Initialize the maimai.py client.

        Args:
            timeout: the timeout of the requests, defaults to 20.0.
        """
        self._client = httpx.AsyncClient(timeout=timeout, **kwargs)

    async def songs(
        self,
        flush=False,
        provider: ISongProvider = UNSET,
        alias_provider: IAliasProvider = UNSET,
        curve_provider: ICurveProvider = UNSET,
    ) -> MaimaiSongs:
        """Fetch all maimai songs from the provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`.

        Available alias providers: `YuzuProvider`, `LXNSProvider`.

        Available curve providers: `DivingFishProvider`.

        Args:
            flush: whether to flush the cache, defaults to False.
            provider: override the data source to fetch the player from, defaults to `LXNSProvider`.
            alias_provider: override the data source to fetch the song aliases from, defaults to `YuzuProvider`.
            curve_provider: override the data source to fetch the song curves from, defaults to `DivingFishProvider`.
        Returns:
            A wrapper of the song list, for easier access and filtering.
        Raises:
            httpx.HTTPError: Request failed due to network issues.
        """
        if provider is not UNSET and default_caches._caches_provider["songs"] != provider:
            default_caches._caches_provider["songs"] = provider
            flush = True
        if alias_provider is not UNSET and default_caches._caches_provider["aliases"] != alias_provider:
            default_caches._caches_provider["aliases"] = alias_provider
            flush = True
        if curve_provider is not UNSET and default_caches._caches_provider["curves"] != curve_provider:
            default_caches._caches_provider["curves"] = curve_provider
            flush = True
        return await MaimaiSongs._get_or_fetch(self._client, flush=flush)

    async def players(
        self,
        identifier: PlayerIdentifier,
        provider: IPlayerProvider = LXNSProvider(),
    ) -> DivingFishPlayer | LXNSPlayer | ArcadePlayer:
        """Fetch player data from the provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`, `ArcadeProvider`.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(username="turou")`.
            provider: the data source to fetch the player from, defaults to `LXNSProvider`.
        Returns:
            The player object of the player, with all the data fetched.
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            httpx.HTTPError: Request failed due to network issues.
        Raises:
            TitleServerError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            ArcadeError: Only for ArcadeProvider, maimai response is invalid, or user id is invalid.
        """
        return await provider.get_player(identifier, self._client)

    async def scores(
        self,
        identifier: PlayerIdentifier,
        kind: ScoreKind = ScoreKind.BEST,
        provider: IScoreProvider = LXNSProvider(),
    ) -> MaimaiScores:
        """Fetch player's scores from the provider.

        For WechatProvider, PlayerIdentifier must have the `credentials` attribute, we suggest you to use the `maimai.wechat()` method to get the identifier.
        Also, PlayerIdentifier should not be cached or stored in the database, as the cookies may expire at any time.

        For ArcadeProvider, PlayerIdentifier must have the `credentials` attribute, which is the player's encrypted userId, can be detrived from `maimai.qrcode()`.
        Credentials can be reused, since it won't expire, also, userId is encrypted, can't be used in any other cases outside the maimai.py

        Available providers: `DivingFishProvider`, `LXNSProvider`, `WechatProvider`, `ArcadeProvider`.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(friend_code=664994421382429)`.
            kind: the kind of scores list to fetch, defaults to `ScoreKind.BEST`.
            provider: the data source to fetch the player and scores from, defaults to `LXNSProvider`.
        Returns:
            The scores object of the player, with all the data fetched.
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            httpx.HTTPError: Request failed due to network issues.
        Raises:
            TitleServerError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            ArcadeError: Only for ArcadeProvider, maimai response is invalid, or user id is invalid.
        """
        # MaimaiScores should always cache b35 and b15 scores, in ScoreKind.ALL cases, we can calc the b50 scores from all scores.
        # But there is one exception, LXNSProvider's ALL scores are incomplete, which doesn't contain dx_rating and achievements, leading to sorting difficulties.
        # In this case, we should always fetch the b35 and b15 scores for LXNSProvider.
        await MaimaiSongs._get_or_fetch(self._client)  # Cache the songs first, as we need to use it for scores' property.
        b35, b15, all, songs = None, None, None, None
        if kind == ScoreKind.BEST or isinstance(provider, LXNSProvider):
            b35, b15 = await provider.get_scores_best(identifier, self._client)
        # For some cases, the provider doesn't support fetching b35 and b15 scores, we should fetch all scores instead.
        if kind == ScoreKind.ALL or (b35 == None and b15 == None):
            songs = await MaimaiSongs._get_or_fetch(self._client)
            all = await provider.get_scores_all(identifier, self._client)
        return MaimaiScores(b35, b15, all, songs)

    async def regions(self, identifier: PlayerIdentifier, provider: IRegionProvider = ArcadeProvider()) -> list[PlayerRegion]:
        """Get the player's regions that they have played.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(credentials="encrypted_user_id")`.
            provider: the data source to fetch the player from, defaults to `ArcadeProvider`.
        Returns:
            The list of regions that the player has played.
        Raises:
            TitleServerError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            ArcadeError: Only for ArcadeProvider, maimai response is invalid, or user id is invalid.
        """
        return await provider.get_regions(identifier, self._client)

    async def updates(
        self,
        identifier: PlayerIdentifier,
        scores: list[Score],
        provider: IScoreProvider = LXNSProvider(),
    ) -> None:
        """Update player's scores to the provider.

        For Diving Fish, the player identifier should be the player's username and password, or import token, e.g.:

        `PlayerIdentifier(username="turou", credentials="password")` or `PlayerIdentifier(credentials="my_diving_fish_import_token")`.

        Available providers: `DivingFishProvider`, `LXNSProvider`.

        Args:
            identifier: the identifier of the player to update, e.g. `PlayerIdentifier(friend_code=664994421382429)`.
            scores: the scores to update, usually the scores fetched from other providers.
            provider: the data source to update the player scores to, defaults to `LXNSProvider`.
        Returns:
            Nothing, failures will raise exceptions.
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found, or the import token / password is invalid.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            httpx.HTTPError: Request failed due to network issues.
        """
        await provider.update_scores(identifier, scores, self._client)

    async def plates(
        self,
        identifier: PlayerIdentifier,
        plate: str,
        provider: IScoreProvider = LXNSProvider(),
    ) -> MaimaiPlates:
        """Get the plate achievement of the given player and plate.

        Available providers: `DivingFishProvider`, `LXNSProvider`, `ArcadeProvider`.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(friend_code=664994421382429)`.
            plate: the name of the plate, e.g. "樱将", "真舞舞".
            provider: the data source to fetch the player and scores from, defaults to `LXNSProvider`.
        Returns:
            A wrapper of the plate achievement, with plate information, and matched player scores.
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found.
            InvalidPlateError: Provided version or plate is invalid.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            httpx.HTTPError: Request failed due to network issues.
        """
        songs = await MaimaiSongs._get_or_fetch(self._client)
        scores = await provider.get_scores_all(identifier, self._client)
        return MaimaiPlates(scores, plate[0], plate[1:], songs)

    async def wechat(self, r=None, t=None, code=None, state=None) -> PlayerIdentifier | str:
        """Get the player identifier from the Wahlap Wechat OffiAccount.

        Call the method with no parameters to get the URL, then redirect the user to the URL with your mitmproxy enabled.

        Your mitmproxy should intercept the response from tgk-wcaime.wahlap.com, then call the method with the parameters from the intercepted response.

        With the parameters from specific user's response, the method will return the user's player identifier.

        Never cache or store the player identifier, as the cookies may expire at any time.

        Args:
            r: the r parameter from the request, defaults to None.
            t: the t parameter from the request, defaults to None.
            code: the code parameter from the request, defaults to None.
            state: the state parameter from the request, defaults to None.
        Returns:
            The player identifier if all parameters are provided, otherwise return the URL to get the identifier.
        Raises:
            WechatTokenExpiredError: Wechat token is expired, please re-authorize.
            httpx.HTTPError: Request failed due to network issues.
        """
        if not all([r, t, code, state]):
            resp = await self._client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/authorize/maimai-dx")
            return resp.headers["location"].replace("redirect_uri=https", "redirect_uri=http")
        params = {"r": r, "t": t, "code": code, "state": state}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6307001e)",
            "Host": "tgk-wcaime.wahlap.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }
        resp = await self._client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/callback/maimai-dx", params=params, headers=headers, timeout=5)
        if resp.status_code != 302:
            raise WechatTokenExpiredError("Wechat token is expired")
        resp_next = await self._client.get(resp.next_request.url, headers=headers)
        return PlayerIdentifier(credentials=resp_next.cookies)

    async def qrcode(self, qrcode: str, http_proxy: str | None = None) -> PlayerIdentifier:
        """Get the player identifier from the Wahlap QR code.

        Player identifier is the encrypted userId, can't be used in any other cases outside the maimai.py.

        Args:
            qrcode: the QR code of the player, should begin with SGWCMAID.
            http_proxy: the http proxy to use for the request, defaults to None.
        Returns:
            The player identifier of the player.
        Raises:
            AimeServerError: Maimai Aime server error, may be invalid QR code or QR code has expired.
            TitleServerError: Maimai title server related errors, possibly network problems.
        """
        resp: ArcadeResponse = await arcade.get_uid_encrypted(qrcode, http_proxy=http_proxy)
        ArcadeResponse._throw_error(resp)
        return PlayerIdentifier(credentials=resp.data.decode())

    async def items(self, item: Type[CachedType], flush=False, provider: IItemListProvider = UNSET) -> MaimaiItems[CachedType]:
        """Fetch maimai player items from the cache default provider.

        Available items: `PlayerIcon`, `PlayerNamePlate`, `PlayerFrame`, `PlayerTrophy`, `PlayerChara`, `PlayerPartner`.

        Args:
            item: the item type to fetch, e.g. `PlayerIcon`.
            flush: whether to flush the cache, defaults to False.
            provider: override the default item list provider, defaults to `LXNSProvider` and `LocalProvider`.
        Returns:
            A wrapper of the item list, for easier access and filtering.
        Raises:
            FileNotFoundError: The item file is not found.
            httpx.HTTPError: Request failed due to network issues.
        """
        if provider and provider is not UNSET:
            default_caches._caches_provider[item._cache_key()] = provider
        items = await default_caches.get_or_fetch(item._cache_key(), self._client, flush=flush)
        return MaimaiItems[CachedType](items)

    async def areas(self, lang: Literal["ja", "zh"] = "ja", provider: IAreaProvider = LocalProvider()) -> MaimaiAreas:
        """Fetch maimai areas from the provider.

        Available providers: `LocalProvider`.

        Args:
            lang: the language of the area to fetch, available languages: `ja`, `zh`.
            provider: override the default area provider, defaults to `ArcadeProvider`.
        Returns:
            A wrapper of the area list, for easier access and filtering.
        Raises:
            FileNotFoundError: The area file is not found.
        """

        return MaimaiAreas(lang, await provider.get_areas(lang, self._client))

    async def flush(self) -> None:
        """Flush the caches of the client, this will perform a full re-fetch of all the data.

        Notice that only items ("songs", "aliases", "curves", "icons", "plates", "frames", "trophy", "chara", "partner") will be cached, this will only affect those items.
        """
        await default_caches.flush(self._client)
