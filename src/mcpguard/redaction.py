from __future__ import annotations

import re
from typing import Any


REDACTION_TEXT = "[REDACTED]"

DEFAULT_REDACTION_PATTERNS: tuple[str, ...] = (
    r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"]?[^'\"\s,;]+",
    r"ghp_[A-Za-z0-9_]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"sk-[A-Za-z0-9_-]{20,}",
    r"xox[baprs]-[A-Za-z0-9-]{20,}",
    r"AKIA[0-9A-Z]{16}",
)


def configured_redaction_patterns(config: dict[str, Any]) -> list[str]:
    redaction = config.get("redaction")
    custom_patterns: list[str] = []
    default_enabled = True
    if isinstance(redaction, dict):
        default_enabled = redaction.get("default_patterns", True) is not False
        patterns = redaction.get("patterns")
        if isinstance(patterns, list):
            custom_patterns = [pattern for pattern in patterns if isinstance(pattern, str) and pattern]

    patterns = []
    if default_enabled:
        patterns.extend(DEFAULT_REDACTION_PATTERNS)
    patterns.extend(custom_patterns)
    return patterns


def redact_value(value: Any, patterns: list[str]) -> Any:
    if isinstance(value, str):
        return redact_text(value, patterns)
    if isinstance(value, list):
        return [redact_value(item, patterns) for item in value]
    if isinstance(value, dict):
        return {key: redact_value(item, patterns) for key, item in value.items()}
    return value


def redact_text(value: str, patterns: list[str]) -> str:
    redacted = value
    for pattern in patterns:
        redacted = re.sub(pattern, _redact_match, redacted)
    return redacted


def _redact_match(match: re.Match[str]) -> str:
    text = match.group(0)
    separator_match = re.match(r"(?is)^(.+?[:=]\s*['\"]?).+$", text)
    if separator_match:
        return f"{separator_match.group(1)}{REDACTION_TEXT}"
    return REDACTION_TEXT
