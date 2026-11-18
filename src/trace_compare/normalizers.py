"""Turn non-JSON component output into a dict of fields the rules can address.

A manifest entry selects one of these by name with `"normalizer": "<function name>"`.
They run only when the output is not valid JSON.
"""

import re


def extract_reflection_fields_v2(text: str) -> dict[str, str]:
    """
    Extract overall_status_analysis and strategic_recommendation from a
    reflection-style output with markdown headers, bold labels or plain-text titles.
    """
    decoded = text.replace("\r\n", "\n").replace("\r", "\n")

    def normalize(line: str) -> str:
        s = line.strip().strip("*_`#> -\t")
        return re.sub(r"\s+", " ", s).lower()

    # Keys starting with "_" bound the sections during slicing but are not returned.
    heading_aliases = {
        "overall_status_analysis": (
            "overall status analysis",
            "overall status",
            "status analysis",
        ),
        "_progress_summary": (
            "summary of progress",
            "progress summary",
        ),
        "strategic_recommendation": (
            "strategic recommendation",
            "recommendation",
        ),
    }

    lines = decoded.split("\n")
    first_pos: dict[str, int] = {}
    for i, line in enumerate(lines):
        norm = normalize(line)
        for key, needles in heading_aliases.items():
            if key not in first_pos and any(n in norm for n in needles):
                first_pos[key] = i
                break

    if not first_pos:
        return {}

    ordered = sorted(first_pos.items(), key=lambda kv: kv[1])
    result: dict[str, str] = {}
    for idx, (key, header_idx) in enumerate(ordered):
        start = header_idx + 1
        end = ordered[idx + 1][1] if idx + 1 < len(ordered) else len(lines)
        if not key.startswith("_"):
            result[key] = "\n".join(lines[start:end]).strip()

    return result


def extract_code_agent_content(text: str) -> dict[str, str]:
    """
    Return the text of a code-writing output with fenced Python blocks removed:
    brief reasoning before the code, a plain-language answer, or "" for code only.
    """
    content = re.sub(r"```(?:python)?\s*.*?```", "", text, flags=re.DOTALL)
    return {"content": content.strip()}
