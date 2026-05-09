# Rumor Service

`rumor_service` отвечает за слухи, инсайды и публикации источников.


## Зона ответственности

- Хранение источников: Telegram-каналы, СМИ, инсайдеры.
- Хранение исходных публикаций и нормализованных rumor records.
- Расчет и хранение confidence score.
- Связь слуха с потенциальными событиями prediction market.
- История качества источников и признаков достоверности.

## Границы с другими сервисами

- Сбор сырых данных выполняет `etl_service`.
- Модерация и жизненный цикл событий находятся в `event_service`.
- Ставки и AMM находятся в `market_service`.
- Аналитика по пользователям и рейтингам находится в `rating_service`.

## Текущий статус

Сервис инициализирован как отдельный backend-сервис с собственной PostgreSQL
базой, Alembic-миграциями, DI-контейнером, SQLAlchemy imperative mapping и
FastAPI endpoints.

## API

Базовый путь через gateway: `/rumor/api/v1`.

- `GET /sources` — список источников.
- `POST /sources` — создать источник.
- `GET /sources/{source_id}` — получить источник.
- `POST /raw-publications` — сохранить сырую публикацию.
- `GET /raw-publications/{publication_id}` — получить сырую публикацию.
- `GET /raw-publications/source/{source_id}` — публикации источника.
- `GET /rumors` — список слухов с фильтрами по статусу и источнику.
- `POST /rumors` — создать нормализованный слух.
- `GET /rumors/{rumor_id}` — получить слух.
- `PATCH /rumors/{rumor_id}/status` — обновить статус слуха.
