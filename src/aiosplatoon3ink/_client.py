from types import TracebackType
from typing import Self

from aiohttp import ClientSession, ClientTimeout
from yarl import URL

from aiosplatoon3ink.festivals import Festivals
from aiosplatoon3ink.gear import Gesotown, MonthlyGear, _CoopFeed, _GearFeed
from aiosplatoon3ink.schedules import Schedules, _SchedulesFeed

DEFAULT_BASE_URL = URL("https://splatoon3.ink/data/")


class Splatoon3InkClient:
    """Reads the data feeds that splatoon3.ink publishes.

    splatoon3.ink updates its feeds once an hour. Its terms ask that clients cache rather than fetch more often than
    that, send a User-Agent that says how to reach them, credit splatoon3.ink wherever the data is shown, and stay free
    of charge: https://github.com/misenhower/splatoon3.ink/wiki/Data-Access

    Each method raises :class:`aiohttp.ClientError` when a request fails, and :class:`pydantic.ValidationError` when a
    feed doesn't have the shape the models expect.
    """

    def __init__(
        self,
        user_agent: str,
        *,
        session: ClientSession | None = None,
        base_url: URL | str = DEFAULT_BASE_URL,
    ) -> None:
        """
        :param user_agent: Sent with every request, so splatoon3.ink can tell who to contact if something goes wrong:
            for example, ``"MyBot/1.0 (+https://github.com/me/mybot)"``.
        :param session: A session to make requests with, which the caller keeps and closes. Without one, the client
            opens its own on the first request and closes it in :meth:`close`.
        :param base_url: Where the feeds are served from.
        """
        self.user_agent = user_agent
        self.base_url = URL(base_url)
        self._session = session
        self._owns_session = session is None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the session the client opened, if it opened one."""
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def _get(self, path: str) -> bytes:
        if self._session is None:
            self._session = ClientSession(timeout=ClientTimeout(total=30))
        async with self._session.get(self.base_url / path, headers={"User-Agent": self.user_agent}) as response:
            response.raise_for_status()
            return await response.read()

    async def schedules(self) -> Schedules:
        """Fetch every battle and Salmon Run rotation, and the current Splatfest."""
        return _SchedulesFeed.model_validate_json(await self._get("schedules.json")).data

    async def gear(self) -> Gesotown:
        """Fetch the gear on sale at SplatNet's shop."""
        return _GearFeed.model_validate_json(await self._get("gear.json")).data.gesotown

    async def monthly_gear(self) -> MonthlyGear:
        """Fetch the month's Salmon Run reward gear."""
        return _CoopFeed.model_validate_json(await self._get("coop.json")).data.coop_result.monthly_gear

    async def festivals(self) -> Festivals:
        """Fetch every Splatfest, in each region."""
        return Festivals.model_validate_json(await self._get("festivals.json"))


__all__ = ["DEFAULT_BASE_URL", "Splatoon3InkClient"]
