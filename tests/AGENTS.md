# Test Tree Rules

This file applies to everything under `tests/`.

## Test intent

- Unit tests should isolate a single behavior and avoid infrastructure dependencies.
- Integration tests should verify wiring, database behavior, and API flows.
- Keep assertions focused on one concept per test.

## Test structure

- Mirror the project layer when it helps readability:
  - `tests/unit/domain`
  - `tests/unit/processing`
  - `tests/unit/presentation`
  - `tests/integration`
- Reuse fixtures from `tests/fixtures/` when they already model the required object graph.

## Change rules

- Do not couple unit tests to the real database or external APIs unless the test is explicitly integration-level.
- When adding behavior, cover the contract at the lowest sensible layer first.
- Keep fixture names and helpers aligned with the domain language used in `src/`.
