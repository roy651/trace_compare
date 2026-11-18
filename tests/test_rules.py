from conftest import CUGA_AGENT

from trace_compare.rules import load_agent_prompts, load_normalizers, load_rules


def test_rules_are_blank_line_separated_json_keyed_by_component(tmp_path):
    rules_file = tmp_path / "rules.txt"
    rules_file.write_text(
        '{\n  "agent_name": "A",\n  "fields": []\n}\n\n\n'
        '{"agent_name": "B",\n "fields": [{"schema_field_name": "x", "comparison_mode": "exact_match"}]}'
    )

    rules = load_rules(rules_file)

    assert list(rules) == ["A", "B"]
    assert rules["B"]["fields"][0]["schema_field_name"] == "x"


def test_cuga_manifest_maps_prompts_and_normalizers():
    prompts = load_agent_prompts(CUGA_AGENT)

    assert len(prompts) == 7
    assert prompts["Reflection"].startswith("As an advanced strategic guidance")
    assert load_normalizers(CUGA_AGENT) == {
        "Code Agent": "extract_code_agent_content",
        "Reflection": "extract_reflection_fields_v2",
    }
