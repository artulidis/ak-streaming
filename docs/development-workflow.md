# Development Workflow

## Branching

Use a staged integration workflow with a stable branch, an integration branch,
and short-lived topic branches.

- `main` is the stable branch for completed project phases.
- `working` is the integration branch for completed milestones within the
	current phase.
- Create a short-lived topic branch from `working` for each focused change.
- Merge completed topic branches back into `working`.
- Merge `working` into `main` only when a full phase is ready.
- After promoting a phase to `main`, recreate or reset `working` from `main`
	before starting the next phase.

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
