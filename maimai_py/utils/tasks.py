from typing import Coroutine, Iterable


async def empty_task() -> None:
    pass


def build_tasks(tasks: Iterable[Coroutine | None]) -> list[Coroutine]:
    return [task if task else empty_task for task in tasks]
