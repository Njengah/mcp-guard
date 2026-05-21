# Policy Model

## Server Model

A server is stored in `.mcpguard/config.json` under `servers` with:

- `name`
- `created_at`
- `enabled`
- `description`

## Tool Policy Model

Tool policies are stored in `.mcpguard/policies.json` by server and tool. Each policy contains:

- `server`
- `tool`
- `mode`
- `updated_at`
- `agent_tool`
- `mcp_transport`
- `risk_score`
- `approval_actor`
- `source_repo`
- `agenttrace_run_id`

## Modes

- `allow`: the proposed tool call is allowed.
- `block`: the proposed tool call is blocked.
- `approve`: the proposed tool call requires approval.

If no policy exists for a tool, MCPGuard returns `REQUIRE_APPROVAL` by default.

## Report Fields

Reports include:

- configured servers
- policy coverage summary
- servers without explicit policies
- policy summary
- high-risk tools
- tools requiring approval
- blocked tools
- high-risk unknown simulations
- recent simulations
- approval activity
- experimental proxy events
- governance evidence counts
- recommendations

## Governance Evidence

MCPGuard treats the following as governance evidence:

- configured servers
- configured tool policies
- simulated decisions
- approval records
- experimental proxy events
- generated report timestamp
