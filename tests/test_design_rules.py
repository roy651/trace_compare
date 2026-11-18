import pytest

from trace_compare.design_rules import parse_rule

ANSWER = (
    '{"output_schema": {"status": "string"}, '
    '"fields": [{"schema_field_name": "status", "comparison_mode": "exact_match"}]}'
)


@pytest.mark.parametrize(
    "llm_output",
    [ANSWER, f"```json\n{ANSWER}\n```", f"```json\n{ANSWER}\n```\n", f"\n{ANSWER}\n"],
    ids=["bare", "fenced", "fenced with trailing newline", "surrounding whitespace"],
)
def test_parse_rule_accepts_bare_and_fenced_answers(llm_output):
    rule = parse_rule("Verifier", llm_output)

    assert rule["agent_name"] == "Verifier"
    assert rule["fields"] == [{"schema_field_name": "status", "comparison_mode": "exact_match"}]


def test_parse_rule_yields_no_fields_for_an_unparseable_answer():
    assert not parse_rule("Verifier", "I cannot help with that.")["fields"]
