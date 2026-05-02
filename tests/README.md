# Тестовое пространство

Этот каталог содержит unit- и integration-тесты backend-сервисов.

## Структура

- `unit/{service}/` содержит изолированные тесты конкретного сервиса.
- `unit/nsi/domain/` содержит тесты доменных сущностей и сервисов NSI.
- `unit/nsi/processing/` содержит тесты расчетных сервисов NSI.
- `unit/nsi/presentation/` содержит тесты presentation-слоя NSI.
- `integration/{service}/` содержит тесты API, DI, репозиториев, БД и сервисных сценариев.
- `integration/api_gateway/` содержит тесты proxy, cache, rate-limit и swagger gateway.
- `integration/auth/` содержит интеграционные тесты auth API.
- `integration/nsi/` содержит интеграционные тесты NSI API и репозиториев.
- `fixtures/` содержит переиспользуемые фикстуры данных, builders и test helpers.
- `conftest.py` регистрирует только глобальные pytest plugins и общие настройки.
- `integration/conftest.py` намеренно тонкий: integration-specific фикстуры лежат рядом с тестами конкретного модуля.

## Модули фикстур

- `fixtures/shared/entities.py` создает in-memory доменные сущности NSI для unit-тестов.
- `fixtures/shared/services.py` создает экземпляры доменных сервисов.
- `integration/nsi/conftest.py` владеет NSI integration setup: контейнерами, engine/session, репозиториями, API client и Dishka container.
- `integration/auth/conftest.py` владеет auth integration setup: тестовой БД и API client.
- `integration/api_gateway/conftest.py` владеет gateway integration setup: Redis container, settings, upstream mocks, API clients и JWT helpers.

## Правила

- Тестовые файлы должны содержать сценарии и assertions, а не инфраструктурный setup.
- Переиспользуемые builders и model/data fixtures кладем в `tests/fixtures/`.
- Integration-only setup, контейнеры, клиенты, токены и DI wiring кладем в ближайший `conftest.py` соответствующего integration-модуля.
- Имена фикстур должны отражать язык домена: `api_client`, `auth_client`, `gateway_client`, `player_repository`.
- Интеграционные DB fixtures должны стартовать с чистой схемы. Если контейнер переиспользуется, используем `drop_all` + `create_all`.
- Не создаем application services, repositories, Redis clients или DI containers прямо внутри тестовых сценариев, если этим может владеть fixture.
- Если fixture возвращает несколько связанных ресурсов, используем небольшой helper object/dataclass.
- Unit-тесты не должны зависеть от Docker, Postgres, Redis, HTTP clients или Dishka containers.
- Integration-тесты могут использовать Testcontainers и ASGI clients, но внешние системы должны быть замоканы, если конкретная интеграционная граница не является предметом теста.

## Частые фикстуры

```python
async def test_api_flow(api_client):
    response = await api_client.get("/api/v1/players")
    assert response.status_code == 200
```

```python
async def test_gateway(gateway_client):
    client, calls, upstream_requests, redis_client = gateway_client
    response = await client.get("/auth/health")
    assert response.status_code == 200
```

```python
async def test_repository(player_repository, sample_player_entity):
    saved = await player_repository.save(sample_player_entity)
    assert saved.id == sample_player_entity.id
```

## Добавление тестов

- Новые фикстуры доменных объектов для unit-тестов добавляем в `fixtures/shared/entities.py`.
- Database-backed fixtures добавляем в `conftest.py` соответствующего integration-модуля.
- Новое поведение mock upstream для gateway добавляем в `integration/api_gateway/conftest.py`, а не внутрь test functions.
- Builders должны быть детерминированными, где это возможно; `uuid4()` используем только когда нужна уникальность.
- Новые integration-тесты кладем под сервис или boundary, которую они проверяют.
- Service-specific тесты храним в service module, например `integration/nsi/`, `integration/auth/` или `unit/nsi/`.
