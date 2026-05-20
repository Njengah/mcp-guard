from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import DuplicateServerError, UnknownServerError
from .policy import evaluate_policy, validate_mode
from .storage import (
    append_jsonl,
    init_state,
    project_paths,
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


def inspect_state(root: Path | None = None) -> dict[str, Any]:
    paths = project_paths(root)
    config = read_config(paths)
    policies = read_policies(paths)
    return {
        "config": config,
        "policies": policies,
    }


def simulate(server: str, tool: str, root: Path | None = None) -> dict[str, Any]:
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
        "approval_actor": None,
        "source_repo": config.get("future_integrations", {}).get("source_repo"),
        "agenttrace_run_id": config.get("future_integrations", {}).get("agenttrace_run_id"),
    }
    append_jsonl(paths.logs_dir / "simulations.jsonl", entry)
    return entry


def build_report(root: Path | None = None) -> Path:
    paths = project_paths(root)
    config = read_config(paths)
    policies = read_policies(paths)
    simulations = read_jsonl_dir(paths.logs_dir)
    timestamp = utc_now()

    content = render_report(config, policies, simulations, timestamp)
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

    lines.extend(["", "## Policy Summary", ""])
    total_policies = 0
    blocked: list[str] = []
    approvals: list[str] = []
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
                approvals.append(item)
            if risk >= 70:
                high_risk.append(item)

    lines.extend(["", "## High-Risk Tools", ""])
    lines.extend([f"- {item}" for item in high_risk] or ["- No high-risk tools identified."])

    lines.extend(["", "## Tools Requiring Approval", ""])
    lines.extend([f"- {item}" for item in approvals] or ["- No explicit approval policies configured."])

    lines.extend(["", "## Blocked Tools", ""])
    lines.extend([f"- {item}" for item in blocked] or ["- No blocked tools configured."])

    lines.extend(["", "## Recent Simulations", ""])
    recent = sorted(simulations, key=lambda entry: entry.get("timestamp", ""))[-10:]
    if recent:
        for entry in recent:
            lines.append(
                "- {timestamp} {decision}: {server}.{tool} - {reason}".format(
                    timestamp=entry.get("timestamp", "unknown"),
                    decision=entry.get("decision", "UNKNOWN"),
                    server=entry.get("server", "unknown"),
                    tool=entry.get("tool", "unknown"),
                    reason=entry.get("reason", "no reason recorded"),
                )
            )
    else:
        lines.append("- No simulations recorded.")

    lines.extend(
        [
            "",
            "## Governance Evidence",
            "",
            f"- Configured servers: {len(servers)}",
            f"- Configured tool policies: {total_policies}",
            f"- Simulated decisions: {len(simulations)}",
            f"- Report timestamp: {timestamp}",
            "",
            "## Recommendations",
            "",
        ]
    )
    if not servers:
        lines.append("- Add MCP servers before relying on governance reports.")
    if any(not policy_servers.get(server_name) for server_name in servers):
        lines.append("- Add explicit policies for servers with no policy coverage.")
    if approvals:
        lines.append("- Define approval actors and response procedures for approval-required tools.")
    if blocked:
        lines.append("- Review blocked tools periodically to keep security controls intentional.")
    if not simulations:
        lines.append("- Run simulations for expected MCP tool calls to create audit evidence.")
    if servers and total_policies and simulations:
        lines.append("- Export this report into security reviews after each material policy change.")

    lines.append("")
    return "\n".join(lines)

