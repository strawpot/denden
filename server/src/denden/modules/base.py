from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from denden.server import DenDenServer


class Module(ABC):
    """Base class for dynamically loadable server modules."""

    @abstractmethod
    def name(self) -> str:
        """Return a unique name for this module."""
        ...

    @abstractmethod
    def methods(self) -> dict[str, Callable]:
        """Return a map of method_name -> handler callable."""
        ...

    def on_load(self, server: DenDenServer) -> None:
        """Called when the module is loaded into the server."""
        pass
