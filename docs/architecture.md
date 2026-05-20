# Architecture

MCPGuard is a dependency-light Python CLI. The MVP keeps all state local to the current project in `.mcpguard/` and separates command routing, policy evaluation, and persistence.

## Modules

- `mcpguard.cli`: argparse command routing and terminal output.
- `mcpguard.core`: command behavior and report generation.
- `mcpguard.policy`: allow, block, and approval decision logic.
- `mcpguard.storage`: JSON and JSONL persistence helpers.
- `mcpguard.errors`: expected user-facing error types.

## Data Flow

1. `mcpguard init` creates local state files and directories.
2. `add-server` updates `config.json` and prepares an empty server policy map.
3. `policy add` writes tool policy entries into `policies.json`.
4. `simulate` evaluates the tool against the policy map and appends a JSONL audit entry.
5. `report` reads config, policies, and logs, then writes a Markdown governance report.

## Design Constraints

- Local-first storage.
- No runtime package dependencies.
- Idempotent initialization.
- Human-readable JSON and Markdown outputs.
- Future-ready fields for live gateway integrations.

