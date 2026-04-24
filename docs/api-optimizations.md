# API Optimizations Log

## Phase 1 - Serializer Synchronization and Field Exposure Hardening

Date: 2026-04-21

### Exact changes made

1. Replaced every serializer that referenced deleted models (`MyUser`, `UserFollowingCount`, `WatchList`, `Comment`) with serializers built against the current models in [backend/api/models.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/models.py).
2. Added `UserSummarySerializer` for safe, reusable nested user payloads that expose only `id`, `username`, `display_name`, and `avatar_url`.
3. Added `UserRegistrationSerializer` with `password` as `write_only`, `email` as required input, and `create_user()`-based account creation.
4. Added `UserProfileSerializer` with explicit public profile fields and read-only counters (`followers_count`, `following_count`).
5. Replaced `fields = '__all__'` patterns with explicit field lists across every serializer.
6. Added `TopicSerializer` with trimmed-name validation to reject blank topic names.
7. Rebuilt `VideoSerializer` around the current `Video` model, exposing nested read-only `topics`, a write-only `topic_ids` mapping for updates, nested read-only `user`, and read-only counters (`views`, `like_count`, `dislike_count`) plus `created`.
8. Added `FollowSerializer` with a read-only nested `follower`, a slug-based `following` field, and serializer-level protection against self-follow attempts.
9. Added `VideoReactionSerializer` for the current `VideoReaction` model with read-only `user` and `created_at` fields.
10. Added `StreamSessionSerializer` for the current `StreamSession` model and intentionally excluded `stream_key` from the serialized API surface.
11. Added `ChatMessageSerializer` for the current `ChatMessage` model with read-only `user` and `created_at` fields plus trimmed-message validation.

### Why each change was made

1. The existing serializer layer was structurally invalid because it depended on models that no longer exist. Rebuilding it against the current schema was required before any view or route cleanup could be trusted.
2. A dedicated user summary serializer avoids repeating larger user payloads and reduces accidental leakage of sensitive or internal account fields in nested responses.
3. Registration needs separate handling from profile reads. Making `password` write-only and delegating creation to `create_user()` ensures proper password hashing and avoids exposing credentials in API responses.
4. Public profile data should be explicit and stable. Marking follower counters as read-only prevents clients from mutating denormalized state directly.
5. Explicit field lists are safer than `__all__` because future model changes do not automatically expand the public API surface.
6. Basic serializer-level trimming and validation improves input quality and gives clients clearer feedback before model constraints are hit.
7. The video serializer now reflects the actual `Video` model and separates read concerns from write concerns for topics, which keeps the payload predictable for clients and supports safer future view logic.
8. The follow serializer now models the relationship correctly and blocks self-follow requests earlier, producing cleaner API behavior before the database constraint is triggered.
9. Reintroducing reactions through the real model is necessary for the later view rewrite and prevents the API from continuing to reference obsolete like or dislike fields.
10. `stream_key` is sensitive operational data and should not be exposed by default. Omitting it reduces the immediate attack surface while still allowing the session resource to be represented.
11. Chat messages are the current replacement for the deleted comment model, and trimming message input prevents empty whitespace messages from being accepted.

### How this contributes to optimizing the API layer

- Restores correctness by aligning the serializer layer with the current data model.
- Reduces data exposure by removing password reads, hiding sensitive stream session fields, and locking derived counters behind read-only fields.
- Makes the API surface more predictable by replacing broad serializer exposure with explicit, resource-specific contracts.
- Prepares the codebase for the next phases, where views and routes can safely adopt DRF permissions, generic views, and cleaner REST-oriented endpoints.

### Validation

- `c:/Users/artul/OneDrive/Desktop/Projects/WebStream/.venv/Scripts/python.exe -m py_compile backend/api/serializers.py`
- Result: passed with no output.

## Phase 2 - View Reorganization, Permission Enforcement, and Unsafe Code Removal

Date: 2026-04-21

### Exact changes made

1. Rewrote [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) so every active API view now references current models (`User`, `Follow`, `Topic`, `Video`, `VideoReaction`, `ChatMessage`) and current serializers.
2. Added a reusable `IsOwnerOrReadOnly` permission class to enforce object-level write protection for user-owned resources.
3. Replaced the old user views with a public registration-and-list collection view, an authenticated owner-protected user detail view, and safe read-only avatar lookup views.
4. Replaced the broken follow-count views with current follow-edge views: one view lists followers for a target user and safely creates a follow relationship, while another lists who a user is following.
5. Replaced the deleted watchlist view with a compatibility endpoint that returns `410 Gone` because the underlying resource no longer exists in the current data model.
6. Rebuilt the topic endpoint as a DRF `GenericAPIView` with list, create, and retrieve mixins so the existing two URL patterns can continue working without referencing deleted code.
7. Rebuilt the main video collection, user-specific video list, and video detail endpoints against the current `Video` model and `VideoSerializer`.
8. Replaced the unsafe video creation compatibility endpoint with a standard authenticated `CreateAPIView` that uses the same current serializer and ownership assignment as the main collection endpoint.
9. Replaced the obsolete likes or dislikes endpoint with a compatibility view that reads and updates `VideoReaction` rows for the authenticated user, then synchronizes denormalized `like_count` and `dislike_count` values on the video.
10. Replaced the obsolete thumbnail endpoint with a compatibility view that only accepts thumbnail updates and enforces ownership checks.
11. Replaced the deleted comment views with current chat message collection views, including a video-scoped message endpoint that safely injects the path video id during create.
12. Removed all `print()` debugging statements and manual serializer handling that bypassed DRF generic view behavior.
13. Added compatibility aliases at the bottom of the file so the existing URL module can keep importing the old class names until Phase 3 rewrites the route structure.

### Why each change was made

1. The previous view layer could not be trusted because it imported non-existent models and serializers. Rewriting against the real schema was required to restore correctness.
2. Authentication alone is not enough for mutating endpoints. Object-level permission checks are necessary to prevent users from editing or deleting resources they do not own.
3. Separating registration, profile detail, and avatar lookups gives each user endpoint a smaller and clearer responsibility while keeping mutation restricted to the account owner.
4. The old follower-related views were modeled around deleted count tables and unsafe update behavior. Recasting them around the actual `Follow` model restores a resource-oriented shape and removes direct count mutation from the API surface.
5. Keeping a dead route active against a deleted model is worse than failing explicitly. Returning `410 Gone` makes the break intentional and prevents unsafe or misleading behavior while Phase 3 removes the route entirely.
6. The topic URL wiring currently mixes collection and detail patterns. Using DRF mixins lets the project preserve temporary compatibility without carrying forward the old invalid implementation.
7. Video collection and detail operations are core resources, so they now use DRF generic views with explicit ownership assignment and read/write permission handling.
8. The old custom `post()` implementation duplicated DRF behavior, returned the wrong status code, and included debug output. Replacing it with a normal `CreateAPIView` reduces custom code and restores correct `201 Created` behavior.
9. The codebase no longer stores likes and dislikes directly as client-writable fields. The compatibility reaction view now uses the actual `VideoReaction` model and keeps counters synchronized server-side, which is safer and closer to the real data model.
10. Thumbnail updates are still temporarily exposed through the old route, but the new implementation now requires authentication, ownership, and the presence of the thumbnail field instead of allowing broad arbitrary updates.
11. The project's current message resource is `ChatMessage`, not `Comment`. Moving those endpoints over was necessary to remove dead model usage and to keep write ownership tied to `request.user`.
12. Debug prints can leak request payloads and manual serializer flows are easy to get wrong. Removing both reduces accidental data exposure and lets DRF handle request lifecycles consistently.
13. Compatibility aliases keep this phase tightly scoped to the view layer. That avoids mixing route redesign into the current task while still making the old URL module import the new implementations.

### How this contributes to optimizing the API layer

- Restores a functional view layer that is aligned with the real serializer and model surface.
- Enforces authentication and object ownership on write paths instead of leaving mutation behavior effectively open.
- Replaces ad hoc manual request handling with DRF generic views and mixins, which reduces duplication and makes behavior more predictable.
- Removes unsafe debugging behavior and explicit references to deleted resources.
- Creates a stable compatibility bridge so the next phase can cleanly redesign URLs without carrying broken view code forward.

### Validation

- `c:/Users/artul/OneDrive/Desktop/Projects/WebStream/.venv/Scripts/python.exe -m py_compile backend/api/views.py`
- Result: passed with no output.
- Additional attempted validation: Django import of `api.urls` through the configured virtual environment.
- Result: blocked because the local `.venv` currently contains only `pip` and does not have Django or DRF installed, so full runtime import validation is not available in this session.

## Phase 3 - Route Cleanup, Versioning Prefix, and Direct Resource Wiring

Date: 2026-04-21

### Exact changes made

1. Removed the temporary `RemovedEndpointView` from [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py).
2. Removed all remaining compatibility aliases at the bottom of the same file so the URL layer now references the real current view classes directly.
3. Removed compatibility-only view code that existed only to support dead or transitional routes, including the user avatar by-id view, the user avatar by-username view, the dedicated compatibility video-create view, and the dedicated compatibility thumbnail view.
4. Renamed the follower and following views to `UserFollowerCollectionView` and `UserFollowingCollectionView` so their purpose matches the route structure they now serve.
5. Updated the following list view to look users up by `username` instead of the old integer owner id parameter so the nested user routes use one consistent user identifier.
6. Split the old mixed topic collection/detail behavior into two direct DRF views: `TopicCollectionView` and `TopicDetailView`.
7. Renamed the reaction endpoint implementation to `VideoReactionView` and kept it attached to the current `VideoReaction` model instead of the deleted likes/dislikes fields.
8. Reduced message routing to the video-scoped message collection and renamed that view to `VideoMessageCollectionView`.
9. Rewrote [backend/api/urls.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/urls.py) with a direct, plural-noun route surface:
	- `users/`
	- `users/<username>/`
	- `users/<username>/followers/`
	- `users/<username>/following/`
	- `users/<username>/videos/`
	- `topics/`
	- `topics/<id>/`
	- `videos/`
	- `videos/<id>/`
	- `videos/<id>/reactions/`
	- `videos/<video_id>/messages/`
	- `tokens/`
	- `tokens/refreshes/`
10. Removed old dead or inconsistent routes from `api/urls.py`, including singular user and video detail paths, profile-image paths, subscription, watchlists, `videos/post/topic/`, thumbnail-only routes, likes/dislikes routes, and comment routes.
11. Added `app_name = 'api'` to `api/urls.py` so the API URL module can be namespaced cleanly.
12. Updated [backend/main/urls.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/main/urls.py) so the API is mounted at `api/v1/` instead of the unversioned `api/` prefix.
13. During validation, fixed a local defect introduced during the route cutover by restoring the missing `ChatMessageSerializer` import in `views.py` and removing a duplicated serializer assignment.

### Why each change was made

1. `RemovedEndpointView` was never part of the desired API design. Once the dead routes were removed, the placeholder itself became unnecessary noise and needed to be deleted.
2. Compatibility aliases are useful only while the old URL module is still in control. Keeping them after the routing rewrite would make the API harder to read and easier to regress.
3. Compatibility-only views that no longer have corresponding routes should not stay in the codebase. They increase maintenance cost and obscure which endpoints are actually supported.
4. View names should match the resources they expose. Renaming the follow-related views makes the routing layer easier to understand and lines the code up with the URL surface.
5. A nested user route should use one stable identifier. Moving both follower and following routes to `username` avoids mixing ids and slugs for the same user resource.
6. A clean route structure works best when collection and detail endpoints are backed by separate views with clear responsibilities. Splitting topics into collection and detail views removes the earlier mixed-mode behavior.
7. The reaction endpoint should describe the current reaction resource, not obsolete fields from the previous schema. Renaming and keeping it model-backed makes the intent explicit.
8. Messages in the current model belong to videos, so the nested `videos/<video_id>/messages/` route is more accurate and more predictable than keeping a broad transitional comment-style surface.
9. The new route set uses consistent plural nouns and resource nesting, which makes the API easier for clients to discover and reason about.
10. Dead or legacy routes create confusion and keep old assumptions alive in client code. Removing them is necessary to make the API surface truthful.
11. URL namespacing is a small but important cleanup step because it prevents collisions and supports future expansion of versioned APIs.
12. Adding the `v1` prefix establishes a concrete version boundary so future breaking changes do not have to be shipped through an unversioned API root.
13. Fixing the import defect immediately after validation kept the phase coherent and ensured the route cleanup ended in a clean, internally consistent state.

### How this contributes to optimizing the API layer

- Removes dead routes and compatibility-only code so the public API surface accurately reflects the current backend model.
- Makes endpoints more predictable through consistent plural-noun naming and stable nested resource structure.
- Introduces an explicit `v1` API boundary, which is an important step toward maintainable versioned API evolution.
- Simplifies view-to-route mapping by removing aliases and making URLs point directly to the real resource views.
- Reduces the cognitive load of the API layer, which makes future permission, pagination, and performance work easier to apply correctly.

### Validation

- `c:/Users/artul/OneDrive/Desktop/Projects/WebStream/.venv/Scripts/python.exe -m py_compile backend/api/views.py backend/api/urls.py backend/main/urls.py`
- Result: passed with no output.
- Route-surface spot check confirmed that the old dead paths no longer appear in `backend/api/urls.py` and that the API include point is now `api/v1/`.

## Phase 4 - Global DRF Defaults, Router Cleanup, and Django 5.1 Alignment

Date: 2026-04-21

### Exact changes made

1. Expanded the `REST_FRAMEWORK` settings in [backend/main/settings.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/main/settings.py) to add:
	- `DEFAULT_PERMISSION_CLASSES = ['rest_framework.permissions.IsAuthenticatedOrReadOnly']`
	- `DEFAULT_PAGINATION_CLASS = 'rest_framework.pagination.PageNumberPagination'`
	- `PAGE_SIZE = 20`
2. Changed `SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']` from 5 seconds to 15 minutes in the same settings file.
3. Removed the duplicate `django.middleware.common.CommonMiddleware` entry from `MIDDLEWARE`.
4. Converted the top-level user endpoints in [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) from separate collection/detail generic views into a single `UserViewSet`.
5. Converted the top-level topic endpoints into a `TopicViewSet`.
6. Converted the top-level video endpoints into a `VideoViewSet`.
7. Kept the nested follow, reaction, and message routes as explicit views, but removed redundant `permission_classes` declarations from views that now inherit the global `IsAuthenticatedOrReadOnly` default correctly.
8. Updated [backend/api/urls.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/urls.py) to register `users`, `topics`, and `videos` through a DRF `SimpleRouter` while keeping nested routes explicit.
9. Updated [backend/api/models.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/models.py) so the `Follow` model uses `CheckConstraint(condition=...)`, matching Django 5.1 semantics.
10. Updated the key backend dependency pins in [backend/requirements.txt](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/requirements.txt) to align the runtime with Django 5.1, including Django, DRF, SimpleJWT, Channels, Daphne, `channels-redis`, `asgiref`, and `django-cors-headers`.

### Why each change was made

1. Global DRF defaults remove repeated permission and pagination configuration from individual views and make the API behavior more consistent across endpoints.
2. A 5-second access token lifetime is too short for a realistic authenticated API and creates unnecessary refresh churn. Moving to 15 minutes is a much more sensible baseline.
3. Duplicate middleware adds unnecessary request processing noise and should be removed as basic framework hygiene.
4. The user list/detail surface was a reasonable place to adopt DRF viewsets because it consolidates related actions under one resource controller without changing the outward route shape.
5. Topics are a simple collection/detail resource and fit naturally into a small viewset.
6. Videos are also a clear collection/detail resource, and consolidating them into a viewset reduces boilerplate while preserving the existing ownership checks and parser setup.
7. Once `IsAuthenticatedOrReadOnly` is defined globally, redeclaring it on every matching view becomes noise. Keeping only the exceptions and custom ownership enforcement makes the view layer cleaner.
8. A router is appropriate for the top-level resources because it reduces repetitive URL wiring while still allowing the nested routes to stay explicit and readable.
9. The model layer was using Django 4.1-style constraint syntax while the intended direction was Django 5.1. Restoring `condition=` keeps the code aligned with the selected framework version.
10. Changing the framework target without updating the surrounding package set would leave the environment internally inconsistent. The requirements update keeps the runtime aligned with the codebase and avoids forcing Django 4.1 compatibility fixes back into the models.

### How this contributes to optimizing the API layer

- Centralizes core DRF behavior so the API is easier to reason about and less repetitive to maintain.
- Introduces pagination as a default scalability measure instead of leaving collection endpoints unbounded.
- Uses viewsets and a router where they genuinely reduce boilerplate, without forcing every nested endpoint into an awkward abstraction.
- Aligns the repository with Django 5.1 so the API layer can use the current model semantics instead of carrying compatibility workarounds for Django 4.1.
- Keeps the top-level route surface cleaner while preserving explicit control over the nested follow, reaction, and message endpoints.

### Validation

- `c:/Users/artul/OneDrive/Desktop/Projects/WebStream/.venv/Scripts/python.exe -m py_compile backend/api/models.py backend/main/settings.py backend/api/views.py backend/api/urls.py`
- Result: passed with no output.
- Runtime verification was executed against a temporary SQLite database with a temporary URLConf that mounted only `api/v1/`, so the API layer could be tested without requiring the full RTMP/Celery stack.
- Verified behavior:
	- `GET /api/v1/videos/` without a token returned `200`.
	- `POST /api/v1/videos/` without a token returned `401`.
	- The paginated response included `count`, `next`, `previous`, and `results`.
- Note: the unauthenticated write returned `401` rather than `403` because `JWTAuthentication` issues an authentication challenge. The write is still correctly blocked by the global `IsAuthenticatedOrReadOnly` policy.

## Phase 5 - V1 Contract Finalization, Migration Repair, and Runtime Validation

Date: 2026-04-23

### Exact changes made

1. Expanded the DRF settings in [backend/main/settings.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/main/settings.py) to add `DEFAULT_VERSIONING_CLASS = 'rest_framework.versioning.URLPathVersioning'`, `DEFAULT_VERSION = 'v1'`, and `ALLOWED_VERSIONS = ('v1',)`.
2. Updated [backend/main/urls.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/main/urls.py) so the API include point is version-parameterized as `api/<str:version>/` rather than a hardcoded `api/v1/` string.
3. Split the user serializer contract in [backend/api/serializers.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/serializers.py) by adding `UserProfileWriteSerializer`, and updated [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) so user registration and owner profile updates respond with the canonical `UserProfileSerializer` shape.
4. Split the video serializer contract in [backend/api/serializers.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/serializers.py) into `VideoListSerializer`, `VideoDetailSerializer`, and `VideoWriteSerializer`.
5. Updated [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) so `VideoViewSet` selects serializers by action, returns detail payloads after create or update, and supports canonical collection filtering through `?user={username}` and `?topic={id}` query parameters.
6. Removed the nested `users/<username>/videos/` route from [backend/api/urls.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/urls.py), making the filtered top-level `videos/` collection the only supported video listing surface in V1.
7. Removed topic creation from public V1 by changing `TopicViewSet` in [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) to a read-only list and retrieve viewset.
8. Replaced the old follow-edge write contract with an explicit singleton follow-state contract by removing the writable follow serializer path, adding `UserFollowStateSerializer` in [backend/api/serializers.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/serializers.py), and adding `UserFollowStateView` plus the `users/<username>/follow/` route in [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) and [backend/api/urls.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/urls.py).
9. Converted follower and following list endpoints in [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) to return paginated `UserSummarySerializer` records instead of follow-edge objects, so the collection payload reflects the actual public resource.
10. Replaced the old collection-shaped reaction contract with a singleton reaction-state contract by adding `VideoReactionStateSerializer` and `VideoReactionWriteSerializer` in [backend/api/serializers.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/serializers.py), changing the route to `videos/<id>/reaction/` in [backend/api/urls.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/urls.py), and updating [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) so the subresource returns only `reaction` as `like`, `dislike`, or `null`.
11. Split the message serializer contract in [backend/api/serializers.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/serializers.py) into `ChatMessageReadSerializer` and `ChatMessageWriteSerializer`, and updated [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) so message writes accept only `message`, path binding uses `videos/<id>/messages/`, and response payloads always use the read serializer.
12. Renamed the token refresh endpoint in [backend/api/urls.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/urls.py) from `tokens/refreshes/` to `tokens/refresh/`.
13. Updated `CustomTokenObtainPairSerializer` in [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) so `POST /api/v1/tokens/` returns a stable `user` summary alongside `access` and `refresh`.
14. Added [docs/api-multiphase-plan.md](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/docs/api-multiphase-plan.md) to capture the larger redesign sequence and added [docs/api-v1-contract.md](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/docs/api-v1-contract.md) to freeze the V1 response shapes, list envelopes, write contracts, and removed legacy routes.
15. Replaced the stale legacy schema in [backend/api/migrations/0001_initial.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/migrations/0001_initial.py) with a Django-generated initial migration that matches the current `User`, `Follow`, `Topic`, `Video`, `VideoReaction`, `StreamSession`, and `ChatMessage` models.
16. Updated [backend/requirements.txt](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/requirements.txt) so the PostgreSQL and image dependencies use Python 3.13-compatible versions: `psycopg[binary]==3.2.12` and `Pillow==11.2.1`.
17. Installed the missing local runtime packages in the workspace environment for validation, including `psycopg[binary]==3.2.12`, `celery==5.2.7`, and `Pillow==11.2.1`, so `manage.py check` could run successfully under the current project settings.

### Why each change was made

1. URL-path versioning should be a DRF concept, not only a string in the URLConf. Adding versioning settings makes `request.version` available and formalizes the V1 boundary.
2. A version-parameterized include point lets the router and settings cooperate on versioning instead of treating `v1` as a hardcoded path fragment.
3. Public read payloads and owner write payloads should not share one serializer when their concerns differ materially. Splitting them prevents write-only assumptions from leaking into the public resource contract.
4. The video surface had drifted into one serializer handling list, detail, and write semantics simultaneously. Separating those concerns makes payload size and write intent explicit.
5. A design-first V1 should expose one canonical collection with filters instead of multiple overlapping collection shapes. Moving user and topic scoping into query parameters makes the top-level collection authoritative.
6. Keeping both `users/<username>/videos/` and `videos/?user={username}` would preserve duplicate discovery surfaces in the contract. Removing the nested route makes the V1 video collection unambiguous.
7. Topics currently have no ownership or moderation boundary, so allowing arbitrary public writes would create a contract the rest of the system is not ready to govern. Making topics read-only in V1 is the safer and cleaner baseline.
8. Following another user is singleton state from the caller's perspective, not creation within somebody else's follower collection. The dedicated `/follow/` route fixes that semantic mismatch and restores idempotent `PUT` or `DELETE` behavior.
9. Follower and following endpoints are public collections of users, so returning follow-edge records was exposing internal relationship structure instead of the actual resource clients need.
10. A caller can have at most one reaction state per video, so the old plural `reactions/` route and mixed response body were misleading. The new singular state contract matches the data model and keeps counts on the video resource where they belong.
11. Messages belong to a video, and the server should own the parent binding. Splitting read and write serializers removes the need for view-layer payload rewriting and makes the nested write contract truthful.
12. `tokens/refreshes/` was awkward naming and did not read like a resource-oriented V1 path. Renaming it to `tokens/refresh/` makes the auth surface more predictable.
13. Returning only raw tokens forces clients to recover user identity indirectly from JWT internals. Adding a stable user summary makes the login response self-describing and more design-first.
14. The implementation now has explicit contract and sequencing documents, which lowers ambiguity for future agents and makes the V1 break legible before phase 2 begins.
15. SQLite-backed validation was blocked because the initial API migration still described the 2022 schema with deleted models and fields. Rewriting it to the current model set removes that structural drift and lets normal migration-based validation run again.
16. The existing PostgreSQL and Pillow pins were too old for the workspace Python 3.13 interpreter, so they could not support real runtime validation in this environment. Updating the pins aligns the manifest with the runtime actually in use.
17. The project imports RTMP and Celery-backed code during Django startup, so local validation depends on those packages being installed even though the current milestone does not modify streaming behavior itself.

### How this contributes to optimizing the API layer

- Finalizes a clean V1 contract where collections, singleton subresources, read payloads, and write payloads map cleanly to the underlying data model.
- Makes the API more predictable for clients by standardizing route names, filtering strategy, response shapes, and token payloads.
- Removes more view-layer payload mutation by pushing truth into serializers and canonical resource routes.
- Establishes a documented contract baseline in `docs/` so future phases can harden security and performance without reopening basic response-shape questions.
- Restores migration-backed SQLite validation and real `manage.py check` support in the workspace, which makes further API iteration safer.

### Validation

- `c:/Users/artul/OneDrive/Desktop/Projects/WebStream/.venv/Scripts/python.exe -m py_compile backend/api/views.py backend/api/serializers.py backend/api/urls.py backend/main/settings.py backend/main/urls.py backend/api/migrations/0001_initial.py`
- Result: passed with no output.
- `manage.py check` was executed successfully after installing compatible runtime dependencies and supplying `SECRET_KEY`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` in the shell.
- Runtime verification was executed against a temporary in-memory SQLite database with the real `api` migration path enabled and a temporary URLConf that mounted `api/<str:version>/`.
- Verified behavior:
	- `GET /api/v1/videos/` returned `200`.
	- `GET /api/v1/videos/?user=owner` returned `200` with the expected filtered count.
	- `POST /api/v1/users/` returned `201` with the canonical user profile response shape.
	- `POST /api/v1/tokens/` returned `200` with `access`, `refresh`, and `user`.
	- `POST /api/v1/tokens/refresh/` returned `200`.
	- `PUT` and `GET /api/v1/users/{username}/follow/` returned `200` with `{"is_following": true}`.
	- `PUT` and `GET /api/v1/videos/{id}/reaction/` returned `200` with `{"reaction": "like"}`.
	- `POST /api/v1/videos/{id}/messages/` returned `201`, and `GET /api/v1/videos/{id}/messages/` returned `200` with the expected message item shape.
	- Legacy routes `videos/{id}/reactions/` and `tokens/refreshes/` returned `404`.

## Phase 6 - Authentication and Authorization Hardening

Date: 2026-04-23

### Exact changes made

1. Updated [backend/api/serializers.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/serializers.py) so `UserRegistrationSerializer` now runs Django `validate_password()` during registration and reports failures on the `password` field instead of allowing weak passwords through or returning only non-field validation errors.
2. Added [backend/api/permissions.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/permissions.py) and moved `IsOwnerOrReadOnly` out of [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) so owner checks live in a reusable permission module instead of being embedded in the view layer.
3. Added [backend/api/auth_helpers.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/auth_helpers.py) with `ensure_authenticated_user()`, `bind_authenticated_user()`, and `create_chat_message()` so actor binding for user-owned writes is centralized instead of repeated inline.
4. Updated [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) so `VideoViewSet.perform_create()` and `VideoMessageCollectionView.perform_create()` now use the shared actor-binding helper, and `VideoMessageCollectionView` declares its permission behavior explicitly with `IsAuthenticatedOrReadOnly` instead of relying only on the global default.
5. Added [backend/api/throttles.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/throttles.py) with targeted throttle classes for registration, login, token refresh, token revoke, reaction writes, REST message writes, and websocket message writes.
6. Expanded [backend/main/settings.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/main/settings.py) to add `rest_framework_simplejwt.token_blacklist` to `INSTALLED_APPS` and define named throttle rates for the new auth, reaction, and message throttles.
7. Updated [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) so `UserViewSet.create()` is registration-throttled, `VideoReactionView` throttles only mutating requests, and `VideoMessageCollectionView` throttles only `POST` writes.
8. Replaced the framework-only token refresh wiring with local auth views in [backend/api/views.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/views.py) by adding `CustomTokenRefreshView` and `TokenRevokeView`, each with explicit `AllowAny` permissions and endpoint-specific throttles.
9. Updated [backend/api/urls.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/api/urls.py) so `tokens/refresh/` now uses the local refresh view and the API exposes a new `tokens/revoke/` endpoint for explicit refresh-token blacklisting.
10. Added [backend/websocket/auth.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/websocket/auth.py) with JWT-aware Channels middleware that reads a `token` query parameter and resolves `scope.user` through SimpleJWT instead of trusting session-only auth.
11. Updated [backend/main/asgi.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/main/asgi.py) so websocket routing now uses the JWT-aware middleware stack and removes the username parameter from the chat route, changing the path shape to `ws/videos/<id>/`.
12. Rewrote [backend/websocket/consumers.py](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/websocket/consumers.py) to replace the stale `AsyncConsumer` implementation that referenced deleted models with an `AsyncJsonWebsocketConsumer` that:
	- rejects unauthenticated connections,
	- resolves the acting user from `scope.user`,
	- validates message content through the shared chat-message creation helper,
	- throttles websocket message sends, and
	- broadcasts the canonical `ChatMessageReadSerializer` payload so websocket chat cannot impersonate another user through URL or payload data.
13. Updated [frontend/src/pages/VideoPage.js](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/frontend/src/pages/VideoPage.js) so the active websocket client now connects to `ws://127.0.0.1/ws/videos/<id>/?token=<access-token>`, removes the username from the path, stops sending spoofable `user` and `video` fields in chat payloads, and cleans up the socket in a `useEffect` teardown.
14. Updated [backend/requirements.txt](c:/Users/artul/OneDrive/Desktop/Projects/WebStream/backend/requirements.txt) again to raise `redis` from `4.3.4` to `4.6.0` and `typing_extensions` from `4.3.0` to `4.12.2`, resolving the dependency conflicts that blocked container builds for the real Docker-backed backend environment.
15. Executed `docker compose run --rm --build ... backend python manage.py migrate` against the compose-backed PostgreSQL service so the `token_blacklist` tables and the current API schema exist in the real database environment, not only in temporary SQLite validation runs.

### Why each change was made

1. Django password validators were already configured in settings, but registration bypassed them entirely. Enforcing them in the serializer closes that gap at the API boundary and keeps weak-password failures tied to the password input itself.
2. Ownership checks were previously defined inside the view module, which made them harder to reuse and easier to duplicate. Moving them into a dedicated permission module makes the enforcement boundary clearer.
3. Phase 2 requires authenticated identity to be the only actor source for writes. A shared helper prevents future view or consumer code from drifting back toward client-supplied actor fields.
4. The REST message path already bound `request.user`, but it did so inline. Converting it to the shared helper makes the write contract explicit and aligns it with websocket message persistence.
5. The project had no throttling at all. Dedicated throttle classes keep rate-limiting local to the sensitive write paths instead of introducing a broad global throttle that would change read behavior unnecessarily.
6. `BLACKLIST_AFTER_ROTATION` and refresh rotation were already enabled in configuration, but they were incomplete without the SimpleJWT blacklist app and real throttle-rate configuration. Adding both turns those settings into working server behavior.
7. Registration, reactions, and messages have very different abuse profiles. Per-endpoint throttles let the codebase tune those paths independently without over-throttling normal reads.
8. Leaving refresh handling entirely in third-party view classes makes project-specific policy harder to evolve. Local view subclasses provide a stable place for throttles and future auth policy changes.
9. Rotation-only blacklisting is not enough when clients need an explicit logout or token-revocation path. The revoke endpoint makes refresh-token invalidation an intentional API capability.
10. The API layer uses JWT authentication, but websocket chat still depended on session middleware and a username in the URL. JWT-aware socket middleware closes that mismatch and makes the realtime path follow the same actor model as the HTTP API.
11. Removing the username path segment is the concrete step that prevents route data from standing in for caller identity on websocket chat.
12. The old consumer trusted deleted models and spoofable route data. Rewriting it against the current models and serializer contract closes the impersonation gap and keeps websocket message persistence aligned with the REST write path.
13. Backend-only websocket hardening would have broken the active frontend client immediately. Updating the one live socket caller keeps the shipped client aligned with the new authenticated websocket contract.
14. The real migration step surfaced dependency conflicts that the local virtualenv did not expose because the Docker backend image builds under Python 3.10 with a full resolver pass. Fixing those pins at the manifest level removes an environment-specific deployment blocker instead of working around it locally.
15. Phase 2 required refresh-token blacklisting to exist in the actual Postgres environment. Running migrations against the compose database makes the blacklist support operational for the deployed stack rather than only validated in tests.

### How this contributes to optimizing the API layer

- Enforces password strength and authenticated actor binding at the serializer, permission, and consumer boundaries instead of depending on client honesty.
- Turns JWT refresh rotation into a complete lifecycle with blacklist-backed revocation instead of a partially configured token policy.
- Adds abuse resistance on the highest-risk write paths without changing list or detail read behavior.
- Reduces duplicated auth logic by centralizing ownership checks and actor-bound writes in small reusable modules.
- Brings the websocket chat path into the same security model as the REST API, which removes one of the largest remaining identity inconsistencies in the backend surface.
- Keeps the real Docker-backed environment buildable and migratable, which is necessary for the hardened auth flow to exist outside local smoke tests.

### Validation

- `c:/Users/artul/OneDrive/Desktop/Projects/WebStream/.venv/Scripts/python.exe -m py_compile backend/api/serializers.py`
- Result: passed with no output.
- `c:/Users/artul/OneDrive/Desktop/Projects/WebStream/.venv/Scripts/python.exe -m py_compile backend/api/serializers.py backend/api/permissions.py backend/api/auth_helpers.py backend/api/throttles.py backend/api/views.py backend/api/urls.py backend/main/settings.py`
- Result: passed with no output.
- `c:/Users/artul/OneDrive/Desktop/Projects/WebStream/.venv/Scripts/python.exe -m py_compile backend/websocket/auth.py backend/main/asgi.py backend/websocket/consumers.py`
- Result: passed with no output.
- `manage.py check` was executed successfully after supplying `SECRET_KEY`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` in the shell.
- Additional runtime verification was executed against a temporary file-backed SQLite database with the real migration path enabled and an in-memory Channels layer.
- Verified behavior:
	- `POST /api/v1/users/` rejected a weak password with `400` and a `password` validation error.
	- `POST /api/v1/users/` accepted a strong password and returned `201`.
	- `POST /api/v1/tokens/` returned `200` with `access`, `refresh`, and `user`.
	- `POST /api/v1/tokens/refresh/` returned `200`, and reusing the old refresh token after rotation failed with `401`.
	- `POST /api/v1/tokens/revoke/` returned `200`, and refreshing with the revoked token failed afterward.
	- `PUT /api/v1/videos/{id}/reaction/` without credentials returned `401`, while the authenticated write returned `200` with `{"reaction": "like"}`.
	- `POST /api/v1/videos/{id}/messages/` with an authenticated token returned `201` and persisted the authenticated user in the response payload.
	- Websocket connect to `ws/videos/{id}/` without a JWT was rejected.
	- Websocket connect to `ws/videos/{id}/?token=...` succeeded, and sending a payload with a spoofed `user` value still persisted and broadcast the authenticated user from the token.
	- The active websocket client in `frontend/src/pages/VideoPage.js` was updated to use the new tokenized `ws/videos/{id}/` URL shape and no longer sends caller identity in the payload.
	- `docker compose run --rm --build ... backend python manage.py migrate` completed successfully against the compose-backed PostgreSQL service and applied the `token_blacklist` migration set in the real database environment.
