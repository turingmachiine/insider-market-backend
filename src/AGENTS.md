# Source Tree Rules

This file applies to everything under `src/`.

## Layer boundaries

- `domain` contains the core business model and interfaces only.
- `application` coordinates use cases, DTOs, mappers, and ports.
- `infrastructure` contains implementations for persistence, external APIs, logging, cache, and DI providers.
- `presentation` contains FastAPI routes and Pydantic schemas.
- `processing` contains algorithmic services used by application/presentation flows.

## Change rules

- Keep imports pointed in the allowed direction.
- Prefer constructor injection and Dishka wiring instead of manual object creation.
- Put conversion logic in mappers, not in DTOs, entities, or routes.
- Preserve async boundaries where repositories, use cases, and routes already use async.
- Avoid adding cross-layer shortcuts, especially direct access from presentation to infrastructure.

## Naming and structure

- Use explicit, descriptive class names.
- Keep one class per file when extending existing patterns.
- Keep helper functions local to the module unless they are broadly reusable.
