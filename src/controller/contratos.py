"""Contratos mínimos usados pelo mediador da aplicação.

As implementações concretas podem usar qualquer biblioteca de áudio, MIDI ou
persistência. A UI e o AppController não dependem dessas bibliotecas.
"""

from typing import Any, Protocol


class ApplicationService(Protocol):
    """Porta opcional para casos de uso da aplicação."""

    def __getattr__(self, name: str) -> Any: ...


class ApplicationInfrastructure(Protocol):
    """Porta opcional para arquivos, reprodução e exportação."""

    def __getattr__(self, name: str) -> Any: ...
