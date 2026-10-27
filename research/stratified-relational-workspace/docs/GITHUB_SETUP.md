# GitHub setup

## Suggested repository settings

- **Repository name:** `stratified-relational-workspace-theory`
- **Description:** Formal core-transfer theory of persistent relational workspaces across heterogeneous agents and artifacts.
- **Suggested topics:** `distributed-cognition`, `human-ai-collaboration`, `multi-agent-systems`, `causal-inference`, `sheaf-theory`, `spectral-methods`, `agency`, `latex`

Enable Issues, Discussions if desired, GitHub Actions, private vulnerability reporting, and branch protection for `main`. Require the `build-and-verify` workflow before merging.

## Initial publication with GitHub CLI

From the repository directory in PowerShell:

```powershell
git init; git branch -M main; git add .; git commit -m "Initial public repository release: SRWT v1.0.0"; gh repo create stratified-relational-workspace-theory --public --source . --remote origin --push
```

Then apply topics:

```powershell
gh repo edit --add-topic distributed-cognition --add-topic human-ai-collaboration --add-topic multi-agent-systems --add-topic causal-inference --add-topic sheaf-theory --add-topic spectral-methods --add-topic agency --add-topic latex
```

## First release

```powershell
git tag -a v1.0.0 -m "SRWT v1.0.0"; git push origin v1.0.0
```

The tagged-release workflow uses GitHub CLI with the repository-scoped `GITHUB_TOKEN` to publish the generated assets.
