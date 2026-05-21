# Start Here

MCPGuard is designed for teams adopting MCP servers with AI coding agents. It gives you a local policy and evidence workflow before you rely on a live proxy.

## Core Concepts

- **Server**: A named MCP server such as `github`, `filesystem`, `database`, or `browser`.
- **Tool**: A capability exposed by a server, such as `read_file` or `delete_repository`.
- **Policy**: A decision mode for a server/tool pair.
- **Simulation**: A local evaluation of what MCPGuard would decide for a proposed tool call.
- **Approval record**: A local record of request, approval, or rejection.
- **Report**: A generated Markdown summary for governance review.

## Recommended Path

1. Install MCPGuard locally.
2. Initialize `.mcpguard/` state in a project.
3. Apply a policy pack or add policies manually.
4. Run simulations for expected and risky tool calls.
5. Record approvals for sensitive actions.
6. Generate a report and review gaps.
7. Treat the proxy command as experimental until a live transport exists.
