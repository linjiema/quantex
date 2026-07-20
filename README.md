# Quantex

Quantex is a PyQt-based control application for confocal imaging, pulsed ESR, and polarization
measurements. The current hardware application is being migrated incrementally to a modular package
architecture while preserving the working laboratory code.

## Current application

The legacy application still starts from the repository root:

```console
python main.py
```

The laboratory environment currently targets Python 3.11 on Windows. Vendor prerequisites such as
the Visual Studio 2010 runtime, TimeTagger SDK, device DLLs, and device drivers must be installed
separately on the control computer.

The existing `requirements.txt` and `config/env_config.yaml` are retained as legacy snapshots of a
working machine. They contain machine-specific Conda paths and are not portable dependency files.

## Package foundation

The new package is located under `src/quantex`. During the migration it intentionally coexists with
the legacy `src.*` and `ui.*` packages. Installing the package foundation does not yet replace the
`python main.py` entry point.

Create and activate a Python 3.11 virtual environment, then install the package in editable mode:

```console
python -m pip install -e ".[dev]"
```

Hardware-related PyPI dependencies can be installed separately:

```console
python -m pip install -e ".[hardware]"
```

The `hardware` extra does not install vendor SDKs or bundled DLL prerequisites.

## Development checks

Run the package smoke tests and lint the new package boundary:

```console
python -m pytest
python -m ruff check src/quantex tests/unit
```

Legacy hardware scripts are deliberately excluded from default test discovery. They will be
classified into manual and hardware-in-the-loop test suites in a later migration step.

## Architecture direction

The target dependency direction is:

```text
GUI -> experiment logic -> hardware interfaces <- concrete drivers
```

Core services will own configuration, module lifecycle, managed jobs, cancellation, and exclusive
hardware resource access. This package-foundation change only creates the destination package and
development metadata; it does not change experiment or device behavior.
