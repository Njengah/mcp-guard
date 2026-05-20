from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import CorruptedStateError, NotInitializedError

SCHEMA_VERSION = "0.1"
STATE_DIR = ".mcpguard"
CONFIG_FILE = "config.json"
POLICIES_FILE = "policies.json"
LOGS_DIR = "logs"
REPORTS_DIR = "reports"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class Paths:
    root: Path

    @property
    def state_dir(self) -> Path:
        return self.root / STATE_DIR

    @property
    def config_file(self) -> Path:
        return self.state_dir / CONFIG_FILE

    @property
    def policies_file(self) -> Path:
        return self.state_dir / POLICIES_FILE

    @property
    def logs_dir(self) -> Path:
        return self.state_dir / LOGS_DIR

    @property
    def reports_dir(self) -> Path:
        return self.state_dir / REPORTS_DIR

    @property
    def report_file(self) -> Path:
        return self.reports_dir / "report.md"


def project_paths(root: Path | None = None) -> Paths:
    return Paths((root or Path.cwd()).resolve())


def ensure_initialized(paths: Paths) -> None:
    if not paths.config_file.exists() or not paths.policies_file.exists():
        raise NotInitializedError("MCPGuard is not initialized. Run 'mcpguard init' first.")


def default_config(project_name: str, timestamp: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "project_name": project_name,
        "created_at": timestamp,
        "servers": {},
        "future_integrations": {
            "source_repo": None,
            "agenttrace_run_id": None,
        },
    }


def default_policies(timestamp: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": timestamp,
        "servers": {},
    }


def init_state(paths: Paths) -> tuple[dict[str, Any], dict[str, Any]]:
    timestamp = utc_now()
    paths.logs_dir.mkdir(parents=True, exist_ok=True)
    paths.reports_dir.mkdir(parents=True, exist_ok=True)

    if not paths.config_file.exists():
        write_json(paths.config_file, default_config(paths.root.name, timestamp))
    if not paths.policies_file.exists():
        write_json(paths.policies_file, default_policies(timestamp))

    return read_config(paths), read_policies(paths)


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise CorruptedStateError(f"Corrupted JSON file: {path}") from exc
    except OSError as exc:
        raise CorruptedStateError(f"Could not read state file: {path}") from exc
    if not isinstance(data, dict):
        raise CorruptedStateError(f"State file must contain a JSON object: {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp_path.replace(path)


def read_config(paths: Paths) -> dict[str, Any]:
    ensure_initialized(paths)
    return read_json(paths.config_file)


def read_policies(paths: Paths) -> dict[str, Any]:
    ensure_initialized(paths)
    return read_json(paths.policies_file)


def append_jsonl(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, sort_keys=True))
        handle.write("\n")


def read_jsonl_dir(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for log_file in sorted(path.glob("*.jsonl")):
        try:
            with log_file.open("r", encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    value = json.loads(line)
                    if isinstance(value, dict):
                        entries.append(value)
        except json.JSONDecodeError as exc:
            raise CorruptedStateError(
                f"Corrupted JSONL log file: {log_file}:{line_number}"
            ) from exc
    return entries

