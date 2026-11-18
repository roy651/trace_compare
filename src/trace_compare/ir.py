"""Format-independent representation of a trace: an ordered list of LLM steps."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TraceStep:
    """One LLM call made by one component of the agent."""

    step_number: int
    agent_name: str
    system_prompt: str | None = None
    user_input: str | None = None
    llm_output_raw: str | None = None
    llm_output_structured: dict[str, Any] | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.llm_output_structured is None:
            self.llm_output_structured = {}


@dataclass
class TraceIR:
    """A complete trace of one task execution."""

    trace_id: str
    task_formulation: str | None = None
    steps: list[TraceStep] = field(default_factory=list)
    agent_sequence: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_step(self, step: TraceStep) -> None:
        self.steps.append(step)
        self.agent_sequence.append(step.agent_name)

    def get_step(self, step_number: int) -> TraceStep | None:
        """Return the step at a 0-based position, or None when out of range."""
        if 0 <= step_number < len(self.steps):
            return self.steps[step_number]
        return None

    @property
    def num_steps(self) -> int:
        return len(self.steps)
