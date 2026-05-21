from __future__ import annotations

from typing import Any


DEFAULT_BASE_SCORE = 30
DEFAULT_RISK_KEYWORDS: tuple[str, ...] = (
    "write",
    "delete",
    "remove",
    "publish",
    "deploy",
    "execute",
    "run",
    "update",
)
DEFAULT_KEYWORD_MODIFIER = 40
DEFAULT_BLOCK_MODIFIER = 20
DEFAULT_APPROVE_MODIFIER = 10
DEFAULT_UNKNOWN_MODIFIER = 10
DEFAULT_HIGH_RISK_THRESHOLD = 70


def default_risk_config() -> dict[str, Any]:
    return {
        "base_score": DEFAULT_BASE_SCORE,
        "keywords": list(DEFAULT_RISK_KEYWORDS),
        "keyword_modifier": DEFAULT_KEYWORD_MODIFIER,
        "mode_modifiers": {
            "allow": 0,
            "approve": DEFAULT_APPROVE_MODIFIER,
            "block": DEFAULT_BLOCK_MODIFIER,
            "unknown": DEFAULT_UNKNOWN_MODIFIER,
        },
        "server_defaults": {},
        "pack_defaults": {},
        "high_risk_threshold": DEFAULT_HIGH_RISK_THRESHOLD,
    }


def risk_score(
    tool: str,
    mode: str | None,
    config: dict[str, Any] | None = None,
    *,
    server: str | None = None,
    policy_pack: str | None = None,
) -> int:
    risk_config = _merged_risk_config(config)
    score = _int_value(risk_config.get("base_score"), DEFAULT_BASE_SCORE)
    if server:
        score += _scoped_modifier(risk_config.get("server_defaults"), server)
    if policy_pack:
        score += _scoped_modifier(risk_config.get("pack_defaults"), policy_pack)

    lowered = tool.lower()
    keywords = risk_config.get("keywords")
    if not isinstance(keywords, list):
        keywords = list(DEFAULT_RISK_KEYWORDS)
    if any(isinstance(keyword, str) and keyword.lower() in lowered for keyword in keywords):
        score += _int_value(risk_config.get("keyword_modifier"), DEFAULT_KEYWORD_MODIFIER)

    mode_key = mode if mode in {"allow", "approve", "block"} else "unknown"
    mode_modifiers = risk_config.get("mode_modifiers")
    if not isinstance(mode_modifiers, dict):
        mode_modifiers = {}
    score += _int_value(mode_modifiers.get(mode_key), default_risk_config()["mode_modifiers"][mode_key])
    return max(0, min(score, 100))


def high_risk_threshold(config: dict[str, Any] | None = None) -> int:
    risk_config = _merged_risk_config(config)
    threshold = _int_value(risk_config.get("high_risk_threshold"), DEFAULT_HIGH_RISK_THRESHOLD)
    return max(0, min(threshold, 100))


def _merged_risk_config(config: dict[str, Any] | None) -> dict[str, Any]:
    merged = default_risk_config()
    configured = config.get("risk") if isinstance(config, dict) else None
    if not isinstance(configured, dict):
        return merged
    for key in ("base_score", "keywords", "keyword_modifier", "high_risk_threshold"):
        if key in configured:
            merged[key] = configured[key]
    for key in ("mode_modifiers", "server_defaults", "pack_defaults"):
        if isinstance(configured.get(key), dict):
            merged[key].update(configured[key])
    return merged


def _scoped_modifier(values: Any, key: str) -> int:
    if not isinstance(values, dict):
        return 0
    return _int_value(values.get(key), 0)


def _int_value(value: Any, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    return default
