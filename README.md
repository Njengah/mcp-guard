# MCPGuard

MCPGuard is a local-first CLI for governance, approvals, and audit trails for MCP tool calls.

MCP servers can expose sensitive systems such as source control, databases, internal documents, browser automation, publishing workflows, and production APIs. MCPGuard gives teams a lightweight way to define local tool policies, simulate decisions, and generate readable governance evidence before introducing a live gateway.

## Install

From this repository:

```powershell
python -m pip install -e .
```

You can also run it without installing by setting `PYTHONPATH=src` and using:

```powershell
python -m mcpguard --help
```

## Quick Start

```powershell
mcpguard init
mcpguard add-server github
mcpguard policy add github read_file --mode allow
mcpguard policy add github delete_repo --mode block
mcpguard policy add github create_issue --mode approve
mcpguard inspect
mcpguard simulate github delete_repo
mcpguard report
```

## Commands

- `mcpguard init` creates local `.mcpguard/` state.
- `mcpguard add-server <name>` registers an MCP server.
- `mcpguard policy add <server> <tool> --mode allow|block|approve` adds or updates a tool policy.
- `mcpguard inspect` prints servers and policies grouped by server.
- `mcpguard simulate <server> <tool>` evaluates a proposed MCP tool call and writes an audit log entry.
- `mcpguard report` writes `.mcpguard/reports/report.md`.

## Decision Rules

- Explicit `block` policy: `BLOCK`
- Explicit `approve` policy: `REQUIRE_APPROVAL`
- Explicit `allow` policy: `ALLOW`
- Missing policy: `REQUIRE_APPROVAL`

## Output Structure

MCPGuard stores local state in:

```text
.mcpguard/
  config.json
  policies.json
  logs/
  reports/
    report.md
```

Generated `.mcpguard/` artifacts are ignored by Git by default.

## MVP Limitations

This MVP simulates governance decisions and generates audit reports. It is not yet a live MCP proxy, does not intercept real tool calls, and does not implement human approval workflows or secret redaction.

