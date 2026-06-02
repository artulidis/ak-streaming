# API V1 Contract

This document freezes the response-shape decisions for the current V1 API layer so Phase 2 can build on a stable contract.

## Versioning

- The canonical API root is `/api/v1/`.
- DRF URL-path versioning is the active versioning scheme for V1.
- Legacy route forms outside this path are not part of the supported contract.

## List Envelope

- Collection endpoints use DRF page-number pagination.
- The response envelope is:

```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

- This applies to `users/`, `videos/`, `users/{username}/followers/`, `users/{username}/following/`, and `videos/{id}/messages/`.

## Resource Shapes

### User Summary

- Used by user lists, follower/following lists, nested message authors, nested video owners, and token responses.

```json
{
  "id": 1,
  "username": "viewer",
  "display_name": "Viewer Name",
  "avatar_url": ""
}
```

### User Profile

- Used by `GET /api/v1/users/{username}/`, `POST /api/v1/users/`, `PUT /api/v1/users/{username}/`, and `PATCH /api/v1/users/{username}/` responses.

```json
{
  "id": 1,
  "username": "viewer",
  "display_name": "Viewer Name",
  "bio": "",
  "avatar_url": "",
  "followers_count": 0,
  "following_count": 0
}
```

- User writes accept only `display_name`, `bio`, and `avatar`.
- User read serializers expose `avatar_url` as the resolved file URL for the stored avatar image.
- User registration writes accept only `username` and `password`.

### Topic

- Topics are read-only in public V1.

```json
{
  "id": 1,
  "name": "Gameplay"
}
```

### Video List Item

- Used inside `GET /api/v1/videos/` results.

```json
{
  "id": 1,
  "user": {"id": 1, "username": "owner", "display_name": "", "avatar_url": ""},
  "name": "Launch Stream",
  "views": 0,
  "like_count": 0,
  "dislike_count": 0,
  "topics": [{"id": 1, "name": "Gameplay"}],
  "thumbnail": null,
  "created": "2026-04-24T00:00:00Z"
}
```

- The canonical video collection supports query filters such as `?user={username}` and `?topic_name={name}`.

### Video Detail

- Used by `GET /api/v1/videos/{id}/`, `POST /api/v1/videos/`, `PUT /api/v1/videos/{id}/`, and `PATCH /api/v1/videos/{id}/` responses.

```json
{
  "id": 1,
  "user": {"id": 1, "username": "owner", "display_name": "", "avatar_url": ""},
  "name": "Launch Stream",
  "description": "Smoke check video",
  "views": 0,
  "like_count": 0,
  "dislike_count": 0,
  "topics": [{"id": 1, "name": "Gameplay"}],
  "thumbnail": null,
  "created": "2026-04-24T00:00:00Z"
}
```

- Video writes accept only `name`, `description`, `topic_names`, and `thumbnail`.

### Follow State

- Used by `GET` and `PUT /api/v1/users/{username}/follow/`.

```json
{
  "is_following": true
}
```

- `DELETE /api/v1/users/{username}/follow/` returns `204` with no body.

### Reaction State

- Used by `GET` and `PUT /api/v1/videos/{id}/reaction/`.

```json
{
  "reaction": "like"
}
```

- `reaction` may be `"like"`, `"dislike"`, or `null`.
- `DELETE /api/v1/videos/{id}/reaction/` returns `204` with no body.
- Reaction counts belong on the video resource, not on the reaction-state subresource.

### Message Item

- Used by `POST /api/v1/videos/{id}/messages/` and message list results.

```json
{
  "id": 1,
  "user": {"id": 2, "username": "viewer", "display_name": "Viewer Name", "avatar_url": ""},
  "message": "hello world",
  "created_at": "2026-04-24T00:00:00Z"
}
```

- Message writes accept only `message`.

### Token Pair Response

- Used by `POST /api/v1/tokens/`.

```json
{
  "access": "...",
  "refresh": "...",
  "user": {"id": 2, "username": "viewer", "display_name": "Viewer Name", "avatar_url": ""}
}
```

### Token Refresh Response

- Used by `POST /api/v1/tokens/refresh/`.

```json
{
  "access": "...",
  "refresh": "..."
}
```

## Removed Legacy Routes

- `GET|PUT|PATCH|DELETE /api/v1/videos/{id}/reactions/`
- `POST /api/v1/tokens/refreshes/`
- `GET /api/v1/users/{username}/videos/`

These legacy forms are not part of the supported V1 contract.