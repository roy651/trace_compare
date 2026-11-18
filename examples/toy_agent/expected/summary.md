# Failure Clusters

## ToolSelector drops the booking (write) tool from the selected tool set
**Severity:** high

In the majority of tasks the first divergence is in `ToolSelector.selected_tools`: the mutating booking tool (`flights.book`, `hotels.book`) is omitted while the search and payment tools are kept. Because the Executor may only call selected tools, the booking step becomes unexecutable, yet the payment step still runs.

**Examples:**
- Comparison 1 (Boston→Denver): `['flights.search','flights.book','payments.charge']` vs `['flights.search','payments.charge']`.
- Comparison 2 (London→Tokyo): same omission of `flights.book`.
- Comparison 5 (Louvre hotel): `hotels.book` omitted; only search + charge selected.

---

## Payment executed without a confirmed booking (unsafe side effect)
**Severity:** high

Once the booking tool is missing, the Executor still calls `payments.charge`, so the user's card is charged with no reservation. Verifier flags it only after the irreversible action has happened.

**Examples:**
- Comparison 1: Verifier `status=failed`, issues `['card charged but no booking reference']`, amount 212.40 charged.
- Comparison 5: issues `['payment taken but no reservation exists']`, 418.00 EUR charged.
- Responder messages: "I charged 212.40 USD but could not confirm a booking", "Payment … went through, but the room is not reserved."

---

## Planner under-decomposes compound, multi-app requests
**Severity:** high

For requests containing a secondary clause ("…and add to my calendar", "…and a hotel there"), the Planner drops the second app from `required_apps` and the corresponding step, and the truncated intent loses the clause. This propagates to ToolSelector and Executor.

**Examples:**
- Comparison 4: `required_apps` missing `calendar`; 3 steps instead of 4; calendar event never created.
- Comparison 6: `required_apps` missing `hotels`; steps become flight search+book instead of flight book + hotel book.
- Comparison 6 intent: "and a hotel for two nights" loses the "there" (Chicago) binding.

---

## Verifier accepts incomplete executions (shallow validation)
**Severity:** high

The Verifier reports `status=ok` when plan steps were never executed or when the charged amount covers only part of the request. It validates presence of a charge, not coverage of the user's request.

**Examples:**
- Comparison 4: `status=ok`, `issues=None` although no `calendar.add_event` was ever called.
- Comparison 6: `status=ok` with amount 289.00 vs expected 689.00 (hotel never booked, never detected).

---

## Executor re-calls a completed read tool instead of surfacing the missing tool
**Severity:** medium

When the required booking tool is absent from the selection, the Executor silently substitutes/repeats `flights.search` / `hotels.search` rather than aborting or requesting re-selection. This also shifts all later steps by one position, making traces hard to align.

**Examples:**
- Comparisons 1, 2, 5 step 4: expected `flights.book`/`hotels.book`, actual repeated `*.search`.
- Comparison 4 steps 4–6: executed `hotels.search`, `hotels.book`, `payments.charge` — one step behind the reference trace.

---

## Premature exit from the execution loop (early Responder handoff)
**Severity:** medium

Even with a fully correct tool selection, the failed model can leave the Executor loop after the first tool call, skipping Verifier entirely, or terminate the trace mid-execution.

**Examples:**
- Comparison 3: after `flights.search`, failed trace calls Responder where the successful trace continues with Executor (agent-identity divergence).
- Comparison 2: failed trace ends at step 4 after the repeated `flights.search`.

---

## Responder under-reports scope and omits unfulfilled steps
**Severity:** low

Final answers reflect the truncated plan without explicitly telling the user what was not done, so partial failures look like successes.

**Examples:**
- Comparison 4: "Riverside Lodge … is booked" — no mention that the calendar entry is missing.
- Comparison 6: "Booked AA 2210 … for 289.00 USD" — hotel silently dropped.

---

# Root Causes

## ToolSelector has no plan-step → tool coverage constraint
Nothing forces `selected_tools` to contain at least one tool per Planner step, and the prompt appears to favour a minimal/deduplicated tool list. Mutating tools (`*.book`) are the ones dropped, likely because the search tool is treated as sufficient for the "flight/hotel" app. The Executor's hard constraint ("cannot call a tool that was not selected") turns this omission into an unrecoverable gap.

**Related clusters:** ToolSelector drops the booking (write) tool from the selected tool set, Executor re-calls a completed read tool instead of surfacing the missing tool, Payment executed without a confirmed booking

## No transactional invariant between booking and payment
The pipeline treats `payments.charge` as an independent step rather than one gated on a booking reference. There is no precondition check or rollback, so an irreversible financial action executes on an incomplete plan.

**Related clusters:** Payment executed without a confirmed booking, Verifier accepts incomplete executions

## Planner prompt does not enforce clause-by-clause decomposition
Compound requests with a trailing or subordinate clause are summarised into a single primary goal; `intent`, `required_apps`, and `steps` are generated from that compressed intent, so the secondary app (calendar, hotels) is never requested. Planner errors are the earliest and most damaging divergence since every downstream agent inherits them.

**Related clusters:** Planner under-decomposes compound, multi-app requests, Responder under-reports scope and omits unfulfilled steps

## Verifier checks only status/amount fields, not request coverage
The Verifier has no access to (or no obligation to compare against) the original request and the full plan: it does not assert a booking reference per booking step, does not confirm every planned step executed, and does not reconcile the charged amount against expected components. `approximate_numeric` on `amount` also hides large discrepancies when the Verifier itself reports the wrong total (289 vs 689).

**Related clusters:** Verifier accepts incomplete executions, Payment executed without a confirmed booking, Responder under-reports scope

## Missing orchestration guard on loop termination
Control flow permits a transition from Executor to Responder (or trace end) before all plan steps are consumed and before the Verifier runs. There is no "all steps executed or explicit abort" gate.

**Related clusters:** Premature exit from the execution loop, Executor re-calls a completed read tool instead of surfacing the missing tool

## Executor lacks a failure path for unavailable tools
Faced with a needed-but-unselected tool, the Executor improvises (repeats the previous read call) instead of raising an error or triggering re-selection, masking the upstream defect and desynchronising step indices.

**Related clusters:** Executor re-calls a completed read tool instead of surfacing the missing tool, Premature exit from the execution loop

---

# Remediation Actions

## Enforce plan-step → tool coverage in ToolSelector with a schema validator
**Severity:** high

Add a deterministic post-check: every Planner step must map to at least one tool in `selected_tools`, and any step whose action is a mutation (`book`, `charge`, `add_event`) must map to the corresponding write tool. Reject and re-prompt ToolSelector on violation. Update its system prompt with examples where search and book tools are both required for one app.

**Related clusters:** ToolSelector drops the booking (write) tool, Executor re-calls a completed read tool, Payment executed without a confirmed booking

## Gate payments on a confirmed booking reference
**Severity:** high

Make `payments.charge` require a non-empty booking/reservation ID produced by a prior `*.book` call. If absent, block the call and route to an error/abort path instead of charging. Add compensating action (void/refund) when a charge exists without a booking.

**Related clusters:** Payment executed without a confirmed booking, Verifier accepts incomplete executions

## Strengthen the Verifier into a coverage checker
**Severity:** high

Require the Verifier to (a) receive the original request and the full plan, (b) assert one confirmation artifact per planned booking/calendar step, (c) reconcile the reported `amount` against the sum of executed charges, and (d) return `status=failed` with explicit `issues` whenever any planned step has no result. Treat any `issues` entry as a hard failure for the run.

**Related clusters:** Verifier accepts incomplete executions, Payment executed without a confirmed booking, Responder under-reports scope

## Revise the Planner prompt for compound multi-app requests
**Severity:** high

Add explicit instruction and few-shot examples: enumerate every clause of the request, keep the full intent text, and emit one step per clause (including calendar entries and secondary bookings with inherited location/date context). Add a validator that flags intents containing conjunctions ("and", "also", "add to") whose `required_apps` has fewer apps than detected clauses.

**Related clusters:** Planner under-decomposes compound multi-app requests, Responder under-reports scope

## Add an orchestration gate before the Responder
**Severity:** medium

Forbid the Executor→Responder transition until every plan step has a recorded result and the Verifier has run; otherwise force continuation or an explicit abort with reason. Log step index alignment so skipped/duplicated steps are detected automatically.

**Related clusters:** Premature exit from the execution loop, Executor re-calls a completed read tool

## Give the Executor an explicit "tool unavailable" failure path
**Severity:** medium

Prohibit repeating an already-successful read-only call and prohibit substituting a different tool for the current step. On a missing tool, emit a structured error that triggers ToolSelector re-selection (bounded retries) instead of silently improvising.

**Related clusters:** Executor re-calls a completed read tool, ToolSelector drops the booking (write) tool

## Require the Responder to disclose unfulfilled steps
**Severity:** medium

Template the final answer to enumerate each requested item with its outcome (booked / not booked / not done), and to lead with any Verifier `issues` (e.g., charge without reservation) including next steps for the user.

**Related clusters:** Responder under-reports scope, Payment executed without a confirmed booking

## Add regression tests for each failure cluster
**Severity:** medium

Unit/integration tests: (1) compound request with calendar clause → calendar app and tool present; (2) multi-app flight+hotel request → both book tools called; (3) tool-selection with a missing book tool → run aborts before charging; (4) truncated execution → Responder blocked; (5) amount reconciliation mismatch → Verifier fails.

**Related clusters:** All clusters

---