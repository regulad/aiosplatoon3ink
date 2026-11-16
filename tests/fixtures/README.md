# Fixtures

Feeds exactly as splatoon3.ink served them, chosen so the tests cover each shape the feeds take. The data comes from
SplatNet 3 through [splatoon3.ink](https://splatoon3.ink/).

| File | Served | Shows |
| --- | --- | --- |
| `schedules.json` | 2026-11-16, live | No Splatfest: every battle mode, a Challenge, regular Salmon Run |
| `schedules-splatfest.json` | 2026-01-10 22:20 UTC, [Wayback Machine](https://web.archive.org/web/20260110222036/https://splatoon3.ink/data/schedules.json) | A Splatfest's first half: Splatfest Battles replace the other modes |
| `schedules-splatfest-scheduled.json` | 2025-02-07 08:06 UTC, [Wayback Machine](https://web.archive.org/web/20250207080620/https://splatoon3.ink/data/schedules.json) | A Splatfest announced but not yet started |
| `schedules-big-run.json` | 2025-06-15 02:10 UTC, [Wayback Machine](https://web.archive.org/web/20250615021027/https://splatoon3.ink/data/schedules.json) | A Big Run |
| `schedules-eggstra-work.json` | 2025-05-08 04:46 UTC, [Wayback Machine](https://web.archive.org/web/20250508044653/https://splatoon3.ink/data/schedules.json) | An upcoming Eggstra Work |
| `gear.json` | 2026-11-16, live | SplatNet's shop |
| `coop.json` | 2026-11-16, live | The month's Salmon Run reward gear |
| `festivals.json` | 2026-11-16, live | Every Splatfest in every region, back to the first in September 2022 |

The live tests (`pytest -m live`) check the models against the feeds as they are now.
