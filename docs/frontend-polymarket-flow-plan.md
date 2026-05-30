# План реализации frontend для "Инсайдер Маркет"

Документ обновлен после реализации backend-изменений в ветке
`feature/polymarket-changes`. Его можно использовать как рабочий план для FE.

## Backend Base URL

Frontend должен ходить через `api_gateway`.

Проксированные сервисы доступны по gateway-prefix:

- `event_service`: `/event/api/v1/...`
- `market_service`: `/market/api/v1/...`
- `rating_service`: `/rating/api/v1/...`
- `rumor_service`: `/rumor/api/v1/...`
- `profile_service`: `/profile/api/v1/...`
- `auth_service`: `/auth/api/v1/...`

Новый BFF endpoint главной витрины находится прямо в gateway:

- `GET /feed/home`

## Реализованные backend-контракты

### Главная витрина

`GET /feed/home`

Query:

- `limit`: number, `1..100`, default `20`
- `category`: optional event category

Response:

```ts
type HomeFeedResponse = {
  brand: "Инсайдер Маркет";
  filters: {
    events: EventCategory[];
    leaderboard: LeaderboardPeriod[];
  };
  main_event: EventCard | null;
  events: EventCard[];
  limit: number;
  category: EventCategory | null;
};
```

`main_event` выбирается backend по максимальному `bets_count` среди активных
событий в ответе.

### События

`GET /event/api/v1/events`

Query:

- `limit`: number, default `100`, max `500`
- `offset`: number, default `0`
- `status`: optional `draft | pending_moderation | active | rejected | resolved | cancelled`
- `category`: optional `transfers | matches | dismissals | titles | other`
- `sort`: optional `created_at | deadline_at | popularity`
- `source_rumor_id`: optional UUID

Response:

```ts
type EventListResponse = {
  items: EventResponse[];
  total: number;
  limit: number;
  offset: number;
};

type EventResponse = {
  id: string;
  title: string;
  description: string;
  category: EventCategory;
  status: EventStatus;
  source_rumor_id: string | null;
  candidate_payload: Record<string, unknown>;
  deadline_at: string | null;
  resolution_rules: string | null;
  outcome: "yes" | "no" | "void" | null;
  resolution_notes: string | null;
  created_by_user_id: string | null;
  resolved_by_user_id: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
};
```

`GET /event/api/v1/events/{event_id}` возвращает `EventResponse`.

`POST /event/api/v1/events/proposals` требует авторизации и permission
`EVENT_WRITE`. Использовать для формы "Предложить событие" из слуха.

Request:

```ts
type EventProposalCreate = {
  title: string;
  description: string;
  category: EventCategory;
  source_rumor_id: string;
  candidate_payload?: Record<string, unknown>;
  deadline_at?: string | null;
  resolution_rules?: string | null;
  submit_for_moderation?: boolean; // default true
};
```

### Markets и ставки

`GET /market/api/v1/markets`

Query:

- `limit`, `offset`
- `status`: optional `draft | active | paused | closed | resolved | cancelled`
- `event_id`: optional UUID

Response item:

```ts
type MarketResponse = {
  id: string;
  event_id: string;
  title: string;
  description: string;
  initial_probability: number;
  liquidity_parameter: number;
  yes_pool: number;
  no_pool: number;
  yes_probability: number;
  no_probability: number;
  yes_odds: number;
  no_odds: number;
  bets_count: number;
  status: MarketStatus;
  close_at: string | null;
  outcome: "yes" | "no" | "void" | null;
  created_by_user_id: string | null;
  resolved_by_user_id: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
};
```

`POST /market/api/v1/markets/{market_id}/bets` требует авторизации и permission
`MARKET_TRADE`.

Request:

```ts
type BetCreate = {
  side: "yes" | "no";
  amount: string | number;
};
```

Важно: `user_id` больше не передается с клиента. Backend берет пользователя из
JWT.

### Лидерборд

`GET /rating/api/v1/ratings/leaderboard`

Query:

- `limit`, `offset`
- `period`: `week | month | all_time`

Response:

```ts
type LeaderboardResponse = {
  items: LeaderboardEntry[];
  total: number;
  limit: number;
  offset: number;
  period: LeaderboardPeriod;
};

type LeaderboardEntry = {
  rank: number;
  profile: RatingProfile;
  achievements: RatingAchievement[];
  is_profile_public: boolean | null;
};
```

Backend уже принимает `period`, но текущая реализация пока возвращает
all-time рейтинг для всех периодов. FE должен сделать UI переключателя периода
с текущим контрактом, без клиентской пересборки статистики.

`is_profile_public` пока может быть `null`, потому что rating_service не
обогащает ответ данными profile_service. Для перехода в профиль использовать
дополнительную проверку `GET /profile/api/v1/profiles/public/{user_id}`.

### Публичные слухи

`GET /rumor/api/v1/rumors/public`

Query:

- `limit`, `offset`
- `event_id`: optional UUID

Response:

```ts
type PublicRumorListResponse = {
  items: PublicRumor[];
  total: number;
  limit: number;
  offset: number;
};

type PublicRumor = {
  rumor: RumorResponse;
  source: Record<string, unknown> | null;
};
```

`GET /rumor/api/v1/rumors/{rumor_id}` возвращает `RumorResponse`.

### Профили

`GET /profile/api/v1/profiles/public/{user_id}`

Response `200`: публичный профиль.

Response `404`: профиля нет или он приватный. FE должен трактовать это как
"профиль недоступен", а не как ошибку приложения.

`PATCH /profile/api/v1/profiles/{user_id}` требует авторизации владельца.
В форме профиля можно редактировать:

- `display_name`
- `bio`
- `avatar_url`
- `favorite_club`
- `is_public`

## Клиентские enum

```ts
type EventCategory =
  | "transfers"
  | "matches"
  | "dismissals"
  | "titles"
  | "other";

type EventSort = "created_at" | "deadline_at" | "popularity";

type LeaderboardPeriod = "week" | "month" | "all_time";

type MarketSide = "yes" | "no";
```

UI labels:

- `transfers`: "Трансферы"
- `matches`: "Игры"
- `dismissals`: "Отставки"
- `titles`: "Названия"
- `other`: "Другое"
- `week`: "За неделю"
- `month`: "За месяц"
- `all_time`: "За все время"

## Общая навигация

### Шапка

- Логотип/название: "Инсайдер Маркет".
- Первый ряд:
  - "События" -> `/events`
  - "Список лидеров" -> `/leaderboard`
  - "Последние новости" -> `/news`
- Правая часть:
  - анонимный пользователь: "Войти/Зарегистрироваться";
  - авторизованный пользователь: "Профиль".

### Второй ряд

- Для `/events`: category tabs.
- Для `/leaderboard`: period tabs.
- Для `/news`: второй ряд не отображается.

Состояние вкладок должно синхронизироваться с query string:

- `/events?category=transfers&sort=popularity`
- `/leaderboard?period=week`

## Главный экран `/`

Источник данных: `GET /feed/home`.

Показать:

- `main_event` как главный dashboard;
- список `events` под ним;
- вероятности `yes_probability`/`no_probability`;
- `bets_count`;
- дату разрешения `deadline_at`;
- кнопку ставки, если у карточки есть `market_id` и пользователь авторизован.

Если `main_event = null`, показывать пустое состояние и CTA перейти в
`/events`.

После успешной ставки инвалидировать:

- `GET /feed/home`
- `GET /market/api/v1/markets?event_id=...`
- `GET /event/api/v1/events...`

## Экран "События" `/events`

Источник событий: `GET /event/api/v1/events`.

Для каждой карточки дополнительно получить market:

- `GET /market/api/v1/markets?event_id={event.id}&limit=1`

Для первого релиза допустим N+1 запрос на market по карточкам. Если список
станет тяжелым, использовать только `/feed/home` для главной витрины или
добавить отдельный BFF endpoint.

Controls:

- view mode: list/card;
- category tabs;
- sort select:
  - `created_at`: "По дате создания";
  - `deadline_at`: "По дате разрешения";
  - `popularity`: "По популярности".

Карточка:

- `title`
- `description`
- `deadline_at`
- `category`
- market probability block, если market найден;
- `bets_count`;
- "Сделать ставку", если market active и пользователь авторизован.

Анонимный пользователь при клике на ставку открывает auth flow.

## Модальное окно ставки

Endpoint: `POST /market/api/v1/markets/{market_id}/bets`.

Поля:

- переключатель `yes/no`;
- amount;
- текущая вероятность выбранной стороны;
- кнопка подтверждения.

Backend preview endpoint пока не реализован. Для первого релиза не показывать
точный расчет shares до покупки; после покупки использовать `BetResponse` и
обновить market/card queries.

Обработать ошибки:

- `401/403`: открыть login или показать недостаточно прав;
- `400`: показать backend `detail`, например market inactive или wallet issue;
- network error: retry UI.

## Экран деталей события `/events/:eventId`

Источник:

- `GET /event/api/v1/events/{eventId}`
- `GET /market/api/v1/markets?event_id={eventId}&limit=1`
- `GET /rumor/api/v1/rumors/public?event_id={eventId}`
- если `source_rumor_id` есть: `GET /rumor/api/v1/rumors/{source_rumor_id}`

Показать:

- заголовок, описание, категорию, дату разрешения;
- probability dashboard по market;
- исходный слух, если `source_rumor_id` есть;
- публичные новости/слухи по событию;
- кнопку ставки для авторизованного пользователя.

Не реализовано на backend и не должно блокировать первый FE-релиз:

- чат события;
- форма отправки новости по событию;
- история изменения вероятности.

Для этих блоков оставить feature flag или скрыть.

## Экран "Список лидеров" `/leaderboard`

Источник: `GET /rating/api/v1/ratings/leaderboard?period=...`.

Показать:

- `rank`;
- рейтинг;
- ROI;
- accuracy;
- total predictions;
- current/best streak;
- achievements.

Визуальные правила:

- `rank=1`: коронка;
- `rank=1..3`: золото, серебро, бронза;
- achievements показывать компактными бейджами.

Переход в публичный профиль:

1. При клике на пользователя запросить
   `GET /profile/api/v1/profiles/public/{user_id}`.
2. Если `200`, перейти на `/users/{user_id}` и использовать полученные данные
   или закешировать query.
3. Если `404`, показать "Профиль закрыт".

## Экран "Последние новости" `/news`

Источник: `GET /rumor/api/v1/rumors/public`.

Показать:

- source name/type/url, если есть;
- `rumor.title`;
- `rumor.text`;
- `rumor.tags`;
- `rumor.published_at ?? rumor.created_at`;
- переход в `/news/:rumorId`.

## Детали слуха `/news/:rumorId`

Источник:

- `GET /rumor/api/v1/rumors/{rumorId}`
- при необходимости source уже можно взять из списка; отдельный source endpoint
  есть в rumor_service.

Для авторизованных пользователей показать "Предложить событие".

Форма отправляет:

- `POST /event/api/v1/events/proposals`

Request заполнять так:

- `source_rumor_id = rumor.id`
- `title`
- `description`
- `category`
- `deadline_at`
- `resolution_rules`
- `submit_for_moderation = true`

После успеха показать статус "Отправлено на модерацию" и ссылку на созданное
событие, если FE решит вести пользователя в детали draft/pending события.

## Профиль `/profile`

Для владельца использовать существующие protected endpoints:

- `GET /profile/api/v1/profiles/{user_id}`
- `PATCH /profile/api/v1/profiles/{user_id}`
- `GET /profile/api/v1/profiles/{user_id}/activity`
- `GET /profile/api/v1/profiles/{user_id}/achievements`
- `GET /rating/api/v1/ratings/profiles/{user_id}`

Форма личной информации:

- display name;
- bio;
- avatar url;
- favorite club;
- toggle `is_public`.

## Публичный профиль `/users/:userId`

Источник:

- `GET /profile/api/v1/profiles/public/{userId}`
- `GET /rating/api/v1/ratings/profiles/{userId}` может требовать auth по
  текущей security model; для первого релиза использовать только public profile,
  если rating profile недоступен.

Не показывать:

- баланс;
- balance transactions;
- приватную activity.

## Auth и capabilities

FE должен вычислять capabilities из auth-состояния и данных карточки:

```ts
type Capabilities = {
  canPlaceBet: boolean; // auth && market_id != null && market.status === "active"
  canProposeEvent: boolean; // auth
  canEditOwnProfile: boolean; // auth && profile.user_id === currentUser.id
  canOpenPublicProfile: boolean; // проверяется через public profile endpoint
};
```

После login возвращать пользователя к исходному действию:

- ставка;
- предложение события;
- переход в профиль.

## Рекомендуемые FE queries

- `homeFeed({ category, limit })`
- `events({ category, sort, status, limit, offset })`
- `eventDetails(eventId)`
- `marketByEvent(eventId)`
- `placeBet(marketId, { side, amount })`
- `leaderboard({ period, limit, offset })`
- `publicRumors({ limit, offset, eventId })`
- `rumorDetails(rumorId)`
- `proposeEventFromRumor(rumorId, payload)`
- `ownProfile(userId)`
- `updateOwnProfile(userId, payload)`
- `publicProfile(userId)`

## Приоритеты реализации

1. API client, DTO types, auth token handling.
2. Новая шапка и routing.
3. Главный экран на `/feed/home`.
4. `/events` со списком, фильтрами, сортировкой и market enrichment.
5. Модальное окно ставки.
6. `/events/:eventId` без чата и отправки новости.
7. `/leaderboard` с period tabs и profile availability check.
8. `/news` и `/news/:rumorId`.
9. Форма предложения события из слуха.
10. `/profile` с переключателем публичности.
11. `/users/:userId` public profile.

## Known Backend Gaps

- `leaderboard.period` принимается, но пока не меняет расчет.
- `LeaderboardEntry.is_profile_public` пока может быть `null`.
- Нет preview/quote endpoint для ставки.
- Нет event chat.
- Нет пользовательской отправки новости по событию.
- Нет probability history.
- Детали события не возвращают одним ответом source rumor + source + market;
  FE собирает эти данные несколькими запросами.

## Проверки перед релизом FE

- Публичные страницы открываются без JWT:
  - `/`
  - `/events`
  - `/events/:eventId`
  - `/leaderboard`
  - `/news`
  - `/news/:rumorId`
- Mutating actions без JWT переводят в auth flow.
- Ставка не отправляет `user_id`.
- После ставки обновляются вероятность и `bets_count`.
- Приватный профиль возвращает `404` и не раскрывает данные.
- Период leaderboard сохраняется в URL.
- Category/sort events сохраняются в URL.
- На мобильной ширине второй ряд фильтров не перекрывает контент.
