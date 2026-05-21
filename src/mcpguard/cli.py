from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .core import (
    add_policy,
    add_server,
    approve_request,
    apply_policy_pack,
    available_policy_packs,
    build_report,
    export_policies,
    import_policies,
    init,
    inspect_state,
    reject_request,
    request_approval,
    simulate,
)
from .errors import MCPGuardError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcpguard",
        description="Local-first governance, approvals, and audit trails for MCP tool calls.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize MCPGuard state in this project.")
    init_parser.set_defaults(func=cmd_init)

    add_server_parser = subparsers.add_parser("add-server", help="Register an MCP server.")
    add_server_parser.add_argument("name", help="Server name to register.")
    add_server_parser.set_defaults(func=cmd_add_server)

    policy_parser = subparsers.add_parser("policy", help="Manage MCP tool policies.")
    policy_subparsers = policy_parser.add_subparsers(dest="policy_command", required=True)
    policy_add = policy_subparsers.add_parser("add", help="Add or update a tool policy.")
    policy_add.add_argument("server", help="Configured MCP server name.")
    policy_add.add_argument("tool", help="Tool name exposed by the server.")
    policy_add.add_argument(
        "--mode",
        required=True,
        choices=["allow", "block", "approve"],
        help="Policy behavior for this tool.",
    )
    policy_add.set_defaults(func=cmd_policy_add)

    policy_apply_pack = policy_subparsers.add_parser(
        "apply-pack",
        help="Apply a built-in starter policy pack.",
    )
    policy_apply_pack.add_argument(
        "name",
        choices=available_policy_packs(),
        help="Built-in policy pack name.",
    )
    policy_apply_pack.set_defaults(func=cmd_policy_apply_pack)

    policy_export = policy_subparsers.add_parser("export", help="Export tool policies as JSON.")
    policy_export.add_argument("path", nargs="?", help="Optional output file path.")
    policy_export.set_defaults(func=cmd_policy_export)

    policy_import = policy_subparsers.add_parser("import", help="Import tool policies from JSON.")
    policy_import.add_argument("path", help="Policy JSON file to import.")
    policy_import.set_defaults(func=cmd_policy_import)

    inspect_parser = subparsers.add_parser("inspect", help="Print configured servers and policies.")
    inspect_parser.set_defaults(func=cmd_inspect)

    simulate_parser = subparsers.add_parser("simulate", help="Evaluate a proposed MCP tool call.")
    simulate_parser.add_argument("server", help="Configured MCP server name.")
    simulate_parser.add_argument("tool", help="Tool name to evaluate.")
    simulate_parser.add_argument("--actor", help="Person, service, or agent requesting the tool call.")
    simulate_parser.add_argument("--reason", help="Human-readable reason for the simulated request.")
    simulate_parser.add_argument("--request-id", help="External request or ticket identifier.")
    simulate_parser.add_argument("--source-repo", help="Repository associated with the simulated request.")
    simulate_parser.add_argument("--run-id", help="Automation, CI, or agent run identifier.")
    simulate_parser.set_defaults(func=cmd_simulate)

    approval_parser = subparsers.add_parser("approval", help="Manage local approval records.")
    approval_subparsers = approval_parser.add_subparsers(dest="approval_command", required=True)
    approval_request = approval_subparsers.add_parser("request", help="Create an approval request.")
    approval_request.add_argument("server", help="Configured MCP server name.")
    approval_request.add_argument("tool", help="Tool name requiring approval.")
    approval_request.add_argument("--request-id", required=True, help="Request, ticket, or change ID.")
    approval_request.add_argument("--requester", help="Person, service, or agent requesting approval.")
    approval_request.add_argument("--reason", help="Reason the approval is needed.")
    approval_request.add_argument("--expires-at", help="Optional approval request expiration timestamp.")
    approval_request.set_defaults(func=cmd_approval_request)

    approval_approve = approval_subparsers.add_parser("approve", help="Record an approval decision.")
    approval_approve.add_argument("request_id", help="Request ID to approve.")
    approval_approve.add_argument("--approver", required=True, help="Person or service approving the request.")
    approval_approve.add_argument("--reason", help="Decision reason.")
    approval_approve.add_argument("--expires-at", help="Optional approval expiration timestamp.")
    approval_approve.set_defaults(func=cmd_approval_approve)

    approval_reject = approval_subparsers.add_parser("reject", help="Record a rejection decision.")
    approval_reject.add_argument("request_id", help="Request ID to reject.")
    approval_reject.add_argument("--approver", required=True, help="Person or service rejecting the request.")
    approval_reject.add_argument("--reason", help="Decision reason.")
    approval_reject.set_defaults(func=cmd_approval_reject)

    report_parser = subparsers.add_parser("report", help="Generate a governance report.")
    report_parser.set_defaults(func=cmd_report)

    return parser


def cmd_init(_args: argparse.Namespace) -> int:
    init()
    print("Initialized MCPGuard state in .mcpguard/")
    return 0


def cmd_add_server(args: argparse.Namespace) -> int:
    server = add_server(args.name)
    print(f"Added server: {server['name']}")
    return 0


def cmd_policy_add(args: argparse.Namespace) -> int:
    policy = add_policy(args.server, args.tool, args.mode)
    print(f"Policy saved: {policy['server']}.{policy['tool']} -> {policy['mode']}")
    return 0


def cmd_policy_apply_pack(args: argparse.Namespace) -> int:
    result = apply_policy_pack(args.name)
    policy_count = len(result["policies"])
    print(f"Policy pack applied: {result['pack']} ({policy_count} policies)")
    return 0


def cmd_policy_export(args: argparse.Namespace) -> int:
    policies = export_policies()
    content = json.dumps(policies, indent=2, sort_keys=True) + "\n"
    if args.path:
        path = Path(args.path)
        path.write_text(content, encoding="utf-8")
        print(f"Policies exported: {path.resolve()}")
    else:
        print(content, end="")
    return 0


def cmd_policy_import(args: argparse.Namespace) -> int:
    policies = import_policies(Path(args.path))
    policy_count = sum(len(tools) for tools in policies.get("servers", {}).values())
    print(f"Policies imported: {policy_count}")
    return 0


def cmd_inspect(_args: argparse.Namespace) -> int:
    state = inspect_state()
    config = state["config"]
    policies = state["policies"]
    servers = config.get("servers", {})
    policy_servers = policies.get("servers", {})

    print(f"MCPGuard project: {config.get('project_name', 'unknown')}")
    print(f"Schema version: {config.get('schema_version', 'unknown')}")
    print("")
    print("Servers:")
    if not servers:
        print("  (none configured)")
    for name, server in sorted(servers.items()):
        enabled = "enabled" if server.get("enabled", True) else "disabled"
        print(f"  - {name} [{enabled}]")
        tool_policies = policy_servers.get(name, {})
        if not tool_policies:
            print("    ! no policies configured; unknown tools require approval")
            continue
        for tool, policy in sorted(tool_policies.items()):
            mode = policy.get("mode", "unknown")
            marker = _mode_marker(mode)
            print(f"    {marker} {tool}: {mode}")
    return 0


def cmd_simulate(args: argparse.Namespace) -> int:
    result = simulate(
        args.server,
        args.tool,
        actor=args.actor,
        request_reason=args.reason,
        request_id=args.request_id,
        source_repo=args.source_repo,
        run_id=args.run_id,
    )
    print(f"Decision: {result['decision']}")
    print(f"Reason: {result['reason']}")
    print(f"Server: {result['server']}")
    print(f"Tool: {result['tool']}")
    print(f"Timestamp: {result['timestamp']}")
    if result.get("actor"):
        print(f"Actor: {result['actor']}")
    if result.get("request_reason"):
        print(f"Request reason: {result['request_reason']}")
    if result.get("request_id"):
        print(f"Request ID: {result['request_id']}")
    if result.get("source_repo"):
        print(f"Source repo: {result['source_repo']}")
    if result.get("run_id"):
        print(f"Run ID: {result['run_id']}")
    return 0


def cmd_approval_request(args: argparse.Namespace) -> int:
    record = request_approval(
        args.server,
        args.tool,
        request_id=args.request_id,
        requester=args.requester,
        reason=args.reason,
        expires_at=args.expires_at,
    )
    print(f"Approval requested: {record['request_id']} for {record['server']}.{record['tool']}")
    return 0


def cmd_approval_approve(args: argparse.Namespace) -> int:
    record = approve_request(
        args.request_id,
        approver=args.approver,
        reason=args.reason,
        expires_at=args.expires_at,
    )
    print(f"Approval recorded: {record['request_id']} -> approved")
    return 0


def cmd_approval_reject(args: argparse.Namespace) -> int:
    record = reject_request(
        args.request_id,
        approver=args.approver,
        reason=args.reason,
    )
    print(f"Approval recorded: {record['request_id']} -> rejected")
    return 0


def cmd_report(_args: argparse.Namespace) -> int:
    report_path = build_report()
    print(f"Report written: {Path(report_path).resolve()}")
    return 0


def _mode_marker(mode: str) -> str:
    if mode == "block":
        return "[BLOCK]"
    if mode == "approve":
        return "[APPROVE]"
    if mode == "allow":
        return "[ALLOW]"
    return "[UNKNOWN]"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except MCPGuardError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
