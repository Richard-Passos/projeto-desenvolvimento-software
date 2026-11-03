from abc import ABC, abstractmethod
from typing import Any


class IViewObserver(ABC):
    """Contract used by views to notify the application mediator."""

    @abstractmethod
    def notificar_evento(self, tipo_evento: str, dados: dict[str, Any]) -> None:
        """Receive a user-originated event from a view."""
        raise NotImplementedError


Observer = IViewObserver | None
