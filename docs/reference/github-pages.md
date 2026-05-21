# GitHub Pages Deployment

MCPGuard uses the same MkDocs Material deployment pattern as AgentTrace.

## Files

- `mkdocs.yml`: site metadata, theme, extensions, and navigation.
- `requirements-docs.txt`: docs build dependency list.
- `docs/`: Markdown source files.
- `.github/workflows/docs.yml`: GitHub Pages deployment workflow.

## Workflow

The workflow runs on pushes to `main` and on manual dispatch:

1. Check out the repository.
2. Install Python 3.12.
3. Install docs dependencies.
4. Run `mkdocs build --strict`.
5. Upload the generated `site/` artifact.
6. Deploy using `actions/deploy-pages`.

## Repository Settings

In GitHub, Pages should use GitHub Actions as its source.
