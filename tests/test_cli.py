import json

from conftest import TOY_AGENT

from trace_compare.cli import main

EXPECTED = TOY_AGENT / "expected"


def _assert_matches_expected(out_dir):
    for name in ("step_comparison.md", "divergences.json"):
        assert (out_dir / name).read_bytes() == (EXPECTED / name).read_bytes(), name


def test_demo_writes_expected_outputs_and_prints_table(tmp_path, capsys):
    main(["demo", "--out", str(tmp_path)])

    _assert_matches_expected(tmp_path)
    printed = capsys.readouterr().out
    assert "## Comparison 1" in printed
    assert "step 2 ToolSelector (selected_tools)" in printed


def test_compare_writes_expected_outputs_and_config(tmp_path):
    main(["compare", "--traces", str(TOY_AGENT / "traces"), "--agent", str(TOY_AGENT), "--out", str(tmp_path)])

    _assert_matches_expected(tmp_path)
    config = json.loads((tmp_path / "config.json").read_text())
    assert config["seed"] == 0
    assert config["num_pairs"] == 6
    assert [p["task"] for p in config["pairs"]] == [
        "flight-bos-den",
        "flight-lon-tyo",
        "flight-sea-sfo",
        "hotel-austin-calendar",
        "hotel-paris",
        "trip-chicago",
    ]


def test_expected_divergences_show_the_designed_failures():
    records = {r["task"]: r for r in json.loads((EXPECTED / "divergences.json").read_text())}

    for task in ("flight-bos-den", "flight-lon-tyo", "hotel-paris"):
        assert records[task]["first_divergence"]["component"] == "ToolSelector"
    for task in ("hotel-austin-calendar", "trip-chicago"):
        assert records[task]["first_divergence"]["component"] == "Planner"
    assert records["flight-sea-sfo"]["first_divergence"] is None
    assert records["flight-sea-sfo"]["end_state"] == "Final divergence: different agents are called for the two traces"
    assert records["flight-lon-tyo"]["end_state"] == "Final divergence: Failed trace completed"
