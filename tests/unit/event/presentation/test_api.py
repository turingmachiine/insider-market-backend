from src.event_service.main import app


def test_health_route_is_registered() -> None:
    health_routes = [
        route
        for route in app.routes
        if getattr(route, "path", None) == "/health"
        and "GET" in getattr(route, "methods", set())
    ]

    assert len(health_routes) == 1


def test_openapi_contains_event_routes() -> None:
    schema = app.openapi()

    assert "/api/v1/events" in schema["paths"]
    assert "/api/v1/events/moderation-queue" in schema["paths"]
    assert "/api/v1/events/{event_id}/approve" in schema["paths"]
    assert "/api/v1/events/{event_id}/resolve" in schema["paths"]
