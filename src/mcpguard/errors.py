class MCPGuardError(Exception):
    """Base class for expected CLI errors."""


class NotInitializedError(MCPGuardError):
    """Raised when .mcpguard state does not exist."""


class UnknownServerError(MCPGuardError):
    """Raised when a command references a server that is not configured."""


class DuplicateServerError(MCPGuardError):
    """Raised when adding a server that already exists."""


class InvalidPolicyModeError(MCPGuardError):
    """Raised when a policy mode is not supported."""


class InvalidPolicyFileError(MCPGuardError):
    """Raised when an imported policy file does not match the expected shape."""


class UnknownPolicyPackError(MCPGuardError):
    """Raised when a command references an unknown built-in policy pack."""


class CorruptedStateError(MCPGuardError):
    """Raised when persisted JSON cannot be read as valid MCPGuard state."""
