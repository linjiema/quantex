"""Unit tests for named resource ownership."""

from queue import Queue
from threading import Barrier, Event, Thread

import pytest

from quantex.core import (
    InvalidResourceRequestError,
    ResourceAlreadyRegisteredError,
    ResourceBusyError,
    ResourceManager,
    UnknownResourceError,
)


def test_acquire_and_release_single_resource() -> None:
    manager = ResourceManager("counter")

    lease = manager.acquire(owner="confocal", resources="counter")

    assert lease.owner == "confocal"
    assert lease.resources == frozenset({"counter"})
    assert manager.owner_of("counter") == "confocal"
    assert lease.release() is True
    assert manager.owner_of("counter") is None


def test_multiple_resources_are_acquired_atomically() -> None:
    manager = ResourceManager({"counter", "microwave", "pulser"})
    manager.acquire(owner="confocal", resources="counter")

    with pytest.raises(ResourceBusyError) as error:
        manager.acquire(owner="pulsed_odmr", resources={"counter", "microwave", "pulser"})

    assert error.value.conflicts == {"counter": "confocal"}
    assert manager.owner_of("microwave") is None
    assert manager.owner_of("pulser") is None


def test_context_manager_releases_resources() -> None:
    manager = ResourceManager({"counter", "pulser"})

    with manager.acquire(owner="confocal", resources={"counter", "pulser"}):
        assert manager.snapshot().owners == {"counter": "confocal", "pulser": "confocal"}

    assert manager.snapshot().owners == {}


def test_context_manager_releases_resources_after_error() -> None:
    manager = ResourceManager("counter")

    with pytest.raises(RuntimeError, match="measurement failed"):
        with manager.acquire(owner="confocal", resources="counter"):
            raise RuntimeError("measurement failed")

    assert manager.owner_of("counter") is None


def test_release_is_idempotent() -> None:
    manager = ResourceManager("counter")
    lease = manager.acquire(owner="confocal", resources="counter")

    assert lease.release() is True
    assert lease.release() is False
    assert lease.released is True


def test_unknown_resources_do_not_change_existing_ownership() -> None:
    manager = ResourceManager({"counter", "pulser"})

    with pytest.raises(UnknownResourceError) as error:
        manager.acquire(owner="confocal", resources={"counter", "missing"})

    assert error.value.resources == frozenset({"missing"})
    assert manager.snapshot().owners == {}


@pytest.mark.parametrize(
    ("owner", "resources"),
    [
        ("", "counter"),
        ("   ", "counter"),
        ("confocal", ""),
        ("confocal", []),
        ("confocal", ["counter", " "]),
    ],
)
def test_invalid_acquire_requests_are_rejected(owner: str, resources: object) -> None:
    manager = ResourceManager("counter")

    with pytest.raises(InvalidResourceRequestError):
        manager.acquire(owner=owner, resources=resources)  # type: ignore[arg-type]


def test_duplicate_registration_is_atomic() -> None:
    manager = ResourceManager({"counter", "pulser"})

    with pytest.raises(ResourceAlreadyRegisteredError):
        manager.register({"microwave", "pulser"})

    assert manager.snapshot().registered == frozenset({"counter", "pulser"})


def test_snapshot_cannot_mutate_manager_state() -> None:
    manager = ResourceManager({"counter", "pulser"})
    manager.acquire(owner="confocal", resources="counter")
    snapshot = manager.snapshot()

    with pytest.raises(TypeError):
        snapshot.owners["pulser"] = "other"  # type: ignore[index]

    assert manager.owner_of("pulser") is None
    assert snapshot.available == frozenset({"pulser"})


def test_only_one_thread_can_acquire_a_resource() -> None:
    manager = ResourceManager("counter")
    start = Barrier(2)
    release_winner = Event()
    results: Queue[tuple[str, str]] = Queue()

    def acquire(owner: str) -> None:
        start.wait()
        try:
            with manager.acquire(owner=owner, resources="counter"):
                results.put(("acquired", owner))
                release_winner.wait(timeout=2)
        except ResourceBusyError:
            results.put(("busy", owner))
            release_winner.set()

    threads = [Thread(target=acquire, args=(owner,)) for owner in ("confocal", "pulsed_odmr")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    outcomes = sorted(results.get_nowait()[0] for _ in range(2))
    assert outcomes == ["acquired", "busy"]
    assert manager.owner_of("counter") is None
    assert all(not thread.is_alive() for thread in threads)
