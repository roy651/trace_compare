"""Command line entry point: demo, compare, design-rules, diagnose."""

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from trace_compare.align import DIVERGENCES_FILE, REPORT_FILE, run_comparison
from trace_compare.pairing import MAX_PAIRS_DEFAULT, PAIRING_MODES, build_pairs, collect_traces
from trace_compare.rules import RULES_FILE

CONFIG_FILE = "config.json"
REPO_ROOT = Path(__file__).resolve().parents[2]
TOY_AGENT_DIR = REPO_ROOT / "examples" / "toy_agent"


def compare(
    traces_dir: Path,
    agent_dir: Path,
    out_dir: Path,
    pairing_mode: str = "one_pair_per_task",
    n: int = 5,
    max_pairs: int = MAX_PAIRS_DEFAULT,
    task_ids: list[str] | None = None,
    seed: int = 0,
) -> list[dict]:
    """Pair the traces, compare each pair, and write the report, divergences and config into out_dir."""
    by_task = collect_traces(traces_dir)

    if task_ids:
        unknown = [t for t in task_ids if t not in by_task]
        if unknown:
            print(f"Warning: task IDs not found: {unknown}")
        by_task = {t: by_task[t] for t in task_ids if t in by_task}

    pairs = build_pairs(by_task, pairing_mode, n, None if max_pairs == 0 else max_pairs, seed)
    if not pairs:
        sys.exit("No task has both a pass and a fail trace. Nothing to compare.")
    print(f"Comparing {len(pairs)} pair(s) using mode '{pairing_mode}'.")

    records = run_comparison(pairs, agent_dir, out_dir)

    config = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "traces_dir": str(traces_dir),
        "agent_dir": str(agent_dir),
        "pairing_mode": pairing_mode,
        "n": n,
        "max_pairs": max_pairs,
        "seed": seed,
        "task_ids": task_ids,
        "num_pairs": len(pairs),
        "pairs": [
            {
                "comparison": r["comparison"],
                "task": r["task"],
                "successful_trace": r["successful_trace"],
                "failed_trace": r["failed_trace"],
            }
            for r in records
        ],
    }
    (out_dir / CONFIG_FILE).write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return records


def print_divergence_table(records: list[dict]) -> None:
    rows = [("#", "task", "first divergence", "end state")]
    for r in records:
        divergence = r["first_divergence"]
        if divergence:
            fields = ", ".join(f["field"] for f in divergence["failed_fields"])
            where = f"step {divergence['step']} {divergence['component']} ({fields})"
        else:
            where = "none"
        rows.append((str(r["comparison"]), r["task"], where, r["end_state"] or ""))

    widths = [max(len(row[i]) for row in rows) for i in range(4)]
    for row in rows:
        print("  ".join(cell.ljust(width) for cell, width in zip(row, widths)).rstrip())


def run_demo(args) -> None:
    if not TOY_AGENT_DIR.is_dir():
        sys.exit("The demo uses examples/toy_agent from the trace-compare repository; clone it and run from there.")

    out_dir = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="trace-compare-demo-"))
    records = compare(TOY_AGENT_DIR / "traces", TOY_AGENT_DIR, out_dir)

    print((out_dir / REPORT_FILE).read_text(encoding="utf-8"))
    print_divergence_table(records)
    print(f"\nOutputs written to {out_dir}")


def run_compare(args) -> None:
    out_dir = Path(args.out)
    compare(
        Path(args.traces),
        Path(args.agent),
        out_dir,
        args.pairing_mode,
        args.n,
        args.max_pairs,
        args.task_ids,
        args.seed,
    )
    for name in (REPORT_FILE, DIVERGENCES_FILE, CONFIG_FILE):
        print(f"Wrote {out_dir / name}")


def run_design_rules(args) -> None:
    from trace_compare.design_rules import design_rules

    agent_dir = Path(args.agent)
    if (agent_dir / RULES_FILE).exists() and not args.force:
        sys.exit(f"{agent_dir / RULES_FILE} exists. Pass --force to overwrite it.")
    print(f"Wrote {design_rules(agent_dir, args.model)}")


def run_diagnose(args) -> None:
    from trace_compare.diagnose import diagnose

    report_path = Path(args.report)
    out_path = Path(args.out) if args.out else report_path.parent / "summary.md"
    print(f"Wrote {diagnose(report_path, Path(args.agent), args.model, out_path)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="trace-compare", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    demo = commands.add_parser("demo", help="Compare the bundled synthetic example (no model calls).")
    demo.add_argument("--out", help="Output directory (default: a new temporary directory).")
    demo.set_defaults(handler=run_demo)

    compare_cmd = commands.add_parser("compare", help="Pair traces and compare them step by step (no model calls).")
    compare_cmd.add_argument("--traces", required=True, help="Directory laid out as <task_id>/{pass,fail}/*.json.")
    compare_cmd.add_argument("--agent", required=True, help="Agent config directory with manifest.json and rules.txt.")
    compare_cmd.add_argument("--pairing-mode", default="one_pair_per_task", choices=PAIRING_MODES)
    compare_cmd.add_argument("--n", type=int, default=5, help="Number of pairs for n_pairs mode (default: 5).")
    compare_cmd.add_argument(
        "--max-pairs",
        type=int,
        default=MAX_PAIRS_DEFAULT,
        help=f"Cap for all_permutations and all_trajectories (default: {MAX_PAIRS_DEFAULT}; 0 disables).",
    )
    compare_cmd.add_argument("--task-ids", nargs="+", help="Only compare these task IDs.")
    compare_cmd.add_argument("--seed", type=int, default=0, help="Seed for random pairing (default: 0).")
    compare_cmd.add_argument("--out", default="trace-compare-output", help="Output directory.")
    compare_cmd.set_defaults(handler=run_compare)

    design = commands.add_parser("design-rules", help="Generate rules.txt from the component prompts (LLM).")
    design.add_argument("--agent", required=True, help="Agent config directory with manifest.json.")
    design.add_argument("--model", required=True, help="Any LiteLLM model string.")
    design.add_argument("--force", action="store_true", help="Overwrite an existing rules.txt.")
    design.set_defaults(handler=run_design_rules)

    diagnose_cmd = commands.add_parser("diagnose", help="Root-cause analysis of a step comparison report (LLM).")
    diagnose_cmd.add_argument("--report", required=True, help="Path to step_comparison.md.")
    diagnose_cmd.add_argument("--agent", required=True, help="Agent config directory with system_description.md.")
    diagnose_cmd.add_argument("--model", required=True, help="Any LiteLLM model string.")
    diagnose_cmd.add_argument("--out", help="Output file (default: summary.md next to the report).")
    diagnose_cmd.set_defaults(handler=run_diagnose)

    return parser


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    args = build_parser().parse_args(argv)
    args.handler(args)
