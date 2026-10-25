from abc import ABC, abstractmethod


# TODO tests
class Player(ABC):
    @abstractmethod
    def load(self, path: str) -> None: ...

    @abstractmethod
    def play(self) -> None: ...

    @abstractmethod
    def pause(self) -> None: ...

    @abstractmethod
    def unpause(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def position(self) -> float: ...

    @abstractmethod
    def busy(self) -> bool: ...
