# Troubleshooting

## `Run 'mcpguard init' first`

Run:

```powershell
mcpguard init
```

MCPGuard commands expect `.mcpguard/config.json` and `.mcpguard/policies.json` in the current project.

## `Unknown server`

Add the server before policy, simulation, approval, or proxy commands:

```powershell
mcpguard add-server github
```

Or apply a pack:

```powershell
mcpguard policy apply-pack github
```

## Proxy command exits `2`

Exit code `2` means the experimental proxy decision was `hold`. The policy was blocked, required approval, or was missing.

## Report does not show expected activity

Check that the relevant log file exists under `.mcpguard/logs/`:

- `simulations.jsonl`
- `approvals.jsonl`
- `proxy.jsonl`

Then rerun:

```powershell
mcpguard report
```
