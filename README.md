# Football Research Insider Market

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **Платформа прогнозов на основе футбольных инсайдов. Превращаем слухи в игру.**

---

## 📖 Оглавление

- [Описание проекта](#описание-проекта)
- [Основная идея и концепция](#основная-идея-и-концепция)
- [Ключевые особенности](#ключевые-особенности)
- [Стек технологий](#стек-технологий)
- [Backend микросервисы](#backend-микросервисы)
- [Архитектура и конвенции](#архитектура-и-конвенции)
- [API Документация](#api-документация)
- [Разработка](#разработка)
- [Лицензия](#лицензия)

---

## Описание проекта

**Insider Market** — это веб-платформа, где пользователи делают прогнозы (ставят виртуальные токены) на достоверность футбольных инсайдов и слухов, публикуемых в Telegram-каналах и спортивных СМИ.

Система автоматически собирает инсайды, извлекает из них потенциальные события, предлагает их для модерации администратору, после чего пользователи могут делать ставки. По итогам ведется рейтинг пользователей на основе точности их прогнозов.

Проект сочетает в себе:
- Сложную **backend-архитектуру** (ETL, AMM, real-time updates)
- **Игровую механику** (ставки, рейтинги, достижения)
- **Интеграции с внешними сервисами** (Telegram API, спортивные API)
- **Удобный интерфейс для администратора** (модерация, управление событиями)
---

## Основная идея и концепция

### Проблема

В российском футболе существует огромное количество слухов и инсайдов — трансферы, увольнения тренеров, конфликты. Фанаты активно обсуждают их, но:
- Нет объективного способа проверить, кто из инсайдеров наиболее точен
- Нет игрового механизма, позволяющего "конвертировать" знание футбольной тусовки в соревновательный опыт
- Аналитика инсайдеров разрознена и не систематизирована

### Решение

**Insider Market** создает замкнутый цикл:
Инсайдер пишет пост → Система извлекает событие → Пользователи делают ставки
↓ ↓
Историческая аналитика ← Событие разрешается ← Рейтинг пользователей


### Ценность для разных аудиторий

| Аудитория | Что получает |
|-----------|--------------|
| **Футбольные фанаты** | Возможность проверить свою интуицию, посоревноваться с другими, следить за трансферными слухами |
| **Спортивные журналисты** | Объективный рейтинг точности инсайдеров, база подтвержденных слухов |
| **Аналитики и клубы** | Данные о достоверности различных источников, тренды в трансферном рынке |


---

## Ключевые особенности

### 🔄 Автоматический ETL пайплайн
- Парсинг Telegram-каналов топ-инсайдеров (Карпов, Егоров, Казаков)
- Rule-based извлечение событий из текста (без ML, чистая логика)
- Расчет confidence score для автоматического создания событий

### 🎮 Prediction Market с AMM
- Автоматический маркет-мейкер для динамических коэффициентов
- Коэффициенты меняются после каждой ставки (как на бирже)
- WebSocket для live-обновлений

### 👑 Система рейтинга
- Композитный Score: `Accuracy² × log₂(Bets + 1) × (1 + HighRiskBonus)`
- ELO рейтинг для более точного сравнения игроков
- Множественные периоды (all-time, сезон, месяц, неделя)

### 🛠️ Административная панель
- Модерация событий из очереди (с confidence score)
- Ручное создание/редактирование/резолв событий
- Управление источниками и весами инсайдеров
- Мониторинг "проблемных" событий (невалидные инсайды, ошибки парсинга)

### 🏆 Геймификация
- Система ачивок и достижений
- Еженедельные турниры
- Лиги друзей (приватные группы)

---
## Стек технологий

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0 (императивный маппинг)
- Dishka (DI)
- PostgreSQL
- Redis
- Alembic (миграции)
- Docker / Docker Compose
- pytest

## Backend микросервисы

Backend разделен на сервисы с отдельными зонами ответственности. Уже реализованные
сервисы описаны рядом с кодом, новые сервисы пока инициализированы документацией и
предназначены для дальнейшей реализации в том же стиле чистой архитектуры.

| Сервис | Назначение | Статус |
|--------|------------|--------|
| `api_gateway` | Единая точка входа, маршрутизация запросов, rate limit, CORS, проксирование во внутренние сервисы | Существует |
| `auth_service` | Аутентификация, пользователи как учетные записи, роли, permissions, JWT | Существует |
| `nsi_service` | Футбольный справочник и аналитическая база: игроки, клубы, лиги, команды, радары, похожие игроки, shadow-team | Существует |
| `etl_service` | ETL-пайплайны сбора Telegram/СМИ/спортивных API и подготовки сырых данных | Запланирован |
| `rumor_service` | Слухи и инсайды: источники, тексты публикаций, confidence score, кандидаты событий | Существует |
| `event_service` | События prediction market: доменная модель события, жизненный цикл, дедлайны, модерационные команды и резолюция исходов | Существует |
| `market_service` | Prediction Market и AMM: рынки, коэффициенты, ставки, ликвидность | Запланирован |
| `rating_service` | Рейтинги, accuracy, ELO, периодические лидерборды и расчет результатов | Запланирован |
| `profile_service` | Публичные профили пользователей, достижения, подписки, социальные связи | Запланирован |
| `notification_service` | WebSocket/SSE/live updates, уведомления о рынках, событиях, ставках и рейтингах | Запланирован |
| `admin_service` | Административная панель и BFF: кросс-сервисные операционные сценарии, аудит и управление через сервисы-владельцы | Запланирован |

Подробное описание каждого сервиса находится в `README.md` внутри
соответствующей директории `src/backend/{service_name}/`.

## Архитектура и конвенции

### Проект следует принципам чистой архитектуры:

```
src/
├── domain/              # Доменный слой
│   ├── entities/        # Сущности (Player, Club, League, Team)
│   ├── value_objects/   # Value Objects (Position)
│   └── repositories/    # Интерфейсы репозиториев
├── application/         # Application слой
│   ├── dto/            # Data Transfer Objects
│   ├── usecases/       # Use Cases
│   └── ports/          # Порты (интерфейсы)
├── infrastructure/      # Infrastructure слой
│   ├── db/             # База данных (ORM, репозитории)
│   ├── api_clients/    # Клиенты внешних API
│   └── logging/        # Логирование
├── processing/          # Обработка данных
│   ├── radar/          # Построение радар-чартов
│   ├── matching/       # Подбор похожих игроков
│   └── shadow_team/    # Формирование shadow-team
└── presentation/        # Presentation слой (API)
    └── api/v1/
        ├── routes/     # Endpoints
        └── schemas/    # Pydantic схемы
```

### Конвенции проекта

#### 1 файл = 1 класс

Каждый класс должен находиться в отдельном файле с соответствующим именем:

```
✅ Правильно:
src/core/mapping/
├── player_mapper.py      # class PlayerMapper
├── club_mapper.py        # class ClubMapper
└── league_mapper.py      # class LeagueMapper

❌ Неправильно:
src/core/mapping/
└── mappers.py            # class PlayerMapper, class ClubMapper, ...
```

**Исключения:**
- Вспомогательные функции/утилиты могут быть в одном файле
- `__init__.py` для экспортов

#### Внедрение зависимостей (DI)

Все зависимости внедряются через **dishka**. Запрещено создание зависимостей внутри классов:

```python
# ✅ Правильно
class PlayerUseCases:
    def __init__(
        self,
        player_repository: IPlayerRepository,
        player_mapper: PlayerMapper,
    ):
        self.player_repo = player_repository
        self.player_mapper = player_mapper

# ❌ Неправильно
class PlayerUseCases:
    def __init__(self, player_repository: IPlayerRepository):
        self.player_repo = player_repository
        self.player_mapper = PlayerMapper()  # Нельзя создавать внутри!
```

#### Маппинг между слоями

Используйте мапперы из `src/core/mapping/` вместо методов `from_entity()`:

```python
# ✅ Правильно
class PlayerMapper(Mapper[Player, PlayerDTO]):
    def to_dto(self, entity: Player) -> PlayerDTO:
        ...

# Использование через DI
class PlayerUseCases:
    def __init__(self, player_mapper: PlayerMapper):
        self.player_mapper = player_mapper

    async def get_player(self, player_id: UUID) -> Optional[PlayerDTO]:
        player = await self.player_repo.get_by_id(player_id)
        return self.player_mapper.to_dto(player) if player else None

# ❌ Неправильно
class PlayerDTO:
    @classmethod
    def from_entity(cls, player: Player) -> "PlayerDTO":
        ...

# Использование
player_dto = PlayerDTO.from_entity(player)
```

#### Структура мапперов

- **DTO мапперы**: `XxxMapper` с методами `to_dto()`, `to_entity()`
- **ORM мапперы**: `XxxORMMapper` с методами `to_orm()`, `to_entity()`
- **Create мапперы**: `CreateXxxMapper` с методом `create_entity()`
- **Update мапперы**: `UpdateXxxMapper` с методом `apply_to_entity()`

#### Слои приложения

- **Domain**: только бизнес-логика, нет зависимостей от других слоёв
- **Application**: use cases, DTO, порты
- **Infrastructure**: реализации репозиториев, ORM, внешние клиенты
- **Presentation**: API endpoints, Pydantic схемы

Зависимости: `Presentation → Application → Domain ← Infrastructure`

## API Документация

После запуска приложения:

- **Документация проекта**: http://localhost:8000/docs
- **Общий Swagger UI**: http://localhost:8000/swagger-ui
- **Общий OpenAPI JSON**: http://localhost:8000/swagger/swagger.json
- **Swagger UI отдельных сервисов**: ссылки доступны со страницы документации.

## Разработка

### Локальная разработка (рекомендуется)

```bash
# Копирование конфига
cp .env.example .env

# Запуск локального окружения (с hot-reload)
docker-compose -f docker-compose.local.yml up -d

# Просмотр логов
docker-compose -f docker-compose.local.yml logs -f app

# Остановка
docker-compose -f docker-compose.local.yml down
```

**Дополнительные сервисы для разработки:**

```bash
# Запуск с pgAdmin и Redis Commander
docker-compose -f docker-compose.local.yml --profile tools up -d
```

- pgAdmin: http://localhost:5050 (admin/admin)
- Redis Commander: http://localhost:8081

### Production

```bash
# Запуск production окружения
docker-compose up -d

# Просмотр логов
docker-compose logs -f app
```

### Локальная установка (без Docker)

```bash
# Установка uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Клонирование и установка
git clone https://github.com/yourusername/football-research.git
cd football-research
uv sync --dev

# Pre-commit хуки
pre-commit install

# Копирование конфига
cp .env.example .env

# Запуск
uv run python -m uvicorn src.backend.nsi_service.main:app --reload
```

### Использование скрипта миграций

```bash
# Создать новую миграцию
./scripts/migrate.sh migrate "Add new column"

# Применить все миграции
./scripts/migrate.sh upgrade

# Применить миграции Rumor Service
./scripts/migrate.sh rumor upgrade

# Откатить последнюю миграцию
./scripts/migrate.sh downgrade

# Показать текущую версию
./scripts/migrate.sh current

# Показать историю миграций
./scripts/migrate.sh history
```

### Прямое использование Alembic

```bash
# Создать миграцию
alembic -c migrations/nsi_service/alembic.ini revision --autogenerate -m "Description"

# Создать миграцию Rumor Service
alembic -c migrations/rumor_service/alembic.ini revision --autogenerate -m "Description"

# Применить миграции
alembic -c migrations/nsi_service/alembic.ini upgrade head

# Откатить на одну миграцию
alembic -c migrations/nsi_service/alembic.ini downgrade -1

# Показать текущую версию
alembic -c migrations/nsi_service/alembic.ini current
```

### Миграции в Docker

```bash
# Запуск миграций вручную
docker-compose run --rm migrations

# Для локальной разработки
docker-compose -f docker-compose.local.yml run --rm migrations
```

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=src --cov-report=html

# Конкретный тест
pytest tests/unit/domain/test_entities.py -v
```

### Проверка типов

```bash
mypy src/
```

### Линтинг

```bash
# Black форматирование
black src/ --check

# isort импорты
isort src/ --check

# flake8
flake8 src/
```

### Pre-commit хуки

Проект использует pre-commit для автоматических проверок:

```bash
# Установка
pre-commit install

# Запуск всех хуков
pre-commit run --all-files
```

Хуки включают:
- Black (форматирование)
- isort (сортировка импортов)

## Лицензия

MIT License
