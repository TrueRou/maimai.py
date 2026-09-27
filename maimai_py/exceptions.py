from typing import Type

from maimai_ffi.exceptions import AimeServerError as AimeServerError
from maimai_ffi.exceptions import ArcadeError as ArcadeError
from maimai_ffi.exceptions import ArcadeIdentifierError as ArcadeIdentifierError
from maimai_ffi.exceptions import TitleServerBlockedError as TitleServerBlockedError
from maimai_ffi.exceptions import TitleServerNetworkError as TitleServerNetworkError

ArcadeError: Type[Exception]
AimeServerError: Type[Exception]
ArcadeIdentifierError: Type[Exception]
TitleServerBlockedError: Type[Exception]
TitleServerNetworkError: Type[Exception]


class MaimaiPyError(Exception):
    """Base exception class for all exceptions raised by maimai_py."""


class InvalidJsonError(MaimaiPyError):
    """Invalid JSON response from the provider."""


class InvalidPlayerIdentifierError(MaimaiPyError):
    """Player identifier is invalid for the provider.

    For example, friend code is not applicable for Diving Fish provider, the username is not applicable for LXNS provider.

    Also, if the player is not found on that provider, this exception will be raised.
    """


class InvalidDeveloperTokenError(MaimaiPyError):
    """Developer token is not provided or token is invalid."""


class InvalidPlateError(MaimaiPyError):
    """Provided version or plate is invalid.

    Plate should be formatted as two/three characters (version + kind), e.g. "桃将", "舞舞舞"

    The following versions are valid:

    霸, 舞, 初, 真, 超, 檄, 橙, 晓, 桃, 樱, 紫, 堇, 白, 雪, 辉, 熊, 华, 爽, 煌, 星, 宙, 祭, 祝, 双, 宴.

    The following kinds are valid:

    将, 者, 極, 极, 舞舞, 神

    """


class PrivacyLimitationError(MaimaiPyError):
    """The user has not accepted the privacy policy or exceeded the privacy limit of the provider."""


class PlayerNotAuthorizedError(MaimaiPyError):
    """The user has not authorized the application to access their data, or the token lacks the required scope.

    For the Diving Fish OAuth, this is raised when the token exchange returns ``consent_required``: the user
    has not consented to your application, or does not exist at all (the server deliberately does not
    distinguish the two cases). It is also raised when an endpoint rejects the access token because it lacks
    the scope required by that endpoint. Guide the user through the authorization flow instead of reporting
    a plain query failure.
    """


class RateLimitError(MaimaiPyError):
    """The provider's rate limit or daily quota is exceeded."""


class InvalidWechatTokenError(MaimaiPyError):
    """Wahlap Wechat OffiAccount token is invalid or expired."""


WechatTokenExpiredError = InvalidWechatTokenError
