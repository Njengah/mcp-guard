from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import (
    DuplicateServerError,
    InvalidPolicyFileError,
    InvalidPolicyModeError,
    UnknownPolicyPackError,
    UnknownServerError,
)
from .packs import POLICY_PACKS, PolicyPack, list_policy_packs
from .policy import evaluate_policy, validate_mode
from .redaction import configured_redaction_patterns, redact_text, redact_value
from .storage import (
    SCHEMA_VERSION,
    append_jsonl,
    init_state,
    project_paths,
    read_json,
    read_config,
    read_jsonl_dir,
    read_policies,
    utc_now,
    write_json,
)


def init(root: Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    return init_state(project_paths(root))


def add_server(name: str, root: Path | None = None) -> dict[str, Any]:
    paths = project_paths(root)
    config = read_config(paths)
    policies = read_policies(paths)
    servers = config.setdefault("servers", {})
    if name in servers:
        raise DuplicateServerError(f"Server '{name}' already exists.")

    timestamp = utc_now()
    servers[name] = {
        "name": name,
        "created_at": timestamp,
        "enabled": True,
        "description": None,
    }
    policies.setdefault("servers", {})[name] = {}
    write_json(paths.config_file, config)
    write_json(paths.policies_file, policies)
    return servers[name]


def add_policy(server: str, tool: str, mode: str, root: Path | None = None) -> dict[str, Any]:
    mode = validate_mode(mode)
    paths = project_paths(root)
    config = read_config(paths)
    policies = read_policies(paths)
    if server not in config.get("servers", {}):
        raise UnknownServerError(f"Unknown server '{server}'. Add it with 'mcpguard add-server {server}'.")

    timestamp = utc_now()
    server_policies = policies.setdefault("servers", {}).setdefault(server, {})
    server_policies[tool] = {
        "server": server,
        "tool": tool,
        "mode": mode,
        "updated_at": timestamp,
        "agent_tool": None,
        "mcp_transport": None,
        "risk_score": default_risk_score(tool, mode),
        "approval_actor": None,
        "source_repo": config.get("future_integrations", {}).get("source_repo"),
        "agenttrace_run_id": config.get("future_integrations", {}).get("agenttrace_run_id"),
    }
    write_json(paths.policies_file, policies)
    return server_policies[tool]


def apply_policy_pack(pack_name: str, root: Path | None = None) -> dict[str, Any]:
    pack = _get_policy_pack(pack_name)
    paths = project_paths(root)
    config = read_config(paths)
    policies = read_policies(paths)
    timestamp = utc_now()

    servers = config.setdefault("servers", {})
    if pack.name not in servers:
        servers[pack.name] = {
            "name": pack.name,
            "created_at": timestamp,
            "enabled": True,
            "description": pack.server_description,
        }
    elif not servers[pack.name].get("description"):
        servers[pack.name]["description"] = pack.server_description

    server_policies = policies.setdefault("servers", {}).setdefault(pack.name, {})
    for tool in pack.tools:
        mode = validate_mode(tool.mode)
        server_policies[tool.name] = {
            "server": pack.name,
            "tool": tool.name,
            "mode": mode,
            "updated_at": timestamp,
            "description": tool.description,
            "agent_tool": None,
            "mcp_transport": None,
            "risk_score": default_risk_score(tool.name, mode),
            "approval_actor": None,
            "source_repo": config.get("future_integrations", {}).get("source_repo"),
            "agenttrace_run_id": config.get("future_integrations", {}).get("agenttrace_run_id"),
            "policy_pack": pack.name,
        }

    write_json(paths.config_file, config)
    write_json(paths.policies_file, policies)
    return {
        "pack": pack.name,
        "server": servers[pack.name],
        "policies": server_policies,
    }


def available_policy_packs() -> tuple[str, ...]:
    return list_policy_packs()


def _get_policy_pack(pack_name: str) -> PolicyPack:
    normalized = pack_name.lower()
    pack = POLICY_PACKS.get(normalized)
    if pack is None:
        available = ", ".join(list_policy_packs())
        raise UnknownPolicyPackError(f"Unknown policy pack '{pack_name}'. Available packs: {available}.")
    return pack


def export_policies(root: Path | None = None) -> dict[str, Any]:
    return read_policies(project_paths(root))


def import_policies(source: Path, root: Path | None = None) -> dict[str, Any]:
    imported = read_json(source)
    validate_policy_file(imported)
    paths = project_paths(root)
    read_config(paths)
    write_json(paths.policies_file, imported)
    return imported


def validate_policy_file(policies: dict[str, Any]) -> None:
    schema_version = policies.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise InvalidPolicyFileError(
            f"Unsupported policy schema version '{schema_version}'. Expected '{SCHEMA_VERSION}'."
        )

    servers = policies.get("servers")
    if not isinstance(servers, dict):
        raise InvalidPolicyFileError("Policy file must contain a 'servers' object.")

    for server_name, tool_policies in servers.items():
        if not isinstance(server_name, str) or not server_name:
            raise InvalidPolicyFileError("Policy server names must be non-empty strings.")
        if not isinstance(tool_policies, dict):
            raise InvalidPolicyFileError(f"Policies for server '{server_name}' must be an object.")
        for tool_name, policy in tool_policies.items():
            if not isinstance(tool_name, str) or not tool_name:
                raise InvalidPolicyFileError(
                    f"Policy tool names for server '{server_name}' must be non-empty strings."
                )
            if not isinstance(policy, dict):
                raise InvalidPolicyFileError(
                    f"Policy '{server_name}.{tool_name}' must be an object."
                )
            mode = policy.get("mode")
            if not isinstance(mode, str):
                raise InvalidPolicyFileError(
                    f"Policy '{server_name}.{tool_name}' must include a string mode."
                )
            try:
                policy["mode"] = validate_mode(mode)
            except InvalidPolicyModeError as exc:
                raise InvalidPolicyFileError(
                    f"Policy '{server_name}.{tool_name}' has invalid mode '{mode}'."
                ) from exc
            if policy.get("server", server_name) != server_name:
                raise InvalidPolicyFileError(
                    f"Policy '{server_name}.{tool_name}' has a mismatched server field."
                )
            if policy.get("tool", tool_name) != tool_name:
                raise InvalidPolicyFileError(
                    f"Policy '{server_name}.{tool_name}' has a mismatched tool field."
                )


def inspect_state(root: Path | None = None) -> dict[str, Any]:
    paths = project_paths(root)
    config = read_config(paths)
    policies = read_policies(paths)
    return {
        "config": config,
        "policies": policies,
    }


def simulate(
    server: str,
    tool: str,
    root: Path | None = None,
    *,
    actor: str | None = None,
    request_reason: str | None = None,
    request_id: str | None = None,
    source_repo: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    paths = project_paths(root)
    config = read_config(paths)
    policies = read_policies(paths)
    if server not in config.get("servers", {}):
        raise UnknownServerError(f"Unknown server '{server}'. Add it with 'mcpguard add-server {server}'.")

    policy_entry = policies.get("servers", {}).get(server, {}).get(tool)
    mode = policy_entry.get("mode") if isinstance(policy_entry, dict) else None
    result = evaluate_policy(mode)
    timestamp = utc_now()
    entry = {
        "timestamp": timestamp,
        "server": server,
        "tool": tool,
        "decision": result.decision,
        "reason": result.reason,
        "matched_policy": mode,
        "agent_tool": None,
        "mcp_transport": None,
        "risk_score": default_risk_score(tool, mode),
        "actor": _optional_text(actor),
        "request_reason": _optional_text(request_reason),
        "request_id": _optional_text(request_id),
        "approval_actor": None,
        "source_repo": _optional_text(source_repo)
        or config.get("future_integrations", {}).get("source_repo"),
        "run_id": _optional_text(run_id)
        or config.get("future_integrations", {}).get("agenttrace_run_id"),
    }
    redacted_entry = redact_value(entry, configured_redaction_patterns(config))
    append_jsonl(paths.logs_dir / "simulations.jsonl", redacted_entry)
    return redacted_entry


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def request_approval(
    server: str,
    tool: str,
    *,
    request_id: str,
    requester: str | None = None,
    reason: str | None = None,
    expires_at: str | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    paths = project_paths(root)
    config = read_config(paths)
    if server not in config.get("servers", {}):
        raise UnknownServerError(f"Unknown server '{server}'. Add it with 'mcpguard add-server {server}'.")

    record = {
        "timestamp": utc_now(),
        "type": "request",
        "request_id": request_id,
        "server": server,
        "tool": tool,
        "requester": _optional_text(requester),
        "reason": _optional_text(reason),
        "expires_at": _optional_text(expires_at),
        "decision": "pending",
        "approver": None,
        "decision_reason": None,
    }
    return _append_approval_record(paths, config, record)


def approve_request(
    request_id: str,
    *,
    approver: str,
    reason: str | None = None,
    expires_at: str | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    return _record_approval_decision(
        request_id,
        decision="approved",
        approver=approver,
        reason=reason,
        expires_at=expires_at,
        root=root,
    )


def reject_request(
    request_id: str,
    *,
    approver: str,
    reason: str | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    return _record_approval_decision(
        request_id,
        decision="rejected",
        approver=approver,
        reason=reason,
        expires_at=None,
        root=root,
    )


def _record_approval_decision(
    request_id: str,
    *,
    decision: str,
    approver: str,
    reason: str | None,
    expires_at: str | None,
    root: Path | None,
) -> dict[str, Any]:
    paths = project_paths(root)
    config = read_config(paths)
    record = {
        "timestamp": utc_now(),
        "type": "decision",
        "request_id": request_id,
        "server": None,
        "tool": None,
        "requester": None,
        "reason": None,
        "expires_at": _optional_text(expires_at),
        "decision": decision,
        "approver": _optional_text(approver),
        "decision_reason": _optional_text(reason),
    }
    return _append_approval_record(paths, config, record)


def _append_approval_record(paths: Any, config: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    redacted_record = redact_value(record, configured_redaction_patterns(config))
    append_jsonl(paths.logs_dir / "approvals.jsonl", redacted_record)
    return redacted_record


def build_report(root: Path | None = None) -> Path:
    paths = project_paths(root)
    config = read_config(paths)
    policies = read_policies(paths)
    simulations = read_jsonl_dir(paths.logs_dir, "simulations*.jsonl")
    approvals = read_jsonl_dir(paths.logs_dir, "approvals*.jsonl")
    timestamp = utc_now()

    patterns = configured_redaction_patterns(config)
    redacted_simulations = redact_value(simulations, patterns)
    redacted_approvals = redact_value(approvals, patterns)
    content = redact_text(
        render_report(config, policies, redacted_simulations, redacted_approvals, timestamp),
        patterns,
    )
    paths.reports_dir.mkdir(parents=True, exist_ok=True)
    paths.report_file.write_text(content, encoding="utf-8")
    return paths.report_file


def default_risk_score(tool: str, mode: str | None) -> int:
    lowered = tool.lower()
    risky_words = ("write", "delete", "remove", "publish", "deploy", "execute", "run", "update")
    score = 30
    if any(word in lowered for word in risky_words):
        score += 40
    if mode == "block":
        score += 20
    if mode == "approve" or mode is None:
        score += 10
    return min(score, 100)


def render_report(
    config: dict[str, Any],
    policies: dict[str, Any],
    simulations: list[dict[str, Any]],
    approvals: list[dict[str, Any]],
    timestamp: str,
) -> str:
    servers = config.get("servers", {})
    policy_servers = policies.get("servers", {})
    lines = [
        "# MCPGuard Governance Report",
        "",
        f"Generated: {timestamp}",
        f"Project: {config.get('project_name', 'unknown')}",
        f"Schema version: {config.get('schema_version', 'unknown')}",
        "",
        "## Configured Servers",
        "",
    ]

    if not servers:
        lines.append("- No MCP servers configured.")
    else:
        for name, server in sorted(servers.items()):
            enabled = "enabled" if server.get("enabled", True) else "disabled"
            lines.append(f"- {name}: {enabled}, created {server.get('created_at', 'unknown')}")

    coverage = _policy_coverage(servers, policy_servers)
    lines.extend(
        [
            "",
            "## Policy Coverage Summary",
            "",
            f"- Servers configured: {coverage['server_count']}",
            f"- Servers with explicit policies: {coverage['covered_server_count']}",
            f"- Servers without explicit policies: {coverage['uncovered_server_count']}",
            f"- Policy coverage: {coverage['coverage_percent']}%",
            f"- Allow policies: {coverage['allow_count']}",
            f"- Approval policies: {coverage['approve_count']}",
            f"- Block policies: {coverage['block_count']}",
            f"- Unknown-mode policies: {coverage['unknown_count']}",
            "",
            "## Servers Without Explicit Policies",
            "",
        ]
    )
    if coverage["uncovered_servers"]:
        for server_name in coverage["uncovered_servers"]:
            lines.append(f"- {server_name}: unknown tools default to approval until policies are added.")
    else:
        lines.append("- All configured servers have at least one explicit policy.")

    lines.extend(["", "## Policy Summary", ""])
    total_policies = 0
    blocked: list[str] = []
    approval_policies: list[str] = []
    high_risk: list[str] = []

    for server_name in sorted(servers):
        tool_policies = policy_servers.get(server_name, {})
        if not tool_policies:
            lines.append(f"- {server_name}: no policies configured; unknown tools require approval.")
            continue
        for tool_name, policy in sorted(tool_policies.items()):
            total_policies += 1
            mode = policy.get("mode", "unknown")
            risk = policy.get("risk_score", default_risk_score(tool_name, mode))
            item = f"{server_name}.{tool_name} ({mode}, risk {risk})"
            lines.append(f"- {item}")
            if mode == "block":
                blocked.append(item)
            if mode == "approve":
                approval_policies.append(item)
            if risk >= 70:
                high_risk.append(item)

    lines.extend(["", "## High-Risk Tools", ""])
    lines.extend([f"- {item}" for item in high_risk] or ["- No high-risk tools identified."])

    lines.extend(["", "## Tools Requiring Approval", ""])
    lines.extend([f"- {item}" for item in approval_policies] or ["- No explicit approval policies configured."])

    lines.extend(["", "## Blocked Tools", ""])
    lines.extend([f"- {item}" for item in blocked] or ["- No blocked tools configured."])

    high_risk_unknown = _high_risk_unknown_simulations(simulations)
    lines.extend(["", "## High-Risk Unknown Simulations", ""])
    if high_risk_unknown:
        for entry in high_risk_unknown:
            lines.append(
                "- {server}.{tool} risk {risk}: {decision} at {timestamp}".format(
                    server=entry.get("server", "unknown"),
                    tool=entry.get("tool", "unknown"),
                    risk=entry.get("risk_score", default_risk_score(entry.get("tool", ""), None)),
                    decision=entry.get("decision", "UNKNOWN"),
                    timestamp=entry.get("timestamp", "unknown"),
                )
            )
    else:
        lines.append("- No high-risk unknown simulated tools identified.")

    lines.extend(["", "## Recent Simulations", ""])
    recent = sorted(simulations, key=lambda entry: entry.get("timestamp", ""))[-10:]
    if recent:
        for entry in recent:
            metadata = _format_simulation_metadata(entry)
            suffix = f" ({metadata})" if metadata else ""
            lines.append(
                "- {timestamp} {decision}: {server}.{tool} - {reason}{suffix}".format(
                    timestamp=entry.get("timestamp", "unknown"),
                    decision=entry.get("decision", "UNKNOWN"),
                    server=entry.get("server", "unknown"),
                    tool=entry.get("tool", "unknown"),
                    reason=entry.get("reason", "no reason recorded"),
                    suffix=suffix,
                )
            )
    else:
        lines.append("- No simulations recorded.")

    lines.extend(["", "## Approval Activity", ""])
    recent_approvals = sorted(approvals, key=lambda entry: entry.get("timestamp", ""))[-10:]
    if recent_approvals:
        for entry in recent_approvals:
            lines.append(f"- {_format_approval_record(entry)}")
    else:
        lines.append("- No approval activity recorded.")

    lines.extend(
        [
            "",
            "## Governance Evidence",
            "",
            f"- Configured servers: {len(servers)}",
            f"- Servers with policy coverage: {coverage['covered_server_count']}",
            f"- Servers without policy coverage: {coverage['uncovered_server_count']}",
            f"- Configured tool policies: {total_policies}",
            f"- Allow policies: {coverage['allow_count']}",
            f"- Approval policies: {coverage['approve_count']}",
            f"- Block policies: {coverage['block_count']}",
            f"- Simulated decisions: {len(simulations)}",
            f"- High-risk unknown simulations: {len(high_risk_unknown)}",
            f"- Approval records: {len(approvals)}",
            f"- Report timestamp: {timestamp}",
            "",
            "## Recommendations",
            "",
        ]
    )
    if not servers:
        lines.append("- Add MCP servers before relying on governance reports.")
    if any(not policy_servers.get(server_name) for server_name in servers):
        uncovered = ", ".join(coverage["uncovered_servers"])
        lines.append(f"- Add explicit policies for servers with no policy coverage: {uncovered}.")
    if high_risk_unknown:
        lines.append("- Convert high-risk unknown simulated tools into explicit allow, approve, or block policies.")
    if coverage["unknown_count"]:
        lines.append("- Review policies with unknown modes before sharing this report.")
    if approval_policies:
        lines.append("- Define approval actors and response procedures for approval-required tools.")
    if blocked:
        lines.append("- Review blocked tools periodically to keep security controls intentional.")
    if not simulations:
        lines.append("- Run simulations for expected MCP tool calls to create audit evidence.")
    if approvals:
        lines.append("- Review approval activity for stale pending requests and expired approvals.")
    if servers and total_policies and simulations:
        lines.append("- Export this report into security reviews after each material policy change.")

    lines.append("")
    return "\n".join(lines)


def _format_simulation_metadata(entry: dict[str, Any]) -> str:
    labels = (
        ("actor", "actor"),
        ("request_reason", "reason"),
        ("request_id", "request"),
        ("source_repo", "repo"),
        ("run_id", "run"),
    )
    parts = []
    for key, label in labels:
        value = entry.get(key)
        if value:
            parts.append(f"{label}: {value}")
    return "; ".join(parts)


def _policy_coverage(
    servers: dict[str, Any],
    policy_servers: dict[str, Any],
) -> dict[str, Any]:
    uncovered_servers = [
        server_name
        for server_name in sorted(servers)
        if not policy_servers.get(server_name)
    ]
    mode_counts = {
        "allow_count": 0,
        "approve_count": 0,
        "block_count": 0,
        "unknown_count": 0,
    }
    for tool_policies in policy_servers.values():
        if not isinstance(tool_policies, dict):
            continue
        for policy in tool_policies.values():
            mode = policy.get("mode") if isinstance(policy, dict) else None
            key = f"{mode}_count"
            if key in mode_counts:
                mode_counts[key] += 1
            else:
                mode_counts["unknown_count"] += 1

    server_count = len(servers)
    covered_server_count = server_count - len(uncovered_servers)
    coverage_percent = round((covered_server_count / server_count) * 100) if server_count else 0
    return {
        "server_count": server_count,
        "covered_server_count": covered_server_count,
        "uncovered_server_count": len(uncovered_servers),
        "uncovered_servers": uncovered_servers,
        "coverage_percent": coverage_percent,
        **mode_counts,
    }


def _high_risk_unknown_simulations(simulations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    high_risk: list[dict[str, Any]] = []
    for entry in simulations:
        if entry.get("matched_policy") is not None:
            continue
        tool = entry.get("tool", "")
        risk = entry.get("risk_score", default_risk_score(tool, None))
        if risk >= 70:
            high_risk.append(entry)
    return sorted(high_risk, key=lambda entry: entry.get("timestamp", ""))[-10:]


def _format_approval_record(entry: dict[str, Any]) -> str:
    timestamp = entry.get("timestamp", "unknown")
    request_id = entry.get("request_id", "unknown")
    decision = entry.get("decision", "unknown")
    if entry.get("type") == "request":
        target = f"{entry.get('server', 'unknown')}.{entry.get('tool', 'unknown')}"
        parts = [f"{timestamp} request {request_id}: {target} ({decision})"]
        if entry.get("requester"):
            parts.append(f"requester: {entry['requester']}")
        if entry.get("reason"):
            parts.append(f"reason: {entry['reason']}")
        if entry.get("expires_at"):
            parts.append(f"expires: {entry['expires_at']}")
        return "; ".join(parts)

    parts = [f"{timestamp} decision {request_id}: {decision}"]
    if entry.get("approver"):
        parts.append(f"approver: {entry['approver']}")
    if entry.get("decision_reason"):
        parts.append(f"reason: {entry['decision_reason']}")
    if entry.get("expires_at"):
        parts.append(f"expires: {entry['expires_at']}")
    return "; ".join(parts)
