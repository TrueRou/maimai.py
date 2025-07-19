import hashlib
from collections import defaultdict
from json import JSONDecodeError
from typing import TYPE_CHECKING

from httpx import HTTPStatusError, RequestError, Response
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from maimai_py.exceptions import InvalidJsonError, MaimaiPyError

from .base import IAliasProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient


class YuzuProvider(IAliasProvider):
    """The provider that fetches song aliases from the Yuzu.

    Yuzu is a bot API that provides song aliases for maimai DX.

    Yuzu: https://bot.yuzuchan.moe/
    """

    base_url = "https://www.yuzuchan.moe/api/"
    """The base URL for the Yuzu API."""

    def _hash(self) -> str:
        return hashlib.md5(b"yuzu").hexdigest()

    def _check_response(self, resp: Response) -> dict:
        try:
            resp_json = resp.json()
            if not resp.is_success:
                resp.raise_for_status()
            return resp_json
        except JSONDecodeError as exc:
            raise InvalidJsonError(resp.text) from exc
        except HTTPStatusError as exc:
            raise MaimaiPyError(exc) from exc

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def get_aliases(self, client: "MaimaiClient") -> dict[int, list[str]]:
        resp = await client._client.get(self.base_url + "maimaidx/maimaidxalias")
        resp_json = self._check_response(resp)
        grouped = defaultdict(list)
        for item in resp_json["content"]:
            grouped[item["SongID"] % 10000].extend(item["Alias"])
        return grouped
