"""Stage 1-2: walk a successful and a failed trace side by side and compare each step's output.

The walk is positional. It stops at the first step where the two traces call different
components, and it records the first step whose outputs differ under the rules.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trace_compare.adapters.langfuse import load_langfuse_trace
from trace_compare.ir import TraceIR
from trace_compare.modes import VALUE_COMPARISONS, both_or_none
from trace_compare.rules import RULES_FILE, load_agent_prompts, load_normalizers, load_rules

REPORT_FILE = "step_comparison.md"
DIVERGENCES_FILE = "divergences.json"

# Steps of these components are skipped when both outputs are one of the listed values.
# Kept from the CUGA setup; it has no effect for components with other names.
SKIP_STEP_OUTPUT_RULES = {"APIPlannerAgent": [""]}


@dataclass
class PairComparison:
    report: str
    first_divergence: dict[str, Any] | None
    end_state: str | None


def get_nested_from_dict(d, s):
    """
    Read a value by dot-separated path. When the path reaches a list, the next key is
    applied to every element and a list of results is returned ("a[].b" and "a.b" both
    fan out; "[]" is only a marker). Returns None when the root is not a dict or a key is missing.
    """
    if not isinstance(d, dict):
        return None

    keys = s.split(".")
    curr: Any = d

    for key in keys:
        key = key.replace("[]", "")
        if isinstance(curr, dict):
            if key in curr:
                curr = curr[key]
            else:
                return None

        elif isinstance(curr, list):
            curr = [elem[key] if isinstance(elem, dict) and key in elem else None for elem in curr]

        else:
            return None

    return curr


def _field_header(field_name, successful_value, failed_value, mode) -> str:
    return (
        f"\nComparison field: {field_name}\n"
        f"\nSuccessful trace: {successful_value}\n"
        f"\nFailed trace: {failed_value}\n"
        f"\nComparison mode: {mode}\n"
    )


def perform_step_comparison(
    fields: list[dict[str, str]],
    successful_output,
    failed_output,
    divergence_found: bool,
    agent_name: str,
) -> tuple[str, list[dict[str, str]]]:
    """
    Compare one step's outputs field by field.

    Returns the report text for the step and the fields that differ, as {field, mode}.
    """
    report = ""
    at_least_one_match = False
    different_fields: list[dict[str, str]] = []

    for rule in fields:
        field_name = rule["schema_field_name"]
        mode = rule["comparison_mode"]

        successful_value = get_nested_from_dict(successful_output, field_name)
        failed_value = get_nested_from_dict(failed_output, field_name)

        if mode == "field_exists":
            report += _field_header(field_name, successful_value, failed_value, mode)
            is_similar = both_or_none(successful_value, failed_value)

        elif successful_value is not None and failed_value is not None:
            report += _field_header(field_name, successful_value, failed_value, mode)
            if mode not in VALUE_COMPARISONS:
                print(
                    f"Warning: unknown comparison mode {mode!r} for field {field_name!r} "
                    f"(agent: {agent_name!r}) — skipping."
                )
                continue
            is_similar = VALUE_COMPARISONS[mode](successful_value, failed_value)

        else:
            continue

        if is_similar:
            at_least_one_match = True
            report += "Fields are similar\n\n"
        else:
            report += "**Fields are different**\n\n"
            different_fields.append({"field": field_name, "mode": mode})

    if at_least_one_match and not different_fields:
        report += "**Step outputs are similar**\n\n"
    elif different_fields:
        report += "**Step outputs are different**\n\n"
    else:
        report += "Comparison could not be performed\n\n"

    if not divergence_found and different_fields:
        report += f"**First divergence between steps is detected**\nAgent name: {agent_name}\nDifferent fields: "
        report += ", ".join(f["field"] for f in different_fields) + "\n\n"

    return report, different_fields


def perform_trace_comparison(
    rules: dict[str, dict[str, Any]],
    successful_trace: TraceIR,
    failed_trace: TraceIR,
) -> PairComparison:
    """Walk the two traces step by step. This is the algorithm used for the paper's results."""
    num_steps1 = successful_trace.num_steps
    num_steps2 = failed_trace.num_steps

    report = ""
    first_divergence = None
    end_state = None
    divergence_found = False

    current_successful_step = 0
    current_failed_step = 0
    step_counter = 1

    comparison_length = min(num_steps1, num_steps2)

    while current_successful_step < num_steps1 and current_failed_step < num_steps2:
        step1 = successful_trace.get_step(current_successful_step)
        step2 = failed_trace.get_step(current_failed_step)

        current_successful_agent = step1.agent_name
        current_failed_agent = step2.agent_name

        current_successful_output = step1.llm_output_structured
        current_failed_output = step2.llm_output_structured

        if current_successful_agent == current_failed_agent:
            skip_output_values = SKIP_STEP_OUTPUT_RULES.get(current_successful_agent)
            if (
                skip_output_values is not None
                and current_failed_output in skip_output_values
                and current_successful_output in skip_output_values
            ):
                current_successful_step += 1
                current_failed_step += 1
                continue

        step_label = step_counter
        report += f"### Step {step_label}\n\n"
        step_counter += 1

        report += f"Successful trace: {current_successful_agent}\n\n"
        report += f"Failed trace: {current_failed_agent}\n\n"

        if current_successful_agent != current_failed_agent:
            end_state = "Final divergence: different agents are called for the two traces"
            report += f"**{end_state}**\n\n\n"
            break

        if current_successful_agent in rules:
            # Retry heuristic: when one side has an empty output and that side's component
            # is called again next while the other side moves on, compare against the retry.
            if current_failed_step < comparison_length - 1 and current_successful_step < comparison_length - 1:
                if current_successful_output and not current_failed_output:
                    next_step1 = successful_trace.get_step(current_successful_step + 1)
                    next_step2 = failed_trace.get_step(current_failed_step + 1)
                    if (
                        next_step1
                        and next_step2
                        and next_step1.agent_name != current_successful_agent
                        and next_step2.agent_name == current_failed_agent
                    ):
                        current_failed_step += 1
                        step2 = failed_trace.get_step(current_failed_step)
                        if step2:
                            current_failed_output = step2.llm_output_structured

                elif not current_successful_output and current_failed_output:
                    next_step1 = successful_trace.get_step(current_successful_step + 1)
                    next_step2 = failed_trace.get_step(current_failed_step + 1)
                    if (
                        next_step1
                        and next_step2
                        and next_step2.agent_name != current_failed_agent
                        and next_step1.agent_name == current_successful_agent
                    ):
                        current_successful_step += 1
                        step1 = successful_trace.get_step(current_successful_step)
                        if step1:
                            current_successful_output = step1.llm_output_structured

            if not current_failed_output:
                report += "Output of failed trace is empty\n\n"

            if current_successful_output and current_failed_output:
                step_report, different_fields = perform_step_comparison(
                    rules[current_successful_agent]["fields"],
                    current_successful_output,
                    current_failed_output,
                    divergence_found,
                    current_successful_agent,
                )
                report += step_report
                if different_fields and not divergence_found:
                    first_divergence = {
                        "step": step_label,
                        "component": current_successful_agent,
                        "failed_fields": different_fields,
                    }
                    divergence_found = True

        successful_at_end = current_successful_step >= num_steps1 - 1
        failed_at_end = current_failed_step >= num_steps2 - 1
        if successful_at_end and not failed_at_end:
            end_state = "Final divergence: Successful trace completed"
        elif failed_at_end and not successful_at_end:
            end_state = "Final divergence: Failed trace completed"
        elif successful_at_end and failed_at_end:
            end_state = "Both traces completed"
        if successful_at_end or failed_at_end:
            report += f"**{end_state}**\n\n\n"

        current_successful_step += 1
        current_failed_step += 1

    return PairComparison(report, first_divergence, end_state)


def _task_heading(successful_trace: TraceIR, failed_trace: TraceIR) -> str:
    """Pick the task text for the report heading, warning when the two traces disagree."""
    task1 = successful_trace.task_formulation
    task2 = failed_trace.task_formulation

    if task1 is None and task2 is None:
        print("Warning! Task formulations were not found.")
        return "Unknown Task"
    if task1 is None:
        print("Warning! First task formulation was not found.")
        return task2
    if task2 is None:
        print("Warning! Second task formulation was not found.")
    elif task1.strip() != task2.strip():
        print(f"Warning! Task formulations are not synced.\n{task1}\n{task2}")
    return task1


def run_comparison(pairs: list[tuple[str, str, str]], agent_dir: Path, out_dir: Path) -> list[dict[str, Any]]:
    """
    Compare each (task_id, successful_path, failed_path) pair and write
    step_comparison.md and divergences.json into out_dir. Returns the divergence records.
    """
    rules = load_rules(agent_dir / RULES_FILE)
    agent_prompts = load_agent_prompts(agent_dir)
    normalizers = load_normalizers(agent_dir)

    report = ""
    records = []

    for comparison_number, (task_id, successful_path, failed_path) in enumerate(pairs, start=1):
        successful_trace = load_langfuse_trace(successful_path, agent_prompts, normalizers)
        failed_trace = load_langfuse_trace(failed_path, agent_prompts, normalizers)

        result = perform_trace_comparison(rules, successful_trace, failed_trace)

        report += f"## Comparison {comparison_number}\n\n"
        report += "### Task: " + _task_heading(successful_trace, failed_trace) + "\n\n"
        report += result.report

        records.append(
            {
                "comparison": comparison_number,
                "task": task_id,
                "successful_trace": Path(successful_path).stem,
                "failed_trace": Path(failed_path).stem,
                "first_divergence": result.first_divergence,
                "end_state": result.end_state,
            }
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / REPORT_FILE).write_text(report, encoding="utf-8")
    (out_dir / DIVERGENCES_FILE).write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    return records
