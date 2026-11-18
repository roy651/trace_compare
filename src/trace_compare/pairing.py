"""Collect traces from <traces_dir>/<task_id>/{pass,fail}/*.json and pair successes with failures."""

import random
from itertools import product
from pathlib import Path

PAIRING_MODES = ["all_permutations", "one_pair_per_task", "n_pairs", "all_trajectories"]
MAX_PAIRS_DEFAULT = 50


def collect_traces(traces_dir: Path) -> dict[str, dict[str, list[str]]]:
    """Return {task_id: {"pass": [paths], "fail": [paths]}}, with paths sorted by name."""
    by_task = {}
    for task_dir in sorted(p for p in traces_dir.iterdir() if p.is_dir()):
        by_task[task_dir.name] = {
            outcome: [str(p) for p in sorted((task_dir / outcome).glob("*.json"))] for outcome in ("pass", "fail")
        }
    return by_task


def build_pairs(
    by_task: dict[str, dict[str, list[str]]],
    pairing_mode: str,
    n: int = 1,
    max_pairs: int | None = MAX_PAIRS_DEFAULT,
    seed: int = 0,
) -> list[tuple[str, str, str]]:
    """
    Build (task_id, successful_path, failed_path) pairs. Tasks without both outcomes are skipped.

    Modes:
        all_permutations   every (success, failure) combination per task
        one_pair_per_task  one random pair per task
        n_pairs            one random pair per task, then n of those at random
        all_trajectories   every trace takes part in at least one pair (per task: shuffle
                           both lists, then zip, recycling the shorter list)

    max_pairs caps all_permutations and all_trajectories; None disables the cap.
    """
    rng = random.Random(seed)
    pairs: list[tuple[str, str, str]] = []

    for task_id, outcomes in sorted(by_task.items()):
        successes = list(outcomes["pass"])
        failures = list(outcomes["fail"])
        if not successes or not failures:
            continue

        if pairing_mode == "all_permutations":
            for s, f in product(successes, failures):
                pairs.append((task_id, s, f))
        elif pairing_mode in ("one_pair_per_task", "n_pairs"):
            pairs.append((task_id, rng.choice(successes), rng.choice(failures)))
        elif pairing_mode == "all_trajectories":
            rng.shuffle(successes)
            rng.shuffle(failures)
            for i in range(max(len(successes), len(failures))):
                pairs.append((task_id, successes[i % len(successes)], failures[i % len(failures)]))

    if pairing_mode == "n_pairs":
        rng.shuffle(pairs)
        pairs = pairs[:n]

    if pairing_mode in ("all_permutations", "all_trajectories") and max_pairs is not None:
        if len(pairs) > max_pairs:
            print(f"Capping {len(pairs)} pairs to --max-pairs {max_pairs}.")
            rng.shuffle(pairs)
            pairs = pairs[:max_pairs]

    return pairs
