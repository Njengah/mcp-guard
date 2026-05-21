from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PackTool:
    name: str
    mode: str
    description: str


@dataclass(frozen=True)
class PolicyPack:
    name: str
    server_description: str
    tools: tuple[PackTool, ...]


POLICY_PACKS: dict[str, PolicyPack] = {
    "browser": PolicyPack(
        name="browser",
        server_description="Browser automation tools for navigation, page interaction, and capture.",
        tools=(
            PackTool("navigate", "allow", "Open a requested URL in the browser."),
            PackTool("screenshot", "allow", "Capture page evidence for review."),
            PackTool("click", "approve", "Interact with page controls or links."),
            PackTool("type_text", "approve", "Enter user-provided text into page fields."),
            PackTool("download_file", "approve", "Download files from browser sessions."),
            PackTool("execute_script", "block", "Run arbitrary browser-side scripts."),
        ),
    ),
    "database": PolicyPack(
        name="database",
        server_description="Database tools for schema inspection and query execution.",
        tools=(
            PackTool("list_tables", "allow", "List available tables or collections."),
            PackTool("describe_schema", "allow", "Inspect table or collection schema."),
            PackTool("select_query", "approve", "Run read queries that may expose sensitive data."),
            PackTool("insert_row", "approve", "Create database records."),
            PackTool("update_row", "approve", "Modify database records."),
            PackTool("delete_row", "block", "Delete database records."),
            PackTool("drop_table", "block", "Drop tables, collections, or schemas."),
        ),
    ),
    "filesystem": PolicyPack(
        name="filesystem",
        server_description="Filesystem tools for local file and directory operations.",
        tools=(
            PackTool("read_file", "allow", "Read project files for context."),
            PackTool("list_directory", "allow", "List files and directories."),
            PackTool("write_file", "approve", "Create or overwrite files."),
            PackTool("move_file", "approve", "Move or rename files."),
            PackTool("delete_file", "block", "Delete files from disk."),
            PackTool("execute_command", "block", "Run shell commands through a filesystem server."),
        ),
    ),
    "github": PolicyPack(
        name="github",
        server_description="GitHub tools for repository, issue, and pull request operations.",
        tools=(
            PackTool("get_file_contents", "allow", "Read repository file contents."),
            PackTool("list_repositories", "allow", "List accessible repositories."),
            PackTool("create_issue", "approve", "Create GitHub issues."),
            PackTool("create_pull_request", "approve", "Open pull requests."),
            PackTool("update_file", "approve", "Modify repository files."),
            PackTool("merge_pull_request", "approve", "Merge pull requests."),
            PackTool("delete_repository", "block", "Delete a repository."),
        ),
    ),
}


def list_policy_packs() -> tuple[str, ...]:
    return tuple(sorted(POLICY_PACKS))
