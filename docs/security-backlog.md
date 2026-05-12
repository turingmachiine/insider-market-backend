# Security Backlog

Этот документ фиксирует дальнейшую работу по доведению приложения до production-ready уровня безопасности.

## Цели

- Сделать авторизацию и права управляемыми из БД, а не из кода.
- Исключить bypass прав на уровне отдельных объектов.
- Закрыть внутренние сервисные вызовы и чувствительные операции.
- Добавить наблюдаемость и защиту от злоупотреблений.

## Принципы

- `Database as source of truth` для ролей, permissions и связей.
- `JWT` остается быстрым переносчиком identity/permissions, но не источником бизнес-истины.
- `Public by default` только для витринных `GET`, все mutating операции считаются защищенными.
- Любой доступ к чужому объекту должен проверяться отдельно от global permission.

## Backlog

### P0

#### 1. Object-level authorization

- Проверить доступ к конкретным сущностям: profile, wallet, team, market, event, notification.
- Убрать доверие к клиентским `user_id`/`X-User-ID` без сверки с токеном.
- Разделить `read own` и `read any`, где это необходимо.

Статус:

- `profile`: `profile_service` больше не доверяет `user_id` из тела создания профиля; владелец берется из `sub` JWT. Чтение чужого профиля, баланса, транзакций, активности и достижений требует `profile:read:any`, а изменение профиля и связанных пользовательских данных доступно только владельцу.
- `team`: `nsi_service` больше не доверяет `X-User-ID` при создании и чтении списка команд; владелец берется из `sub` JWT. Чтение чужой команды требует отдельного permission `team:read:any`, а изменение команды доступно только владельцу.
- `wallet`: `market_service` больше не доверяет `user_id` из тела создания кошелька и ставки; владелец берется из `sub` JWT. Чтение чужого кошелька требует `wallet:read:any`.
- `market`: `market_service` больше не доверяет `created_by_user_id` и `resolved_by_user_id` из тела запроса; actor берется из `sub` JWT.
- `event`: `event_service` больше не доверяет `created_by_user_id` и `resolved_by_user_id` из тела запроса; actor берется из `sub` JWT. Изменение и отправка на модерацию доступны только создателю event.
- `notification`: персональные stream/ws-подписки нельзя открыть на чужой `user_id` без `notification:read:any`.
- `rating`: `rating_service` больше не доверяет `user_id` из тела rating event; владелец берется из `sub` JWT. Чтение чужого rating profile и достижений требует `rating:read:any`.

Критерий готовности:

- Пользователь не может читать или менять чужой объект, даже если у него есть общий `*_READ` или `*_WRITE`.

#### 2. Token lifecycle

- Добавить refresh token flow.
- Продумать отзыв токенов после:
  - смены пароля,
  - деактивации пользователя,
  - смены ролей/permissions,
  - ручного revoke.
- Зафиксировать TTL access token и политику его обновления.

Статус:

- `auth_service` выдает пару `access_token` + `refresh_token` при `login`.
- `refresh_token` хранится в БД только в виде SHA-256 hash, имеет отдельный TTL `REFRESH_TOKEN_TTL` и ротируется при каждом `/refresh`.
- `/logout` отзывает конкретный refresh token, `/users/{user_id}/tokens/revoke` отзывает все refresh-сессии пользователя вручную.
- Деактивация пользователя и изменение роли отзывают все refresh-сессии пользователя.
- `access_token` остается stateless JWT для межсервисной проверки; изменение ролей/permissions начинает гарантированно действовать после истечения `JWT_TTL`, а новые access-токены через refresh получают актуальные permissions из БД.

Критерий готовности:

- Протухшие или отозванные токены больше не работают.
- Изменение прав пользователя начинает действовать предсказуемо и документировано.

#### 3. Service-to-service auth

- Защитить внутренние вызовы между сервисами.
- Отделить user auth от service auth.
- Ввести отдельные credentials или signed service tokens для gateway/BFF/internal clients.

Критерий готовности:

- Внутренний endpoint нельзя дернуть просто по сети без доверенного service identity.

### P1

#### 4. Audit log

- Логировать:
  - login/logout,
  - register,
  - role assignment,
  - permission changes,
  - wallet operations,
  - market resolution,
  - moderation actions.
- Сохранять actor, target, action, before/after, correlation id.

Критерий готовности:

- По audit trail можно восстановить, кто и что изменил.

#### 5. Rate limiting and brute-force protection

- Ограничить `login`, `register`, password reset, websocket connect.
- Добавить защиту от перебора паролей и массовых запросов.
- Сделать отдельные лимиты для public routes и sensitive routes.

Критерий готовности:

- Атаки перебора не дают бесконечные попытки и не создают шум в сервисах.

#### 6. Password security

- Проверить параметры hashing алгоритма.
- Добавить password policy.
- Добавить reset password flow.
- Продумать lockout / cooldown на неудачные попытки.

Критерий готовности:

- Пароли хранятся безопасно, а восстановление/смена пароля не ломают authorization model.

#### 7. Security headers and gateway hardening

- Зафиксировать security headers на gateway.
- Ограничить CORS.
- Проверить CSP, HSTS, X-Frame-Options, Referrer-Policy.

Критерий готовности:

- Gateway задает безопасный браузерный контур по умолчанию.

### P2

#### 8. Permission and role governance

- Добавить админские сценарии изменения ролей/permissions через БД.
- Сформировать seed/migration для базовых ролей и permissions.
- Убрать runtime dependency от кодовой карты permissions, оставив ее только как seed/reference.

Критерий готовности:

- Роли и permissions можно сопровождать без правок кода.

#### 9. Security observability

- Добавить алерты на:
  - всплески `401/403`,
  - brute-force попытки,
  - подозрительные admin actions,
  - repeated permission denied.
- Привязать security события к `request_id`/`user_id`.

Критерий готовности:

- Security инциденты видны в логах и метриках, а не ищутся вручную.

#### 10. Data and infrastructure scanning

- Проверить dependency scanning.
- Проверить image scanning.
- Зафиксировать process обновления зависимостей и базовых образов.

Критерий готовности:

- Известные CVE не игнорируются бесконечно.

## Recommended execution order

1. Object-level authorization.
2. Token lifecycle and revoke strategy.
3. Service-to-service auth.
4. Audit log.
5. Rate limiting and brute-force protection.
6. Password security.
7. Gateway hardening.
8. Permission governance.
9. Security observability.
10. Scanning and maintenance.

## Notes

- Public `GET`-эндпоинты остаются доступными без авторизации, но только если они не раскрывают приватные данные.
- Для защищенных endpoint’ов intent должен быть явным в коде через auth-decorator/permission dependency.
- Этот backlog нужно обновлять по мере закрытия пунктов и по мере появления новых сервисов или сценариев.
