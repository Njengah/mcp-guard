# Install And Run

## Requirements

- Python 3.10 or newer
- A local checkout of the repository

## Editable Install

```powershell
python -m pip install -e .
mcpguard --help
```

## Run Without Installing

```powershell
$env:PYTHONPATH = "src"
python -m mcpguard --help
```

## Verify The Project

```powershell
python scripts/test.py
```

This runs the repository test suite without requiring a permanent editable install.

## Initialize A Project

Run this from the project directory you want to govern:

```powershell
mcpguard init
```

MCPGuard creates `.mcpguard/` with config, policy, log, and report paths.
