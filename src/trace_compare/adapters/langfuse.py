"""Read a Langfuse trace JSON export into a TraceIR.

Each GENERATION observation becomes one step, in startTime order. The component that made
the call is identified by matching its system prompt against the known component prompts.
"""

import json
import os
import re
from datetime import datetime
from typing import Any

from trace_compare import normalizers as normalizer_functions
from trace_compare.ir import TraceIR, TraceStep

PROMPT_PREFIX_LENGTH = 100

_JINJA_ONLY_LINE = re.compile(r"^\s*(\{%-?.*?-?%\}|\{\{.*?\}\}|\s)*\s*$")


def _strip_jinja_prefix(text):
    """Skip leading lines that contain only Jinja tags ({% %} or {{ }}) or are empty."""
    for i, line in enumerate(text.split("\n")):
        if not _JINJA_ONLY_LINE.match(line):
            return "\n".join(text.split("\n")[i:]).lstrip("\n")
    return ""


def get_agent_name_from_prompt(agent_prompts, system_prompt):
    """
    Return the component whose prompt shares the first 100 characters with system_prompt
    (whole-text equality when either is shorter), or "Unknown Agent".
    """
    agent_name = "Unknown Agent"
    system_prompt_cmp = _strip_jinja_prefix(system_prompt).lstrip("\n")

    for name in agent_prompts.keys():
        current_system_prompt = _strip_jinja_prefix(agent_prompts[name]).lstrip("\n")
        if len(current_system_prompt) >= PROMPT_PREFIX_LENGTH and len(system_prompt_cmp) >= PROMPT_PREFIX_LENGTH:
            if current_system_prompt[0:PROMPT_PREFIX_LENGTH] == system_prompt_cmp[0:PROMPT_PREFIX_LENGTH]:
                agent_name = name
                break
        else:
            if current_system_prompt == system_prompt_cmp:
                agent_name = name
                break

    return agent_name


def load_langfuse_trace(
    file_path: str,
    agent_prompts: dict[str, str],
    normalizers: dict[str, str],
) -> TraceIR:
    """
    Load one Langfuse trace export.

    Args:
        file_path: Path to the trace JSON file.
        agent_prompts: Component name to system prompt text.
        normalizers: Component name to a function name in trace_compare.normalizers,
            applied when that component's output is not valid JSON.
    """
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    trace_id = data.get("id", os.path.basename(file_path).split(".")[0])
    trace = TraceIR(trace_id=trace_id)
    trace.task_formulation = _read_task_formulation(data.get("input"))

    observations = data.get("observations", [])
    generation_observations = [obs for obs in observations if obs.get("type") == "GENERATION"]
    generation_observations.sort(key=lambda x: x.get("startTime", ""))

    for step_number, observation in enumerate(generation_observations):
        trace.add_step(_read_step(step_number, observation, agent_prompts, normalizers))

    return trace


def _read_task_formulation(raw_input: Any) -> str | None:
    """
    The task text comes from the trace-level input: either a dict with an "intent" key,
    or a list of chat messages whose first user message holds it. Non-string content
    (multi-modal blocks) is ignored.
    """
    candidate: Any = None
    if isinstance(raw_input, dict):
        candidate = raw_input.get("intent")
    elif isinstance(raw_input, list):
        candidate = next(
            (m.get("content") for m in raw_input if isinstance(m, dict) and m.get("role") == "user"),
            None,
        )
    return candidate if isinstance(candidate, str) else None


def _read_step(
    step_number: int,
    observation: dict[str, Any],
    agent_prompts: dict[str, str],
    normalizers: dict[str, str],
) -> TraceStep:
    system_prompt = None
    user_input = None
    llm_output = None

    # First system and first user message of the call
    input_data = observation.get("input", [])
    if isinstance(input_data, list):
        for message in input_data:
            if isinstance(message, dict):
                role = message.get("role")
                content = message.get("content")

                if role == "system" and system_prompt is None:
                    system_prompt = content
                elif role == "user" and user_input is None:
                    user_input = content

    output_data = observation.get("output")
    if isinstance(output_data, dict) and output_data.get("role") == "assistant":
        llm_output = output_data.get("content")

    metadata = observation.get("metadata", {})

    # Match the system prompt; fall back to metadata only when there is nothing to match
    agent_name = None
    if agent_prompts and system_prompt:
        agent_name = get_agent_name_from_prompt(agent_prompts, system_prompt)
    if agent_name is None:
        agent_name = metadata.get("langgraph_node", observation.get("name", "Unknown"))

    return TraceStep(
        step_number=step_number,
        agent_name=agent_name,
        system_prompt=system_prompt,
        user_input=user_input,
        llm_output_raw=llm_output,
        llm_output_structured=_parse_llm_output(llm_output, agent_name, normalizers),
        start_time=_parse_timestamp(observation.get("startTime")),
        end_time=_parse_timestamp(observation.get("endTime")),
        metadata={
            "observation_id": observation.get("id"),
            "observation_name": observation.get("name"),
            "model": observation.get("model"),
            "langgraph_node": metadata.get("langgraph_node"),
            "langgraph_step": metadata.get("langgraph_step"),
        },
    )


def _parse_llm_output(llm_output: str | None, agent_name: str, normalizers: dict[str, str]):
    """Parse the output as JSON; otherwise apply the component's normalizer, if any; otherwise {}."""
    if not llm_output:
        return {}

    try:
        return json.loads(llm_output)

    except Exception as e:
        print(f"LLM output for {agent_name} is not valid JSON: {e}")

        if agent_name in normalizers:
            parsing_function = getattr(normalizer_functions, normalizers[agent_name])

            try:
                return parsing_function(llm_output)
            except Exception as e2:
                print(f"Parsing function for {agent_name} failed: {e2}")

        return {}


def _parse_timestamp(timestamp_str: str | None) -> datetime | None:
    if not timestamp_str:
        return None

    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except Exception as e:
        print(f"Failed to parse timestamp {timestamp_str}: {e}")
        return None
