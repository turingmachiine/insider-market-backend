# Event Service

`event_service` управляет событиями prediction market.

## Зона ответственности

- Создание событий из rumor candidates.
- Хранение очереди событий, ожидающих модерации.
- Ручное создание и редактирование событий.
- Управление статусами и допустимыми переходами: draft,
  pending moderation, active, rejected, resolved, cancelled.
- Хранение дедлайнов и правил резолюции.
- Фиксация итогового исхода события.
- Доменные команды approve, reject, resolve и cancel для событий.

## Границы с другими сервисами

- `rumor_service` хранит исходные слухи и публикации.
- `market_service` создает и обслуживает рынки по активным событиям.
- `rating_service` пересчитывает пользовательские результаты после резолюции.
- `admin_service` может предоставлять удобный BFF для административных сценариев,
  но не должен владеть доменной моделью события или самостоятельно менять
  жизненный цикл события в обход `event_service`.
- `auth_service` отвечает за роли и permissions администраторов, а
  `event_service` проверяет, что вызывающая сторона имеет право выполнить
  доменную команду.

## API

Базовый путь через gateway: `/event/api/v1`.

- `GET /events` — список событий с фильтрами по статусу и исходному слуху.
- `POST /events` — создать событие вручную или из rumor candidate payload.
- `GET /events/{event_id}` — получить событие.
- `PATCH /events/{event_id}` — обновить редактируемые детали события.
- `GET /events/moderation-queue` — очередь событий, ожидающих модерации.
- `POST /events/{event_id}/submit-moderation` — отправить draft на модерацию.
- `POST /events/{event_id}/approve` — активировать событие после модерации.
- `POST /events/{event_id}/reject` — отклонить событие на модерации.
- `POST /events/{event_id}/resolve` — зафиксировать outcome события.
- `POST /events/{event_id}/cancel` — отменить событие до terminal-статуса.

## Текущий статус

Сервис инициализирован как отдельный backend-сервис с собственной PostgreSQL
базой, Alembic-миграциями, DI-контейнером, SQLAlchemy imperative mapping и
FastAPI endpoints.
