# Your First Governance Flow

This flow creates a GitHub server policy set, simulates decisions, and generates evidence.

```powershell
mcpguard init
mcpguard add-server github
mcpguard policy add github get_file_contents --mode allow
mcpguard policy add github create_pull_request --mode approve
mcpguard policy add github delete_repository --mode block
mcpguard inspect
```

Simulate common calls:

```powershell
mcpguard simulate github get_file_contents --actor alex@example.com --request-id REQ-1
mcpguard simulate github create_pull_request --actor alex@example.com --request-id REQ-2
mcpguard simulate github delete_repository --actor alex@example.com --request-id REQ-3
```

Generate the report:

```powershell
mcpguard report
```

Open `.mcpguard/reports/report.md` to review policy coverage, high-risk tools, recent simulations, approval activity, proxy events, evidence counts, and recommendations.
