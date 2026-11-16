"""An asyncio client for the Splatoon 3 data that splatoon3.ink publishes, with typed models of each feed.

>>> async with Splatoon3InkClient("MyBot/1.0 (+https://github.com/me/mybot)") as client:
...     schedules = await client.schedules()

The models live in :mod:`aiosplatoon3ink.schedules`, :mod:`aiosplatoon3ink.festivals` and :mod:`aiosplatoon3ink.gear`.
"""

from aiosplatoon3ink._base import Color, Image
from aiosplatoon3ink._client import DEFAULT_BASE_URL, Splatoon3InkClient
from aiosplatoon3ink.festivals import Festivals, Region
from aiosplatoon3ink.gear import Gesotown, MonthlyGear
from aiosplatoon3ink.schedules import Schedules

__all__ = [
    "DEFAULT_BASE_URL",
    "Color",
    "Festivals",
    "Gesotown",
    "Image",
    "MonthlyGear",
    "Region",
    "Schedules",
    "Splatoon3InkClient",
]
