# Project Context

This repository is a Python 3.12+ backend for football analytics built with clean architecture, FastAPI, SQLAlchemy 2.0, Dishka, Alembic, and pytest.

## What this project is for

- Football data collection from external providers
- Player radar charts and comparison workflows
- Similar player search with league-strength adjustment
- Shadow-team composition for squad strengthening
- API-first backend development with strong layering boundaries

## High-level architecture

Keep dependency direction strict:

`presentation -> application -> domain <- infrastructure`

The current codebase uses service-local packages under
`src/backend/{service_name}/`:

- `domain`: entities, value objects, repository interfaces, domain services
- `application`: DTOs, use cases, mappers, ports, decorators, orchestration services
- `infrastructure`: database tables, repositories, DI, API clients, logging, cache
- `processing`: domain-adjacent calculation services for radar, matching, shadow team
- `presentation`: FastAPI routes, schemas, response mappers, middleware

## Working rules

- Prefer the existing architecture and naming conventions over introducing new abstractions.
- Keep classes in separate files when the codebase already follows that pattern.
- Do not instantiate infrastructure/application dependencies directly inside classes when DI is already used.
- Preserve the current layering. Domain must not import infrastructure or presentation.
- Use explicit mappers between entities, DTOs, ORM models, and API schemas.
- Keep changes focused. Avoid unrelated refactors, renames, or style churn.
- Keep service structure consistent with `nsi_service` unless there is a documented reason not to.
- Put domain entities in `domain/entities`, not in `infrastructure/db/models`.
- Put repository interfaces in `domain/interfaces/repositories`, one interface per file named `i_*_repository.py`.
- Put repository implementations in `infrastructure/db/repositories`, one repository per file.
- Repositories should work with domain entities and table definitions, not infrastructure ORM model classes.
- For SQLAlchemy imperative mapping, map domain entities to tables in `infrastructure/db/mappers.py`.
- Define SQLAlchemy `Table` objects under `infrastructure/db/tables`, one table per file, using service-local `metadata.py`.
- Prefer table-column expressions such as `users_table.c.email` in repositories. Do not use `getattr(Model, "field")` to work around typing.
- Wire dependencies through Dishka providers in `infrastructure/di/providers`; route handlers should use `@inject` and `FromDishka` where DI is already configured.
- Do not manually create repositories, services, database sessions, Redis clients, or settings-backed dependencies in FastAPI routes.
- Application services may depend on domain repository interfaces, cache/application ports, and settings, but not on concrete infrastructure repositories.
- Presentation must not import infrastructure repositories or database tables directly.
- Keep internal code-facing text in English: identifiers, helper names, test helper classes, technical comments, and code-oriented strings.
- Keep public project documentation in Russian: `README.md`, documentation pages, and user-facing project guides.

## Where to look first

- README for product and architectural intent
- `pyproject.toml` for runtime, tooling, and test configuration
- `src/backend/nsi_service/` as the reference structure for service layering
- `src/backend/{service}/infrastructure/di/container_factory.py` and provider modules for dependency wiring
- `src/backend/{service}/application/usecases/` or `application/service.py` for orchestration logic
- `src/backend/{service}/domain/` for business rules, entities, and repository interfaces
- `src/backend/{service}/infrastructure/db/tables/`, `mappers.py`, and `repositories/` for persistence
- `src/backend/{service}/presentation/api/v1/routes/` for API contracts

## Notes from the current tree

- The README mentions `src/core/mapping`, but the actual code uses `src/application/mappers` and `src/core/mappers`.
- `processing/` contains substantial business logic and should be treated carefully when changing algorithms or DTO contracts.
- Tests are split into unit and integration suites; keep additions aligned with that split.
- `auth_service` should mirror `nsi_service` structure: domain entities and repository interfaces in `domain`, imperative SQLAlchemy table mapping in `infrastructure/db`, concrete repositories in `infrastructure/db/repositories`, and Dishka providers in `infrastructure/di/providers`.
