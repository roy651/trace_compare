"""The report must stay byte-identical to what the original cuga-eval code produced.

The golden files were written by the original run_comparison on the same pairs:
- toy: examples/toy_agent, all_permutations (9 pairs).
- cuga: CUGA prompts and rules, synthetic CUGA-shaped traces with non-JSON Code Agent and
  Reflection outputs, both retry-skip branches, an unmatched prompt and a metadata fallback.

semantic_calls.json records every semantic_similarity decision of that run (with the real
embedding model), so the cuga test can run without torch.
"""

import json

import pytest
from conftest import CUGA_AGENT, TESTS, TOY_AGENT

from trace_compare import align
from trace_compare.pairing import build_pairs, collect_traces

GOLDEN = TESTS / "golden"


def _run(traces_dir, agent_dir, out_dir):
    pairs = build_pairs(collect_traces(traces_dir), "all_permutations")
    align.run_comparison(pairs, agent_dir, out_dir)
    return (out_dir / "step_comparison.md").read_bytes()


def test_toy_report_matches_original_code(tmp_path):
    report = _run(TOY_AGENT / "traces", TOY_AGENT, tmp_path)
    assert report == (GOLDEN / "toy" / "step_comparison.md").read_bytes()


def test_cuga_report_matches_original_code(tmp_path, monkeypatch):
    calls = json.loads((GOLDEN / "cuga" / "semantic_calls.json").read_text())
    recorded = {json.dumps([c["successful"], c["failed"]]): c["similar"] for c in calls}
    monkeypatch.setitem(align.VALUE_COMPARISONS, "semantic_similarity", lambda x, y: recorded[json.dumps([x, y])])

    report = _run(GOLDEN / "cuga" / "traces", CUGA_AGENT, tmp_path)
    assert report == (GOLDEN / "cuga" / "step_comparison.md").read_bytes()


def test_cuga_report_matches_original_code_with_real_model(tmp_path):
    pytest.importorskip("sentence_transformers")
    report = _run(GOLDEN / "cuga" / "traces", CUGA_AGENT, tmp_path)
    assert report == (GOLDEN / "cuga" / "step_comparison.md").read_bytes()
