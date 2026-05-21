# Policy Packs

Policy packs reduce blank-page setup by applying starter policies for common MCP server categories.

## Built-In Packs

- `github`: repository, issue, and pull request operations.
- `filesystem`: local file and directory operations.
- `browser`: browser navigation, interaction, capture, downloads, and script execution.
- `database`: schema inspection and database query operations.

## Apply A Pack

```powershell
mcpguard init
mcpguard policy apply-pack github
```

Applying a pack creates the matching server if it does not already exist. Reapplying a pack refreshes that pack's starter policies.

## Review Pack Output

```powershell
mcpguard inspect
mcpguard policy export policies.json
```

Review exported policies before sharing them across projects.
