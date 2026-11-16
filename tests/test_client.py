from collections.abc import Awaitable, Callable

import pytest
from aiohttp import ClientResponseError, ClientSession, web
from aiohttp.test_utils import TestServer
from conftest import FIXTURES
from pydantic import ValidationError

from aiosplatoon3ink import Region, Splatoon3InkClient

type ServerFactory = Callable[[web.Application], Awaitable[TestServer]]

USER_AGENT = "aiosplatoon3ink-tests/1.0"


@pytest.fixture
async def feeds(aiohttp_server: ServerFactory) -> tuple[TestServer, list[str]]:
    """Serve the fixtures as splatoon3.ink serves its feeds, recording each request's User-Agent."""
    user_agents: list[str] = []

    async def serve(request: web.Request) -> web.StreamResponse:
        user_agents.append(request.headers.get("User-Agent", ""))
        if not (FIXTURES / request.match_info["name"]).is_file():
            raise web.HTTPNotFound()
        return web.FileResponse(FIXTURES / request.match_info["name"])

    async def serve_wrong_shape(request: web.Request) -> web.StreamResponse:
        return web.json_response({"data": {"regularSchedules": "not a connection"}})

    app = web.Application()
    app.router.add_get("/data/{name}", serve)
    app.router.add_get("/wrong-shape/{name}", serve_wrong_shape)
    return await aiohttp_server(app), user_agents


async def test_fetches_each_feed_with_the_user_agent(feeds: tuple[TestServer, list[str]]) -> None:
    server, user_agents = feeds

    async with Splatoon3InkClient(USER_AGENT, base_url=server.make_url("/data/")) as client:
        schedules = await client.schedules()
        gesotown = await client.gear()
        monthly_gear = await client.monthly_gear()
        festivals = await client.festivals()

    assert schedules.regular_schedules
    assert gesotown.pickup_brand.brand.name == "Firefin"
    assert monthly_gear.name == "Octavio Dome"
    assert festivals.in_region(Region.EU)
    assert user_agents == [USER_AGENT] * 4


async def test_closes_only_its_own_session(feeds: tuple[TestServer, list[str]]) -> None:
    server, _ = feeds

    client = Splatoon3InkClient(USER_AGENT, base_url=server.make_url("/data/"))
    await client.monthly_gear()
    session = client._session
    await client.close()
    assert session is not None and session.closed

    async with ClientSession() as shared:
        async with Splatoon3InkClient(USER_AGENT, session=shared, base_url=server.make_url("/data/")) as client:
            await client.monthly_gear()
        assert not shared.closed


async def test_raises_on_http_errors(feeds: tuple[TestServer, list[str]]) -> None:
    server, _ = feeds

    async with Splatoon3InkClient(USER_AGENT, base_url=server.make_url("/missing/")) as client:
        with pytest.raises(ClientResponseError) as raised:
            await client.schedules()
    assert raised.value.status == 404


async def test_raises_on_a_feed_of_the_wrong_shape(feeds: tuple[TestServer, list[str]]) -> None:
    server, _ = feeds

    async with Splatoon3InkClient(USER_AGENT, base_url=server.make_url("/wrong-shape/")) as client:
        with pytest.raises(ValidationError):
            await client.schedules()
