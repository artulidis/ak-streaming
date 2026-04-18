# Development Workflow

## Branching

Use trunk-based development with short-lived feature branches.

- `main` is the trunk.
- Create a short-lived branch for each focused change.
- Rebase onto `main` before merging when needed.
- Merge small, reviewable changes back to `main` quickly.

## Commit Messages

This repository uses the following commit template:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

# --- Guidelines ---
# Type: feat, fix, docs, style, refactor, test, chore
# Subject: Max 50 chars, imperative mood, no period at end
# Body: Explain WHAT and WHY (not how), wrap at 72 chars
# Footer: Reference issues (e.g., Fixes #123) or Breaking Changes
```

Enable it locally:

```powershell
git config commit.template .gitmessage
```

## Local Quality Checks

Install the backend development dependencies:

```powershell
pip install -r backend/requirements-dev.txt
```

Install pre-commit hooks:

```powershell
pre-commit install
```

Run checks manually when needed:

```powershell
ruff check .
ruff format .
pre-commit run --all-files
```

## Scope Discipline

When working with agents, the long-term direction lives in [docs/vision.md](vision.md) and the active scope lives in [docs/current-milestone.md](current-milestone.md). Work should stay inside the current milestone unless the user explicitly changes scope.

## Milestone Approval Gate

When an agent believes it has completed the active milestone, it should first check its work against the active milestone document and then present a review summary of all changes it made, including why each change was made.

After that review summary, the agent should ask the user whether the milestone is complete or whether more work is needed. If more work is needed, the agent should ask for further direction and continue within the same milestone.

User confirmation that a milestone is complete is separate from commit approval. If the user signs off on the milestone, the agent should ask whether it may create a commit.

Push approval is also separate. After committing changes, the agent should ask whether the user wants the committed changes pushed to GitHub.
