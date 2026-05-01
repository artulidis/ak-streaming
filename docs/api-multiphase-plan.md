# WebStream API Hardening & Redesign: Multiphase Execution Plan

## Overview

This document outlines the recommended phases for transitioning the WebStream backend API to a secure, performant, and design-first implementation. Each phase targets a coherent set of issues, with intent, codebase focus, and subplans specified for agent and contributor clarity.

---

## Phase 1: Contract Design and Versioning

**Targets:**
- Mixed resource semantics
- Awkward custom routes
- Versioning that is only a URL prefix
- Serializers whose writable contract is partly enforced in views

**Intent:**
Define the API contract first so later security and performance work lands on a stable resource model instead of continuing to reshape endpoints.

**Codebase:**
API route definitions, serializers, view contracts, DRF versioning/schema configuration.

**Subplan:**
- Define canonical resources and method/status matrix
- Normalize singleton vs collection endpoints (e.g., reactions, follows)
- Choose a real versioning approach
- Split list/detail/write serializers where payloads should differ

---

## Phase 2: Authentication and Authorization Hardening

**Targets:**
- Registration does not enforce Django password validators
- JWT rotation is only partially configured
- No throttling
- Ownership rules are still spread across views

**Intent:**
Make every mutating endpoint bind actor identity and authorization consistently at the framework boundary.

**Codebase:**
Registration and token serializers, permission classes, auth views, DRF settings.

**Subplan:**
- Enforce password validation during registration
- Fully enable refresh-token blacklisting or simplify JWT config
- Add throttling for auth, reaction, and message writes
- Centralize actor/owner checks
- Remove any path where URL data can stand in for authenticated identity

---

## Phase 3: Streaming Control Plane Redesign

**Targets:**
- RTMP start flow is unsafe
- Raw command execution exposed to client boundary
- Websocket chat trusts a URL username
- `StreamSession` exists without being the public control resource

**Intent:**
Move streaming behind authenticated, server-managed session resources instead of trusting transport-layer input.

**Codebase:**
Stream session models/serializers/views, RTMP task/view code, websocket consumer/auth wiring.

**Subplan:**
- Expose stream-session resources in the API
- Generate and validate stream keys or scoped tokens server-side
- Remove client-supplied FFmpeg commands
- Derive chat identity from authenticated websocket user and validate session/video access

---

## Phase 4: Business Logic Extraction and Data Consistency

**Targets:**
- Follow counters not maintained in write path
- Reaction counter sync embedded in views
- Domain rules duplicated across endpoints

**Intent:**
Move invariants and transaction rules into a small service layer so REST and realtime flows share the same behavior.

**Codebase:**
Follow, reaction, and message write flows; model managers or service modules; transaction boundaries.

**Subplan:**
- Extract follow create/delete services with counter synchronization
- Extract reaction set/clear services
- Unify message persistence between REST and websocket paths
- Make idempotency and concurrency rules explicit