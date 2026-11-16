"""Models for https://splatoon3.ink/data/schedules.json: every battle and Salmon Run rotation, and the current Splatfest.

The feed is SplatNet 3's ``StageScheduleQuery`` response, with images moved to splatoon3.ink's servers and a few
fields of splatoon3.ink's own, which start with ``__splatoon3ink``.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import AwareDatetime, Field

from aiosplatoon3ink._base import Color, Image, Nodes, Splatoon3InkModel
from aiosplatoon3ink.festivals import FestState


class VsRuleKey(StrEnum):
    """The rule of a battle, as SplatNet names it internally."""

    TURF_WAR = "TURF_WAR"
    SPLAT_ZONES = "AREA"
    TOWER_CONTROL = "LOFT"
    RAINMAKER = "GOAL"
    CLAM_BLITZ = "CLAM"
    TRICOLOR_TURF_WAR = "TRI_COLOR"


class VsRule(Splatoon3InkModel):
    """The rule of a battle."""

    id: str
    name: str
    """The rule's name in English, such as "Tower Control"."""
    rule: VsRuleKey


class VsStage(Splatoon3InkModel):
    """A battle stage, as a schedule lists it."""

    id: str
    vs_stage_id: int
    name: str
    image: Image
    """A small, low-resolution picture of the stage. :attr:`Schedules.vs_stages` has a large one."""


class VsSetting(Splatoon3InkModel):
    """The rule and stages of one rotation of a battle mode."""

    vs_rule: VsRule
    vs_stages: tuple[VsStage, ...]


class BankaraMode(StrEnum):
    """The two kinds of Anarchy Battle."""

    SERIES = "CHALLENGE"
    OPEN = "OPEN"


class BankaraMatchSetting(VsSetting):
    """The rule and stages of one kind of Anarchy Battle."""

    bankara_mode: BankaraMode


class FestMode(StrEnum):
    """The two kinds of Splatfest Battle."""

    OPEN = "REGULAR"
    PRO = "CHALLENGE"


class FestMatchSetting(VsSetting):
    """The rule and stages of one kind of Splatfest Battle."""

    fest_mode: FestMode


class LeagueMatchEvent(Splatoon3InkModel):
    """A Challenge: a limited-time event with its own rules."""

    id: str
    league_match_event_id: str
    """The event's internal name, such as ``SpecialRush_UltraStamp``."""
    name: str
    desc: str
    """A one-line summary. It can hold HTML line breaks (``<br />``) where the game wraps it."""
    regulation: str
    """The event's rules, in HTML: lines are separated by ``<br />``."""
    regulation_url: str | None


class LeagueMatchSetting(VsSetting):
    """The Challenge, rule and stages of one Challenge event."""

    league_match_event: LeagueMatchEvent


class TimePeriod(Splatoon3InkModel):
    """A span of time, from its start up to its end."""

    start_time: AwareDatetime
    end_time: AwareDatetime

    def is_active(self, now: datetime) -> bool:
        """Whether this period has started and not yet ended at ``now``, an aware datetime."""
        return self.start_time <= now < self.end_time


class RegularSchedule(TimePeriod):
    """One rotation of Regular Battle."""

    regular_match_setting: VsSetting | None
    """The rotation's rule and stages, or None while a Splatfest replaces Regular Battle."""


class BankaraSchedule(TimePeriod):
    """One rotation of Anarchy Battle, both Series and Open."""

    bankara_match_settings: tuple[BankaraMatchSetting, ...] | None
    """The rule and stages of each kind of Anarchy Battle, or None while a Splatfest replaces them."""

    def setting(self, mode: BankaraMode) -> BankaraMatchSetting | None:
        """The rule and stages of one kind of Anarchy Battle, if it's being played in this rotation."""
        return next((s for s in self.bankara_match_settings or () if s.bankara_mode == mode), None)


class XSchedule(TimePeriod):
    """One rotation of X Battle."""

    x_match_setting: VsSetting | None
    """The rotation's rule and stages, or None while a Splatfest replaces X Battle."""


class FestSchedule(TimePeriod):
    """One rotation of Splatfest Battle, both Open and Pro."""

    fest_match_settings: tuple[FestMatchSetting, ...] | None
    """The rule and stages of each kind of Splatfest Battle, or None when no Splatfest is running."""

    def setting(self, mode: FestMode) -> FestMatchSetting | None:
        """The rule and stages of one kind of Splatfest Battle, if it's being played in this rotation."""
        return next((s for s in self.fest_match_settings or () if s.fest_mode == mode), None)


class EventSchedule(Splatoon3InkModel):
    """A Challenge event, and the periods during which it can be played."""

    league_match_setting: LeagueMatchSetting
    time_periods: tuple[TimePeriod, ...]


class CoopRule(StrEnum):
    """The kind of a Salmon Run rotation."""

    REGULAR = "REGULAR"
    BIG_RUN = "BIG_RUN"
    EGGSTRA_WORK = "TEAM_CONTEST"


class CoopBoss(Splatoon3InkModel):
    """A King Salmonid."""

    id: str
    name: str


class CoopStage(Splatoon3InkModel):
    """A Salmon Run stage."""

    id: str
    name: str
    image: Image
    thumbnail_image: Image


class CoopWeapon(Splatoon3InkModel):
    """A weapon supplied in a Salmon Run rotation.

    A random weapon is listed as one named "Random", and a random rare weapon as one with Grizzco's name.
    """

    splatoon3ink_id: str = Field(alias="__splatoon3ink_id")
    """A stable ID that splatoon3.ink derives from the weapon, to look it up in its translations."""
    name: str
    image: Image


class CoopSetting(Splatoon3InkModel):
    """The stage, weapons and King Salmonid of a Salmon Run rotation."""

    rule: CoopRule | None = None
    """The kind of rotation. splatoon3.ink's feed has stopped carrying it for regular rotations."""
    boss: CoopBoss | None = None
    """The King Salmonid, which Eggstra Work doesn't have."""
    coop_stage: CoopStage
    weapons: tuple[CoopWeapon, ...]


class CoopSchedule(TimePeriod):
    """One Salmon Run rotation."""

    setting: CoopSetting
    king_salmonid_guess: str | None = Field(default=None, alias="__splatoon3ink_king_salmonid_guess")
    """splatoon3.ink's guess at the King Salmonid, by name."""


class CoopGroupingSchedule(Splatoon3InkModel):
    """Every Salmon Run rotation, by kind."""

    banner_image: Image | None
    """The banner announcing an upcoming Big Run or Eggstra Work, if one is scheduled."""
    regular_schedules: Nodes[CoopSchedule]
    big_run_schedules: Nodes[CoopSchedule]
    team_contest_schedules: Nodes[CoopSchedule]
    """Eggstra Work rotations."""


class TricolorStage(Splatoon3InkModel):
    """A stage of a Splatfest's Tricolor Turf War."""

    id: str
    name: str
    image: Image


class CurrentFestTeam(Splatoon3InkModel):
    """A team of the running Splatfest. Its name is in the Splatfest's record in the festivals feed."""

    id: str
    color: Color


class CurrentFest(Splatoon3InkModel):
    """The Splatfest being played in the region splatoon3.ink's schedules come from."""

    id: str
    title: str
    start_time: AwareDatetime
    end_time: AwareDatetime
    midterm_time: AwareDatetime
    """When the second half starts, and with it Tricolor Turf War."""
    state: FestState
    teams: tuple[CurrentFestTeam, ...]
    tricolor_stages: tuple[TricolorStage, ...] | None = None


class VsStageDetail(Splatoon3InkModel):
    """A battle stage, with a large picture."""

    id: str
    vs_stage_id: int
    name: str
    original_image: Image


class Schedules(Splatoon3InkModel):
    """Every battle and Salmon Run rotation SplatNet lists, and the current Splatfest.

    Each list runs from the current rotation, which may already have ended if the feed is up to an hour old, to about a
    day ahead.
    """

    regular_schedules: Nodes[RegularSchedule]
    bankara_schedules: Nodes[BankaraSchedule]
    """Anarchy Battle rotations."""
    x_schedules: Nodes[XSchedule]
    event_schedules: Nodes[EventSchedule]
    """Challenge events."""
    fest_schedules: Nodes[FestSchedule]
    coop_grouping_schedule: CoopGroupingSchedule
    """Salmon Run rotations."""
    current_fest: CurrentFest | None
    vs_stages: Nodes[VsStageDetail]
    """Every battle stage, with a large picture of each."""


class _SchedulesFeed(Splatoon3InkModel):
    data: Schedules


__all__ = [
    "BankaraMatchSetting",
    "BankaraMode",
    "BankaraSchedule",
    "CoopBoss",
    "CoopGroupingSchedule",
    "CoopRule",
    "CoopSchedule",
    "CoopSetting",
    "CoopStage",
    "CoopWeapon",
    "CurrentFest",
    "CurrentFestTeam",
    "EventSchedule",
    "FestMatchSetting",
    "FestMode",
    "FestSchedule",
    "LeagueMatchEvent",
    "LeagueMatchSetting",
    "RegularSchedule",
    "Schedules",
    "TimePeriod",
    "TricolorStage",
    "VsRule",
    "VsRuleKey",
    "VsSetting",
    "VsStage",
    "VsStageDetail",
    "XSchedule",
]
