from pathlib import Path


class SwaggerResourcePaths:
    def __init__(self, resource_root: Path | None = None) -> None:
        self._resource_root = resource_root or self._default_resource_root()

    @property
    def html_template(self) -> Path:
        return self._resource_root / "index.html"

    @property
    def static_root(self) -> Path:
        return self._resource_root

    @property
    def resource_root(self) -> Path:
        return self._resource_root

    @staticmethod
    def _default_resource_root() -> Path:
        project_root = Path(__file__).resolve().parents[4]
        return project_root / "resources" / "api_gateway" / "swagger"


class SwaggerLandingPage:
    def __init__(self, resource_paths: SwaggerResourcePaths | None = None) -> None:
        self._resource_paths = resource_paths or SwaggerResourcePaths()
        self._html: str | None = None

    def render(self) -> str:
        if self._html is None:
            self.load()
        return self._html or ""

    def load(self) -> str:
        self._html = self._resource_paths.html_template.read_text(encoding="utf-8")
        return self._html

    @property
    def resource_paths(self) -> SwaggerResourcePaths:
        return self._resource_paths
