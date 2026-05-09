# ETL Service

`etl_service` отвечает за регулярный сбор, очистку и подготовку внешних данных.

## Зона ответственности

- Сбор публикаций из Telegram-каналов и спортивных СМИ.
- Сбор футбольных данных из внешних спортивных API.
- Нормализация сырых payloads и сохранение источников для аудита.
- Запуск rule-based извлечения кандидатов слухов и событий.
- Передача подготовленных данных в `rumor_service` и `nsi_service`.

## Предпочтительная технология

Для запуска ETL используется Taskiq:

- async-first task queue без тяжелой orchestration-платформы;
- cron-расписания через `LabelScheduleSource`;
- Redis broker через `taskiq-redis`;
- официальная интеграция с Dishka.

## Границы сервиса

- ETL не принимает пользовательские ставки.
- ETL не модерирует события.
- ETL не является публичным API для frontend.

## Текущий статус

Сервис реализован как Taskiq-оркестрируемый backend-компонент без публичного
HTTP API. Taskiq task handlers находятся в presentation-слое, бизнес-логика
вынесена в application use cases, а интеграции с `rumor_service`, внешними
источниками, Redis broker и Taskiq scheduler находятся в infrastructure.

Зависимости собираются через Dishka-контейнер в `infrastructure/di`. Taskiq
tasks получают use cases через `dishka.integrations.taskiq` и не создают
HTTP-клиенты, fetchers, extractors или use cases напрямую.

## Реализованные джобы

### `insider_market_backend_import_raw_publications`

Периодически получает активные источники из `rumor_service`, забирает новые
публикации из Telegram/медиа/API источников и создает сырые публикации через
`rumor_service`.

Основной use case:

- `ImportRawPublicationsUseCase`

Порты:

- `RumorServicePort`
- `PublicationFetcher`

### `insider_market_backend_normalize_rumors`

Периодически получает сырые публикации из `rumor_service`, применяет rule-based
извлечение слухов и создает нормализованные кандидаты слухов со статусом
`candidate`.

Основной use case:

- `NormalizeRumorsUseCase`

Порты:

- `RumorServicePort`
- `RumorExtractor`

## Структура

```text
src/etl_service/
├── application/
│   ├── dto/
│   ├── ports/
│   └── usecases/
├── domain/
│   └── entities/
├── infrastructure/
│   ├── clients/
│   ├── di/
│   ├── extractors/
│   ├── fetchers/
│   └── taskiq/
└── presentation/
    └── taskiq/
```

## Настройки

- `RUMOR_SERVICE_URL` — URL `rumor_service`.
- `TASKIQ_REDIS_URL` — Redis URL для Taskiq broker.
- `TASKIQ_QUEUE_NAME` — имя очереди Taskiq.
- `RAW_IMPORT_CRON` — расписание импорта сырых публикаций.
- `RUMOR_NORMALIZATION_CRON` — расписание нормализации слухов.
- `SOURCE_FETCH_LIMIT` — максимальное число публикаций за один проход источника.
- `RAW_PUBLICATIONS_LIMIT` — размер окна сырых публикаций для проверки дублей.
- `EXISTING_RUMORS_LIMIT` — размер окна слухов для проверки уже обработанных публикаций.

## Границы реализации

- ETL не пишет напрямую в таблицы `rumor_service`.
- ETL не импортирует репозитории или ORM-модели `rumor_service`.
- ETL не модерирует события и не создает рынки prediction market.
- Taskiq tasks только запускают application use cases, полученные через DI.

## Запуск

Worker:

```bash
taskiq worker src.etl_service.infrastructure.taskiq.broker:broker
```

Scheduler:

```bash
taskiq scheduler src.etl_service.infrastructure.taskiq.scheduler:scheduler
```

Docker Compose:

```bash
docker compose --profile etl up etl_worker etl_scheduler
```

## Реализации портов

- `RumorServicePort` → `RumorServiceHttpClient`.
- `PublicationFetcher` → `HttpPublicationFetcher`.
- `RumorExtractor` → `RuleBasedRumorExtractor`.
