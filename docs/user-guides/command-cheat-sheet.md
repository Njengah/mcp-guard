# Command Cheat Sheet

## Project Setup

```powershell
mcpguard init
mcpguard inspect
```

## Servers

```powershell
mcpguard add-server github
```

## Policies

```powershell
mcpguard policy add github read_file --mode allow
mcpguard policy add github create_issue --mode approve
mcpguard policy add github delete_repository --mode block
mcpguard policy apply-pack github
mcpguard policy export policies.json
mcpguard policy import policies.json
```

## Simulations

```powershell
mcpguard simulate github delete_repository --actor alex@example.com --request-id CHG-123
```

## Approvals

```powershell
mcpguard approval request github delete_repository --request-id CHG-123
mcpguard approval approve CHG-123 --approver security@example.com
mcpguard approval reject CHG-124 --approver security@example.com
```

## Experimental Proxy

```powershell
mcpguard proxy evaluate github read_file
```

## Reports

```powershell
mcpguard report
```
