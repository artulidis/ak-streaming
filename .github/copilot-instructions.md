# WebStream Agent Instructions

- Start every substantial task by reading [docs/vision.md](../docs/vision.md) and [docs/current-milestone.md](../docs/current-milestone.md).
- Stay within the active milestone. Do not propose or implement work outside that scope unless the user explicitly changes the milestone.
- Keep documentation minimal. Add or expand docs only when they are required for the current milestone.
- Prefer small, reversible changes that fit the documented branch workflow.
- When an agent believes it has completed the active milestone, it must compare its work against the active milestone's completion criteria before treating the work as complete.
- At that point, the agent must present a review summary of all changes it made and explain why each change was made, then ask the user whether the milestone is complete or whether more work is needed.
- If the user wants more work, the agent must ask for further direction and continue within the current milestone rather than assuming completion.
- User confirmation that the milestone is complete does not authorize a commit by itself. The agent must ask for explicit permission before creating a commit.
- After committing, the agent must ask separately whether the user wants the committed changes pushed to GitHub. Commit approval does not imply push approval.
