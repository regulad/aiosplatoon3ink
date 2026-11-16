"""Models for https://splatoon3.ink/data/gear.json and https://splatoon3.ink/data/coop.json: gear on sale at SplatNet's
shop, and the month's Salmon Run reward gear.

The gear feed is SplatNet 3's ``GesotownQuery`` response, and the co-op feed its ``CoopHistoryQuery`` response. Fields
about splatoon3.ink's own account, such as its orders and Salmon Run record, are left out.
"""

from enum import StrEnum

from pydantic import AwareDatetime, Field

from aiosplatoon3ink._base import Image, Splatoon3InkModel


class GearKind(StrEnum):
    """Where a piece of gear is worn."""

    HEAD = "HeadGear"
    CLOTHING = "ClothingGear"
    SHOES = "ShoesGear"


class GearPower(Splatoon3InkModel):
    """A gear ability."""

    splatoon3ink_id: str = Field(alias="__splatoon3ink_id")
    """A stable ID that splatoon3.ink derives from the ability, to look it up in its translations."""
    name: str
    image: Image


class UsualGearPower(GearPower):
    """The ability a brand favours in gear's additional slots."""

    desc: str
    is_empty_slot: bool


class Brand(Splatoon3InkModel):
    """A gear brand. Each place SplatNet lists a brand includes different details of it."""

    id: str
    name: str
    image: Image | None = None
    usual_gear_power: UsualGearPower | None = None


class Gear(Splatoon3InkModel):
    """A piece of gear, with the abilities it comes with."""

    splatoon3ink_id: str = Field(alias="__splatoon3ink_id")
    """A stable ID that splatoon3.ink derives from the gear, to look it up in its translations."""
    kind: GearKind = Field(alias="__typename")
    name: str
    image: Image
    brand: Brand
    primary_gear_power: GearPower
    additional_gear_powers: tuple[GearPower, ...]


class SaleGear(Splatoon3InkModel):
    """Gear on sale at SplatNet's shop."""

    id: str
    sale_end_time: AwareDatetime
    price: int
    gear: Gear


class PickupBrand(Splatoon3InkModel):
    """The brand of the day, and its gear on sale."""

    brand: Brand
    image: Image
    sale_end_time: AwareDatetime
    brand_gears: tuple[SaleGear, ...]
    next_brand: Brand


class Gesotown(Splatoon3InkModel):
    """Everything on sale at SplatNet's shop."""

    pickup_brand: PickupBrand
    limited_gears: tuple[SaleGear, ...]
    """The gear on sale for a limited time, each on its own schedule."""


class _GesotownData(Splatoon3InkModel):
    gesotown: Gesotown


class _GearFeed(Splatoon3InkModel):
    data: _GesotownData


class MonthlyGear(Splatoon3InkModel):
    """The month's Salmon Run reward gear."""

    splatoon3ink_id: str = Field(alias="__splatoon3ink_id")
    """A stable ID that splatoon3.ink derives from the gear, to look it up in its translations."""
    kind: GearKind = Field(alias="__typename")
    name: str
    image: Image


class _CoopResult(Splatoon3InkModel):
    monthly_gear: MonthlyGear


class _CoopData(Splatoon3InkModel):
    coop_result: _CoopResult


class _CoopFeed(Splatoon3InkModel):
    data: _CoopData


__all__ = [
    "Brand",
    "Gear",
    "GearKind",
    "GearPower",
    "Gesotown",
    "MonthlyGear",
    "PickupBrand",
    "SaleGear",
    "UsualGearPower",
]
