# Architecture Context

This file is a compact reference for future implementation work.

## Stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0
- Dishka for dependency injection
- PostgreSQL and Redis
- Alembic for migrations
- pytest for tests

## Core flows

1. Request enters `presentation/api/v1/routes/*`
2. Route receives dependencies from Dishka
3. Use case in `application/usecases/*` orchestrates work
4. Domain entities and services hold business rules
5. Infrastructure repositories, clients, and transactions perform I/O
6. Route maps DTOs to response schemas

## Domain objects

- `Player`
- `Club`
- `League`
- `Team`
- `Position`

## Main application areas

- Player CRUD and analytics
- Club and league CRUD
- Team management
- Radar chart generation
- Similar player matching
- Shadow team generation

## Important implementation patterns

- Use cases are the orchestration boundary.
- Mappers convert between layers.
- Repository interfaces live in the domain layer.
- Infrastructure provides repository implementations and external clients.
- Transaction management is abstracted behind domain/application interfaces.

## Practical editing guidance

- Treat README conventions as intent, but verify against the current tree before changing code.
- Keep feature work consistent with the existing module split instead of collapsing it.
- If a change touches DTOs, routes, and repositories together, update the corresponding mappers and tests in the same pass.

## Security work tracker

- Active backlog: [docs/security-backlog.md](./security-backlog.md)

## Product flow plans

- Backend plan for the "Инсайдер Маркет" public flow: [docs/backend-polymarket-flow-plan.md](./backend-polymarket-flow-plan.md)
- Frontend plan for the "Инсайдер Маркет" public flow: [docs/frontend-polymarket-flow-plan.md](./frontend-polymarket-flow-plan.md)
