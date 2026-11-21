from abc import ABC, abstractmethod


class Command[T](ABC):
    @abstractmethod
    def execute(self, handler: T) -> None: ...
