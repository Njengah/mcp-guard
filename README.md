# MCPGuard

Local-first CLI for **governance, approvals, and audit trails** on MCP tool calls.

MCP servers can reach source control, databases, internal docs, browsers, and production APIs. MCPGuard lets a team define allow / block / approve policies, simulate a call, record a human decision, and write a readable report — before putting a live gateway in the path.

**This is not a live MCP proxy.** It does not intercept real tool traffic. The `proxy evaluate` command is an experimental decision spike that reuses the same policy, risk, redaction, and logging code.

## Install

```bash
python -m pip install -e .
mcpguard --help
```

Or without installing:

```bash
PYTHONPATH=src python -m mcpguard --help
```

## Quick start

```bash
mcpguard init
mcpguard policy apply-pack github
mcpguard simulate github delete_repository --actor alex@example.com --reason "review destructive access" --request-id CHG-123
mcpguard approval request github delete_repo --request-id CHG-123 --requester alex@example.com --reason "maintenance window"
mcpguard approval approve CHG-123 --approver security@example.com --reason "approved for maintenance window"
mcpguard report
```

`mcpguard report` writes `.mcpguard/reports/report.md` (policy coverage, unknown high-risk tools, simulations, approvals, recommendations).

## What it does

| Command | Effect |
|---|---|
| `init` | Creates local `.mcpguard/` state |
| `add-server` | Registers an MCP server name |
| `policy add` | Sets a tool to `allow`, `block`, or `approve` |
| `policy apply-pack` | Loads a conservative starter pack (`github`, `filesystem`, `browser`, `database`) |
| `policy export` / `import` | JSON round-trip |
| `inspect` | Prints servers and policies |
| `simulate` | Evaluates a proposed call and appends an audit log |
| `approval request` / `approve` / `reject` | Local human-decision records |
| `proxy evaluate` | Experimental: `forward` vs `hold` (not a live transport) |
| `report` | Markdown governance evidence |

**Decision rules:** explicit `block` → `BLOCK`. Explicit `approve` or missing policy → `REQUIRE_APPROVAL`. Explicit `allow` → `ALLOW`.

## Evidence on disk

```text
.mcpguard/
  config.json
  policies.json
  logs/
    approvals.jsonl
    proxy.jsonl
    simulations.jsonl
  reports/
    report.md
```

`.mcpguard/` is gitignored. Optional `--actor`, `--reason`, `--request-id`, `--source-repo`, `--run-id` are stored on simulations and shown in reports.

## Redaction and risk

Secret-like values are redacted before logs and reports (API keys, tokens, GitHub/OpenAI/Slack/AWS shapes). Tune patterns and risk scoring in `.mcpguard/config.json`. Docs: [redaction and risk](docs/user-guides/redaction-and-risk.md).

Default risk: base `30`, risky-keyword `+40`, block `+20`, approve/unknown `+10`, high-risk threshold `70`.

## Tests

```bash
python scripts/test.py
```

## License

MIT. See [`LICENSE`](./LICENSE).
