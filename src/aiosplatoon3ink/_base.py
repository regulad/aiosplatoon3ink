"""The pieces every splatoon3.ink model shares."""

from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict
from pydantic.alias_generators import to_camel


class Splatoon3InkModel(BaseModel):
    """Base of every model: immutable, and read from the feeds' camelCase keys.

    Fields the models don't declare are ignored, so splatoon3.ink can add fields without breaking anything. Models can
    also be built by their Python field names, as tests that make their own data do.
    """

    model_config = ConfigDict(alias_generator=to_camel, frozen=True, validate_by_name=True)


def _unwrap_nodes(value: Any) -> Any:
    # SplatNet's GraphQL connections wrap their lists as {"nodes": [...]}.
    if isinstance(value, dict) and "nodes" in value:
        return value["nodes"]
    return value


type Nodes[T] = Annotated[tuple[T, ...], BeforeValidator(_unwrap_nodes)]
"""A GraphQL connection, read as the tuple of its nodes."""


class Image(Splatoon3InkModel):
    """An image, served from splatoon3.ink's own copy of SplatNet's assets."""

    url: str


class Color(Splatoon3InkModel):
    """A colour, with each channel from 0 to 1."""

    r: float
    g: float
    b: float
    a: float = 1.0

    @property
    def rgb(self) -> tuple[int, int, int]:
        """The red, green and blue channels, each from 0 to 255."""
        return round(self.r * 255), round(self.g * 255), round(self.b * 255)


__all__ = ["Color", "Image", "Nodes", "Splatoon3InkModel"]
