from dataclasses import dataclass
from typing import dataclass_transform


@dataclass_transform(
    frozen_default=True,
    kw_only_default=True,
)
def use_case[T](cls: type[T]) -> type[T]:
    return dataclass(
        slots=True,
        repr=False,
        kw_only=True,
    )(cls)
