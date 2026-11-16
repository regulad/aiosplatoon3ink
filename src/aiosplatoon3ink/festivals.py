"""Models for https://splatoon3.ink/data/festivals.json: every Splatfest, in each of SplatNet's four regions.

Each region's list is SplatNet 3's ``FestRecordQuery`` response, with each Splatfest's details from
``DetailFestRecordDetailQuery`` merged in. Fields about splatoon3.ink's own account, such as its team and votes, are
left out.
"""

from enum import StrEnum
from typing import Annotated, Any

from pydantic import AwareDatetime, BeforeValidator, Field

from aiosplatoon3ink._base import Color, Image, Splatoon3InkModel


class Region(StrEnum):
    """A region that holds its own Splatfests."""

    US = "US"
    """The Americas, Australia and New Zealand."""
    EU = "EU"
    """Europe."""
    JP = "JP"
    """Japan."""
    AP = "AP"
    """Hong Kong and South Korea (Asia/Pacific)."""


# splatoon3.ink's ID for a Splatfest starts with a letter for each region that held it, such as "JUEA-00108".
_REGION_LETTERS = {"U": Region.US, "E": Region.EU, "J": Region.JP, "A": Region.AP}


class FestState(StrEnum):
    """How far along a Splatfest is."""

    SCHEDULED = "SCHEDULED"
    FIRST_HALF = "FIRST_HALF"
    SECOND_HALF = "SECOND_HALF"
    CLOSED = "CLOSED"


class FestTeamRole(StrEnum):
    """A team's side in Tricolor Turf War: the leading team defends against the other two."""

    ATTACK = "ATTACK"
    DEFENSE = "DEFENSE"


class FestTeamResult(Splatoon3InkModel):
    """A team's results in a Splatfest, once announced.

    Each category has a ratio, the team's share of it, and flags for the teams that came first and second. SplatNet
    calls conch shells ``horagai``, Splatfest Battle (Open) ``regular`` and Splatfest Battle (Pro) ``challenge``.
    """

    is_winner: bool
    is_second_winner: bool | None = None
    total_point: int | None = None

    vote_ratio: float
    is_vote_ratio_top: bool
    is_vote_ratio_second: bool | None = None
    vote_point: int | None = None

    horagai_ratio: float
    """The team's share of conch shells."""
    is_horagai_ratio_top: bool
    is_horagai_ratio_second: bool | None = None
    horagai_point: int | None = None

    regular_contribution_ratio: float
    """The team's share of the wins in Splatfest Battle (Open)."""
    is_regular_contribution_ratio_top: bool
    is_regular_contribution_ratio_second: bool | None = None
    regular_contribution_point: int | None = None

    challenge_contribution_ratio: float
    """The team's share of the wins in Splatfest Battle (Pro)."""
    is_challenge_contribution_ratio_top: bool
    is_challenge_contribution_ratio_second: bool | None = None
    challenge_contribution_point: int | None = None

    tricolor_contribution_ratio: float | None = None
    """The team's share of the wins in Tricolor Turf War, which early Splatfests didn't count."""
    is_tricolor_contribution_ratio_top: bool | None = None
    is_tricolor_contribution_ratio_second: bool | None = None
    tricolor_contribution_point: int | None = None


class FestTeam(Splatoon3InkModel):
    """A team in a Splatfest."""

    id: str
    team_name: str
    color: Color
    image: Image
    role: FestTeamRole | None
    """The team's side in Tricolor Turf War, once the second half starts."""
    result: FestTeamResult | None
    """The team's results, once announced."""


class Fest(Splatoon3InkModel):
    """A Splatfest."""

    splatoon3ink_id: str = Field(alias="__splatoon3ink_id")
    """splatoon3.ink's ID for the Splatfest, shared by every region that held it, such as ``JUEA-00108``."""
    id: str
    """SplatNet's ID for the Splatfest, which differs between regions."""
    title: str
    start_time: AwareDatetime
    end_time: AwareDatetime
    state: FestState
    image: Image
    is_votable: bool
    teams: tuple[FestTeam, ...]

    @property
    def regions(self) -> frozenset[Region]:
        """The regions that held this Splatfest."""
        letters = self.splatoon3ink_id.partition("-")[0]
        return frozenset(region for letter, region in _REGION_LETTERS.items() if letter in letters)

    @property
    def has_results(self) -> bool:
        """Whether the results have been announced."""
        return any(team.result is not None for team in self.teams)


def _unwrap_fest_records(value: Any) -> Any:
    # Each region is SplatNet's whole response: {"data": {"festRecords": {"nodes": [...]}}}.
    if isinstance(value, dict) and "data" in value:
        return value["data"]["festRecords"]["nodes"]
    return value


type _FestRecords = Annotated[tuple[Fest, ...], BeforeValidator(_unwrap_fest_records)]


class Festivals(Splatoon3InkModel):
    """Every Splatfest, newest first, for each region."""

    us: _FestRecords = Field(alias="US")
    eu: _FestRecords = Field(alias="EU")
    jp: _FestRecords = Field(alias="JP")
    ap: _FestRecords = Field(alias="AP")

    def in_region(self, region: Region) -> tuple[Fest, ...]:
        """Every Splatfest held in a region, newest first."""
        match region:
            case Region.US:
                return self.us
            case Region.EU:
                return self.eu
            case Region.JP:
                return self.jp
            case Region.AP:
                return self.ap


__all__ = ["Fest", "FestState", "FestTeam", "FestTeamResult", "FestTeamRole", "Festivals", "Region"]
