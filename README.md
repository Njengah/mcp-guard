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

## Development

From a fresh checkout, run the test suite without setting `PYTHONPATH`:

```powershell
python scripts/test.py
```

For an editable local install, use:

```powershell
python -m pip install -e .
python -m unittest discover -s tests
```

After the editable install, the CLI is available as:

```powershell
mcpguard --help
```

## Quick Start

```powershell
mcpguard init
mcpguard add-server github
mcpguard policy add github read_file --mode allow
mcpguard policy add github delete_repo --mode block
mcpguard policy add github create_issue --mode approve
mcpguard policy apply-pack github
mcpguard policy export policies.json
mcpguard policy import policies.json
mcpguard inspect
mcpguard simulate github delete_repo --actor alex@example.com --reason "review destructive access" --request-id CHG-123
mcpguard approval request github delete_repo --request-id CHG-123 --requester alex@example.com --reason "maintenance window"
mcpguard approval approve CHG-123 --approver security@example.com --reason "approved for maintenance window"
mcpguard report
```

## Commands

- `mcpguard init` creates local `.mcpguard/` state.
- `mcpguard add-server <name>` registers an MCP server.
- `mcpguard policy add <server> <tool> --mode allow|block|approve` adds or updates a tool policy.
- `mcpguard policy apply-pack <name>` applies a starter policy pack and creates the matching server if needed.
- `mcpguard policy export [path]` prints policies as JSON or writes them to `path`.
- `mcpguard policy import <path>` validates and replaces local policies from a JSON file.
- `mcpguard inspect` prints servers and policies grouped by server.
- `mcpguard simulate <server> <tool>` evaluates a proposed MCP tool call and writes an audit log entry.
- `mcpguard approval request <server> <tool> --request-id <id>` records a local approval request.
- `mcpguard approval approve <request-id> --approver <name>` records an approval decision.
- `mcpguard approval reject <request-id> --approver <name>` records a rejection decision.
- `mcpguard report` writes `.mcpguard/reports/report.md`.

Reports include policy coverage, servers without explicit policies, high-risk unknown simulated tools, recent simulations, approval activity, evidence counts, and recommendations.

Simulation metadata is optional and can be supplied when a simulated decision needs stronger audit context:

```powershell
mcpguard simulate github delete_repo --actor alex@example.com --reason "review destructive access" --request-id CHG-123 --source-repo github.com/acme/service --run-id agent-run-456
```

Supported metadata fields are `--actor`, `--reason`, `--request-id`, `--source-repo`, and `--run-id`. Supplied values are stored in `.mcpguard/logs/simulations.jsonl` and shown in reports.

## Approval Records

Approval records provide a local workflow for documenting human decisions without a hosted service. Requests and decisions are appended to `.mcpguard/logs/approvals.jsonl` and included in governance reports.

```powershell
mcpguard approval request github delete_repo --request-id CHG-123 --requester alex@example.com --reason "maintenance window" --expires-at 2026-06-01T00:00:00Z
mcpguard approval approve CHG-123 --approver security@example.com --reason "approved for maintenance window" --expires-at 2026-06-02T00:00:00Z
mcpguard approval reject CHG-124 --approver security@example.com --reason "missing rollback plan"
```

Approval requests capture the server, tool, requester, reason, expiration, and timestamp. Decisions capture the approver, decision reason, expiration for approvals, and timestamp.

## Redaction

MCPGuard redacts common secret-like values before writing simulation logs and reports. Default patterns cover common API key, token, secret, password, GitHub token, OpenAI key, Slack token, and AWS access key shapes.

Custom project patterns can be added in `.mcpguard/config.json`:

```json
{
  "redaction": {
    "default_patterns": true,
    "patterns": ["internal-[0-9]+"]
  }
}
```

Set `default_patterns` to `false` only when a project intentionally wants to manage every redaction pattern itself.

## Policy Packs

Policy packs provide starter policies for common MCP server categories. They are intentionally conservative: read-only discovery tools are usually allowed, mutating tools require approval, and destructive or arbitrary execution tools are blocked.

Built-in packs:

- `github`: repository, issue, and pull request operations.
- `filesystem`: local file and directory operations.
- `browser`: browser navigation, interaction, capture, downloads, and script execution.
- `database`: schema inspection and database query operations.

Apply a pack with:

```powershell
mcpguard policy apply-pack github
```

Applying a pack creates the matching server when it does not already exist. Reapplying a pack refreshes that pack's starter policies.

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
    approvals.jsonl
    simulations.jsonl
  reports/
    report.md
```

Generated `.mcpguard/` artifacts are ignored by Git by default.

## MVP Limitations

This MVP simulates governance decisions, stores local approval records, and generates audit reports. It is not yet a live MCP proxy and does not intercept real tool calls.
