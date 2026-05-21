# Configuration

Project configuration is stored in `.mcpguard/config.json`.

## Redaction

```json
{
  "redaction": {
    "default_patterns": true,
    "patterns": ["internal-[0-9]+"]
  }
}
```

`default_patterns` keeps MCPGuard's built-in secret-like patterns enabled.

## Risk

```json
{
  "risk": {
    "base_score": 30,
    "keywords": ["write", "delete", "remove", "publish", "deploy", "execute", "run", "update"],
    "keyword_modifier": 40,
    "mode_modifiers": {
      "allow": 0,
      "approve": 10,
      "block": 20,
      "unknown": 10
    },
    "server_defaults": {},
    "pack_defaults": {},
    "high_risk_threshold": 70
  }
}
```

MCPGuard clamps final scores to the `0` to `100` range.
