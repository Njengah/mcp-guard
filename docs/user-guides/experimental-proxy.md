# Experimental Proxy

`mcpguard proxy evaluate` is an experimental gateway decision path.

It does not run a live MCP transport and does not forward real traffic. It evaluates the configured policy for a proposed server/tool call, returns a gateway action, and writes evidence to `.mcpguard/logs/proxy.jsonl`.

## Evaluate A Call

```powershell
mcpguard proxy evaluate github read_file --actor agent --request-id REQ-1 --run-id agent-run-456
```

## Actions

- `forward`: explicit `allow` policy matched.
- `hold`: `block`, `approve`, or missing policy decision.

`hold` exits with code `2` so scripts can distinguish it from a forwarded call.

## Limitations

- No MCP transport is started.
- No real tool call is executed.
- No approval queue is enforced.
- Proxy events are evidence for review, not runtime enforcement.
