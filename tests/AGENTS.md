# Test Tree Rules

This file applies to everything under `tests/`.

## Test intent

- Unit tests should isolate a single behavior and avoid infrastructure dependencies.
- Integration tests should verify wiring, database behavior, and API flows.
- Keep assertions focused on one concept per test.

## Test structure

- Mirror the project layer when it helps readability:
  `tests/unit/{service}/domain`, `tests/unit/{service}/processing`,
  `tests/unit/{service}/presentation`, `tests/integration/{service}`.
- Keep service tests grouped by service. Current service modules include
  `tests/unit/nsi`, `tests/integration/nsi`, `tests/integration/auth`, and
  `tests/integration/api_gateway`.
- Reuse fixtures from `tests/fixtures/` when they already model the required object graph.
- Keep `tests/conftest.py` thin. It should register fixture plugins and pytest settings only.
- Put integration-only setup in the nearest service integration `conftest.py`.
  Examples: `integration/nsi/conftest.py`, `integration/auth/conftest.py`,
  `integration/api_gateway/conftest.py`.
- Keep test files focused on scenarios and assertions; move clients, containers, tokens, DI setup, and mock upstreams into fixtures.
- Use helper objects/dataclasses when a fixture returns multiple related resources.
- Keep top-level `tests/fixtures/` for reusable data/model fixtures that can be used by unit, integration, or future test types.
- Split shared fixture packages by responsibility when they grow. Prefer files such as `entities.py`, `services.py`, `builders.py`, or `payloads.py` over large catch-all modules.

## Change rules

- Do not couple unit tests to the real database or external APIs unless the test is explicitly integration-level.
- When adding behavior, cover the contract at the lowest sensible layer first.
- Keep fixture names and helpers aligned with the domain language used in `src/`.
- Ensure integration database fixtures start from a clean schema when containers are reused.
- Do not define `pytest_plugins` in nested `conftest.py`; register plugins from top-level `tests/conftest.py`.
- Document new fixture modules in `tests/README.md`.
- Keep test code, fixture names, helper class names, and code-facing comments in English.
- Keep test README and public test documentation in Russian.
