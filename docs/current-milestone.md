# Current Milestone

## Goal

Reorganize and optimize the backend data model for a read-heavy, high-concurrency streaming system.

## In Scope

- Replace implicit M2M relationships (likes, dislikes, follows) with explicit edge tables and denormalized counters.
- Separate ephemeral state (live chat, stream sessions) from persistent content (videos, user profiles).
- Tighten nullability and enforce data integrity at the schema level.
- Add deliberate indexing aligned with dominant query patterns.
- Remove unused models (WatchList, UserFollowingCount).
- Update serializers, views, URLs, and WebSocket consumers to match the revised model.
- Generate and validate Django migrations for the new schema.

## Out of Scope

- Tests and test-suite buildout.
- Caching and buffering layers (Redis, async counter flushes).
- Docker and deployment changes.
- Frontend changes.
- Streaming infrastructure repairs.

## Done Means

- The revised models compile and pass `makemigrations` / `migrate` cleanly.
- Serializers, views, and URL routes reference only the new models.
- The WebSocket consumer writes to `ChatMessage` instead of `Comment`.
- No references to removed models (`WatchList`, `UserFollowingCount`, old M2M likes/dislikes) remain in application code.
- The data model matches the design rationale documented by the user.

Meeting these criteria means the milestone appears technically complete. Final milestone completion still requires explicit user confirmation before the work is treated as signed off.
