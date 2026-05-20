# Product Definition

## Product Thesis

MCPGuard gives teams a local-first governance layer for MCP tool calls, helping them define allowed, blocked, and approval-required tools before agents interact with sensitive systems.

## User Persona

The initial user is a security-conscious engineering lead or platform engineer adopting AI coding agents with MCP servers. They need clear controls, fast local workflows, and evidence they can bring to security review.

## Enterprise Problem

MCP servers may expose databases, internal documents, GitHub operations, browser automation, publishing systems, and production APIs. Without a control layer, teams cannot easily prove which tools were available, what policies existed, or how risky tool calls would be handled.

## MVP Scope

- Initialize local MCPGuard state.
- Register MCP servers.
- Add allow, block, and approval-required policies for tools.
- Inspect configured governance state.
- Simulate policy decisions for proposed MCP tool calls.
- Log simulations.
- Generate a Markdown governance report.

## Non-Goals

- Live MCP traffic interception.
- Distributed team policy synchronization.
- Built-in identity provider integration.
- Real approval queues.
- Full sensitive-data redaction.
- Hosted dashboard.

## Future Expansion Paths

- Live MCP proxy or gateway mode.
- AgentTrace integration.
- Policy packs for common server categories.
- Secret and PII redaction.
- Web dashboard.
- Team approval workflows and signed audit trails.

