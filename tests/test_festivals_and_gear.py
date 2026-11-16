from datetime import UTC, datetime

from conftest import fixture

from aiosplatoon3ink.festivals import FestState, Festivals, Region
from aiosplatoon3ink.gear import GearKind, _CoopFeed, _GearFeed


def festivals() -> Festivals:
    return Festivals.model_validate_json(fixture("festivals.json"))


def test_every_region_lists_every_splatfest_newest_first() -> None:
    feed = festivals()

    for region in Region:
        fests = feed.in_region(region)
        assert len(fests) == 30
        assert fests[0].start_time == datetime(2026, 10, 31, tzinfo=UTC)
        assert fests[-1].start_time.year == 2022
    assert feed.in_region(Region.US)[0].title == "What would you be in a fantasy world?"
    assert feed.in_region(Region.JP)[0].title == "ファンタジーの世界に飛びこむなら？"


def test_splatfest_results() -> None:
    fest = festivals().in_region(Region.US)[0]

    assert fest.state is FestState.CLOSED
    assert fest.regions == frozenset(Region)
    assert fest.has_results
    assert len(fest.teams) == 3
    winners = [team for team in fest.teams if team.result is not None and team.result.is_winner]
    assert len(winners) == 1
    results = [team.result for team in fest.teams if team.result is not None]
    assert abs(sum(result.vote_ratio for result in results) - 1) < 0.01


def test_first_splatfest_predates_tricolor_scoring() -> None:
    first = festivals().in_region(Region.US)[-1]

    assert all(team.result is not None and team.result.tricolor_contribution_ratio is None for team in first.teams)


def test_gear() -> None:
    gesotown = _GearFeed.model_validate_json(fixture("gear.json")).data.gesotown

    assert gesotown.pickup_brand.brand.name == "Firefin"
    assert gesotown.pickup_brand.brand.usual_gear_power is not None
    assert gesotown.pickup_brand.next_brand.name == "SquidForce"
    assert len(gesotown.limited_gears) == 6
    first = gesotown.limited_gears[0]
    assert first.gear.kind is GearKind.HEAD
    assert first.gear.name == "Mountie Hat"
    assert first.price == 19500
    assert len(first.gear.additional_gear_powers) == 3


def test_monthly_gear() -> None:
    gear = _CoopFeed.model_validate_json(fixture("coop.json")).data.coop_result.monthly_gear

    assert gear.name == "Octavio Dome"
    assert gear.kind is GearKind.HEAD
