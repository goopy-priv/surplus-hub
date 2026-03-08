from abc import ABC, abstractmethod
from typing import Any, Callable

from fastapi import BackgroundTasks


class TaskQueue(ABC):
    @abstractmethod
    def enqueue(self, func: Callable, *args: Any, **kwargs: Any) -> None: ...


class FastAPITaskQueue(TaskQueue):
    """FastAPI BackgroundTasks 기반 초기 구현.
    향후 Celery/Redis 기반 구현으로 교체 가능."""

    def __init__(self, background_tasks: BackgroundTasks):
        self._tasks = background_tasks

    def enqueue(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        self._tasks.add_task(func, *args, **kwargs)
