from src.rumor_service.main import app


def test_health_route_is_registered() -> None:
    health_routes = [
        route
        for route in app.routes
        if getattr(route, "path", None) == "/health"
        and "GET" in getattr(route, "methods", set())
    ]

    assert len(health_routes) == 1


def test_openapi_contains_rumor_routes() -> None:
    schema = app.openapi()

    assert "/api/v1/sources" in schema["paths"]
    assert "/api/v1/raw-publications" in schema["paths"]
    assert "/api/v1/rumors" in schema["paths"]
    assert "/api/v1/rumors/{rumor_id}/status" in schema["paths"]
