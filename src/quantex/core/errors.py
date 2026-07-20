"""Structured errors raised by Quantex core services."""

from collections.abc import Mapping
from types import MappingProxyType


class ResourceManagerError(RuntimeError):
    """Base class for resource-management failures."""


class InvalidResourceRequestError(ResourceManagerError, ValueError):
    """Raised when an owner or resource name is invalid."""


class UnknownResourceError(ResourceManagerError, KeyError):
    """Raised when a request contains resources that were not registered."""

    def __init__(self, resources: set[str] | frozenset[str]) -> None:
        self.resources = frozenset(resources)
        names = ", ".join(sorted(self.resources))
        super().__init__(f"Unknown resources: {names}")

    def __str__(self) -> str:
        return self.args[0]


class ResourceAlreadyRegisteredError(ResourceManagerError):
    """Raised when registration would overwrite existing resources."""

    def __init__(self, resources: set[str] | frozenset[str]) -> None:
        self.resources = frozenset(resources)
        names = ", ".join(sorted(self.resources))
        super().__init__(f"Resources already registered: {names}")


class ResourceBusyError(ResourceManagerError):
    """Raised when one or more requested resources already have an owner."""

    def __init__(self, conflicts: Mapping[str, str]) -> None:
        conflict_copy = dict(sorted(conflicts.items()))
        self.conflicts: Mapping[str, str] = MappingProxyType(conflict_copy)
        details = ", ".join(f"{resource} (owned by {owner})" for resource, owner in conflict_copy.items())
        super().__init__(f"Resources are busy: {details}")
