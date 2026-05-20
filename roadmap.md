# MCPGuard Roadmap

This roadmap tracks practical, reviewable improvements for MCPGuard. Each item should be built on a standalone feature branch and merged through a pull request.

## Working Principles

- Keep each branch focused on one practical improvement.
- Prefer small PRs with tests and README updates.
- Preserve the local-first, dependency-light design unless a feature clearly justifies a dependency.
- Treat reports, logs, and policies as governance evidence that security-conscious teams can review.

## Proposed Feature Sequence

### 1. Developer Test Ergonomics

Branch: `feature/dev-test-ergonomics`

Goal: Make the project easy to verify from a fresh checkout.

Scope:
- Add first-class test instructions that do not rely on remembering `PYTHONPATH=src`.
- Add a simple test runner path, such as editable install docs, unittest config, or a lightweight script.
- Update README with the standard local development workflow.
- Verify the existing test suite still passes.

Review value:
- Establishes a reliable baseline for every later PR.

### 2. Policy Import and Export

Branch: `feature/policy-import-export`

Goal: Let teams move policy state between projects or review policy snapshots outside `.mcpguard/`.

Scope:
- Add `mcpguard policy export`.
- Add `mcpguard policy import`.
- Validate imported policy shape before writing state.
- Add tests for export, import, invalid JSON, and unknown schema handling.

Review value:
- Makes MCPGuard more practical for repeatable team setup.

### 3. Policy Packs

Branch: `feature/policy-packs`

Goal: Provide starter policies for common MCP server categories.

Scope:
- Add built-in packs for GitHub, filesystem, browser automation, and database tools.
- Add a command such as `mcpguard policy apply-pack github`.
- Keep packs human-readable and documented.
- Add tests showing generated policies.

Review value:
- Reduces blank-page setup friction.

### 4. Simulation Metadata

Branch: `feature/simulation-metadata`

Goal: Make simulated decisions closer to real audit records.

Scope:
- Extend `simulate` with optional fields such as actor, reason, request ID, source repo, and run ID.
- Persist metadata in JSONL logs.
- Include useful metadata in reports.
- Keep all fields optional for the current quick-start workflow.

Review value:
- Turns simulation logs into stronger governance evidence.

### 5. Redaction Rules

Branch: `feature/redaction-rules`

Goal: Reduce the chance of leaking secrets or sensitive values into logs and reports.

Scope:
- Add configurable redaction patterns.
- Apply redaction before writing audit logs and reports.
- Include default secret-like patterns.
- Add tests for common secret and token shapes.

Review value:
- Moves the project closer to safe use in sensitive environments.

### 6. Approval Records

Branch: `feature/approval-records`

Goal: Add a local approval workflow without requiring a hosted service.

Scope:
- Add commands for approval requests and approve/reject decisions.
- Store approval records locally.
- Support approver, decision reason, expiration, and timestamp.
- Include approval activity in reports.

Review value:
- Bridges the gap between policy simulation and operational workflow.

### 7. Report Upgrades

Branch: `feature/report-upgrades`

Goal: Make reports more useful for security and governance review.

Scope:
- Add policy coverage summary.
- Highlight servers with no explicit policies.
- Show high-risk unknown tools from simulations.
- Add clearer recommendations and evidence counts.

Review value:
- Improves the main artifact teams would share during review.

### 8. Configurable Risk Engine

Branch: `feature/configurable-risk-engine`

Goal: Let teams tune risk scoring to their own environment.

Scope:
- Add configurable risk keywords and score modifiers.
- Support server-level or pack-level risk defaults.
- Preserve current behavior as defaults.
- Add tests for custom scoring rules.

Review value:
- Makes risk scoring less hard-coded and more credible.

### 9. Experimental MCP Proxy

Branch: `feature/mcp-proxy-spike`

Goal: Explore a minimal live gateway mode after the local governance foundation is stronger.

Scope:
- Document assumptions and limitations.
- Build the smallest viable interception path.
- Reuse existing policy, logging, and reporting primitives.
- Keep the feature clearly marked experimental.

Review value:
- Tests the long-term thesis without destabilizing the MVP.

## Next Feature

Start with `feature/policy-packs`.
