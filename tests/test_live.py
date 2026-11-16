"""Check the models against the feeds splatoon3.ink serves now. Run with ``pytest -m live``."""

import pytest

from aiosplatoon3ink import Region, Splatoon3InkClient

pytestmark = pytest.mark.live

USER_AGENT = "aiosplatoon3ink-tests/1.0 (+https://github.com/regulad/aiosplatoon3ink)"


async def test_every_feed_parses() -> None:
    async with Splatoon3InkClient(USER_AGENT) as client:
        schedules = await client.schedules()
        gesotown = await client.gear()
        monthly_gear = await client.monthly_gear()
        festivals = await client.festivals()

    assert schedules.regular_schedules and schedules.coop_grouping_schedule.regular_schedules
    assert gesotown.limited_gears
    assert monthly_gear.name
    assert all(festivals.in_region(region) for region in Region)
