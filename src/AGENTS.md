# Source Tree Rules

This file applies to everything under `src/`.

## Layer boundaries

- `domain` contains the core business model and interfaces only.
- `application` coordinates use cases, DTOs, mappers, and ports.
- `infrastructure` contains implementations for persistence, external APIs, logging, cache, and DI providers.
- `presentation` contains FastAPI routes and Pydantic schemas.
- `processing` contains algorithmic services used by application/presentation flows.
- Service packages under `src/backend/` should follow the same directory shape as `nsi_service` unless there is a documented reason to diverge.

## Change rules

- Keep imports pointed in the allowed direction.
- Prefer constructor injection and Dishka wiring instead of manual object creation.
- Put conversion logic in mappers, not in DTOs, entities, or routes.
- Preserve async boundaries where repositories, use cases, and routes already use async.
- Avoid adding cross-layer shortcuts, especially direct access from presentation to infrastructure.
- Keep repository interfaces in `domain/interfaces/repositories`; do not keep them in `application`.
- Keep repository implementations in `infrastructure/db/repositories`; do not place concrete persistence logic in `application`.
- Keep domain entities in `domain/entities`; do not define business entities in `infrastructure/db/models`.
- Use domain entities in repositories and map them imperatively to SQLAlchemy tables.
- Define SQLAlchemy tables in `infrastructure/db/tables` and mapping in `infrastructure/db/mappers.py`.
- In repositories, prefer table-column expressions such as `players_table.c.id` or `users_table.c.email`.
- Do not use `getattr(Model, "field")` as a workaround for SQLAlchemy typing.
- Use Dishka providers for repositories, services, settings, sessions, cache clients, and other dependencies.
- FastAPI routes should not manually instantiate repositories, services, sessions, Redis clients, or settings-backed dependencies.
- If a service already uses Dishka, route handlers should use `@inject` and `FromDishka` for injected dependencies.

## Naming and structure

- Use explicit, descriptive class names.
- Keep one class per file when extending existing patterns.
- Keep helper functions local to the module unless they are broadly reusable.
- Name repository interfaces `I<Entity>Repository` and store them in `i_<entity>_repository.py`.
- Name concrete repositories `<Entity>Repository` and store them in `<entity>_repository.py`.
- Keep one SQLAlchemy table per file named `<table_name>_table.py`, exported from `tables/__init__.py`.
