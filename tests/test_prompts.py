from conftest import CUGA_AGENT, TESTS
from jinja2 import Template

from trace_compare.diagnose import render_prompt

REPORT = "## Comparison 1\n\n### Task: example\n\n### Step 1\n\nSuccessful trace: Code Agent\n\n"


def test_root_cause_prompt_for_cuga_is_byte_identical_to_original():
    original_template = (TESTS / "fixtures" / "root_cause_analysis_original.jinja").read_text(encoding="utf-8")
    original = Template(original_template).render(trace_comparison_report=REPORT)

    system_description = (CUGA_AGENT / "system_description.md").read_text(encoding="utf-8")
    assert render_prompt(REPORT, system_description) == original
