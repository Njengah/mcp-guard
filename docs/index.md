# MCPGuard

MCPGuard is a local-first CLI for governing MCP tool calls before agents reach sensitive systems.

It helps teams define policy, simulate decisions, record local approvals, redact sensitive evidence, tune risk scoring, and generate reviewable governance reports.

## What MCPGuard Helps With

- Register MCP servers that expose systems such as GitHub, databases, file systems, and browser automation.
- Define tool policies as `allow`, `approve`, or `block`.
- Apply starter policy packs for common MCP server categories.
- Simulate proposed MCP tool calls and create audit evidence.
- Record local approval requests and decisions.
- Redact secret-like values before writing logs and reports.
- Tune risk scoring for your environment.
- Generate Markdown governance reports for security review.
- Experiment with a proxy decision path before adopting a live gateway.

## Quick Start

```powershell
python -m pip install -e .
mcpguard init
mcpguard policy apply-pack github
mcpguard inspect
mcpguard simulate github delete_repository --actor alex@example.com --request-id CHG-123
mcpguard report
```

The report is written to `.mcpguard/reports/report.md`.

## Documentation Map

- Start with [Install And Run](user-guides/install-and-run.md).
- Try [Your First Governance Flow](user-guides/first-governance-flow.md).
- Use [CLI Reference](reference/cli.md) for command details.
- Review [State Files](reference/state-files.md) before committing evidence or sharing reports.
- Read [Experimental Proxy](user-guides/experimental-proxy.md) before using the proxy spike.
