# CLI Reference

## `mcpguard init`

Initializes local state in `.mcpguard/`.

## `mcpguard add-server <name>`

Registers an MCP server.

## `mcpguard policy add <server> <tool> --mode allow|approve|block`

Adds or updates a policy for a tool.

## `mcpguard policy apply-pack <name>`

Applies a built-in policy pack.

## `mcpguard policy export [path]`

Prints policies as JSON or writes them to a path.

## `mcpguard policy import <path>`

Validates and replaces local policies from JSON.

## `mcpguard inspect`

Prints configured servers and policies.

## `mcpguard simulate <server> <tool>`

Evaluates a proposed MCP tool call and writes a simulation log entry.

Optional metadata:

- `--actor`
- `--reason`
- `--request-id`
- `--source-repo`
- `--run-id`

## `mcpguard approval request <server> <tool> --request-id <id>`

Records an approval request.

Optional metadata:

- `--requester`
- `--reason`
- `--expires-at`

## `mcpguard approval approve <request-id> --approver <name>`

Records an approval decision.

Optional metadata:

- `--reason`
- `--expires-at`

## `mcpguard approval reject <request-id> --approver <name>`

Records a rejection decision.

Optional metadata:

- `--reason`

## `mcpguard proxy evaluate <server> <tool>`

Experimentally evaluates whether a gateway should forward a tool call.

Optional metadata:

- `--actor`
- `--request-id`
- `--source-repo`
- `--run-id`

## `mcpguard report`

Writes `.mcpguard/reports/report.md`.
