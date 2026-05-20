from __future__ import annotations

from dataclasses import dataclass

from .errors import InvalidPolicyModeError

VALID_MODES = {"allow", "block", "approve"}


@dataclass(frozen=True)
class Decision:
    decision: str
    reason: str


def validate_mode(mode: str) -> str:
    normalized = mode.lower()
    if normalized not in VALID_MODES:
        allowed = ", ".join(sorted(VALID_MODES))
        raise InvalidPolicyModeError(f"Invalid policy mode '{mode}'. Expected one of: {allowed}.")
    return normalized


def evaluate_policy(mode: str | None) -> Decision:
    if mode == "block":
        return Decision("BLOCK", "Explicit block policy matched.")
    if mode == "approve":
        return Decision("REQUIRE_APPROVAL", "Explicit approval policy matched.")
    if mode == "allow":
        return Decision("ALLOW", "Explicit allow policy matched.")
    return Decision("REQUIRE_APPROVAL", "No explicit policy found; defaulting to approval.")

