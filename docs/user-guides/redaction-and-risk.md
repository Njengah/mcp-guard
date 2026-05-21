# Redaction And Risk

## Redaction

MCPGuard redacts common secret-like values before writing simulation logs, approval logs, proxy logs, and reports.

Default patterns cover common API key, token, secret, password, GitHub token, OpenAI key, Slack token, and AWS access key shapes.

Custom patterns live in `.mcpguard/config.json`:

```json
{
  "redaction": {
    "default_patterns": true,
    "patterns": ["internal-[0-9]+"]
  }
}
```

## Risk Scoring

Default risk scoring preserves MCPGuard's original behavior:

- base score: `30`
- risky keyword modifier: `40`
- block modifier: `20`
- approval or unknown-policy modifier: `10`
- high-risk threshold: `70`

Customize scoring in `.mcpguard/config.json`:

```json
{
  "risk": {
    "keywords": ["write", "delete", "archive"],
    "keyword_modifier": 40,
    "server_defaults": {
      "database": 15
    },
    "pack_defaults": {
      "github": 5
    },
    "high_risk_threshold": 70
  }
}
```

Risk scores are governance signals. They do not replace review of the actual tool, system, and data involved.
