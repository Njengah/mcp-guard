# Simulation And Reports

Simulations evaluate proposed MCP tool calls without executing those calls.

## Simulate A Tool Call

```powershell
mcpguard simulate github delete_repository `
  --actor alex@example.com `
  --reason "review destructive access" `
  --request-id CHG-123 `
  --source-repo github.com/acme/service `
  --run-id agent-run-456
```

Metadata is optional but useful for audit evidence.

## Generate A Report

```powershell
mcpguard report
```

Reports include:

- configured servers
- policy coverage
- servers without explicit policies
- high-risk tools
- tools requiring approval
- blocked tools
- high-risk unknown simulations
- recent simulations
- approval activity
- experimental proxy events
- governance evidence counts
- recommendations
