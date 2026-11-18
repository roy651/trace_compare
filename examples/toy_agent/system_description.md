This is a synthetic example. The agent, its prompts and all traces were written by hand to
demonstrate trace comparison; they do not come from a real system or real model runs.

Agent Workflow

Planner → ToolSelector → Executor (one call per tool use) → Verifier → Responder

Agent Roles

Planner: Reads the travel request, picks the apps needed (flights, hotels, payments, calendar) and lists the steps.
ToolSelector: Chooses the tools the Executor may call. The Executor cannot call a tool that was not selected.
Executor: Calls one tool per step and records the result.
Verifier: Checks the tool results against the request and reports the amount charged.
Responder: Writes the final message to the user. If the Responder is not reached, the task execution failed.
