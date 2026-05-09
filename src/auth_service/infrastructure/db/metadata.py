from sqlalchemy.orm import registry

mapper_registry = registry()


class Base:
    """Compatibility wrapper for metadata consumers."""

    metadata = mapper_registry.metadata
