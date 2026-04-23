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
