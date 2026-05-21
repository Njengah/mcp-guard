# Approval Workflow

Approval records document human decisions locally. They do not require a hosted service.

## Request Approval

```powershell
mcpguard approval request github delete_repository `
  --request-id CHG-123 `
  --requester alex@example.com `
  --reason "maintenance window" `
  --expires-at 2026-06-01T00:00:00Z
```

## Approve

```powershell
mcpguard approval approve CHG-123 `
  --approver security@example.com `
  --reason "approved for maintenance window" `
  --expires-at 2026-06-02T00:00:00Z
```

## Reject

```powershell
mcpguard approval reject CHG-124 `
  --approver security@example.com `
  --reason "missing rollback plan"
```

Approval records are written to `.mcpguard/logs/approvals.jsonl` and included in reports.
