# Football Research Application

Многомодульное приложение для футбольной аналитики с чистой архитектурой.

## Возможности

- 📊 Сбор статистики с популярных платформ (FBRef, Transfermarkt, Understat)
- 📈 Построение графиков-радаров для сравнения игроков со средними значениями в лиге
- 🔍 Поиск похожих игроков с учетом силы чемпионата
- 🏆 Формирование shadow-team для усиления состава
- 📚 Полная документация API (Swagger/ReDoc)

## Технологии

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0 (императивный маппинг)
- Dishka (DI)
- PostgreSQL
- Redis
- Alembic (миграции)
- Docker / Docker Compose
- pytest

## Архитектура

Проект следует принципам чистой архитектуры:

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

## Конвенции проекта

### 1 файл = 1 класс

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

### Внедрение зависимостей (DI)

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

### Маппинг между слоями

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

### Структура мапперов

- **DTO мапперы**: `XxxMapper` с методами `to_dto()`, `to_entity()`
- **ORM мапперы**: `XxxORMMapper` с методами `to_orm()`, `to_entity()`
- **Create мапперы**: `CreateXxxMapper` с методом `create_entity()`
- **Update мапперы**: `UpdateXxxMapper` с методом `apply_to_entity()`

### Слои приложения

- **Domain**: только бизнес-логика, нет зависимостей от других слоёв
- **Application**: use cases, DTO, порты
- **Infrastructure**: реализации репозиториев, ORM, внешние клиенты
- **Presentation**: API endpoints, Pydantic схемы

Зависимости: `Presentation → Application → Domain ← Infrastructure`

## Лучшие практики чистого кода

### Именование переменных

```python
# ✅ Правильно - понятные имена
for league in leagues:
    process(league)

# ❌ Неправильно - однобуквенные имена (кроме циклов)
for l in leagues_list:
    process(l)
```

### Избегайте магических чисел

```python
# ✅ Правильно
MAX_PLAYERS_PER_TEAM = 25
DEFAULT_PAGE_LIMIT = 50

# ❌ Неправильно
if len(players) > 25:
    ...
```

### Функции должны делать одно дело

```python
# ✅ Правильно
def create_player(dto: CreatePlayerDTO) -> Player:
    player = mapper.create_entity(dto)
    return repository.save(player)

# ❌ Неправильно
def create_player(dto):
    # Валидация, маппинг, сохранение, логирование - всё в одной функции
    ...
```

### Используйте Type Hints

```python
# ✅ Правильно
def get_player(player_id: UUID) -> Optional[PlayerDTO]:
    ...

# ❌ Неправильно
def get_player(player_id):
    ...
```

### Избегайте глубокой вложенности

```python
# ✅ Правильно - guard clauses
def process_player(player: Player) -> None:
    if not player.is_active:
        return
    if player.age < 18:
        return
    # основная логика

# ❌ Неправильно - глубокая вложенность
def process_player(player: Player) -> None:
    if player.is_active:
        if player.age >= 18:
            # основная логика
```

### Документирование

```python
# ✅ Правильно
class PlayerRepository:
    """Репозиторий для работы с игроками"""

    async def get_by_id(self, player_id: UUID) -> Optional[Player]:
        """Получить игрока по ID"""
```

### Обработка ошибок

```python
# ✅ Правильно - конкретные исключения
try:
    player = await repo.get_by_id(player_id)
except PlayerNotFoundError:
    raise HTTPException(status_code=404)

# ❌ Неправильно - bare except
try:
    player = await repo.get_by_id(player_id)
except:
    pass
```

### Тесты

```python
# ✅ Правильно - один assert на концепцию
def test_create_player():
    player = create_player(dto)
    assert player.id is not None
    assert player.name == dto.name

# ❌ Неправильно - слишком много проверок
def test_everything():
    # 50 строк с разными проверками
```

## Быстрый старт

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
uv run python -m uvicorn src.main:app --reload
```

## API Документация

После запуска приложения:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

## Основные эндпоинты

### Игроки
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/players` | Список игроков с пагинацией |
| GET | `/api/v1/players/search?name=...` | Поиск по имени |
| GET | `/api/v1/players/{id}` | Получить игрока по ID |
| POST | `/api/v1/players` | Создать игрока |
| PATCH | `/api/v1/players/{id}` | Обновить игрока |
| DELETE | `/api/v1/players/{id}` | Удалить игрока |
| GET | `/api/v1/players/{id}/radar` | Радар-чарт игрока |
| GET | `/api/v1/players/{id}/similar` | Похожие игроки |
| GET | `/api/v1/players/position/{position}` | Игроки по позиции |
| GET | `/api/v1/players/league/{league_id}` | Игроки лиги |
| GET | `/api/v1/players/club/{club_id}` | Игроки клуба |

### Клубы
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/clubs` | Список клубов |
| GET | `/api/v1/clubs/search?name=...` | Поиск клубов |
| GET | `/api/v1/clubs/{id}` | Получить клуб |
| POST | `/api/v1/clubs` | Создать клуб |
| GET | `/api/v1/clubs/league/{league_id}` | Клубы лиги |

### Лиги
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/leagues` | Список лиг |
| GET | `/api/v1/leagues/top` | Топ лиги |
| GET | `/api/v1/leagues/search?name=...` | Поиск лиг |
| GET | `/api/v1/leagues/{id}` | Получить лигу |
| POST | `/api/v1/leagues` | Создать лигу |

### Команды пользователей
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/teams` | Команды пользователя |
| GET | `/api/v1/teams/{id}` | Получить команду |
| POST | `/api/v1/teams` | Создать команду |
| POST | `/api/v1/teams/{id}/players` | Добавить игрока |
| DELETE | `/api/v1/teams/{id}/players` | Удалить игрока |
| POST | `/api/v1/teams/{id}/shadow-team` | Построить shadow-team |

## Миграции базы данных

### Использование скрипта миграций

```bash
# Создать новую миграцию
./scripts/migrate.sh migrate "Add new column"

# Применить все миграции
./scripts/migrate.sh upgrade

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
alembic revision --autogenerate -m "Description"

# Применить миграции
alembic upgrade head

# Откатить на одну миграцию
alembic downgrade -1

# Показать текущую версию
alembic current
```

### Миграции в Docker

```bash
# Запуск миграций вручную
docker-compose run --rm migrations

# Для локальной разработки
docker-compose -f docker-compose.local.yml run --rm migrations
```

## Разработка

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

### Настройка PyCharm

Для корректной работы импортов в PyCharm:

1. Запустите скрипт настройки:
   ```bash
   ./scripts/setup-pycharm.sh
   ```

2. Выполните **File → Invalidate Caches... → Invalidate and Restart**

3. После перезагрузки:
   - ПКМ на `src` → **Mark Directory as** → **Sources Root**
   - ПКМ на `tests` → **Mark Directory as** → **Tests Root**

4. Проверьте **Settings → Project → Project Structure**:
   - `src` должна быть помечена как **Sources** (синяя)
   - `tests` должна быть помечена как **Tests** (зелёная)
   - Вложенные папки (`core`, `domain`, etc.) **не** должны быть Sources

📖 Подробная инструкция: [docs/pycharm-setup.md](docs/pycharm-setup.md)
- flake8 (линтинг)
- mypy (проверка типов)
- Проверка YAML/JSON/TOML

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `POSTGRES_USER` | Пользователь PostgreSQL | `postgres` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | `postgres` |
| `POSTGRES_HOST` | Хост PostgreSQL | `localhost` |
| `POSTGRES_PORT` | Порт PostgreSQL | `5432` |
| `POSTGRES_DB` | Имя базы данных | `football_db` |
| `REDIS_URL` | URL Redis | `redis://localhost:6379` |
| `DEBUG` | Режим отладки | `false` |
| `LOG_LEVEL` | Уровень логов | `INFO` |
| `PORT` | Порт приложения | `8000` |
| `WORKERS` | Количество workers | `4` |

## Структура миграций

```
alembic/
├── versions/
│   ├── 001_initial.py    # Начальная миграция
│   └── ...
├── env.py                 # Конфигурация окружения
└── script.py.mako         # Шаблон миграций
```

## Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменений (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## Лицензия

MIT License
