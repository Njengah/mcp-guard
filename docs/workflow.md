# Workflow

This example shows a local MCP governance workflow for a GitHub MCP server.

```powershell
mcpguard init
mcpguard add-server github
mcpguard policy add github list_repos --mode allow
mcpguard policy add github create_issue --mode approve
mcpguard policy add github delete_repo --mode block
mcpguard inspect
mcpguard simulate github list_repos
mcpguard simulate github create_issue
mcpguard simulate github delete_repo
mcpguard simulate github unknown_write_tool
mcpguard report
```

The generated report is written to `.mcpguard/reports/report.md` and can be pasted into a security or governance review.

