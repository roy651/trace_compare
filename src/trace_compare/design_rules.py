"""Rule synthesis: one LLM call per component system prompt, producing the comparison rules file."""

import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from jinja2 import Template

from trace_compare.llm import LLMClient
from trace_compare.rules import RULES_FILE, load_agent_prompts

SYSTEM_MESSAGE = "You are an expert that analyses a system prompt of AI agent"


def parse_rule(agent_name: str, llm_output: str) -> dict[str, Any]:
    """Build one rules entry from the model's answer. An unparseable answer yields empty fields."""
    rule: dict[str, Any] = {"agent_name": agent_name}

    if llm_output[0:7] == "```json":
        llm_output = llm_output[7:]
    if llm_output[-3:] == "```":
        llm_output = llm_output[:-3]

    try:
        parsed = json.loads(llm_output)
        rule["output_schema"] = parsed["output_schema"]
        rule["fields"] = parsed["fields"]
    except Exception as e:
        print(f"Rule output for {agent_name} is not valid JSON: {e}")
        rule["output_schema"] = {}
        rule["fields"] = {}

    return rule


def design_rules(agent_dir: Path, model: str) -> Path:
    """Write rules.txt into agent_dir, one entry per component in the manifest."""
    template_text = files("trace_compare").joinpath("prompts/comparison_designer.jinja").read_text(encoding="utf-8")
    template = Template(template_text)
    client = LLMClient(model=model)

    rules_text = ""
    for agent_name, agent_prompt in load_agent_prompts(agent_dir).items():
        print(f"Designing rules for {agent_name} with {model} ...")
        llm_output = client.complete(template.render(agent_info=agent_prompt), SYSTEM_MESSAGE)
        rule_json = json.dumps(parse_rule(agent_name, llm_output), indent=4)
        print(rule_json + "\n")
        rules_text += rule_json + "\n\n"

    rules_path = agent_dir / RULES_FILE
    rules_path.write_text(rules_text, encoding="utf-8")
    return rules_path
