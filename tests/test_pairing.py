from conftest import TOY_AGENT

from trace_compare.pairing import build_pairs, collect_traces

BY_TASK = {
    "t1": {"pass": ["t1/p1", "t1/p2"], "fail": ["t1/f1", "t1/f2", "t1/f3"]},
    "t2": {"pass": ["t2/p1"], "fail": ["t2/f1"]},
    "t3": {"pass": ["t3/p1"], "fail": []},
}


def test_collect_traces_reads_pass_and_fail_folders():
    by_task = collect_traces(TOY_AGENT / "traces")

    assert len(by_task) == 6
    assert len(by_task["hotel-austin-calendar"]["pass"]) == 2
    assert len(by_task["hotel-austin-calendar"]["fail"]) == 2


def test_all_permutations_pairs_every_combination_and_skips_one_sided_tasks():
    pairs = build_pairs(BY_TASK, "all_permutations")

    assert len(pairs) == 2 * 3 + 1
    assert {task for task, _, _ in pairs} == {"t1", "t2"}


def test_one_pair_per_task_is_deterministic_for_a_seed():
    first = build_pairs(BY_TASK, "one_pair_per_task", seed=7)

    assert first == build_pairs(BY_TASK, "one_pair_per_task", seed=7)
    assert [task for task, _, _ in first] == ["t1", "t2"]
    seen = {build_pairs(BY_TASK, "one_pair_per_task", seed=s)[0] for s in range(20)}
    assert len(seen) > 1


def test_n_pairs_takes_at_most_n():
    assert len(build_pairs(BY_TASK, "n_pairs", n=1, seed=3)) == 1
    assert len(build_pairs(BY_TASK, "n_pairs", n=10, seed=3)) == 2


def test_all_trajectories_uses_every_trace():
    pairs = build_pairs(BY_TASK, "all_trajectories", seed=1)
    t1_pairs = [(s, f) for task, s, f in pairs if task == "t1"]

    assert len(t1_pairs) == 3
    assert {s for s, _ in t1_pairs} == {"t1/p1", "t1/p2"}
    assert {f for _, f in t1_pairs} == {"t1/f1", "t1/f2", "t1/f3"}


def test_max_pairs_caps_the_result():
    assert len(build_pairs(BY_TASK, "all_permutations", max_pairs=4, seed=0)) == 4
    assert len(build_pairs(BY_TASK, "all_permutations", max_pairs=None)) == 7
