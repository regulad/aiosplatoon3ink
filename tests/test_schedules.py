from datetime import UTC, datetime, timedelta

from conftest import fixture

from aiosplatoon3ink.festivals import FestState
from aiosplatoon3ink.schedules import BankaraMode, CoopRule, FestMode, Schedules, TimePeriod, VsRuleKey, _SchedulesFeed


def schedules(name: str) -> Schedules:
    return _SchedulesFeed.model_validate_json(fixture(name)).data


def test_battle_rotations_without_a_splatfest() -> None:
    feed = schedules("schedules.json")

    regular = feed.regular_schedules[0].regular_match_setting
    assert regular is not None
    assert regular.vs_rule.rule is VsRuleKey.TURF_WAR
    assert len(regular.vs_stages) == 2
    assert feed.regular_schedules[0].start_time == datetime(2026, 11, 16, 8, tzinfo=UTC)

    anarchy = feed.bankara_schedules[0]
    series, open_ = anarchy.setting(BankaraMode.SERIES), anarchy.setting(BankaraMode.OPEN)
    assert series is not None and series.vs_rule.rule is VsRuleKey.RAINMAKER
    assert open_ is not None and open_.vs_rule.rule is VsRuleKey.TOWER_CONTROL

    assert feed.x_schedules[0].x_match_setting is not None
    assert all(node.fest_match_settings is None for node in feed.fest_schedules)
    assert feed.current_fest is None


def test_challenge_events() -> None:
    event = schedules("schedules.json").event_schedules[0]

    assert event.league_match_setting.league_match_event.name == "Ultra Stamp Rally"
    assert event.league_match_setting.vs_rule.rule is VsRuleKey.TOWER_CONTROL
    assert len(event.time_periods) == 6
    assert event.time_periods[0].end_time - event.time_periods[0].start_time == timedelta(hours=2)


def test_salmon_run() -> None:
    coop = schedules("schedules.json").coop_grouping_schedule

    rotation = coop.regular_schedules[0]
    assert rotation.setting.coop_stage.name == "Bonerattle Arena"
    assert rotation.setting.boss is not None and rotation.setting.boss.name == "Megalodontia"
    assert rotation.king_salmonid_guess == "Megalodontia"
    assert [weapon.name for weapon in rotation.setting.weapons] == [
        "Splash-o-matic",
        "Inkbrush",
        ".52 Gal",
        "Jet Squelcher",
    ]
    assert coop.big_run_schedules == coop.team_contest_schedules == ()


def test_big_run() -> None:
    big_run = schedules("schedules-big-run.json").coop_grouping_schedule.big_run_schedules[0]

    assert big_run.setting.rule is CoopRule.BIG_RUN
    assert big_run.setting.boss is not None and big_run.setting.boss.name == "Triumvirate"
    assert {weapon.name for weapon in big_run.setting.weapons} == {"Random"}


def test_eggstra_work() -> None:
    coop = schedules("schedules-eggstra-work.json").coop_grouping_schedule

    eggstra_work = coop.team_contest_schedules[0]
    assert eggstra_work.setting.rule is CoopRule.EGGSTRA_WORK
    assert eggstra_work.setting.boss is None
    assert coop.banner_image is not None


def test_splatfest_replaces_other_battles() -> None:
    feed = schedules("schedules-splatfest.json")

    assert feed.regular_schedules[0].regular_match_setting is None
    assert feed.bankara_schedules[0].bankara_match_settings is None
    assert feed.x_schedules[0].x_match_setting is None

    fest_rotation = next(node for node in feed.fest_schedules if node.fest_match_settings)
    open_, pro = fest_rotation.setting(FestMode.OPEN), fest_rotation.setting(FestMode.PRO)
    assert open_ is not None and [stage.name for stage in open_.vs_stages] == ["Wahoo World", "Robo ROM-en"]
    assert pro is not None and pro.vs_rule.rule is VsRuleKey.TURF_WAR


def test_current_splatfest() -> None:
    fest = schedules("schedules-splatfest.json").current_fest

    assert fest is not None
    assert fest.state is FestState.FIRST_HALF
    assert fest.midterm_time == datetime(2026, 1, 11, tzinfo=UTC)
    assert len(fest.teams) == 3
    assert fest.teams[0].color.rgb == (61, 98, 199)
    assert fest.tricolor_stages is not None
    assert [stage.name for stage in fest.tricolor_stages] == ["Brinewater Springs", "MakoMart"]


def test_scheduled_splatfest() -> None:
    fest = schedules("schedules-splatfest-scheduled.json").current_fest

    assert fest is not None and fest.state is FestState.SCHEDULED


def test_stage_pictures() -> None:
    stages = schedules("schedules.json").vs_stages

    assert stages[0].name == "Scorch Gorge"
    assert "high_resolution" in stages[0].original_image.url


def test_time_period_is_active() -> None:
    period = TimePeriod.model_validate({"startTime": "2026-11-16T08:00:00Z", "endTime": "2026-11-16T10:00:00Z"})

    assert not period.is_active(datetime(2026, 11, 16, 7, 59, tzinfo=UTC))
    assert period.is_active(datetime(2026, 11, 16, 8, tzinfo=UTC))
    assert not period.is_active(datetime(2026, 11, 16, 10, tzinfo=UTC))
