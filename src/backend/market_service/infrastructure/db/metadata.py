from sqlalchemy.orm import registry

mapper_registry = registry()

__all__ = ["mapper_registry"]
