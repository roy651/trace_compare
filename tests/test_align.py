from trace_compare.align import perform_step_comparison, perform_trace_comparison
from trace_compare.ir import TraceIR, TraceStep

RULES = {
    "Planner": {"fields": [{"schema_field_name": "apps", "comparison_mode": "exact_match"}]},
    "Executor": {"fields": [{"schema_field_name": "tool", "comparison_mode": "exact_match"}]},
    "Verifier": {"fields": [{"schema_field_name": "issues", "comparison_mode": "field_exists"}]},
}


def trace(*steps):
    result = TraceIR(trace_id="t")
    for number, (agent, output) in enumerate(steps):
        result.add_step(TraceStep(step_number=number, agent_name=agent, llm_output_structured=output))
    return result


def test_first_divergence_is_the_first_step_with_a_different_field():
    successful = trace(("Planner", {"apps": ["a"]}), ("Executor", {"tool": "x"}), ("Executor", {"tool": "y"}))
    failed = trace(("Planner", {"apps": ["a"]}), ("Executor", {"tool": "z"}), ("Executor", {"tool": "w"}))

    result = perform_trace_comparison(RULES, successful, failed)

    assert result.first_divergence == {
        "step": 2,
        "component": "Executor",
        "failed_fields": [{"field": "tool", "mode": "exact_match"}],
    }
    assert result.report.count("**First divergence between steps is detected**") == 1
    assert result.end_state == "Both traces completed"


def test_different_component_ends_the_walk():
    successful = trace(("Planner", {"apps": ["a"]}), ("Executor", {"tool": "x"}), ("Verifier", {}))
    failed = trace(("Planner", {"apps": ["a"]}), ("Verifier", {}), ("Executor", {"tool": "x"}))

    result = perform_trace_comparison(RULES, successful, failed)

    assert result.first_divergence is None
    assert result.end_state == "Final divergence: different agents are called for the two traces"
    assert "### Step 3" not in result.report


def test_failed_trace_that_ends_early():
    successful = trace(("Planner", {"apps": ["a"]}), ("Executor", {"tool": "x"}), ("Executor", {"tool": "y"}))
    failed = trace(("Planner", {"apps": ["a"]}), ("Executor", {"tool": "x"}))

    result = perform_trace_comparison(RULES, successful, failed)

    assert result.first_divergence is None
    assert result.end_state == "Final divergence: Failed trace completed"


def test_empty_failed_output_is_compared_against_the_retry():
    successful = trace(("Executor", {"tool": "x"}), ("Verifier", {"ok": 1}), ("Planner", {"apps": []}))
    failed = trace(("Executor", {}), ("Executor", {"tool": "x"}), ("Verifier", {"ok": 1}), ("Planner", {"apps": []}))

    result = perform_trace_comparison(RULES, successful, failed)

    assert result.first_divergence is None
    assert "Successful trace: x" in result.report
    assert "Failed trace: x" in result.report


def test_field_exists_detects_a_field_present_on_one_side_only():
    report, different = perform_step_comparison(
        RULES["Verifier"]["fields"], {"status": "ok"}, {"status": "ok", "issues": ["late"]}, False, "Verifier"
    )

    assert different == [{"field": "issues", "mode": "field_exists"}]
    assert "Different fields: issues\n\n" in report


def test_fields_missing_on_both_sides_are_skipped():
    report, different = perform_step_comparison(RULES["Executor"]["fields"], {"a": 1}, {"a": 2}, False, "Executor")

    assert different == []
    assert report == "Comparison could not be performed\n\n"
