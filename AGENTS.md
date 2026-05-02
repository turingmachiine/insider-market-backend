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

The current codebase uses these packages:

- `src/domain`: entities, value objects, repository interfaces, domain services
- `src/application`: DTOs, use cases, mappers, ports, decorators
- `src/infrastructure`: database, API clients, DI, logging, cache
- `src/processing`: domain-adjacent calculation services for radar, matching, shadow team
- `src/presentation`: FastAPI routes, schemas, response mappers

## Working rules

- Prefer the existing architecture and naming conventions over introducing new abstractions.
- Keep classes in separate files when the codebase already follows that pattern.
- Do not instantiate infrastructure/application dependencies directly inside classes when DI is already used.
- Preserve the current layering. Domain must not import infrastructure or presentation.
- Use explicit mappers between entities, DTOs, ORM models, and API schemas.
- Keep changes focused. Avoid unrelated refactors, renames, or style churn.

## Where to look first

- README for product and architectural intent
- `pyproject.toml` for runtime, tooling, and test configuration
- `src/infrastructure/di/container_factory.py` and provider modules for dependency wiring
- `src/application/usecases/` for orchestration logic
- `src/domain/` for business rules
- `src/presentation/api/v1/routes/` for API contracts

## Notes from the current tree

- The README mentions `src/core/mapping`, but the actual code uses `src/application/mappers` and `src/core/mappers`.
- `processing/` contains substantial business logic and should be treated carefully when changing algorithms or DTO contracts.
- Tests are split into unit and integration suites; keep additions aligned with that split.
