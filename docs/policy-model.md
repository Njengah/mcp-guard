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
- policy summary
- high-risk tools
- tools requiring approval
- blocked tools
- recent simulations
- governance evidence counts
- recommendations

## Governance Evidence

MCPGuard treats the following as governance evidence:

- configured servers
- configured tool policies
- simulated decisions
- generated report timestamp

