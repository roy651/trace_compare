import json

from trace_compare.adapters.langfuse import load_langfuse_trace

PLANNER_PROMPT = "You are the planner. " * 10


def generation(name, start, system, output):
    return {
        "type": "GENERATION",
        "name": name,
        "startTime": start,
        "input": [{"role": "system", "content": system}, {"role": "user", "content": "go"}],
        "output": {"role": "assistant", "content": output},
        "metadata": {"langgraph_node": name},
    }


def test_generations_are_sorted_and_other_observations_ignored(tmp_path):
    trace_file = tmp_path / "trace.json"
    trace_file.write_text(
        json.dumps(
            {
                "id": "t1",
                "input": [{"role": "user", "content": "Book it"}],
                "observations": [
                    generation("second", "2026-01-01T00:00:02Z", "Some other prompt", "not json"),
                    {"type": "SPAN", "name": "tool", "startTime": "2026-01-01T00:00:01Z"},
                    generation("first", "2026-01-01T00:00:00Z", PLANNER_PROMPT + "extra", '{"apps": ["a"]}'),
                ],
            }
        )
    )

    trace = load_langfuse_trace(str(trace_file), {"Planner": PLANNER_PROMPT}, {})

    assert trace.task_formulation == "Book it"
    assert trace.agent_sequence == ["Planner", "Unknown Agent"]
    assert trace.steps[0].llm_output_structured == {"apps": ["a"]}
    assert trace.steps[1].llm_output_structured == {}


def test_metadata_name_is_used_when_no_prompts_are_given(tmp_path):
    trace_file = tmp_path / "trace.json"
    trace_file.write_text(json.dumps({"observations": [generation("planner_node", "1", "x", "{}")]}))

    assert load_langfuse_trace(str(trace_file), {}, {}).agent_sequence == ["planner_node"]
