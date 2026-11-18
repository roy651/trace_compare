"""Read an agent config directory: manifest.json, rules.txt and system_description.md.

manifest.json is a list of entries:
    {"agent_name": "<component>", "system_prompt": "<file under the agent dir>",
     "normalizer": "<optional function name in trace_compare.normalizers>"}

rules.txt holds one JSON object per component, separated by blank lines:
    {"agent_name": "<component>", "output_schema": {...},
     "fields": [{"schema_field_name": "a.b[].c", "comparison_mode": "exact_match"}, ...]}
"""

import json
from pathlib import Path
from typing import Any

MANIFEST_FILE = "manifest.json"
RULES_FILE = "rules.txt"
SYSTEM_DESCRIPTION_FILE = "system_description.md"


def load_rules(rules_path: Path) -> dict[str, dict[str, Any]]:
    """Return the rules keyed by component name."""
    rules: dict[str, dict[str, Any]] = {}
    buffer = ""

    with open(rules_path, encoding="utf-8") as f:
        for line in f:
            if line.strip() == "":
                if buffer.strip():
                    _add_rule(rules, buffer)
                    buffer = ""
            else:
                buffer += line

    if buffer.strip():
        _add_rule(rules, buffer)

    return rules


def _add_rule(rules: dict[str, dict[str, Any]], block: str) -> None:
    rule = json.loads(block)
    rules[rule["agent_name"]] = rule


def load_manifest(agent_dir: Path) -> list[dict[str, str]]:
    return json.loads((agent_dir / MANIFEST_FILE).read_text(encoding="utf-8"))


def load_agent_prompts(agent_dir: Path) -> dict[str, str]:
    """Return component name to system prompt text, in manifest order."""
    return {
        entry["agent_name"]: (agent_dir / entry["system_prompt"]).read_text(encoding="utf-8")
        for entry in load_manifest(agent_dir)
    }


def load_normalizers(agent_dir: Path) -> dict[str, str]:
    """Return component name to normalizer function name, for entries that declare one."""
    return {entry["agent_name"]: entry["normalizer"] for entry in load_manifest(agent_dir) if "normalizer" in entry}
