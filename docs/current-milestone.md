# Current Milestone

## Goal

Integrate professional development practices into the project and make the codebase agent-friendly.

## In Scope

- Document a uniform GitHub workflow using a stable `main` branch, a milestone-integration `working` branch, and short-lived topic branches.
- Provide the repo-owned commit template and local setup instructions.
- Improve repository hygiene for cleaner diffs and searches.
- Configure Ruff and pre-commit.
- Persist only the minimal project context required for future agents.

## Out of Scope

- Tests and test-suite buildout.
- Streaming repairs or redesign.
- Docker and deployment changes.
- Product redesign or data-model redesign.
- Large documentation expansions.

## Done Means

- The repo contains a documented development workflow and commit template setup.
- Noise from generated and local-only files is reduced through repo configuration.
- Ruff and pre-commit are configured for local use.
- A new agent can identify the project direction and the active milestone from the minimal repo docs alone.

Meeting these criteria means the milestone appears technically complete. Final milestone completion still requires explicit user confirmation before the work is treated as signed off.
