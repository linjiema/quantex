"""Thread-safe ownership management for named hardware resources."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from threading import RLock
from types import MappingProxyType
from typing import TypeAlias

from quantex.core.errors import (
    InvalidResourceRequestError,
    ResourceAlreadyRegisteredError,
    ResourceBusyError,
    UnknownResourceError,
)

ResourceNames: TypeAlias = str | Iterable[str]


@dataclass(frozen=True, slots=True)
class ResourceSnapshot:
    """Immutable point-in-time view of resource ownership."""

    registered: frozenset[str]
    owners: Mapping[str, str]

    @property
    def available(self) -> frozenset[str]:
        """Return registered resources that are not currently leased."""
        return self.registered.difference(self.owners)


class ResourceLease:
    """Exclusive ownership of a set of resources.

    Leases are created by :meth:`ResourceManager.acquire` and can be used as
    context managers. Releasing a lease more than once is safe.
    """

    __slots__ = ("_manager", "_owner", "_released", "_resources")

    def __init__(self, manager: ResourceManager, owner: str, resources: frozenset[str]) -> None:
        self._manager = manager
        self._owner = owner
        self._resources = resources
        self._released = False

    @property
    def owner(self) -> str:
        """Return the owner that acquired this lease."""
        return self._owner

    @property
    def resources(self) -> frozenset[str]:
        """Return the resources covered by this lease."""
        return self._resources

    @property
    def released(self) -> bool:
        """Return whether the lease has already been released."""
        return self._manager._is_released(self)

    def release(self) -> bool:
        """Release all resources, returning ``True`` only on first release."""
        return self._manager._release(self)

    def __enter__(self) -> ResourceLease:
        if self.released:
            raise RuntimeError("A released resource lease cannot be reused")
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.release()


class ResourceManager:
    """Register named resources and grant atomic exclusive leases.

    This class tracks ownership only. It deliberately does not initialize,
    close, or otherwise hold concrete hardware devices.
    """

    def __init__(self, resources: ResourceNames | None = None) -> None:
        self._lock = RLock()
        self._registered: set[str] = set()
        self._leases_by_resource: dict[str, ResourceLease] = {}
        if resources is not None:
            self.register(resources)

    def register(self, resources: ResourceNames) -> frozenset[str]:
        """Atomically register resource names and return the normalized names."""
        normalized = _normalize_resources(resources)
        with self._lock:
            duplicates = normalized.intersection(self._registered)
            if duplicates:
                raise ResourceAlreadyRegisteredError(duplicates)
            self._registered.update(normalized)
        return normalized

    def acquire(self, *, owner: str, resources: ResourceNames) -> ResourceLease:
        """Atomically acquire all requested resources for ``owner``.

        If any requested resource is unknown or busy, no resource is acquired.
        """
        normalized_owner = _normalize_owner(owner)
        normalized_resources = _normalize_resources(resources)

        with self._lock:
            unknown = normalized_resources.difference(self._registered)
            if unknown:
                raise UnknownResourceError(unknown)

            conflicts = {
                resource: self._leases_by_resource[resource].owner
                for resource in normalized_resources
                if resource in self._leases_by_resource
            }
            if conflicts:
                raise ResourceBusyError(conflicts)

            lease = ResourceLease(self, normalized_owner, normalized_resources)
            for resource in normalized_resources:
                self._leases_by_resource[resource] = lease
            return lease

    def snapshot(self) -> ResourceSnapshot:
        """Return an immutable copy of current registration and ownership."""
        with self._lock:
            owners = {resource: lease.owner for resource, lease in sorted(self._leases_by_resource.items())}
            return ResourceSnapshot(
                registered=frozenset(self._registered),
                owners=MappingProxyType(owners),
            )

    def owner_of(self, resource: str) -> str | None:
        """Return the current owner of a resource, or ``None`` if available."""
        normalized = _normalize_resource_name(resource)
        with self._lock:
            if normalized not in self._registered:
                raise UnknownResourceError({normalized})
            lease = self._leases_by_resource.get(normalized)
            return None if lease is None else lease.owner

    def _is_released(self, lease: ResourceLease) -> bool:
        with self._lock:
            return lease._released

    def _release(self, lease: ResourceLease) -> bool:
        with self._lock:
            if lease._released:
                return False

            for resource in lease.resources:
                if self._leases_by_resource.get(resource) is not lease:
                    raise RuntimeError(f"Resource lease state is inconsistent for {resource!r}")

            for resource in lease.resources:
                del self._leases_by_resource[resource]
            lease._released = True
            return True


def _normalize_owner(owner: str) -> str:
    if not isinstance(owner, str) or not owner.strip():
        raise InvalidResourceRequestError("Resource owner must be a non-empty string")
    return owner.strip()


def _normalize_resource_name(resource: str) -> str:
    if not isinstance(resource, str) or not resource.strip():
        raise InvalidResourceRequestError("Resource names must be non-empty strings")
    return resource.strip()


def _normalize_resources(resources: ResourceNames) -> frozenset[str]:
    if isinstance(resources, str):
        values = (resources,)
    else:
        try:
            values = tuple(resources)
        except TypeError as error:
            raise InvalidResourceRequestError("Resources must be a string or iterable of strings") from error

    normalized = frozenset(_normalize_resource_name(resource) for resource in values)
    if not normalized:
        raise InvalidResourceRequestError("At least one resource must be requested")
    return normalized
