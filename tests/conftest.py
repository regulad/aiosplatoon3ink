from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str) -> bytes:
    """A feed as splatoon3.ink served it; see fixtures/README.md."""
    return (FIXTURES / name).read_bytes()
