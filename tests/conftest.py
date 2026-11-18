from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
TOY_AGENT = REPO / "examples" / "toy_agent"
CUGA_AGENT = REPO / "examples" / "cuga_appworld"
