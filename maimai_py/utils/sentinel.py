from typing import Any, TypeVar

_T = TypeVar("_T")


class _UnsetSentinel:
    def __repr__(self) -> str:
        return "Unset"

    def __copy__(self: _T) -> _T:
        return self

    def __reduce__(self) -> str:
        return "Unset"

    def __deepcopy__(self: _T, _: Any) -> _T:
        return self


UNSET = _UnsetSentinel()
