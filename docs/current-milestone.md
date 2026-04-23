# Current Milestone

## Goal

Reorganize and clean the backend API layer so the model serializers,
API views, and URL structure are production-grade, secure, and aligned
with Django REST Framework best practices.

## In Scope

- Rework model serializers so they match the revised models, fields,
	and relationships.
- Reorganize API views around clear DRF conventions, safe create and
	update flows, and production-grade request handling.
- Restructure API URLs so resource, detail, and nested routes follow a
	consistent REST-oriented pattern.
- Remove references to deleted models and obsolete fields from
	serializers, views, and URL wiring.
- Tighten authentication, permissions, and validation for mutating
	endpoints.
- Remove debug behavior and unsafe patterns from the API layer.
- Align the API layer cleanly with the revised data model so it is ready
	for future testing and hardening work.

## Out of Scope

- Tests and test-suite buildout.
- Caching, throttling, and buffering layers.
- Docker and deployment changes.
- Frontend changes.
- Streaming infrastructure repairs.
- New product features beyond reorganizing the existing API surface.

## Done Means

- Model serializers reference only the current models and fields.
- API views follow DRF best practices for querysets, lookups,
	validation, and create or update behavior.
- URL routes are consistent, REST-oriented, and mapped cleanly to the
	reorganized API views.
- Mutating endpoints enforce appropriate authentication and permission
	checks.
- Debug prints and unsafe API-layer behavior have been removed.
- The API layer matches the revised data model and is ready for
	production-grade follow-up work.

Meeting these criteria means the milestone appears technically complete. Final milestone completion still requires explicit user confirmation before the work is treated as signed off.
