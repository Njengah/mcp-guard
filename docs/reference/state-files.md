# State Files

MCPGuard stores project-local state in `.mcpguard/`.

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

## `config.json`

Contains project metadata, registered servers, future integration fields, redaction config, and risk config.

## `policies.json`

Contains server/tool policy entries grouped by server.

## `logs/simulations.jsonl`

Append-only simulation evidence.

## `logs/approvals.jsonl`

Append-only local approval activity.

## `logs/proxy.jsonl`

Append-only experimental proxy decision events.

## `reports/report.md`

Generated governance report.
