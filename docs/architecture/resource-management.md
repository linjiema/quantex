# Resource management

Quantex experiments share physical instruments. A measurement must have exclusive ownership of the
resources it configures or closes, otherwise one experiment can invalidate another experiment's
hardware state.

`ResourceManager` provides thread-safe ownership of registered resource names:

```python
from quantex.core import ResourceManager

resources = ResourceManager({"counter", "microwave", "pulser"})

with resources.acquire(
    owner="pulsed_odmr",
    resources={"counter", "microwave", "pulser"},
):
    run_measurement()
```

## Guarantees

- A request for multiple resources is atomic: it either acquires all resources or none.
- A busy resource reports its current owner in `ResourceBusyError.conflicts`.
- Unknown resources are rejected before ownership changes.
- Context-manager exit releases every resource, including when measurement code raises an exception.
- Releasing the same lease more than once is safe.
- Registration, acquisition, release, and snapshots are protected by a re-entrant lock.
- Snapshots cannot be used to mutate manager state.

## Deliberate boundaries

The manager tracks ownership only. It does not construct, initialize, reset, or close hardware
objects. Device lifecycle remains separate so a resource lease cannot accidentally become a service
locator for concrete drivers.

The first version also uses strict exclusive ownership. A second acquisition conflicts even when it
uses the same owner name. Composed workflows must acquire their complete resource set at the
top-level operation and pass the resulting ownership context to their child logic.

Legacy `DeviceManager` and GUI modules are not connected in this change. That integration will only
happen after hardware capability interfaces and adapters are available.
