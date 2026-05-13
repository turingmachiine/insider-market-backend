RATE_LIMIT_WINDOW_SECONDS = 60
TOO_MANY_REQUESTS_DETAIL = "Too Many Requests"

AUTH_SENSITIVE_ENDPOINTS = frozenset(
    {
        "login",
        "register",
        "refresh",
    }
)
