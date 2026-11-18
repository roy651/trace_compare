"""Stage 3: one LLM call over the whole step comparison report, producing failure clusters,
root causes and remediation actions."""

from importlib.resources import files
from pathlib import Path

from jinja2 import Template

from trace_compare.llm import LLMClient
from trace_compare.rules import SYSTEM_DESCRIPTION_FILE

SYSTEM_MESSAGE = "You are an expert that analyzes trace comparison reports for a multi-agent system"


def render_prompt(trace_comparison_report: str, system_description: str) -> str:
    template_text = files("trace_compare").joinpath("prompts/root_cause_analysis.jinja").read_text(encoding="utf-8")
    return Template(template_text).render(
        trace_comparison_report=trace_comparison_report,
        system_description=system_description,
    )


def diagnose(report_path: Path, agent_dir: Path, model: str, out_path: Path) -> Path:
    """Write the root-cause analysis for report_path to out_path and return out_path."""
    report = report_path.read_text(encoding="utf-8")
    system_description = (agent_dir / SYSTEM_DESCRIPTION_FILE).read_text(encoding="utf-8")

    client = LLMClient(model=model)
    print(f"Running root cause analysis with {model} ...")
    analysis = client.complete(render_prompt(report, system_description), SYSTEM_MESSAGE)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(analysis, encoding="utf-8")
    print(analysis)
    if client.last_usage:
        print(f"Token usage: {client.last_usage}")
    return out_path
