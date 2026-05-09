from sqlalchemy.orm import registry

mapper_registry = registry()

metadata = mapper_registry.metadata

__all__ = ["mapper_registry", "metadata"]
