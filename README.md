# aiosplatoon3ink

An asyncio client for the Splatoon 3 data that [splatoon3.ink](https://splatoon3.ink/) publishes, with typed,
immutable [pydantic](https://docs.pydantic.dev/) models of each feed.

```python
from datetime import UTC, datetime

from aiosplatoon3ink import Splatoon3InkClient
from aiosplatoon3ink.schedules import BankaraMode

async with Splatoon3InkClient("MyBot/1.0 (+https://github.com/me/mybot)") as client:
    schedules = await client.schedules()

now = datetime.now(UTC)
rotation = next(node for node in schedules.bankara_schedules if node.is_active(now))
if (series := rotation.setting(BankaraMode.SERIES)) is not None:
    print(series.vs_rule.name, [stage.name for stage in series.vs_stages])
```

## Feeds

| Method | Feed | Returns |
| --- | --- | --- |
| `schedules()` | [`schedules.json`](https://splatoon3.ink/data/schedules.json) | Every battle and Salmon Run rotation, Challenge events, and the current Splatfest |
| `festivals()` | [`festivals.json`](https://splatoon3.ink/data/festivals.json) | Every Splatfest and its results, in each of the four regions |
| `gear()` | [`gear.json`](https://splatoon3.ink/data/gear.json) | Gear on sale at SplatNet's shop |
| `monthly_gear()` | [`coop.json`](https://splatoon3.ink/data/coop.json) | The month's Salmon Run reward gear |

The models follow SplatNet 3's field names in snake_case, so `vsStages` becomes `vs_stages`. Where SplatNet's internal
names differ from the game's, the enums use the game's: `VsRuleKey.TOWER_CONTROL` is `"LOFT"`, and
`BankaraMode.SERIES` is `"CHALLENGE"`. Fields about splatoon3.ink's own Nintendo account are left out, and fields the
models don't know are ignored. Each method raises `aiohttp.ClientError` when a request fails, and
`pydantic.ValidationError` when a feed has a shape the models don't expect.

The translations under `data/locale/` and the X Rank leaderboards aren't modelled yet.

## Using splatoon3.ink's data

splatoon3.ink's [terms](https://github.com/misenhower/splatoon3.ink/wiki/Data-Access) ask that you:

- credit splatoon3.ink wherever you show its data;
- fetch each feed at most once an hour, since that's how often it updates, and cache it in between;
- send a User-Agent that says how to reach you, which the client requires;
- keep whatever you build free of charge.

## Installing

It isn't on PyPI. Install it from git, pinned to a commit:

```sh
poetry add "git+https://github.com/regulad/aiosplatoon3ink.git#<commit>"
```

## Developing

```sh
poetry install --with type
poetry run pytest              # against the snapshots in tests/fixtures
poetry run pytest -m live      # against splatoon3.ink's feeds as they are now
poetry run mypy src tests
poetry run pre-commit run --all-files
```

## License

AGPL-3.0. The data belongs to Nintendo, and reaches you through SplatNet 3 and splatoon3.ink.
